"""Small end-to-end demo: live microphone -> resample/window -> feature extractor."""

import argparse
import asyncio
import json
from pathlib import Path

import numpy as np

from acoustic_dashboard.analysis import AudioPreprocessor, BinnedFFT
from acoustic_dashboard.capture import AudioChunk, LiveMicrophoneSource, list_input_devices

MIMII_BAND_EDGES = [0, 250, 500, 1_000, 2_000, 4_000, 8_000]


def load_config(config_path: str | Path) -> dict:
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def print_devices() -> None:
    devices = list_input_devices()
    if not devices:
        print("No microphone/input devices were found.")
        return

    print("Available input devices:")
    for device in devices:
        print(
            f"  {device['index']:>2}: {device['name']} | "
            f"inputs={device['max_input_channels']} | "
            f"default_rate={device['default_samplerate']:.0f} Hz"
        )


async def run(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    if args.stream not in config:
        raise ValueError(
            f"{args.stream!r} does not exist in {args.config}. "
            f"Available streams: {', '.join(config)}"
        )

    device: int | str | None = args.device
    if isinstance(device, str) and device.isdigit():
        device = int(device)

    source = LiveMicrophoneSource(
        config[args.stream],
        device=device,
        sample_rate=args.capture_sample_rate,
        chunk_duration=args.chunk_duration,
    )
    preprocessor = AudioPreprocessor(
        target_sample_rate=16_000,
        window_duration=args.window_duration,
        hop_duration=args.hop_duration,
    )
    extractor = BinnedFFT(
        sample_rate=16_000,
        n_bins=6,
        edges=MIMII_BAND_EDGES,
    )

    emitted_windows = 0

    def handle_chunk(chunk: AudioChunk) -> None:
        nonlocal emitted_windows

        for window in preprocessor.push(chunk):
            feature_window = extractor.extract(
                window.samples,
                timestamp=window.timestamp,
                source_id=window.source_id,
            )
            values = ", ".join(f"{value:7.2f}" for value in feature_window.vector)
            rms = float(np.sqrt(np.mean(window.samples**2)))
            print(
                f"window={window.window_index:<4} "
                f"capture={chunk.sample_rate:>5}Hz -> analysis={window.sample_rate:>5}Hz "
                f"rms={rms:.4f} bands_dB=[{values}]"
            )
            emitted_windows += 1

    print(f"Input device:       {source.device_name}")
    print(f"Capture sample rate:{source.sample_rate:>7} Hz")
    print("Analysis sample rate: 16000 Hz")
    print(f"Window / hop:       {args.window_duration:.2f}s / {args.hop_duration:.2f}s")
    print("Feature extractor:  six-band BinnedFFT")
    print("Press Ctrl+C to stop.\n")

    await source.stream(handle_chunk, max_chunks=args.max_chunks)
    print(f"\nEmitted {emitted_windows} analysis window(s).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run live microphone audio through the analysis preprocessor and BinnedFFT."
    )
    parser.add_argument("--list-devices", action="store_true")
    parser.add_argument("--stream", default="machine01")
    parser.add_argument("--config", default="machine_config.example.json")
    parser.add_argument("--device")
    parser.add_argument("--capture-sample-rate", type=int)
    parser.add_argument("--chunk-duration", type=float, default=0.25)
    parser.add_argument("--window-duration", type=float, default=1.0)
    parser.add_argument("--hop-duration", type=float, default=1.0)
    parser.add_argument("--max-chunks", type=int)
    args = parser.parse_args()

    try:
        if args.list_devices:
            print_devices()
            return
        asyncio.run(run(args))
    except KeyboardInterrupt:
        print("\nLive feature demo stopped.")
    except (RuntimeError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
