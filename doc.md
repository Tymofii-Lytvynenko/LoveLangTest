# **Technical Specification: Comprehensive Relationship Needs Analysis System (CRNAS)**

## **1. Abstract**

This document outlines the algorithmic architecture for a scientifically grounded relationship needs assessment tool. Unlike traditional "Love Language" models, CRNAS utilizes a multi-layered approach, integrating the **Big Five (OCEAN)** psychometric model, **Self-Determination Theory (SDT)**, **Attachment Theory**, the **Dual Control Model of Sexual Response**, and the **Holland Code (RIASEC)** for professional compatibility.

The system is designed using a **Composition over Inheritance** principle. It treats a user profile not as a monolithic entity, but as a composition of independent, interacting modules (Components).

## **2. Core Methodology & Architecture**

The system operates on distinct processing layers:

1. **The Substrate Layer (Hardware):** Biological and stable psychological traits (Big Five, Neurotype).
2. **The Needs Layer (Interface):** The S.R.M.E. model (Safety, Resource, Resonance, Expansion).
3. **The Occupational Layer (Operation):** Cognitive styles and resource availability driven by career (RIASEC).
4. **The Context Layer (Implementation):** Specific interests, values, and defense mechanisms.

### **2.1. Compositional Structure (Data Entities)**

The UserProfile entity is composed of the following modules:

* PsychometricsComponent (The "Hardware")
* RelationalNeedsComponent (The S.R.M.E. Engine)
* ErosComponent (Sexual Temperament)
* ShadowComponent (Conflict & Attachment)
* ProfessionalComponent (Occupational Compass)
* ContextComponent (Interests & Values)

## **3. Module Specifications & Variables**

### **3.1. Module A: PsychometricsComponent (The Hardware)**

**Purpose:** Acts as a high-resolution coefficient modifier for all other modules. Unlike basic OCEAN models, this component utilizes the **30-Facet Model (NEO-PI-R / IPIP-NEO)** to distinguish specific behavioral drivers (e.g., distinguishing *Intellectual Curiosity* from *Emotional Sensitivity* within Openness).

**Methodology:** Inputs are normalized floats (0.0–1.0).

#### **1. Neuroticism Domain (The Threat Detection System)**
*Primary Driver for: Safety Needs & Conflict Style.*

* **N1: Anxiety:** Tendency to worry and anticipate future danger. *Increases need for Predictability.*
* **N2: Anger (Hostility):** Tendency to experience frustration and bitterness. *Predicts "Fight" response in conflicts.*
* **N3: Depression:** Susceptibility to sadness and hopelessness. *Increases need for Co-Regulation.*
* **N4: Self-Consciousness:** Sensitivity to what others think; shame-prone. *Increases Rejection Sensitivity.*
* **N5: Immoderation:** Difficulty resisting cravings/urges.
* **N6: Vulnerability:** Response to stress/pressure. *High scores indicate a need for a "Safe Haven" partner.*

#### **2. Extraversion Domain (The Energy System)**
*Primary Driver for: Expansion Needs & Social Battery.*

* **E1: Friendliness:** Warmth and affection towards others.
* **E2: Gregariousness:** Preference for company over solitude. *Determines "Social Expansion" needs.*
* **E3: Assertiveness:** Dominance and leadership tendencies. *Influences Power Dynamics.*
* **E4: Activity Level:** Pace of living; busyness. *High mismatch here causes lifestyle friction.*
* **E5: Excitement Seeking:** Need for thrills and stimulation. *Primary driver for Novelty Needs.*
* **E6: Cheerfulness:** Tendency to experience positive emotions.

#### **3. Openness Domain (The Cognitive Style)**
*Primary Driver for: Resonance Type (Cognitive vs. Aesthetic).*

* **O1: Imagination:** Richness of fantasy life.
* **O2: Artistic Interests:** Appreciation for beauty and art. *Driver for Aesthetic Resonance.*
* **O3: Emotionality:** Depth and awareness of feelings. *Driver for Emotional Permeability.*
* **O4: Adventurousness:** Willingness to try new things/routines. *Driver for Behavioral Expansion.*
* **O5: Intellect:** Interest in abstract ideas and philosophical debate (not IQ). *Driver for Cognitive/Sapiosexual Resonance.*
* **O6: Liberalism:** Readiness to challenge authority and convention.

#### **4. Agreeableness Domain (The Social Interface)**
*Primary Driver for: Conflict Resolution & Emotional Safety.*

* **A1: Trust:** Belief in the sincerity of others. *Low scores trigger "Suspicion" defense mechanisms.*
* **A2: Morality (Straightforwardness):** Frankness in expression. *High scores correlate with "Radical Honesty".*
* **A3: Altruism:** Active concern for others' welfare. *Driver for Caregiving capacity.*
* **A4: Cooperation:** Dislike of confrontation. *Predicts "Fawn" or Compromise responses.*
* **A5: Modesty:** Tendency to play down achievements.
* **A6: Sympathy:** Compassion for others' suffering. *Critical for Emotional Validation capacity.*

#### **5. Conscientiousness Domain (The Executive System)**
*Primary Driver for: Resource Provision & Stability.*

* **C1: Self-Efficacy:** Confidence in one's ability to accomplish things.
* **C2: Orderliness:** Personal organization and tidiness. *Major source of domestic friction.*
* **C3: Dutifulness:** Sense of moral obligation/reliability.
* **C4: Achievement Striving:** Ambition and goal-orientation.
* **C5: Self-Discipline:** Ability to persist despite distractions. *Often impaired in ADHD profiles.*
* **C6: Cautiousness:** Tendency to think before acting. *Inverse correlation with Spontaneity.*

#### **6. Neurodivergence Flags (Global Modifiers)**
* **ADHD_Trait (Bool):**
    * Adjusts *Resource Needs* (requires external scaffolding).
    * Increases *Novelty Decay Rate* (boredom sets in faster).
* **ASD_Trait (Bool):**
    * Adjusts *Safety Needs* (Sensory regulation).
    * Modifies *Communication Protocol* (Requires explicit/direct verbalization).

### **3.2. Module B: RelationalNeedsComponent (The S.R.M.E. Model)**

**Theoretical Framework & Methodology:**

The S.R.M.E. model functions as a **semantic abstraction layer** (Adapter Pattern) designed to interface complex psychological constructs with user-facing needs. It avoids pseudoscientific categorization by strictly mapping each dimension to established, empirically supported psychological theories.

Each dimension serves as an aggregate container for specific biological and psychological drivers:

#### **1. Safety (S) – The Foundation**
* **Core Driver:** Affect Regulation, Anxiety Management, and Predictability.
* **Scientific Basis:**
    * **Attachment Theory (Bowlby/Ainsworth):** Corresponds directly to the concepts of "Safe Haven" and "Secure Base." It measures the user's dependency on the partner for emotional regulation.
    * **Polyvagal Theory (Porges):** Addresses the biological need for a "Neuroception of Safety" to down-regulate the sympathetic nervous system (fight/flight response).
* **System Role:** Acts as a blocking dependency. If *Safety* metrics are critical, access to *Resonance* and *Expansion* is psychologically inhibited.

#### **2. Resource (R) – The Structure**
* **Core Driver:** Instrumental Support, Executive Scaffolding, and Logistical Stability.
* **Scientific Basis:**
    * **Social Exchange Theory (Thibaut & Kelley):** Analyzes relationships through a cost-benefit framework, focusing on the exchange of tangible resources (time, labor, finance).
    * **Evolutionary Psychology (Parental Investment):** Correlates with the instinctual drive to secure environmental stability and resource accumulation.
* **System Role:** Quantifies the need for "Acts of Service" and external executive functioning (critical for High-Neuroticism or ADHD profiles).

#### **3. Resonance (M) – The Connection**
* **Core Driver:** Synchronization, Validation, and Intimacy.
* **Scientific Basis:**
    * **Self-Determination Theory (Ryan & Deci):** Maps to the intrinsic need for **Relatedness** (the universal want to interact, be connected to, and experience caring for others).
    * **Limbic Resonance (Lewis, Amini, Lannon):** The capacity for sharing deep emotional states and non-verbal attunement.
    * **Sternberg’s Triangular Theory of Love:** Corresponds to the "Intimacy" vertex (warmth, trust, and bonding).
