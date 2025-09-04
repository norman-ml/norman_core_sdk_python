from dataclasses import dataclass

@dataclass(frozen=True)
class _HttpConfig:
    base_url = "https://api.dev.avremy.public.norman-ai.com/v0/"
    timeout = 10

@dataclass(frozen=True)
class _IOConfig:
    chunk_size = 2 ** 16
    flush_size = 8 * (1024 ** 2)

@dataclass(frozen=True)
class AppConfig:
    http = _HttpConfig
    io = _IOConfig
