from src.domain.professional import ProfessionalComponent
from src.domain.psychometrics import PsychometricsComponent
from src.enums import HollandCode
from src.profile import UserProfile
from src.question_bank import get_question_bank_registry
from src.services.adjustment import NeedsAdjustmentService
from src.services.reporting import ReportGenerator
from src.services.scoring import QuestionnaireScorer


def test_full_single_profile_pipeline_generates_bounded_scores() -> None:
    registry = get_question_bank_registry()
    needs_bank = registry.get("needs")
    shadow_bank = registry.get("shadow")
    eros_bank = registry.get("eros")

    needs = QuestionnaireScorer.build_needs_component(
        needs_bank,
        {question.id: "opt_1" for question in needs_bank.questions},
    )
    shadow = QuestionnaireScorer.build_shadow_component(
        shadow_bank,
        {question.id: question.options[0].id for question in shadow_bank.questions},
    )
    eros = QuestionnaireScorer.build_eros_component(
        eros_bank,
        {question.id: "opt_1" for question in eros_bank.questions},
        erotic_tags=["Sapiosexual"],
    )

    user = UserProfile(
        name="User",
        psychometrics=PsychometricsComponent.from_high_level_scores(62, 41, 58, 67, 39, adhd=True, asd=False),
        shadow=shadow,
        eros=eros,
        needs=NeedsAdjustmentService.adjust_needs(
            needs,
            PsychometricsComponent.from_high_level_scores(62, 41, 58, 67, 39, adhd=True, asd=False),
        ),
        professional=ProfessionalComponent(
        primary_type=HollandCode.INVESTIGATIVE,
        secondary_type=HollandCode.ARTISTIC,
        tertiary_type=HollandCode.REALISTIC,
        career_centrality=0.55,
        ),
    )

    report = ReportGenerator.generate_manual(user)

    for value in report["scores"].values():
        assert 0.0 <= value <= 1.0
    for value in report["provision_scores"].values():
        assert 0.0 <= value <= 1.0
    assert report["neurodivergence_context"] == "ADHD"
    assert report["support_notes"]
