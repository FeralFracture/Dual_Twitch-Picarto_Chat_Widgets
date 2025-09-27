from abc import ABC, abstractmethod

class MessageListener(ABC):
    @abstractmethod
    def on_message(self, message: str):
        pass

class Connector(ABC):
    @abstractmethod
    def start(self):
        pass
