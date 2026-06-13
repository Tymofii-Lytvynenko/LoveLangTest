from src.domain.eros import ErosComponent
from src.domain.needs import RelationalNeedsComponent
from src.domain.professional import ProfessionalComponent
from src.domain.psychometrics import PsychometricsComponent
from src.enums import AttachmentStyle
from src.profile import UserProfile
from src.question_bank import load_question_bank
from src.services.reporting import ReportGenerator
from src.services.scoring import QuestionnaireScorer


def _responses(option_index: int) -> dict[str, str]:
    bank = load_question_bank("shadow")
    return {
        question.id: question.options[option_index].id
        for question in bank.questions
    }


def test_all_shadow_styles_are_reachable() -> None:
    bank = load_question_bank("shadow")

    assert QuestionnaireScorer.build_shadow_component(bank, _responses(0)).attachment_style == AttachmentStyle.SECURE
    assert QuestionnaireScorer.build_shadow_component(bank, _responses(1)).attachment_style == AttachmentStyle.ANXIOUS
    assert QuestionnaireScorer.build_shadow_component(bank, _responses(2)).attachment_style == AttachmentStyle.AVOIDANT
    assert (
        QuestionnaireScorer.build_shadow_component(bank, _responses(3)).attachment_style
        == AttachmentStyle.DISORGANIZED
    )


def test_disorganized_branch_reaches_report_warning() -> None:
    bank = load_question_bank("shadow")
    shadow = QuestionnaireScorer.build_shadow_component(bank, _responses(3))
    user = UserProfile(
        name="User",
        psychometrics=PsychometricsComponent.from_high_level_scores(50, 50, 50, 50, 50),
        shadow=shadow,
        eros=ErosComponent(),
        needs=RelationalNeedsComponent(
            raw_safety=0.5,
            raw_resource=0.5,
            raw_resonance=0.5,
            raw_expansion=0.5,
            adjusted_safety=0.5,
            adjusted_resource=0.5,
            adjusted_resonance=0.5,
            adjusted_expansion=0.5,
        ),
        professional=ProfessionalComponent(),
    )

    report = ReportGenerator.generate_manual(user)
    assert "Хаотична" in report["shadow_warning"]
