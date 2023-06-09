import abc
from typing import Any, TYPE_CHECKING


class System(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        self.components: list["Component"] = []

    @abc.abstractmethod
    def update(self):
        pass


class Component(abc.ABC):
    @abc.abstractmethod
    def __init__(self, owner, system: System) -> None:
        self.owner = owner
        system.components.append(self)
        self.alive = True

    def kill(self):
        self.alive = False

    def update(self) -> bool:
        return self.alive