* **System Role:** Defines the required "bandwidth" and protocol for communication (Emotional vs. Cognitive synchronization).

#### **4. Expansion (E) – The Growth**
* **Core Driver:** Novelty, Autonomy, and Self-Actualization.
* **Scientific Basis:**
    * **Self-Expansion Model (Arthur Aron):** The desire to enter relationships to "expand the self" by acquiring the partner’s resources, perspectives, and identities.
    * **Self-Determination Theory (Ryan & Deci):** Maps to the intrinsic need for **Autonomy** (volition) and growth.
    * **Big Five Correlation:** Heavily driven by the *Openness to Experience* trait.
* **System Role:** Drives the requirement for entropy reduction (fighting boredom) and personal development.

**Purpose:** Defines the core interaction style the user requires based on the aggregated drivers above.

**Dimensions:**

1. **Safety (S):** Need for regulation, predictability, and anxiety reduction.
2. **Resource (R):** Need for instrumental support, acts of service, and logistical scaffolding.
3. **Resonance (M):** Need for shared meaning, cognitive or emotional synchronization.
4. **Expansion (E):** Need for novelty, autonomy, and personal growth facilitation.

**Variables per Dimension:**

* raw_score (Float): Self-reported importance.
* calculated_weight (Float): The final importance score after Big Five adjustment.
* preferred_channel (Enum): The mode of delivery (e.g., *Verbal, Physical, Action-based*).

### **3.3. Module C: ErosComponent (Sexual Profile)**

**Methodology:** Based on the Dual Control Model (Nagoski).

**Variables:**

* accelerator_sensitivity (Float): Ease of arousal.
* brake_sensitivity (Float): Susceptibility to inhibition (stress, environment).
* context_dependency (Enum): *High* (needs specific conditions) vs *Low* (spontaneous).
* erotic_language (List<Tags>): Specific pathways to arousal (e.g., *Sapiosexual, Kinky, Sensory, Devotional*).

### **3.4. Module D: ShadowComponent (Defense & Trauma)**

**Methodology:** Attachment Theory & Gottman Conflict Styles.

**Variables:**

* attachment_style (Enum): *Secure, Anxious, Avoidant, Disorganized*.
* conflict_response (Enum): *Fight (Attack), Flight (Withdraw), Freeze (Shut down), Fawn (Appease)*.
* regulation_method (Enum): *Co-regulation* (needs partner) vs *Auto-regulation* (needs solitude).

### **3.5. Module E: ProfessionalComponent (Occupational Compass)**

**Methodology:** Based on John Holland's Theory of Career Choice (RIASEC).

**Purpose:** Analyzes how professional deformation affects relational communication and resource availability (time/energy).

**Variables:**

* primary_type (Enum): Dominant RIASEC code (e.g., *Realistic, Investigative*). Determines communication style.
* secondary_type (Enum): Supportive trait.
* tertiary_type (Enum): Situational trait.
* career_centrality (Float 0.0-1.0): Percentage of identity tied to work. High values (>0.75) trigger "Low Resource Availability" warnings for partners.

## **4. Algorithmic Logic**

### **4.1. The Correction Algorithm (Normalization and OCEAN Adjustment)**

User self-report is informative but imperfect. CRNAS therefore separates three layers:

```text
raw_score              = what the respondent selected
relationship_score     = score derived from relationship-specific items
OCEAN_prediction       = trait-based expectation from the PsychometricsComponent
calculated_weight      = final OCEAN-informed score with confidence metadata
```

OCEAN must **modify interpretation**, not override direct answers. A high trait score may indicate a likely driver or vulnerability, but it must not force a final relationship score when the respondent's direct answers disagree. Strong disagreement between direct answers and OCEAN should create a **mixed-confidence note**, not a hidden correction.

Recommended default weighting:

```text
direct relationship-specific score: 0.65–0.75
OCEAN-based prediction:             0.15–0.25
Shadow / context modifier:          0.05–0.15
Calibration:                        confidence modifier, not raw-score override
```

Hard override rules such as `if Neuroticism is high, Safety is critical regardless of what the user says` are not allowed unless separately validated with empirical data.

**Pseudocode:**

```python
def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def weighted_mean(parts):
    total_weight = sum(weight for _, weight in parts)
    if total_weight <= 0:
        return 0.0
    return sum(value * weight for value, weight in parts) / total_weight


def calculate_adjusted_score(
    direct_score,
    ocean_prediction,
    context_modifier=0.0,
    direct_weight=0.70,
    ocean_weight=0.20,
    context_weight=0.10,
):
    """
    OCEAN adjusts interpretation but does not erase direct answers.
    The context modifier should be bounded and should not act as a hidden diagnosis.
    """
    return clamp(
        direct_score * direct_weight
        + ocean_prediction * ocean_weight
        + context_modifier * context_weight
    )


def confidence_from_alignment(direct_score, ocean_prediction, calibration_flags):
    disagreement = abs(direct_score - ocean_prediction)

    if calibration_flags.get("critical_contradiction"):
        return "low"
    if disagreement >= 0.40:
        return "mixed"
    if disagreement >= 0.25:
        return "medium"
    return "high"
```

**Example: Safety OCEAN prediction**

```python
def predict_safety_from_ocean(big_five):
    return weighted_mean([
        (big_five.neuroticism.anxiety, 0.30),
        (big_five.neuroticism.vulnerability, 0.25),
        (big_five.neuroticism.self_consciousness, 0.15),
        (1.0 - big_five.agreeableness.trust, 0.20),
        (big_five.conscientiousness.cautiousness, 0.10),
    ])
```

**Interpretation rule:** if direct Safety is low but OCEAN-predicted Safety is high, the report should say that Safety may be situational, underreported, or activated mainly under stress. It must not simply force the Safety score to high.

### **4.2. The Context Interpretation Algorithm**

This algorithm maps Interests to Resonance Types based on Openness.

**Logic:**

* **Input:** User Interest (e.g., "Programming") + Psychometrics.
* **Process:**
  * IF Openness > 0.7 (High):
    * Map "Programming" to **Cognitive Resonance** (Deep discussion, architecture analysis).
  * IF Agreeableness > 0.7 AND Openness < 0.5:
    * Map "Programming" to **Emotional/Support Resonance** (Empathizing with coding burnout, celebrating success).
  * IF Conscientiousness > 0.7:
    * Map "Programming" to **Functional Resonance** (Code reviews, productivity optimization).

### **4.3. The Compatibility Heuristic (Scoring)**

Compatibility is not about identical scores, but about **Need-Provision Fit**.

Formula:
$$Compatibility = \sum (UserA.Needs_i \times UserB.Capacity_i) \times Penalty(ShadowMismatch)$$

**Critical Discussion Flags (High-Risk Interaction Loops):**

These flags are not relationship-failure predictions. They identify zones that require explicit discussion, agreements, and compensating protocols.

1. **Pursuit-Distance Loop:**
   * UserA shows anxious-leaning distance regulation and UserB shows avoidant-leaning overload regulation.
   * *Interpretation:* One partner may seek contact when the other needs distance. The report should recommend a repair protocol, not assign blame.
2. **Expansion-Safety Conflict:**
   * One partner has high Expansion need while the other has high Safety need or low Openness / low novelty tolerance.
   * *Interpretation:* Novelty may feel energizing to one partner and destabilizing to the other. The report should recommend negotiated novelty boundaries.
3. **Resource-Routine Friction:**
   * One partner has high Resource need while the other has low Conscientiousness, high overload, or low practical provision capacity.
   * *Interpretation:* Practical care may fail through execution limits rather than lack of love. The report should distinguish willingness from capacity.
4. **Resonance-Style Mismatch:**
   * One partner seeks deep emotional/cognitive resonance while the other expresses care primarily through practical or low-verbal channels.
   * *Interpretation:* The mismatch may be a language/protocol difference, not absence of care.
