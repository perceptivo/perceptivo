"""
Root Perceptivo Object from which others inherit

"""
from logging import Logger
from perceptivo.data.logging import init_logger
from abc import ABC



class Perceptivo_Object(ABC):
    @property
    def logger(self) -> Logger:
        if not hasattr(self, '_logger') or self._logger is None:
            self._logger = init_logger(self)

        return self._logger


