from dataclasses import dataclass

import numpy as np


@dataclass
class AudioChunk:

    source_id: str
    machine_type: str
    machine_id: str
    machine_profile: str
    chunk_index: int
    stream_start_time: float
    duration: float
    timestamp: str
    sample_rate: int
    samples: np.ndarray
