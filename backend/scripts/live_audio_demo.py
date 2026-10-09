import argparse
import asyncio
import json
from pathlib import Path

import numpy as np

from acoustic_dashboard.capture import (
    AudioChunk,
    LiveMicrophoneSource,
    list_input_devices,
)


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
            f"default_rate={device['default_samplerate']:.0f} Hz | "
            f"hostapi={device['hostapi']}"
        )


def print_chunk(chunk: AudioChunk) -> None:
    peak_amplitude = float(np.max(np.abs(chunk.samples))) if len(chunk.samples) else 0.0
    rms = float(np.sqrt(np.mean(np.square(chunk.samples)))) if len(chunk.samples) else 0.0

    print(
        f"[{chunk.source_id}] "
        f"{chunk.machine_id:<10} "
        f"chunk={chunk.chunk_index:<4} "
        f"stream_time={chunk.stream_start_time:>6.1f}s "
        f"duration={chunk.duration:.2f}s "
        f"samples={len(chunk.samples):<6} "
        f"peak={peak_amplitude:.3f} "
        f"rms={rms:.3f}"
    )


async def run_live_source(args: argparse.Namespace) -> None:
    config = load_config(args.config)

    if args.stream not in config:
        raise ValueError(
            f"'{args.stream}' does not exist in {args.config}. "
            f"Available streams: {', '.join(config)}"
        )

    device: int | str | None = args.device
    if isinstance(device, str) and device.isdigit():
        device = int(device)

    source = LiveMicrophoneSource(
        config[args.stream],
        device=device,
        sample_rate=args.sample_rate,
        chunk_duration=args.chunk_duration,
    )

    print()
    print("=" * 70)
    print("LIVE MICROPHONE SOURCE CONFIGURATION")
    print("=" * 70)
    print(f"Configured stream:  {args.stream}")
    print(f"Source ID:          {source.machine_config['source_id']}")
    print(f"Machine type:       {source.machine_config['machine_type']}")
    print(f"Machine ID:         {source.machine_config['machine_id']}")
    print(f"Machine profile:    {source.machine_config['machine_profile']}")
    print(f"Input device:       {source.device_name}")
    print(f"Selected channel:   {source.channel_index}")
    print(f"Sample rate:        {source.sample_rate} Hz")
    print(f"Chunk duration:     {source.chunk_duration:.2f} sec")
    print()
    print("Starting live capture. Press Ctrl+C to stop.")
    print()

    await source.stream(print_chunk, max_chunks=args.max_chunks)

    if source.dropped_blocks:
        print(f"Warning: dropped {source.dropped_blocks} capture block(s).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture a live microphone/input using the AudioChunk contract."
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available input devices and exit.",
    )
    parser.add_argument(
        "--stream",
        default="machine01",
        help="Machine configuration entry to use (default: machine01).",
    )
    parser.add_argument(
        "--config",
        default="machine_config.example.json",
        help="Path to machine configuration JSON (default: machine_config.example.json).",
    )
    parser.add_argument(
        "--device",
        help="PortAudio input device index or name. Omit to use the default input.",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        help="Requested capture sample rate. Omit to use the device default.",
    )
    parser.add_argument(
        "--chunk-duration",
        type=float,
        default=1.0,
        help="Capture chunk duration in seconds (default: 1.0).",
    )
    parser.add_argument(
        "--max-chunks",
        type=int,
        help="Stop after this many chunks. Omit to capture until Ctrl+C.",
    )

    args = parser.parse_args()

    try:
        if args.list_devices:
            print_devices()
            return
        asyncio.run(run_live_source(args))
    except KeyboardInterrupt:
        print("\nLive capture stopped.")
    except (RuntimeError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
