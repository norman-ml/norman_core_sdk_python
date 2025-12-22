class _HttpConfig:
    base_url = "https://api.dev.noga.public.norman-ai.com/v0"
    timeout_seconds = 1800

class _IOConfig:
    chunk_size = 2 ** 16
    flush_size = 8 * (1024 ** 2)

class AppConfig:
    http = _HttpConfig
    io = _IOConfig