5. **Eros Brake/Pressure Loop:**
   * One partner's closeness increases through initiation and novelty while the other's brakes activate under pressure, fatigue, sensory load, or relational uncertainty.
   * *Interpretation:* The report should recommend low-pressure consent-based pacing and context clarification.

## **5. Survey Methodology (Input Strategy)**

To populate these components, the survey must use **Scenario-Based Inquiries** rather than declarative statements.

**Example Data Collection Pattern:**

* *Do not ask:* "Do you like intellectual conversations?"
* *Ask:* "You and your partner disagree on a complex topic. What is your ideal outcome?"
  * A) We drop it to keep the peace. (Maps to: *Safety > Resonance*)
  * B) We debate until we find the logical truth, even if it gets heated. (Maps to: *Resonance (Cognitive) > Safety*)
  * C) My partner listens to my feelings about the topic. (Maps to: *Resonance (Emotional)*)

### **5.1. Full 100-Item Bank Plan**

CRNAS uses a 100-item Full Mode for practical dyadic comparison. This mode is not intended to create population percentiles or diagnostic labels. Its purpose is to produce a dense, construct-referenced map of a person's needs, provision capacities, regulation strategies, and context sensitivities, so that two profiles can be compared through Need-Provision Fit.

The 100-item bank is divided as follows:

| Block | Items | Purpose |
|---|---:|---|
| SRME Needs | 40 | Measures what the respondent needs from a relationship |
| Shadow / Regulation | 16 | Measures likely regulation and conflict-response strategies |
| Eros / Context | 16 | Measures activation, inhibition, and context-dependency patterns |
| Provision / Capacity | 20 | Measures what the respondent can realistically provide to a partner |
| Consistency / Calibration | 8 | Detects contradiction, situational dependency, and confidence limits |
| **Total** | **100** | Full dyadic compatibility profile |

The 100-item mode should be treated as the recommended profile for serious partner comparison. Shorter modes may be used for first-pass screening, but they should produce lower-confidence outputs.

#### **5.1.1. SRME Needs Block — 40 items**

The SRME Needs block measures the respondent's own relational requirements.

Target dimensions:

- Safety
- Resource
- Resonance
- Expansion

Recommended structure:

| Item family | Items | Distribution |
|---|---:|---|
| Absolute need-intensity items | 24 | 6 per SRME dimension |
| Priority / Best-Worst tradeoff items | 16 | repeated SRME tradeoff blocks |
| **Total** | **40** | 10 usable signals per SRME dimension |

Absolute items measure the strength of one need in one concrete situation. Priority items measure which need wins when not all needs can be satisfied at the same time.

Absolute item rule:

- one scenario;
- one target dimension;
- four ordered anchors;
- vector values only on the target dimension;
- no moral ranking;
- no hidden “healthy answer”.

Recommended anchors:

```text
0.0000 = almost not needed
0.3333 = sometimes helpful
0.6667 = important
1.0000 = critical / required before contact can continue normally
```

Priority item rule:

* one realistic tradeoff situation;
* four balanced options;
* one option mapped to each SRME dimension;
* respondent selects the most important and least critical option;
* no option should sound more mature, responsible, or morally correct than the others.

Priority scores should be interpreted as relative salience under constraint, not as absolute need intensity.

#### **5.1.2. Shadow / Regulation Block — 16 items**

The Shadow / Regulation block measures likely attachment and conflict-response strategies. It must not diagnose attachment style, trauma, or personality pathology.

Target vectors:

* secure
* anxious
* avoidant
* disorganized

Recommended coverage:

| Context                            |  Items |
| ---------------------------------- | -----: |
| Ambiguous distance / delayed reply |      2 |
| Conflict escalation                |      2 |
| Criticism / shame trigger          |      2 |
| Need for closeness vs autonomy     |      2 |
| Repair after rupture               |      2 |
| Partner overwhelm or withdrawal    |      2 |
| Boundary negotiation               |      2 |
| Stress, fatigue, or shutdown       |      2 |
| **Total**                          | **16** |

Each item should present one relational stressor and four plausible responses. The options should describe behavior, not identity.

Bad wording:

```text
I am needy.
I am cold.
I am broken.
I am healthy.
```

Good wording:

```text
I ask directly what happened and wait for a clear answer.
I start checking whether the connection is at risk.
I withdraw until I can think clearly.
I want contact and fear it at the same time.
```

The secure option may represent a more regulated strategy, but it must not be written as morally superior.

#### **5.1.3. Eros / Context Block — 16 items**

The Eros / Context block measures erotic activation and inhibition patterns using the Dual Control Model logic.

Target vectors:

* accelerator
* brake

Recommended coverage:

| Context                              |  Items |
| ------------------------------------ | -----: |
| Emotional safety and trust           |      2 |
| Stress and fatigue                   |      2 |
| Novelty and play                     |      2 |
| Pressure, expectation, or obligation |      2 |
| Sensory comfort / sensory overload   |      2 |
| Initiation and responsiveness        |      2 |
| Recovery, aftercare, and pacing      |      2 |
| Autonomy, consent, and interruption  |      2 |
| **Total**                            | **16** |

Items may load on both vectors when the option implies mixed activation and inhibition. For example, an option may indicate high desire under safe conditions but strong inhibition under pressure.

Eros items must never moralize:

* low desire;
* responsive desire;
* need for context;
* sensory sensitivity;
* need for predictability;
* need for aftercare;
* reduced desire under stress.

The output must describe context patterns, not sexual worth, normality, or adequacy.

#### **5.1.4. Provision / Capacity Block — 20 items**

The Provision / Capacity block is required for stronger dyadic comparison. It measures what the respondent can realistically and sustainably provide to a partner.

This block should mirror SRME, but from the provider side.

Target dimensions:

* safety_provision
* resource_provision
* resonance_provision
* expansion_provision

Recommended structure:

| Provision vector    |  Items | Measures                                                                               |
| ------------------- | -----: | -------------------------------------------------------------------------------------- |
| Safety provision    |      5 | ability to provide predictability, repair, calm tone, emotional safety                 |
| Resource provision  |      5 | ability to provide practical help, planning, task-sharing, executive support           |
| Resonance provision |      5 | ability to provide attention, conversation, validation, cognitive/emotional attunement |
| Expansion provision |      5 | ability to provide novelty, autonomy, exploration, growth, freedom                     |
| **Total**           | **20** | partner-facing capacity map                                                            |

Provision items must distinguish willingness, capacity, and sustainability.

A person may want to provide a form of support but be unable to do it consistently. The scoring should therefore prefer concrete behavior over ideal self-image.

Bad item:

```text
Are you a supportive partner?
```

Good item:

```text
When your partner is overwhelmed and asks for a clear plan, how realistically can you help create structure without becoming controlling or resentful?
```

Provision scoring should use behavioral anchors:

```text
0.0000 = rarely able / drains me quickly
0.3333 = possible in easy conditions
0.6667 = usually able with reasonable limits
1.0000 = strong and sustainable capacity
```

Need-Provision comparison should use both directions:

```text
UserA.need.safety       ↔ UserB.capacity.safety_provision
UserB.need.safety       ↔ UserA.capacity.safety_provision

UserA.need.resource     ↔ UserB.capacity.resource_provision
UserB.need.resource     ↔ UserA.capacity.resource_provision

UserA.need.resonance    ↔ UserB.capacity.resonance_provision
UserB.need.resonance    ↔ UserA.capacity.resonance_provision

UserA.need.expansion    ↔ UserB.capacity.expansion_provision
UserB.need.expansion    ↔ UserA.capacity.expansion_provision
```

This prevents the system from falsely assuming that low personal need means high provision capacity.

#### **5.1.5. Consistency / Calibration Block — 8 items**

The Consistency / Calibration block does not create a personality label. It controls confidence.

Recommended coverage:

