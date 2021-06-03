from dataclasses import dataclass
from discord import TextChannel


@dataclass
class Server:
    id: str
    name: str
    error: str
    channel: TextChannel