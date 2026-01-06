import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Fund:
    name: str
    target: float
    
    type: str = "goal" 
    current: float = 0.0
    
    # Tự động sinh UUID
    id: str = field(default_factory=lambda: str(uuid.uuid4())) 
    
    icon: str = "💰"
    color: str = "#ffffff"
    
    history: List[Dict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict):
        valid_keys = cls.__annotations__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)

    def to_dict(self):
        return self.__dict__

@dataclass
class Goal:
    name: str
    target: float
    
    # Sửa id thành str/uuid cho đồng bộ
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    members: List[Dict] = field(default_factory=list)
    deadline: str = ""
    status: str = "active"

    def to_dict(self):
        return self.__dict__