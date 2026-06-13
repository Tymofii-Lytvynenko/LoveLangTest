from src.domain.needs import RelationalNeedsComponent
from src.domain.professional import ProfessionalComponent
from src.domain.psychometrics import PsychometricsComponent
from src.enums import HollandCode
from src.services.adjustment import NeedsAdjustmentService
from src.services.neurodivergence import NeurodivergenceService
from src.services.provision import ProvisionService


def _professional() -> ProfessionalComponent:
    return ProfessionalComponent(
        primary_type=HollandCode.INVESTIGATIVE,
        secondary_type=HollandCode.ARTISTIC,
        tertiary_type=HollandCode.REALISTIC,
        career_centrality=0.4,
    )


def test_audhd_context_exposes_combined_label_and_notes() -> None:
    psycho = PsychometricsComponent.from_high_level_scores(62, 41, 58, 67, 39, adhd=True, asd=True)

    context = NeurodivergenceService.analyze(psycho)

    assert context.label == "AuDHD"
    assert context.is_enabled
    assert len(context.support_notes) == 3
    assert 0.0 <= context.safety_target <= 1.0
    assert 0.0 <= context.resource_target <= 1.0
    assert 0.0 <= context.resonance_target <= 1.0
    assert 0.0 <= context.expansion_signal <= 1.0


def test_adhd_resource_penalty_depends_on_executive_strain() -> None:
    low_strain = PsychometricsComponent.from_high_level_scores(55, 75, 50, 60, 35, adhd=True, asd=False)
    low_strain.conscientiousness.order = 0.9
    low_strain.conscientiousness.self_discipline = 0.85
    low_strain.conscientiousness.competence = 0.85

    high_strain = PsychometricsComponent.from_high_level_scores(55, 45, 50, 60, 35, adhd=True, asd=False)
    high_strain.conscientiousness.order = 0.2
    high_strain.conscientiousness.self_discipline = 0.25
    high_strain.conscientiousness.competence = 0.45

    low_context = NeurodivergenceService.analyze(low_strain)
    high_context = NeurodivergenceService.analyze(high_strain)

    assert 0.0 <= low_context.resource_provision_penalty < high_context.resource_provision_penalty

    low_provision = ProvisionService.analyze(low_strain, _professional())
    high_provision = ProvisionService.analyze(high_strain, _professional())
    assert low_provision.resource_score > high_provision.resource_score


def test_adjustment_keeps_higher_raw_answer_when_context_floor_is_lower() -> None:
    psycho = PsychometricsComponent.from_high_level_scores(60, 85, 50, 60, 20, adhd=True, asd=False)
    psycho.conscientiousness.order = 0.95
    psycho.conscientiousness.self_discipline = 0.9
    psycho.conscientiousness.competence = 0.9

    raw = RelationalNeedsComponent(
        raw_safety=0.8,
        raw_resource=0.9,
        raw_resonance=0.7,
        raw_expansion=0.85,
    )

    adjusted = NeedsAdjustmentService.adjust_needs(raw, psycho)

    assert adjusted.adjusted_resource == raw.raw_resource
    assert adjusted.adjusted_expansion == raw.raw_expansion
