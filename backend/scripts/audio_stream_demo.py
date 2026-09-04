import argparse
import asyncio
import json
import wave
from pathlib import Path

import numpy as np

from acoustic_dashboard.capture import AudioChunk, WavPlaybackSource


def load_config(config_path: str | Path) -> dict:
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_stream_arguments(arguments: list[str]) -> dict[str, str]:
    streams: dict[str, str] = {}

    for argument in arguments:
        if "=" not in argument:
            raise ValueError(
                f"Invalid stream argument: '{argument}'\n"
                "Expected format: machine01=path/to/file.wav"
            )

        stream_name, wav_path = argument.split("=", 1)
        stream_name = stream_name.strip()
        wav_path = wav_path.strip()

        if not stream_name:
            raise ValueError(f"Invalid stream argument: '{argument}'")

        if not wav_path:
            raise ValueError(f"No WAV path supplied for '{stream_name}'.")

        streams[stream_name] = wav_path

    return streams


def print_chunk(chunk: AudioChunk) -> None:
    peak_amplitude = float(np.max(np.abs(chunk.samples)))

    print(
        f"[{chunk.source_id}] "
        f"{chunk.machine_id:<10} "
        f"chunk={chunk.chunk_index:<4} "
        f"stream_time={chunk.stream_start_time:>6.1f}s "
        f"duration={chunk.duration:.2f}s "
        f"samples={len(chunk.samples):<6} "
        f"peak={peak_amplitude:.3f} "
        f"timestamp={chunk.timestamp}"
    )


async def run_streams(
    stream_arguments: dict[str, str],
    config: dict,
    *,
    chunk_duration: float = 1.0,
) -> None:
    prepared_streams: list[tuple[str, WavPlaybackSource]] = []

    for stream_name, wav_path in stream_arguments.items():
        if stream_name not in config:
            print(
                f"Warning: '{stream_name}' was supplied on the command line "
                "but does not exist in the config file. Skipping."
            )
            continue

        if not Path(wav_path).exists():
            print(
                f"Warning: WAV file for '{stream_name}' does not exist: {wav_path}"
            )
            continue

        try:
            source = WavPlaybackSource(
                wav_path,
                config[stream_name],
                chunk_duration=chunk_duration,
            )
        except (wave.Error, ValueError) as error:
            print(
                f"Warning: could not load '{stream_name}' from "
                f"'{wav_path}'. Skipping."
            )
            print(f"Reason: {error}")
            continue

        prepared_streams.append((stream_name, source))

    if not prepared_streams:
        print("No valid streams were provided.")
        return

    print()
    print("=" * 70)
    print("SIMULATED AUDIO SOURCE CONFIGURATION")
    print("=" * 70)

    for stream_name, source in prepared_streams:
        machine_config = source.machine_config

        print()
        print(f"Configured stream:  {stream_name}")
        print(f"Source ID:          {machine_config['source_id']}")
        print(f"Machine type:       {machine_config['machine_type']}")
        print(f"Machine ID:         {machine_config['machine_id']}")
        print(f"Machine profile:    {machine_config['machine_profile']}")
        print(f"WAV file:           {source.file_path}")
        print(f"Sample rate:        {source.sample_rate} Hz")
        print(f"Original channels:  {source.original_channels}")
        print(f"Selected channel:   {source.channel_index}")
        print(f"Chunk duration:     {source.chunk_duration:.2f} sec")
        print(f"Total chunks:       {source.total_chunks}")

    print()
    print("=" * 70)
    print("STARTING SIMULATED LIVE AUDIO STREAMS")
    print("=" * 70)
    print()

    tasks = [
        asyncio.create_task(source.stream(print_chunk))
        for _, source in prepared_streams
    ]

    await asyncio.gather(*tasks)

    print()
    print("=" * 70)
    print("ALL SIMULATED AUDIO STREAMS COMPLETE")
    print("=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Simulate multiple live industrial microphone streams "
            "using prerecorded WAV files."
        )
    )

    parser.add_argument(
        "streams",
        nargs="+",
        help="Stream mappings in the form machine01=path/to/audio.wav",
    )

    parser.add_argument(
        "--config",
        default="machine_config.example.json",
        help=(
            "Path to machine configuration JSON file "
            "(default: machine_config.example.json)."
        ),
    )

    parser.add_argument(
        "--chunk-duration",
        type=float,
        default=1.0,
        help="Capture chunk duration in seconds (default: 1.0).",
    )

    args = parser.parse_args()

    config = load_config(args.config)
    stream_arguments = parse_stream_arguments(args.streams)

    asyncio.run(
        run_streams(
            stream_arguments=stream_arguments,
            config=config,
            chunk_duration=args.chunk_duration,
        )
    )


if __name__ == "__main__":
    main()
