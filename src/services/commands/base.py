# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class CommandResult(Generic[T]):
    def __init__(self, success: bool, message: str = "", data: T | None = None) -> None:
        self.success = success
        self.message = message
        self.data = data


class BaseCommand(ABC, Generic[T]):
    @abstractmethod
    def execute(self) -> CommandResult[T]:
        pass
