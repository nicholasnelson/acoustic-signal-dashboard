"""Reproducible, read-only comparison of MIMII 6 dB fan and DCASE 2025 fan.

The script audits every WAV header, selects balanced deterministic cohorts, applies
the same channel preparation and 26 feature definitions to both datasets, and
writes descriptive cross-dataset effect sizes. It does not fit a detector, tune a
threshold, pool training data, or modify either source dataset.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import wave
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from matplotlib import pyplot as plt
from scipy.io import wavfile
from scipy.signal import welch
from scipy.stats import ks_2samp, wasserstein_distance

plt.switch_backend("Agg")


SEED = 40122
FEATURES = (
    "rms",
    "rms_dbfs",
    "peak",
    "peak_dbfs",
    "amplitude_mean",
    "amplitude_std",
    "amplitude_p01",
    "amplitude_p05",
    "amplitude_p50",
    "amplitude_p95",
    "amplitude_p99",
    "clipping_ratio",
    "zero_crossing_rate",
    "spectral_centroid_hz",
    "spectral_bandwidth_hz",
    "total_power",
    "low_power",
    "low_mid_power",
    "mid_power",
    "high_mid_power",
    "high_power",
    "low_ratio",
    "low_mid_ratio",
    "mid_ratio",
    "high_mid_ratio",
    "high_ratio",
)
BANDS = {
    "low": (20.0, 250.0),
    "low_mid": (250.0, 500.0),
    "mid": (500.0, 2000.0),
    "high_mid": (2000.0, 4000.0),
    "high": (4000.0, 8000.0),
}
TRAPEZOID = getattr(np, "trapezoid", np.trapz)
DCASE_PATTERN = re.compile(
    r"^section_(?P<section>\d+)_(?P<domain>source|target)_"
    r"(?P<split>train|test)_(?P<condition>normal|anomaly)_"
    r"(?P<index>\d+)_(?P<d1p>[^_]+)_(?P<d1v>[^.]+)\.wav$",
    re.IGNORECASE,
)
DCASE_NOISE_PATTERN = re.compile(
    r"^section_(?P<section>\d+)_noise_(?P<index>\d+)_"
    r"(?P<d1p>[^_]+)_(?P<d1v>[^.]+)\.wav$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Record:
    dataset: str
    path: Path
    relative_path: str
    file_id: str
    condition: str
    machine_id: str = ""
    domain: str = ""
    split: str = ""
    section: str = ""
    attribute: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mimii-root",
        required=True,
        type=Path,
        help="Root containing fan/id_XX/{normal,abnormal}; e.g. .../extracted/6dB",
    )
    parser.add_argument(
        "--dcase-root",
        required=True,
        type=Path,
        help="DCASE 2025 Task 2 development fan root containing train/test/supplemental",
    )
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--summary-json", required=True, type=Path)
    parser.add_argument("--plot", required=True, type=Path)
    parser.add_argument("--per-dataset", type=int, default=200)
    parser.add_argument("--seed", type=int, default=SEED)
    return parser.parse_args()


def stable_id(*parts: str, length: int = 24) -> str:
    return hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()[:length]


def discover_mimii(root: Path) -> list[Record]:
    root = root.resolve()
    records: list[Record] = []
    for path in sorted(root.glob("fan/id_*/*/*.wav"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        parts = relative.split("/")
        if len(parts) != 4 or parts[2].lower() not in {"normal", "abnormal"}:
            continue
        source_condition = parts[2].lower()
        condition = "anomaly" if source_condition == "abnormal" else "normal"
        file_id = stable_id("MIMII", "public-1.0", "6", relative.lower())
        records.append(
            Record(
                dataset="MIMII",
                path=path.resolve(),
                relative_path=relative,
                file_id=file_id,
                condition=condition,
                machine_id=parts[1].lower(),
                split="unspecified",
            )
        )
    if not records:
        raise FileNotFoundError(f"No MIMII fan WAV files found below {root}")
    return records


def discover_dcase(root: Path) -> list[Record]:
    root = root.resolve()
    records: list[Record] = []
    for path in sorted(root.glob("*/*.wav"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        match = DCASE_PATTERN.match(path.name)
        noise = DCASE_NOISE_PATTERN.match(path.name)
        if match:
            fields = match.groupdict()
            records.append(
                Record(
                    dataset="DCASE",
                    path=path.resolve(),
                    relative_path=relative,
                    file_id=stable_id(
                        "DCASE 2025 Task 2 Development",
                        "2025-development",
                        relative.lower(),
                    ),
                    condition=fields["condition"].lower(),
                    domain=fields["domain"].lower(),
                    split=fields["split"].lower(),
                    section=fields["section"],
                    attribute=fields["d1v"],
                )
            )
        elif noise:
            fields = noise.groupdict()
            records.append(
                Record(
                    dataset="DCASE",
                    path=path.resolve(),
                    relative_path=relative,
                    file_id=stable_id(
                        "DCASE 2025 Task 2 Development",
                        "2025-development",
                        relative.lower(),
                    ),
                    condition="noise",
                    split="supplemental",
                    section=fields["section"],
                    attribute=fields["d1v"],
                )
            )
        else:
            raise ValueError(f"Unrecognized DCASE filename: {path.name}")
    if not records:
        raise FileNotFoundError(f"No DCASE WAV files found below {root}")
    return records


def audit_headers(records: list[Record]) -> dict[str, Any]:
    formats: Counter[tuple[int, int, int, float, str]] = Counter()
    errors: list[str] = []
    for index, record in enumerate(records, start=1):
        try:
            with wave.open(str(record.path), "rb") as audio:
                rate = audio.getframerate()
                frames = audio.getnframes()
                observed = (
                    rate,
                    audio.getsampwidth() * 8,
                    audio.getnchannels(),
                    round(frames / rate, 6),
                    audio.getcomptype(),
                )
                formats[observed] += 1
        except (EOFError, OSError, ValueError, wave.Error, ZeroDivisionError) as exc:
            errors.append(f"{record.relative_path}: {type(exc).__name__}: {exc}")
        if index % 1000 == 0:
            print(f"Audited {index}/{len(records)} {records[0].dataset} headers", file=sys.stderr)
    if errors:
        raise ValueError(f"{len(errors)} unreadable WAV files; first error: {errors[0]}")
    return {
        "files": len(records),
        "readable": len(records),
        "errors": 0,
        "formats": [
            {
                "sample_rate_hz": key[0],
                "bit_depth": key[1],
                "channels": key[2],
                "duration_seconds": key[3],
                "compression": key[4],
                "files": count,
            }
            for key, count in sorted(formats.items())
        ],
    }


def rank(record: Record, seed: int) -> str:
    return hashlib.sha256(f"{seed}\0{record.file_id}".encode()).hexdigest()


def balanced_sample(
    records: list[Record],
    total: int,
    primary: Callable[[Record], tuple[str, ...]],
    secondary: Callable[[Record], tuple[str, ...]],
    seed: int,
) -> list[Record]:
    primary_groups: dict[tuple[str, ...], list[Record]] = defaultdict(list)
    for record in records:
        primary_groups[primary(record)].append(record)
    if not primary_groups or total % len(primary_groups):
        raise ValueError("Sample total must divide evenly across primary strata")
    quota = total // len(primary_groups)
    selected: list[Record] = []
    for primary_key in sorted(primary_groups):
        groups: dict[tuple[str, ...], list[Record]] = defaultdict(list)
        for record in primary_groups[primary_key]:
            groups[secondary(record)].append(record)
        for group in groups.values():
            group.sort(key=lambda record: (rank(record, seed), record.relative_path))
        picked: list[Record] = []
        offset = 0
        while len(picked) < quota:
            added = False
            for key in sorted(groups):
                if offset < len(groups[key]):
                    picked.append(groups[key][offset])
                    added = True
                    if len(picked) == quota:
                        break
            if not added:
                raise ValueError(f"Insufficient records in stratum {primary_key}")
            offset += 1
        selected.extend(picked)
    return sorted(selected, key=lambda record: (record.dataset, record.file_id))


def choose_samples(
    mimii: list[Record], dcase: list[Record], per_dataset: int, seed: int
) -> tuple[list[Record], list[Record]]:
    mimii_selected = balanced_sample(
        [record for record in mimii if record.condition in {"normal", "anomaly"}],
        per_dataset,
        primary=lambda record: (record.condition,),
        secondary=lambda record: (record.machine_id,),
        seed=seed,
    )
    dcase_selected = balanced_sample(
        [
            record
            for record in dcase
            if record.split == "test" and record.condition in {"normal", "anomaly"}
        ],
        per_dataset,
        primary=lambda record: (record.domain, record.condition),
        secondary=lambda record: (record.attribute,),
        seed=seed,
    )
    return mimii_selected, dcase_selected


def read_channel_zero(record: Record) -> np.ndarray:
    sample_rate, raw = wavfile.read(record.path, mmap=True)
    if sample_rate != 16_000:
        raise ValueError(f"Expected 16 kHz: {record.relative_path}")
    selected = raw if raw.ndim == 1 else raw[:, 0]
    if not np.issubdtype(selected.dtype, np.integer):
        raise TypeError(f"Expected PCM integer WAV: {record.relative_path}")
    info = np.iinfo(selected.dtype)
    scale = float(max(abs(info.min), info.max))
    waveform = (selected.astype(np.float32) / scale).astype(np.float32)
    if not np.isfinite(waveform).all():
        raise ValueError(f"Non-finite samples: {record.relative_path}")
    return waveform


def extract_features(record: Record) -> dict[str, Any]:
    waveform = read_channel_zero(record)
    values = np.asarray(waveform, dtype=np.float64)
    rms = float(np.sqrt(np.mean(values**2)))
    peak = float(np.max(np.abs(values)))
    power = np.abs(np.fft.rfft(values)) ** 2
    frequencies = np.fft.rfftfreq(values.size, 1 / 16_000)
    fft_total = float(power.sum())
    centroid = float(np.sum(frequencies * power) / fft_total) if fft_total else 0.0
    bandwidth = (
        float(np.sqrt(np.sum(((frequencies - centroid) ** 2) * power) / fft_total))
        if fft_total
        else 0.0
    )
    result: dict[str, Any] = {
        "dataset": record.dataset,
        "condition": record.condition,
        "machine_id": record.machine_id,
        "domain": record.domain,
        "attribute": record.attribute,
        "relative_path": record.relative_path,
        "file_id": record.file_id,
        "rms": rms,
        "rms_dbfs": float(20 * np.log10(max(rms, np.finfo(float).tiny))),
        "peak": peak,
        "peak_dbfs": float(20 * np.log10(max(peak, np.finfo(float).tiny))),
        "amplitude_mean": float(np.mean(values)),
        "amplitude_std": float(np.std(values)),
        "amplitude_p01": float(np.percentile(values, 1)),
        "amplitude_p05": float(np.percentile(values, 5)),
        "amplitude_p50": float(np.percentile(values, 50)),
        "amplitude_p95": float(np.percentile(values, 95)),
        "amplitude_p99": float(np.percentile(values, 99)),
        "clipping_ratio": float(np.mean(np.abs(values) >= 0.999)),
        "zero_crossing_rate": float(
            np.mean(np.signbit(values[1:]) != np.signbit(values[:-1]))
        ),
        "spectral_centroid_hz": centroid,
        "spectral_bandwidth_hz": bandwidth,
    }
    welch_frequency, density = welch(
        waveform, fs=16_000, window="hann", nperseg=min(2048, waveform.size), scaling="density"
    )
    total_power = float(TRAPEZOID(density, welch_frequency))
    result["total_power"] = total_power
    for name, (lower, upper) in BANDS.items():
        mask = (welch_frequency >= lower) & (welch_frequency < upper)
        absolute = float(TRAPEZOID(density[mask], welch_frequency[mask]))
        result[f"{name}_power"] = absolute
        result[f"{name}_ratio"] = absolute / total_power if total_power > 0 else 0.0
    return result


def effect_rows(features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for condition in ("all", "normal", "anomaly"):
        subset = (
            features
            if condition == "all"
            else [row for row in features if row["condition"] == condition]
        )
        for feature in FEATURES:
            mimii = np.asarray(
                [row[feature] for row in subset if row["dataset"] == "MIMII"], dtype=float
            )
            dcase = np.asarray(
                [row[feature] for row in subset if row["dataset"] == "DCASE"], dtype=float
            )
            variance = ((mimii.size - 1) * np.var(mimii, ddof=1)) + (
                (dcase.size - 1) * np.var(dcase, ddof=1)
            )
            pooled_sd = float(np.sqrt(variance / (mimii.size + dcase.size - 2)))
            mean_difference = float(np.mean(mimii) - np.mean(dcase))
            smd = mean_difference / pooled_sd if pooled_sd > np.finfo(float).eps else 0.0
            mimii_iqr = float(np.percentile(mimii, 75) - np.percentile(mimii, 25))
            dcase_iqr = float(np.percentile(dcase, 75) - np.percentile(dcase, 25))
            pooled_iqr = (mimii_iqr + dcase_iqr) / 2
            median_difference = float(np.median(mimii) - np.median(dcase))
            ks = ks_2samp(mimii, dcase, method="auto")
            rows.append(
                {
                    "condition": condition,
                    "feature": feature,
                    "mimii_files": mimii.size,
                    "dcase_files": dcase.size,
                    "mimii_mean": float(np.mean(mimii)),
                    "dcase_mean": float(np.mean(dcase)),
                    "mimii_std": float(np.std(mimii, ddof=1)),
                    "dcase_std": float(np.std(dcase, ddof=1)),
                    "mimii_median": float(np.median(mimii)),
                    "dcase_median": float(np.median(dcase)),
                    "mimii_iqr": mimii_iqr,
                    "dcase_iqr": dcase_iqr,
                    "standardized_mean_difference": float(smd),
                    "absolute_smd": float(abs(smd)),
                    "absolute_median_difference_over_pooled_iqr": (
                        abs(median_difference) / pooled_iqr
                        if pooled_iqr > np.finfo(float).eps
                        else 0.0
                    ),
                    "wasserstein_raw_units": float(wasserstein_distance(mimii, dcase)),
                    "ks_statistic": float(ks.statistic),
                    "ks_pvalue_exploratory": float(ks.pvalue),
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def save_plot(path: Path, features: list[dict[str, Any]], shift: list[dict[str, Any]]) -> None:
    overall = [row for row in shift if row["condition"] == "all"]
    varying = [row for row in overall if row["absolute_smd"] > 0]
    largest = max(varying, key=lambda row: row["absolute_smd"])["feature"]
    smallest = min(varying, key=lambda row: row["absolute_smd"])["feature"]
    groups = [("MIMII", "normal"), ("MIMII", "anomaly"), ("DCASE", "normal"), ("DCASE", "anomaly")]
    labels = [f"{dataset}\n{condition}" for dataset, condition in groups]
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for axis, feature, title in zip(
        axes,
        (largest, smallest),
        ("Largest cross-dataset shift", "Smallest non-constant cross-dataset shift"),
        strict=True,
    ):
        values = [
            [
                row[feature]
                for row in features
                if row["dataset"] == dataset and row["condition"] == condition
            ]
            for dataset, condition in groups
        ]
        axis.boxplot(values, tick_labels=labels, showfliers=False)
        axis.set_title(f"{title}\n{feature}")
        axis.set_ylabel(feature)
        if feature.endswith("_power"):
            axis.set_yscale("log")
        axis.grid(axis="y", alpha=0.25)
    figure.suptitle("MIMII 6 dB fan vs DCASE 2025 fan (balanced cohort)")
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=180)
    plt.close(figure)


def main() -> int:
    args = parse_args()
    outputs = (args.output_csv, args.summary_json, args.plot)
    existing = [path for path in outputs if path.exists()]
    if existing:
        raise FileExistsError("Refusing to overwrite:\n" + "\n".join(map(str, existing)))

    mimii = discover_mimii(args.mimii_root)
    dcase = discover_dcase(args.dcase_root)
    audits = {"MIMII": audit_headers(mimii), "DCASE": audit_headers(dcase)}
    mimii_sample, dcase_sample = choose_samples(mimii, dcase, args.per_dataset, args.seed)
    selected = [*mimii_sample, *dcase_sample]
    features = []
    for index, record in enumerate(selected, start=1):
        features.append(extract_features(record))
        if index % 50 == 0:
            print(f"Extracted {index}/{len(selected)} feature vectors", file=sys.stderr)
    feature_matrix = np.asarray([[row[name] for name in FEATURES] for row in features])
    if not np.isfinite(feature_matrix).all():
        raise ValueError("Feature extraction produced non-finite values")

    shift = effect_rows(features)
    write_csv(args.output_csv, shift)
    save_plot(args.plot, features, shift)
    overall = [row for row in shift if row["condition"] == "all"]
    nonconstant = [row for row in overall if row["absolute_smd"] > 0]
    summary = {
        "method": {
            "seed": args.seed,
            "per_dataset": args.per_dataset,
            "conditions_per_dataset": {
                "normal": args.per_dataset // 2,
                "anomaly": args.per_dataset // 2,
            },
            "channel_policy": {"MIMII": "channel 0 of 8", "DCASE": "native mono channel 0"},
            "sample_rate_hz": 16000,
            "feature_count": len(FEATURES),
            "bands_hz": BANDS,
            "smd_definition": "MIMII mean minus DCASE mean divided by pooled sample SD",
            "large_effect_guide": "absolute SMD >= 0.8; descriptive, not a hypothesis test",
        },
        "inventory": {
            "MIMII": Counter((r.machine_id, r.condition) for r in mimii),
            "DCASE": Counter((r.split, r.domain or "none", r.condition) for r in dcase),
        },
        "header_audit": audits,
        "selected_files": len(selected),
        "feature_values": int(feature_matrix.size),
        "all_feature_values_finite": True,
        "median_absolute_smd": float(np.median([row["absolute_smd"] for row in overall])),
        "large_shift_feature_count": int(sum(row["absolute_smd"] >= 0.8 for row in overall)),
        "large_shift_feature_proportion": float(
            sum(row["absolute_smd"] >= 0.8 for row in overall) / len(overall)
        ),
        "largest_shift": max(nonconstant, key=lambda row: row["absolute_smd"]),
        "smallest_nonconstant_shift": min(nonconstant, key=lambda row: row["absolute_smd"]),
        "models_fitted": False,
        "raw_datasets_pooled": False,
    }
    # Counter keys are tuples, so normalize inventories for JSON output.
    summary["inventory"] = {
        dataset: {"|".join(key): value for key, value in sorted(counts.items())}
        for dataset, counts in summary["inventory"].items()
    }
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "median_absolute_smd": summary["median_absolute_smd"],
                "large_shift_feature_count": summary["large_shift_feature_count"],
                "feature_values": summary["feature_values"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
