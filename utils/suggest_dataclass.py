from dataclasses import dataclass
from datetime import datetime

@dataclass
class SuggestInfo:
    suggest_type: str
    description: str
    date: datetime
    source_link: str
    map_link: str = None
    player: str = None
    pp: str = None