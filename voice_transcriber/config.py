"""Configuration settings for the voice transcription system."""

# Transcription settings
MODEL_SIZE = "base"  # Whisper model size: tiny, base, small, medium, large

# Audio settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024

# Phone socket settings
SOCKET_HOST = "0.0.0.0"  # Listen on all interfaces
SOCKET_PORT = 8000

# Recording settings
DEFAULT_RECORDING_DURATION = 30  # seconds