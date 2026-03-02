# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
from pydantic import BaseModel, Field


class VSI(BaseModel):
    """Data model representing a Virtual Server Instance (VSI)."""

    id: str = Field(default=..., description="Unique identifier of the VSI")
    name: str = Field(default=..., description="Name of the VSI")
    status: str = Field(default=..., description="Current status of the VSI (e.g., running, stopped)")
    zone: str = Field(default=..., description="Zone in which the VSI is deployed")
    cpu: int = Field(default=..., description="Number of virtual CPUs")
    ram: int = Field(default=..., description="Memory (RAM) in MB")
