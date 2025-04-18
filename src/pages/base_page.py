from abc import ABC, abstractmethod


class BasePage(ABC):

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def build_header(self):
        pass

    @abstractmethod
    def build_content(self):
        pass