| Calibration target                                     | Items |
| ------------------------------------------------------ | ----: |
| Stability across stress vs calm conditions             |     2 |
| Difference between ideal answer and realistic behavior |     2 |
| Context dependency                                     |     2 |
| Contradiction between need and priority                |     2 |
| **Total**                                              | **8** |

Calibration items should detect cases such as:

* the respondent reports high Safety in absolute items but repeatedly deprioritizes Safety in tradeoff items;
* the respondent reports low need for support but high distress when support is absent;
* the respondent reports high provision capacity but only under ideal conditions;
* the respondent reports stable eros activation but strong inhibition under stress or pressure.

The system should not simply average contradictions away. It should report them.

Example output:

```text
The profile shows a possible contradiction: Safety is high in direct scenarios but often deprioritized in tradeoff choices. This may mean Safety is only consciously visible under stress, or that the respondent values autonomy and competence so strongly that they underreport safety needs until overloaded.
```

#### **5.1.6. Minimum signal rule**

A vector should not be interpreted strongly unless it has enough independent item signals.

Recommended confidence thresholds:

| Confidence | Requirement                                           |
| ---------- | ----------------------------------------------------- |
| Low        | fewer than 6 usable signals, or strong contradictions |
| Medium     | 6–7 usable signals with partial coherence             |
| High       | 8–10+ usable signals with coherent response patterns  |

For the Full 100-item bank:

* SRME needs should reach high confidence.
* Provision vectors should reach medium-to-high confidence.
* Shadow and Eros should reach at least medium confidence.
* Calibration items should modify confidence, not replace domain scoring.

#### **5.1.7. Difference interpretation for dyadic comparison**

CRNAS should avoid absolute compatibility claims. Differences should be interpreted as discussion signals.

For normalized `0.0–1.0` scores:

|  Difference | Interpretation                                            |
| ----------: | --------------------------------------------------------- |
| `0.00–0.14` | minor or probably not meaningful                          |
| `0.15–0.29` | noticeable difference; worth discussing                   |
| `0.30–0.49` | meaningful mismatch or complementarity                    |
|     `0.50+` | critical gap; requires explicit agreement or compensation |

These thresholds are heuristic. They are not population-validated cutoffs.

Need-Provision gaps should be prioritized over Need-Need differences. A couple may have different needs and still function well if each person can provide what the other person strongly needs.

#### **5.1.8. Item construction methodology**

Every item must be created from a construct map before wording is drafted.

Each item card should document:

```yaml
id:
module:
family:
target_vector:
secondary_vector:
scenario_context:
construct_definition:
response_process_hypothesis:
scoring_rationale:
neurodivergence_risk:
social_desirability_risk:
moral_ranking_risk:
review_status:
bank_version:
```

Item-writing rules:

1. Use one scenario per item.
2. Measure one primary construct per item.
3. Avoid abstract identity claims.
4. Prefer concrete relational situations.
5. Keep all options similarly attractive and similarly specific.
6. Avoid moralized wording.
7. Avoid clinical labels in user-facing text.
8. Avoid double-barreled options.
9. Avoid assumptions about gender, culture, neurotype, sexuality, or relationship model.
10. Do not treat directness, solitude, sensory limits, delayed processing, or low spontaneity as deficits.
11. Do not ask for trauma disclosure unless the item has a specific safety rationale.
12. Every option must be plausible for a reasonable respondent.

#### **5.1.9. Bank balancing rules**

The 100-item bank must be balanced by:

* module;
* vector;
* scenario context;
* emotional intensity;
* option length;
* positive/negative framing;
* neurodivergence accessibility;
* partner-facing vs self-facing perspective.

No single SRME vector should be overrepresented in high-stress scenarios. For example, Safety should not be the only dimension tested under conflict, and Expansion should not be tested only through pleasant novelty. Each dimension should appear in both easy and difficult contexts.

Recommended SRME context coverage:

| Context                | Safety | Resource | Resonance | Expansion |
| ---------------------- | -----: | -------: | --------: | --------: |
| conflict / repair      |    yes |      yes |       yes |       yes |
| fatigue / overload     |    yes |      yes |       yes |       yes |
| daily routine          |    yes |      yes |       yes |       yes |
| planning / uncertainty |    yes |      yes |       yes |       yes |
| closeness / distance   |    yes |      yes |       yes |       yes |
| novelty / change       |    yes |      yes |       yes |       yes |

#### **5.1.10. Validation status and claims**

The 100-item Full Mode may support structured dyadic hypotheses. It must not claim:

* clinical diagnosis;
* population percentile;
* predictive validity for relationship success;
* objective ranking of partners;
* universal compatibility percentage.

Allowed claims:

```text
This result is a structured self-assessment profile.
This result maps needs, capacities, regulation patterns, and context sensitivities.
This result can support partner discussion.
This result can identify likely mismatch zones.
This result is not a diagnosis or a population-normed test.
```

#### **5.1.11. Recommended implementation modes**

CRNAS should support three modes:

| Mode     | Items | Use                           |
| -------- | ----: | ----------------------------- |
| Simple   |    40 | fast first-pass screening     |
| Extended |    72 | stable self-description       |
| Full     |   100 | recommended dyadic comparison |


### **5.2. Psychometric Standards Applied by CRNAS**

CRNAS uses established psychometric standards as methodological guardrails. These standards do not make CRNAS a clinically validated or population-normed instrument by themselves. They define how the question bank should be constructed, documented, reviewed, scored, and reported.

#### **5.2.1. Standards for Educational and Psychological Testing — AERA / APA / NCME, 2014**

**Full name:** *Standards for Educational and Psychological Testing*.

**Organizations:** American Educational Research Association (AERA), American Psychological Association (APA), and National Council on Measurement in Education (NCME).

**Use in CRNAS:** primary standard for test development, validity, reliability, fairness, scoring, reporting, and documentation.

Main principles applied to CRNAS:

1. **Validity is about score interpretation and use.**
   - CRNAS must validate the interpretation it makes, not merely the existence of questions.
   - A CRNAS score is valid only for its stated use: structured self-assessment and dyadic discussion.
   - CRNAS must not claim diagnosis, population percentile, or relationship-success prediction.

2. **Construct definition precedes item writing.**
   - Every item must map to a documented construct.
   - The bank must avoid construct underrepresentation: missing important parts of a construct.
   - The bank must avoid construct-irrelevant variance: measuring literacy, class, cultural style, neurotype, shame, or social desirability instead of the intended construct.

3. **Reliability and measurement error must be acknowledged.**
   - CRNAS must report confidence and contradiction notes.
   - Short modes must produce lower-confidence output than the 100-item Full Mode.
   - Scores should not be interpreted strongly when item signals are sparse or inconsistent.

4. **Fairness is part of validity.**
   - Items must be reviewed for bias against neurodivergent, culturally diverse, nontraditional, disabled, low-resource, queer, asexual-spectrum, or non-cohabiting respondents.
   - Direct communication, need for routine, sensory limits, delayed processing, low spontaneity, low desire under stress, or need for solitude must not be treated as deficits.

5. **Test development and revision must be documented.**
   - CRNAS must keep item cards, construct blueprints, scoring rationales, review status, bank versions, and bank fingerprints.
   - Any scoring or construct change requires versioning.

6. **Administration, scoring, and reporting must fit the intended use.**
   - Reports must state what scores mean and what they do not mean.
   - Reports must avoid deterministic labels.
   - Reports must present mismatch as a discussion signal, not a verdict.

#### **5.2.2. ITC Guidelines on Test Use — International Test Commission**

**Full name:** *International Test Commission Guidelines on Test Use*.

**Use in CRNAS:** ethical use, informed interpretation, responsible reporting, privacy, and appropriate feedback.

Main principles applied to CRNAS:

1. **Use tests only for appropriate purposes.**
   - CRNAS is appropriate for self-reflection and partner discussion.
   - CRNAS is not appropriate for diagnosis, partner screening, coercive relationship decisions, employment, military screening, legal decisions, or clinical assessment.

