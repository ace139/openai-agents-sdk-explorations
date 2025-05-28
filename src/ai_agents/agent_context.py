from typing import Optional

from pydantic import BaseModel


class UserInteractionContext(BaseModel):
    """Context shared between agents during a user interaction."""

    user_id: Optional[int] = None
    exit_requested: bool = False
    # Future fields like user_name can be added here
