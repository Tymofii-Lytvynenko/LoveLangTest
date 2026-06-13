from dataclasses import dataclass, field
from typing import List
from src.enums import ContextDependency

@dataclass
class ErosComponent:
    accelerator: float = 0.5
    brake: float = 0.5
    context_dependency: ContextDependency = ContextDependency.LOW
    erotic_tags: List[str] = field(default_factory=list)

    def calculate_from_quiz(self, accel_score: float, brake_score: float) -> None:
        self.accelerator = min(max(accel_score, 0.0), 1.0)
        self.brake = min(max(brake_score, 0.0), 1.0)
        
        if self.brake > 0.6:
            self.context_dependency = ContextDependency.HIGH
        else:
            self.context_dependency = ContextDependency.LOW