2. **Interpret scores within their limits.**
   - CRNAS must not hide uncertainty.
   - Derived OCEAN-informed provision estimates must be marked as estimates.
   - Confidence should be reported separately from score magnitude.

3. **Protect respondents.**
   - Questions must avoid unnecessary trauma disclosure.
   - Eros questions must be consent-respecting and non-shaming.
   - Exported profiles must include only necessary data and must preserve privacy.

4. **Communicate results responsibly.**
   - Reports should use neutral language.
   - Reports should support discussion and agency.
   - Reports must not tell users that a relationship will succeed or fail.

#### **5.2.3. ITC Guidelines for Translating and Adapting Tests, Second Edition**

**Full name:** *International Test Commission Guidelines for Translating and Adapting Tests, Second Edition*.

**Use in CRNAS:** Ukrainian/English wording, localization, future multilingual versions, and cultural adaptation.

Main principles applied to CRNAS:

1. **Preserve construct equivalence, not literal wording.**
   - If CRNAS is translated, the item must preserve the same psychological construct.
   - Literal translation is not enough if the scenario changes cultural meaning.

2. **Use forward review, back review, and cultural review when possible.**
   - A translated item should be reviewed for semantic equivalence, emotional intensity, option balance, and cultural assumptions.

3. **Avoid culture-bound assumptions.**
   - Items must not assume cohabitation, marriage, children, shared finances, therapy vocabulary, Western individualist communication norms, high income, private housing, or flexible work schedules unless the construct explicitly requires it.

4. **Document adaptation decisions.**
   - If wording is changed for cultural fit, the item card must record the reason.

#### **5.2.4. ITC Guidelines on Computer-Based and Internet-Delivered Testing**

**Full name:** *International Test Commission Guidelines on Computer-Based and Internet-Delivered Testing*.

**Use in CRNAS:** Streamlit/web administration, profile export, client-side comparison, and user interface behavior.

Main principles applied to CRNAS:

1. **Administration must be consistent.**
   - The same mode should use the same items, response format, scoring model, and bank fingerprint.

2. **The interface must not bias answers.**
   - Option order should not imply desirability.
   - Visual design should not emphasize one option as better.
   - Progress indicators should not pressure users into speed over accuracy.

3. **Users need clear instructions.**
   - The app should state that answers should reflect realistic behavior, not ideal self-image.
   - Users should be told that there are no morally correct answers.

4. **Data protection matters.**
   - Exported profiles should be portable but not silently uploaded.
   - Reports should avoid storing unnecessary sensitive raw details.

#### **5.2.5. ITC Guidelines on Quality Control in Scoring, Test Analysis and Reporting of Test Scores**

**Full name:** *International Test Commission Guidelines on Quality Control in Scoring, Test Analysis and Reporting of Test Scores*.

**Use in CRNAS:** scoring reproducibility, quality gates, reporting, and automated tests.

Main principles applied to CRNAS:

1. **Scoring must be reproducible.**
   - Same input + same bank fingerprint + same scoring model must produce the same output.

2. **Scoring must be auditable.**
   - Each score should be traceable to item responses, vector mappings, OCEAN modifiers, and calibration flags.

3. **Reporting must include limitations.**
   - Direct scores, derived scores, OCEAN-adjusted scores, provision scores, confidence, and explanation must be separated.

4. **Quality control should be automated where possible.**
   - Schema validation, vector validation, forbidden wording, option-length balance, context balance, and bank fingerprint changes should be tested.

#### **5.2.6. COSMIN Methodology for Measurement Properties**

**Full name:** *COSMIN — COnsensus-based Standards for the selection of health Measurement INstruments*.

**Use in CRNAS:** adapted as a measurement-quality framework, especially for content validity, structural validity, internal consistency, reliability, measurement error, construct validity, cross-cultural validity / measurement invariance, and responsiveness. CRNAS is not a health outcome instrument, so COSMIN is used as a methodological checklist rather than a claim of health-measure compliance.

Main principles applied to CRNAS:

1. **Content validity is central.**
   - Items must be relevant, comprehensive, and understandable for the intended construct.
   - Each construct must have enough items to cover its domain.

2. **Structural validity is a future empirical target.**
   - If data are collected, CRNAS should test whether SRME, Shadow, Eros, and Provision behave as expected.

3. **Internal consistency should be checked only when appropriate.**
   - Internal consistency is appropriate for reflective multi-item dimensions.
   - It is not appropriate for forced tradeoff / ipsative Best-Worst blocks in the same way as ordinary Likert scales.

4. **Reliability and measurement error should be documented.**
   - If repeat data are available, CRNAS should estimate test-retest stability.
   - Until then, confidence should be based on signal count, contradiction flags, and item coherence.

5. **Cross-cultural validity and measurement invariance are future requirements for public use.**
   - If CRNAS becomes public across languages or groups, it should test whether items function similarly across groups.

#### **5.2.7. Boateng et al. Scale Development Framework, 2018**

**Full name:** *Best Practices for Developing and Validating Scales for Health, Social, and Behavioral Research*.

**Use in CRNAS:** staged item-bank development.

Main principles applied to CRNAS:

1. **Phase 1 — Item development.**
   - Define the domain.
   - Generate item pool.
   - Assess content validity.

2. **Phase 2 — Scale development.**
   - Pretest questions.
   - Administer survey when possible.
   - Reduce or revise weak items.

3. **Phase 3 — Scale evaluation.**
   - Test dimensionality.
   - Estimate reliability.
   - Assess validity.

For CRNAS, Phase 1 is mandatory before activation. Phases 2–3 are optional future empirical validation stages unless the system begins making stronger public claims.

#### **5.2.8. IPIP / Big Five Public-Domain Measurement Tradition**

**Full name:** *International Personality Item Pool (IPIP)*.

**Use in CRNAS:** open, reviewable source tradition for Big Five / OCEAN-related construct language and facet mapping.

Main principles applied to CRNAS:

1. **Use OCEAN as a substrate, not as a moral ranking.**
   - High or low trait values are not good or bad.
   - They indicate likely tendencies, not fixed identity.

2. **Prefer facet-level interpretation.**
   - CRNAS should use facets where possible: Anxiety vs Vulnerability, Emotionality vs Intellect, Orderliness vs Dutifulness, etc.

3. **Keep OCEAN separate from relationship-specific direct answers.**
   - OCEAN provides prediction and explanation.
   - Direct SRME/Shadow/Eros/Provision items provide relationship-specific evidence.

4. **Report disagreement between OCEAN and direct answers.**
   - Trait-based expectation and direct scenario answers may diverge.
   - Divergence should lower confidence or create a nuance note.

### **5.3. Question-Bank Construction Methodology**

This section defines the mandatory methodology for constructing, reviewing, balancing, and maintaining the CRNAS question bank.

CRNAS is a construct-referenced dyadic self-assessment system. Its question bank must be developed from explicit construct definitions, not from intuitive “relationship advice” categories. The bank is intended to generate structured compatibility hypotheses, not diagnoses, population percentiles, or objective predictions of relationship success.

The primary goal of the bank is to support fair, non-moralizing, neurodivergence-aware comparison of two profiles through:

```text
Need ↔ Provision Fit
Regulation ↔ Regulation Interaction
Eros Context ↔ Eros Context Fit
OCEAN-informed interpretation
Confidence and contradiction flags
```

#### **5.3.1. Core item-bank principles**

Every question must satisfy five principles:

1. **Construct relevance**
   - The item must measure a documented CRNAS construct.
   - The item must not measure a vague social preference unless that preference is explicitly mapped to a construct.
   - The item must not mix several constructs unless it is explicitly designed as a tradeoff item.

2. **Dyadic usefulness**
   - The item must produce information that helps compare two people.
   - The item should clarify either what the respondent needs, what the respondent can provide, how the respondent reacts under stress, what conditions activate/inhibit closeness, or where partner mismatch may occur.

3. **Non-diagnostic framing**
   - The item must not diagnose attachment disorder, trauma, personality disorder, sexual dysfunction, ADHD, autism, or any clinical condition.
   - The system may describe patterns, not diagnoses.

