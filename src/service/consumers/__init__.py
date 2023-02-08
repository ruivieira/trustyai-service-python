from abc import ABC, abstractmethod


class DataConsumer(ABC):

    @abstractmethod
    def as_dataframe(self):
        pass
