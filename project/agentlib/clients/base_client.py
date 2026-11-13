from abc import ABC, abstractmethod

class BaseClient(ABC):
    @abstractmethod
    def close(self):
        pass