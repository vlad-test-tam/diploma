from abc import ABC, abstractmethod


class BaseInjectionHandler(ABC):

    @abstractmethod
    def header_injection(self, st, logo):
        pass