4. **Bias minimization**
   - No option should be obviously more mature, healthy, loving, rational, responsible, sexual, independent, or emotionally developed.
   - Options may differ in construct meaning, but not in moral status.

5. **Concrete response process**
   - The respondent should answer from a concrete imagined or remembered situation.
   - The item should not require abstract self-labeling.

Bad pattern:

```text
Are you emotionally mature in conflict?
```

Good pattern:

```text
After a tense conversation, your partner says they need two hours alone before continuing. What response is closest to your usual reaction?
```

#### **5.3.2. Required construct blueprint**

Before an item is written, the target construct must exist in the construct blueprint.

Each construct must be documented using this schema:

```yaml
construct_id:
module:
user_facing_name:
technical_definition:
included_behaviors:
excluded_behaviors:
primary_vectors:
secondary_vectors:
ocean_drivers:
known_bias_risks:
neurodivergence_considerations:
example_contexts:
forbidden_interpretations:
allowed_output_language:
```

Example:

```yaml
construct_id: safety.predictability_after_distance
module: needs
user_facing_name: Predictability after distance
technical_definition: Need for clear timing, contact expectations, and reassurance after relational distance or delayed response.
included_behaviors:
  - wanting clear reply timing
  - needing confirmation that the relationship is not at risk
  - preferring explicit repair after ambiguity
excluded_behaviors:
  - general jealousy
  - control over partner autonomy
  - surveillance
primary_vectors:
  - safety
secondary_vectors:
  - resonance
ocean_drivers:
  - neuroticism.anxiety
  - neuroticism.vulnerability
  - agreeableness.trust_inverse
known_bias_risks:
  - may pathologize anxious regulation
  - may confuse safety need with control
neurodivergence_considerations:
  - explicit timing may be a communication accommodation, not insecurity
forbidden_interpretations:
  - "clingy"
  - "immature"
  - "controlling" unless direct controlling behavior is actually measured
allowed_output_language:
  - "needs explicit timing"
  - "benefits from predictable repair"
  - "may experience ambiguity as unsafe"
```

No item may be added to the bank without a matching construct blueprint entry.

#### **5.3.3. Required item card**

Every item must have a reviewable item card. The deployed JSON may remain compact, but the authoring source must preserve the item card.

```yaml
id:
bank:
version:
module:
family:
response_type:
target_construct:
primary_vector:
secondary_vectors:
scenario_context:
stress_level:
relationship_phase:
item_text:
options:
  - label:
    text:
    vector:
    scoring_rationale:
    expected_response_process:
construct_rationale:
ocean_relevance:
bias_review:
  moral_ranking:
  social_desirability:
  gender_bias:
  culture_bias:
  neurodivergence_bias:
  sexuality_bias:
  class_or_resource_bias:
  trauma_trigger_risk:
language_review:
  reading_level:
  abstractness:
  double_barreled:
  option_length_balance:
  emotional_intensity_balance:
  hidden_social_inference:
status:
review_notes:
```

A question is not valid for the active bank if the item card is missing or incomplete.

#### **5.3.4. Item family rules**

CRNAS uses six item families:

| Family | Purpose | Primary Risk |
|---|---|---|
| `absolute_need` | measures intensity of one need | mixing several constructs |
| `priority_best_worst` | measures tradeoff priority | making one option morally superior |
| `shadow_strategy` | measures stress/regulation response | pathologizing insecure strategies |
| `eros_context` | measures activation/inhibition conditions | moralizing desire or context dependency |
| `provision_capacity` | measures what respondent can provide | social desirability / ideal self-image |
| `calibration` | detects contradiction and confidence limits | making it feel like a trick question |

Each family must have its own writing rules.

#### **5.3.5. Absolute need item rules**

Absolute need items measure the intensity of one SRME need.

Required properties:

```yaml
family: absolute_need
response_type: single_choice
target_vector: exactly one of [safety, resource, resonance, expansion]
option_count: 4
```

Rules:

1. The scenario must activate only one primary SRME dimension.
2. The four options must be ordered by intensity of the same need.
3. The options must not represent four different needs.
4. The strongest option must not sound morally better than the weakest option.
5. The weakest option must not sound emotionally deficient.
6. The item must not imply that lower need is healthier.

Recommended scoring:

```text
0.0000 = not needed / not relevant in this situation
0.3333 = helpful but not necessary
0.6667 = important for comfort or connection
1.0000 = critical for functioning, repair, or continued closeness
```

Bad absolute item:

```text
When you are stressed, what do you want?
A. To be left alone.
B. Practical help.
C. A deep conversation.
D. A new shared experience.
```

This is not an absolute item. It is a priority or preference item because each answer maps to a different construct.

Good absolute item:

```text
When plans change suddenly, how much does it help if your partner clearly explains what changed and what will happen next?
A. It is usually not important to me.
B. It helps a little, but I can manage without it.
C. It is important; I feel much better with a clear explanation.
D. It is critical; without clarity I can become tense or dysregulated.
```

#### **5.3.6. Priority / Best-Worst item rules**

Priority items measure which need wins under constraint.

Required properties:

```yaml
family: priority_best_worst
response_type: best_worst
option_count: 4
vectors:
  - safety
  - resource
  - resonance
  - expansion
```

Rules:

1. Each option must map primarily to one SRME vector.
2. All four options must be similarly attractive.
3. No option may be the obvious “adult” or “healthy” answer.
4. No option may be framed as selfish, childish, cold, needy, chaotic, or boring.
5. Options must be similar in length and emotional intensity.
6. The scenario must make scarcity realistic: limited time, limited energy, post-conflict repair, fatigue, transition, uncertainty, or competing needs.
7. The respondent must choose both most important and least critical.

Good priority item:

```text
You and your partner have only a short evening after a difficult day. What matters most, and what is least critical tonight?

A. Clear reassurance that everything between you is okay.
B. Practical help with one concrete task.
C. A meaningful conversation where you both feel understood.
D. Doing something fresh or playful to reset the mood.
```

Scoring:

```text
best choice  = +1 to selected vector
worst choice = -1 to selected vector
unselected   = 0
```

Priority scores must be interpreted as relative salience, not absolute need intensity.

#### **5.3.7. Shadow / Regulation item rules**

Shadow items measure likely regulation strategies under relational stress.

Target vectors:

```text
secure
anxious
avoidant
disorganized
```

Rules:

1. The item must describe a stressor, not a personality label.
2. Options must describe behavior, not identity.
3. The secure option must not be written as “the correct answer”.
4. Anxious options must not be written as “needy” or “irrational”.
5. Avoidant options must not be written as “cold” or “uncaring”.
6. Disorganized options must not be written as “broken” or “unstable”.
7. Neurodivergent shutdown, delayed processing, sensory overload, or need for solitude must not automatically score as avoidant or disorganized.
8. The item must distinguish needing space to regulate, withdrawing to punish, avoiding vulnerability, and being overloaded.

Bad wording:

```text
I become needy and demand reassurance.
I coldly shut down.
I act chaotic and unstable.
I respond maturely.
```

Good wording:

```text
I ask directly what is happening and what we will do next.
I look for reassurance that the relationship is still safe.
I need distance before I can think or speak clearly.
I feel both pulled toward contact and pushed away from it.
```

Output language must use “strategy”, “pattern”, or “tendency”, not fixed attachment identity.

Allowed:

```text
The profile shows an anxious-leaning response pattern under distance.
```

Not allowed:

```text
You are anxiously attached.
```

#### **5.3.8. Eros / Context item rules**

Eros items measure activation, inhibition, and context dependency.

Target vectors:

```text
accelerator
brake
context_dependency
```

Rules:

1. Items must never moralize desire level.
2. High accelerator must not be treated as better.
3. High brake must not be treated as dysfunction.
4. Responsive desire must not be treated as lower quality than spontaneous desire.
5. Need for safety, predictability, aftercare, sensory comfort, or emotional connection must not be treated as immaturity.
6. The item must explicitly respect consent and autonomy.
7. The item must not pressure disclosure of trauma or explicit sexual history.
8. The item should focus on conditions, not performance.

