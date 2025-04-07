from pydantic import BaseModel

class WhitelistAdd(BaseModel):
    ign: str  # In-game name

class WhitelistRemove(BaseModel):
    ign: str  # In-game name
