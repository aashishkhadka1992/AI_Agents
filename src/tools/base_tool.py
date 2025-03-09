from abc import ABC, abstractmethod
import logging
from utils.location_utils import LocationUtils

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    """Base class for all tools."""
    
    def __init__(self):
        """Initialize the tool with LocationUtils if needed."""
        self.location_utils = LocationUtils()

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def use(self, *args, **kwargs) -> str:
        pass