Bad item:

```text
How sexually open are you?
```

Good item:

```text
When there has been stress or emotional distance during the day, what usually helps closeness become possible again?
```

Eros output must describe context pattern.

Allowed:

```text
High context dependency: closeness is more likely when pressure is low and emotional safety is clear.
```

Not allowed:

```text
Low libido.
Sexually difficult.
Not passionate enough.
```

#### **5.3.9. Provision / Capacity item rules**

Provision items measure what the respondent can realistically provide to a partner.

Target vectors:

```text
safety_provision
resource_provision
resonance_provision
expansion_provision
```

Provision must distinguish four things:

```text
willingness      = I want to provide it
skill            = I know how to provide it
capacity         = I have energy/time to provide it
sustainability   = I can provide it without resentment or collapse
```

Rules:

1. Do not ask whether the respondent is a “good partner”.
2. Do not ask ideal-self questions.
3. Use stressed or imperfect conditions.
4. Include limits and sustainability.
5. Avoid rewarding self-sacrifice.
6. Avoid treating constant availability as high provision.
7. Avoid treating emotional labor as automatically owed.
8. Make “I can provide this with boundaries” a valid high-quality answer.

Bad item:

```text
Are you always there for your partner?
```

Good item:

```text
When your partner needs reassurance but you are tired and overstimulated, what can you realistically provide without becoming resentful or shutting down?
```

Provision scoring anchors:

```text
0.0000 = rarely able, or it drains me quickly
0.3333 = possible only in easy conditions
0.6667 = usually able with reasonable limits
1.0000 = strong, realistic, and sustainable capacity
```

Provision must be combined with OCEAN as an adjustment layer, not replaced by OCEAN.

#### **5.3.10. Calibration item rules**

Calibration items detect reliability limits inside one profile.

Calibration targets:

```text
ideal_self_vs_real_behavior
stress_vs_calm_difference
need_vs_priority_contradiction
capacity_vs_sustainability_contradiction
context_dependency
response_confidence
```

Rules:

1. Calibration items must not feel like trick questions.
2. They must not punish contradiction.
3. They must identify when interpretation should become lower-confidence.
4. They should compare ideal conditions with stressed conditions.
5. They should detect when the respondent answers from values rather than behavior.

Example:

```text
Which is closer to your real pattern, not your ideal?
A. I can usually give support even when I am tired.
B. I want to give support, but my ability drops sharply when I am overloaded.
C. I can give practical help more easily than emotional presence.
D. I need to recover first, otherwise my support becomes tense or resentful.
```

Calibration does not create a new personality score. It modifies confidence and explanation.

#### **5.3.11. OCEAN-informed construction rules**

OCEAN is a mandatory substrate layer, but it must not override direct responses.

OCEAN is used for:

1. selecting construct coverage;
2. generating hypotheses;
3. adjusting final scores;
4. estimating provision potential;
5. explaining mismatch;
6. modifying confidence.

OCEAN must not be used to:

1. diagnose the respondent;
2. invalidate direct answers;
3. force a person into a predetermined profile;
4. treat a trait as moral quality;
5. infer actual partner behavior without evidence.

Recommended rule:

```text
direct item score has priority over OCEAN prediction
OCEAN modifies interpretation, not identity
OCEAN disagreement lowers confidence or creates a contradiction note
```

Example:

```text
If direct Safety need is low but Neuroticism-Anxiety and Vulnerability are high, the system should not force Safety to high. It should report a mixed-confidence hypothesis: Safety may be situational, underreported, or activated mainly under stress.
```

Recommended weights:

```text
Direct relationship-specific score: 0.65–0.75
OCEAN-based prediction:           0.15–0.25
Shadow/context modifier:          0.05–0.15
Calibration modifier:             confidence only, not raw score
```

Hard override rules such as `if Neuroticism is high, Safety is critical regardless of answer` are not allowed unless empirically validated.

#### **5.3.12. Bias and fairness checklist**

Each item must be reviewed against this checklist.

##### Moral bias

Reject or revise if:

- one option sounds obviously more mature;
- one option sounds selfish, childish, cold, needy, unstable, weak, boring, or irresponsible;
- high capacity is framed as constant availability;
- emotional intensity is framed as deeper love;
- low emotional expressiveness is framed as lack of care.

##### Social desirability bias

Reject or revise if:

- the desirable answer is obvious;
- the item asks about values rather than behavior;
- the item rewards self-sacrifice;
- the item punishes boundaries;
- the item asks “are you supportive / honest / mature / caring”.

##### Neurodivergence bias

Reject or revise if:

- need for explicit communication is treated as insecurity;
- need for routine is treated as rigidity;
- need for novelty is treated as immaturity;
- delayed processing is treated as avoidance;
- sensory overload is treated as rejection;
- difficulty with household execution is treated as lack of love;
- direct language is treated as emotional coldness.

##### Gender and relationship-model bias

Reject or revise if:

- the item assumes heterosexual roles;
- the item assumes monogamy unless the construct requires it;
- the item assumes cohabitation;
- the item assumes traditional gendered labor;
- the item assumes one partner should lead emotionally or logistically;
- the item assumes marriage, children, shared finances, or sexual availability.

##### Culture and class bias

Reject or revise if:

- the item requires money, private space, flexible schedule, therapy literacy, or high education to choose the “good” answer;
- the item treats travel, restaurants, gifts, or leisure time as universal relationship resources;
- the item assumes Western individualist communication norms as inherently superior.

##### Sexuality and consent bias

Reject or revise if:

- higher sexual frequency is treated as better;
- spontaneous desire is treated as better than responsive desire;
- pressure tolerance is treated as passion;
- boundaries reduce the score;
- aftercare or predictability is treated as fragility;
- kink, vanilla preferences, low desire, asexual-spectrum experience, or sensory limits are moralized.

##### Trauma and safety bias

Reject or revise if:

- the item asks for trauma disclosure without necessity;
- the item uses graphic or triggering examples;
- the item pathologizes protective behavior;
- the item implies that trust must be given quickly;
- the item treats fear responses as character flaws.

#### **5.3.13. Option-balance rules**

For every multiple-choice item:

1. Options should be within a similar length range.
2. Options should have similar emotional intensity.
3. Options should use the same grammatical form.
4. Options should avoid unequal specificity.
5. No option should contain extra justification that makes it more sympathetic.
6. No option should contain stigmatizing adjectives.
7. No option should include multiple behaviors unless all options do.
8. No option should be a joke, exaggeration, or caricature.
9. “None of the above” should be avoided unless the scoring model supports it.
10. If “it depends” is necessary, the item should probably be rewritten as a context item.

Bad option set:

```text
A. I calmly and maturely explain my feelings.
B. I panic.
C. I disappear.
D. I become chaotic.
```

Better option set:

```text
A. I try to clarify what happened and what each of us needs next.
B. I look for reassurance that the relationship is still safe.
C. I need space before I can continue the conversation.
D. I feel both pulled toward contact and pushed away from it.
```

#### **5.3.14. Scenario-context balancing**

The bank must not test one construct only in easy situations and another only in difficult situations.

Each SRME dimension should appear across:

```text
conflict / repair
distance / delayed response
daily routine
fatigue / overload
planning / uncertainty
closeness / intimacy
novelty / transition
boundaries / autonomy
```

Each module should include low-stress, medium-stress, and high-stress scenarios.

Safety must not appear only in crisis scenarios.
Expansion must not appear only in fun scenarios.
Resource must not appear only in household chores.
Resonance must not appear only in deep emotional talks.

#### **5.3.15. Construct contamination rules**

Reject or revise an item if the target construct is contaminated.

Examples:

1. Safety contaminated with control:
   - Bad: “I need to know where my partner is at all times.”
   - Better: “I feel safer when we have clear expectations about when we will reconnect.”

2. Resource contaminated with obedience:
   - Bad: “My partner should follow the plan I made.”
   - Better: “I function better when responsibilities are clearly divided.”

