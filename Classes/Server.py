from dataclasses import dataclass


@dataclass
class Server:
    id: str = None
    name: str = None
    error: str = None
    discord_channel: int = 0