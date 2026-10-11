"""Small, raw-data-free checks for the MIMII-DCASE comparison."""

from __future__ import annotations

import tempfile
import unittest
import wave
from collections import Counter
from pathlib import Path

import numpy as np

from scripts import compare_mimii_dcase as comparison


def make_record(dataset: str, condition: str, index: int, **metadata: str) -> comparison.Record:
    strata = "/".join(value for _, value in sorted(metadata.items()))
    relative = f"{dataset.lower()}/{strata}/{condition}/{index:03d}.wav"
    return comparison.Record(
        dataset=dataset,
        path=Path(relative),
        relative_path=relative,
        file_id=comparison.stable_id(dataset, relative),
        condition=condition,
        **metadata,
    )


class ComparisonTests(unittest.TestCase):
    def test_sampling_is_deterministic_and_keeps_datasets_separate(self) -> None:
        mimii = [
            make_record("MIMII", condition, index, machine_id=machine_id)
            for condition in ("normal", "anomaly")
            for machine_id in ("id_00", "id_02", "id_04", "id_06")
            for index in range(3)
        ]
        dcase = [
            make_record(
                "DCASE",
                condition,
                index,
                domain=domain,
                split="test",
                attribute=attribute,
            )
            for condition in ("normal", "anomaly")
            for domain in ("source", "target")
            for attribute in ("A", "B")
            for index in range(3)
        ]

        first = comparison.choose_samples(mimii, dcase, per_dataset=16, seed=40122)
        second = comparison.choose_samples(mimii, dcase, per_dataset=16, seed=40122)

        self.assertEqual(
            tuple(record.file_id for cohort in first for record in cohort),
            tuple(record.file_id for cohort in second for record in cohort),
        )
        self.assertTrue(all(record.dataset == "MIMII" for record in first[0]))
        self.assertTrue(all(record.dataset == "DCASE" for record in first[1]))
        self.assertEqual(
            Counter(record.condition for record in first[0]), {"normal": 8, "anomaly": 8}
        )
        self.assertEqual(
            Counter(record.condition for record in first[1]), {"normal": 8, "anomaly": 8}
        )

    def test_extractor_returns_26_finite_features_for_synthetic_wav(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.wav"
            time = np.arange(16_000) / 16_000
            samples = (10_000 * np.sin(2 * np.pi * 440 * time)).astype(np.int16)
            with wave.open(str(path), "wb") as audio:
                audio.setnchannels(1)
                audio.setsampwidth(2)
                audio.setframerate(16_000)
                audio.writeframes(samples.tobytes())

            record = comparison.Record("MIMII", path, "synthetic.wav", "synthetic", "normal")
            extracted = comparison.extract_features(record)
            values = np.asarray([extracted[name] for name in comparison.FEATURES])

        self.assertEqual(len(comparison.FEATURES), 26)
        self.assertEqual(values.size, 26)
        self.assertTrue(np.isfinite(values).all())


if __name__ == "__main__":
    unittest.main()