3. Resonance contaminated with intelligence status:
   - Bad: “I need a partner who can keep up intellectually.”
   - Better: “Shared analysis and abstract conversation help me feel connected.”

4. Expansion contaminated with instability:
   - Bad: “I need constant change or I lose interest.”
   - Better: “Some novelty and exploration help the relationship feel alive to me.”

5. Avoidant regulation contaminated with sensory overload:
   - Bad: “I withdraw because I do not care.”
   - Better: “I need reduced input before I can respond clearly.”

#### **5.3.16. Forbidden wording**

Avoid these words in user-facing item text unless there is a documented reason:

```text
normal
healthy
mature
toxic
clingy
needy
cold
broken
unstable
high-maintenance
low-maintenance
real man
real woman
good partner
bad partner
too much
not enough
frigid
promiscuous
selfish
lazy
irrational
dramatic
```

Preferred wording:

```text
needs
prefers
tends to
is more likely to
under stress
in this situation
with enough recovery
with clear boundaries
with explicit agreement
with low pressure
```

#### **5.3.17. Review workflow**

Every item must pass this workflow before activation.

##### Stage 1 — Authoring review

The author checks:

```text
construct match
single primary construct
scenario clarity
option balance
scoring rationale
OCEAN relevance
bias checklist
```

Status after this stage:

```text
draft
```

##### Stage 2 — Internal methodology review

A second reviewer, or a separate review pass, checks:

```text
construct contamination
moral ranking
social desirability
neurodivergence fairness
sexuality / gender / culture bias
scoring consistency
```

Status after this stage:

```text
reviewed
```

##### Stage 3 — Cognitive review

Even if no large survey is planned, the item should be tested through cognitive review when possible.

Minimum lightweight version:

```text
1–3 people
ask what they think the question is asking
ask why they selected their option
ask whether any option felt judged, missing, or unclear
```

Recommended version:

```text
5–15 respondents
2–3 rounds
revise between rounds
```

Status after this stage:

```text
pretested
```

##### Stage 4 — Activation

An item can become active only if:

```text
status: pretested OR status: reviewed_with_no_pretest_available
bias flags: none critical
construct match: confirmed
scoring rationale: complete
```

Status:

```text
active
```

##### Stage 5 — Retirement or revision

An item must be revised or retired if:

```text
users repeatedly misunderstand it
one option is chosen for moral reasons rather than construct reasons
the item duplicates another item
the item creates strong discomfort unrelated to the construct
the item produces contradictions that are not theoretically meaningful
the construct definition changes
```

Status:

```text
retired
revised
deprecated
```

#### **5.3.18. Bank-level quality gates**

The active bank must pass these quality gates:

```text
all IDs unique
all vectors valid
all vector lengths correct
all response types valid
all item cards complete
no missing construct blueprint entries
no active item with critical bias flag
no module under target item count
no SRME vector below required signal count
no option-length imbalance above allowed threshold
no scenario-context overconcentration
no forbidden wording unless explicitly approved
all scoring values bounded within expected range
```

Recommended automated tests:

```text
test_unique_ids
test_schema_validity
test_vector_labels
test_vector_lengths
test_response_type_allowed
test_required_metadata
test_item_card_presence
test_forbidden_words
test_option_length_balance
test_srme_vector_balance
test_context_balance
test_no_active_critical_bias_flags
test_bank_fingerprint_changes_on_content_change
```

#### **5.3.19. Scoring and interpretation safeguards**

The system must separate:

```text
direct_score
ocean_adjusted_score
provision_score
confidence
explanation
```

The output must not hide uncertainty.

If confidence is low, the report should say that the signal is weak or mixed.

If direct score and OCEAN disagree, the report should show a contradiction note rather than forcing one result.

If need is high and partner provision is low, the report should describe the mismatch as a discussion topic, not as incompatibility proof.

If both partners have different needs, the report should check provision fit before calling it a problem.

Allowed output:

```text
This is a likely mismatch zone that needs explicit agreement.
```

Not allowed:

```text
This relationship will fail.
```

#### **5.3.20. Versioning rules**

Any active bank change must update versioning.

Patch version change:

```text
typo fix
clarity improvement without scoring change
metadata correction
```

Minor version change:

```text
new item
retired item
option wording change affecting interpretation
scenario-context rebalance
```

Major version change:

```text
construct definition change
vector meaning change
scoring rule change
response type change
OCEAN coefficient model change
compatibility formula change
```

Profiles from different major bank versions should not be compared without a migration or compatibility rule.

Each exported profile must include:

```yaml
bank_id:
bank_version:
bank_fingerprint:
scoring_model_version:
ocean_model_version:
created_at:
```

#### **5.3.21. Claim limits**

The bank may support:

```text
structured self-assessment
dyadic comparison
need-provision mapping
mismatch discussion
OCEAN-informed interpretation
confidence-labeled hypotheses
```

The bank must not claim:

```text
clinical validity
diagnosis
attachment diagnosis
sexual diagnosis
population percentile
objective compatibility percentage
relationship success prediction
universal ranking of partners
```

Recommended disclaimer:

```text
CRNAS results are structured hypotheses for self-reflection and partner discussion. They are not clinical diagnoses, population-normed scores, or predictions of relationship success. Scores should be interpreted within the current bank version and with attention to confidence labels.
```

## **6. Output Generation (The "User Manual")**

The final output is a structural directive, not a label.

**Output Object Structure:**

{
  "profile_summary": "High Resonance + High Expansion Profile",
  "drivers": {
    "primary": "Resonance (Intellectual)",
    "secondary": "Expansion (Novelty)"
  },
  "constraints": {
    "safety_mechanism": "Requires Logic-based Reassurance",
    "resource_dependency": "High (Executive Dysfunction detected)"
  },
  "erotic_key": "Sapiosexual / Context-Dependent",
  "shadow_warning": "Possible intellectualization pattern under emotional stress",
  "professional_profile": {
    "key": "INVESTIGATIVE / ARTISTIC / REALISTIC",
    "interaction_style": "Analysis over Emotion. Needs intellectual sparring.",
    "resource_warning": "High Career Centrality: Risk of domestic neglect."
  }
}

## **7. References and Methodological Sources**

The following sources define the methodological guardrails used by CRNAS. They do not certify CRNAS as a validated instrument; they guide development and documentation.

1. American Educational Research Association, American Psychological Association, and National Council on Measurement in Education. (2014). *Standards for Educational and Psychological Testing*. https://www.testingstandards.net/open-access-files.html
2. International Test Commission. *ITC Guidelines on Test Use*. https://www.intestcom.org/page/16
3. International Test Commission. *ITC Guidelines for Translating and Adapting Tests, Second Edition*. https://www.intestcom.org/page/16
4. International Test Commission. *ITC Guidelines on Computer-Based and Internet-Delivered Testing*. https://www.intestcom.org/page/16
5. International Test Commission. *ITC Guidelines on Quality Control in Scoring, Test Analysis and Reporting of Test Scores*. https://www.intestcom.org/page/16
6. COSMIN Initiative. *COSMIN taxonomy and methodology for measurement properties*. https://www.cosmin.nl/
7. Boateng, G. O., Neilands, T. B., Frongillo, E. A., Melgar-Quiñonez, H. R., & Young, S. L. (2018). *Best Practices for Developing and Validating Scales for Health, Social, and Behavioral Research*. Frontiers in Public Health, 6, 149. https://doi.org/10.3389/fpubh.2018.00149
8. International Personality Item Pool. *IPIP: A Scientific Collaboratory for the Development of Advanced Measures of Personality and Other Individual Differences*. https://ipip.ori.org/
9. Lawshe, C. H. (1975). *A quantitative approach to content validity*. Personnel Psychology, 28(4), 563–575.
10. Louviere, J. J., Flynn, T. N., & Marley, A. A. J. (2015). *Best-Worst Scaling: Theory, Methods and Applications*. Cambridge University Press.
11. DeVellis, R. F., & Thorpe, C. T. (2021). *Scale Development: Theory and Applications* (5th ed.). SAGE.

