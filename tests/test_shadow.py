from src.domain.eros import ErosComponent
from src.domain.needs import RelationalNeedsComponent
from src.domain.professional import ProfessionalComponent
from src.domain.psychometrics import PsychometricsComponent
from src.enums import AttachmentStyle
from src.profile import UserProfile
from src.question_bank import load_question_bank
from src.services.reporting import ReportGenerator
from src.services.scoring import QuestionnaireScorer


def _responses(option_id: str) -> dict[str, str]:
    return {
        "att_01": option_id,
        "att_02": option_id,
        "att_03": option_id,
        "att_04": option_id,
    }


def test_all_shadow_styles_are_reachable() -> None:
    bank = load_question_bank("shadow")

    assert QuestionnaireScorer.build_shadow_component(bank, _responses("opt_1")).attachment_style == AttachmentStyle.SECURE
    assert QuestionnaireScorer.build_shadow_component(bank, _responses("opt_2")).attachment_style == AttachmentStyle.ANXIOUS
    assert QuestionnaireScorer.build_shadow_component(bank, _responses("opt_3")).attachment_style == AttachmentStyle.AVOIDANT
    assert (
        QuestionnaireScorer.build_shadow_component(bank, _responses("opt_4")).attachment_style
        == AttachmentStyle.DISORGANIZED
    )


def test_disorganized_branch_reaches_report_warning() -> None:
    bank = load_question_bank("shadow")
    shadow = QuestionnaireScorer.build_shadow_component(bank, _responses("opt_4"))
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
