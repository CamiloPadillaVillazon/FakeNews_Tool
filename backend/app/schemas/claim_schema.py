from pydantic import BaseModel


class ClaimIn(BaseModel):
    title: str
    description: str | None = None


class ClaimOut(ClaimIn):
    id: int
