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

### **4.1. The Correction Algorithm (Normalization)**

User self-reporting is often inaccurate. We use the PsychometricsComponent to adjust the raw_score of needs.

**Pseudocode Logic:**

def calculate_safety_weight(raw_safety, big_five):
    # Neuroticism is the primary driver for Safety needs.
    # If N is high, Safety is critical regardless of what the user says.
    n_weight = 0.7
    base_safety = raw_safety * (1.0 - n_weight)
    implicit_safety = big_five.N_score * n_weight
      
    final_safety = base_safety + implicit_safety
    return clamp(final_safety, 0.0, 1.0)

def calculate_resource_weight(raw_resource, big_five, neurotype):
    # Low Conscientiousness or ADHD increases need for external scaffolding (Resource).
    dysfunction_penalty = (1.0 - big_five.C_score)
      
    if "ADHD" in neurotype:
        dysfunction_penalty += 0.2
          
    final_resource = max(raw_resource, dysfunction_penalty)
    return final_resource

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

**Critical Mismatch Flags (Instant Fail Conditions):**

1. **The Anxious-Avoidant Trap:**
   * UserA.Shadow.Attachment == Anxious AND UserB.Shadow.Attachment == Avoidant.
   * *Result:* Severe Penalty.
2. **The Expansion-Safety Conflict:**
   * UserA.Needs.Expansion > 0.8 AND UserB.Psychometrics.Openness < 0.3.
   * *Result:* UserA will bore UserB, UserB will constrain UserA.
3. **The RIASEC Friction (Cognitive Dissonance):**
   * UserA.Professional == Artistic (Chaos/Emotion) AND UserB.Professional == Conventional (Order/Data).
   * *Result:* High friction in household management and communication styles.

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

## **6. Output Generation (The "User Manual")**

The final output is a structural directive, not a label.

**Output Object Structure:**

{
  "profile_summary": "High-Maintenance Cognitive Explorer",
  "drivers": {
    "primary": "Resonance (Intellectual)",
    "secondary": "Expansion (Novelty)"
  },
  "constraints": {
    "safety_mechanism": "Requires Logic-based Reassurance",
    "resource_dependency": "High (Executive Dysfunction detected)"
  },
  "erotic_key": "Sapiosexual / Context-Dependent",
  "shadow_warning": "Tendency to Intellectualize emotions (Avoidant-Dismissive)",
  "professional_profile": {
    "key": "INVESTIGATIVE / ARTISTIC / REALISTIC",
    "interaction_style": "Analysis over Emotion. Needs intellectual sparring.",
    "resource_warning": "High Career Centrality: Risk of domestic neglect."
  }
}