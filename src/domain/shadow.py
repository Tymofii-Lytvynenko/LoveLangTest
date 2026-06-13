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
    disorganized_score: float = 0.0

    def calculate_from_quiz(self, scores: tuple[float, float, float, float]) -> None:
        (
            self.secure_score,
            self.anxious_score,
            self.avoidant_score,
            self.disorganized_score,
        ) = scores

        dominant_style = max(
            {
                AttachmentStyle.SECURE: self.secure_score,
                AttachmentStyle.ANXIOUS: self.anxious_score,
                AttachmentStyle.AVOIDANT: self.avoidant_score,
                AttachmentStyle.DISORGANIZED: self.disorganized_score,
            }.items(),
            key=lambda item: item[1],
        )[0]
        self.apply_attachment_style(dominant_style)

    def apply_attachment_style(self, attachment_style: AttachmentStyle) -> None:
        self.attachment_style = attachment_style
        if attachment_style == AttachmentStyle.ANXIOUS:
            self.conflict_response = ConflictResponse.FIGHT
            self.regulation_method = RegulationMethod.CO_REGULATION
        elif attachment_style == AttachmentStyle.AVOIDANT:
            self.conflict_response = ConflictResponse.FLIGHT
            self.regulation_method = RegulationMethod.AUTO_REGULATION
        elif attachment_style == AttachmentStyle.DISORGANIZED:
            self.conflict_response = ConflictResponse.FREEZE
            self.regulation_method = RegulationMethod.CO_REGULATION
        else:
            self.conflict_response = ConflictResponse.FAWN
            self.regulation_method = RegulationMethod.CO_REGULATION
