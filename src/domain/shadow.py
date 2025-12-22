from dataclasses import dataclass
from src.enums import AttachmentStyle, ConflictResponse, RegulationMethod

@dataclass
class ShadowComponent:
    attachment_style: AttachmentStyle = AttachmentStyle.SECURE
    conflict_response: ConflictResponse = ConflictResponse.FLIGHT
    regulation_method: RegulationMethod = RegulationMethod.AUTO_REGULATION
    
    secure_score: float = 0.0
    anxious_score: float = 0.0
    avoidant_score: float = 0.0

    def calculate_from_quiz(self, scores: tuple):
        self.secure_score, self.anxious_score, self.avoidant_score = scores
        mx = max(scores)
        if mx == self.anxious_score:
            self.attachment_style = AttachmentStyle.ANXIOUS
            self.conflict_response = ConflictResponse.FIGHT
            self.regulation_method = RegulationMethod.CO_REGULATION
        elif mx == self.avoidant_score:
            self.attachment_style = AttachmentStyle.AVOIDANT
            self.conflict_response = ConflictResponse.FLIGHT
            self.regulation_method = RegulationMethod.AUTO_REGULATION
        else:
            self.attachment_style = AttachmentStyle.SECURE
            self.conflict_response = ConflictResponse.FAWN
            self.regulation_method = RegulationMethod.CO_REGULATION