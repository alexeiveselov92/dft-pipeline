"""Base abstract classes for DFT components"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .data_packet import DataPacket


class DataSource(ABC):
    """Base class for all data sources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", "unknown")
        self.source_type = config.get("source_type", "unknown")
    
    @abstractmethod
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Extract data from source"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to source"""
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)


class DataProcessor(ABC):
    """Base class for all data processors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", "unknown")
        self.processor_type = config.get("processor_type", "unknown")
    
    @abstractmethod
    def process(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Process data packet"""
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)


class DataEndpoint(ABC):
    """Base class for all data endpoints"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", "unknown")
        self.endpoint_type = config.get("endpoint_type", "unknown")
    
    @abstractmethod
    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Load data to endpoint"""
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)


class DataValidator(ABC):
    """Base class for data validators"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", "unknown")
    
    @abstractmethod
    def validate(self, packet: DataPacket) -> tuple[bool, Optional[str]]:
        """Validate data packet
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass