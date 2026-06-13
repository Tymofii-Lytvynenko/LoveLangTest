from dataclasses import dataclass, field
from src.domain.psychometrics import PsychometricsComponent
from src.domain.shadow import ShadowComponent
from src.domain.eros import ErosComponent
from src.domain.needs import RelationalNeedsComponent
from src.domain.professional import ProfessionalComponent

@dataclass
class UserProfile:
    name: str
    psychometrics: PsychometricsComponent
    shadow: ShadowComponent
    eros: ErosComponent
    needs: RelationalNeedsComponent
    professional: ProfessionalComponent
    provision: dict[str, float] | None = None
    calibration_notes: list[str] = field(default_factory=list)