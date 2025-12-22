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

**Purpose:** Acts as a coefficient modifier for all other modules. It represents the user's "operating system."

**Variables:**

* O_score (Float 0.0-1.0): **Openness**. Correlates with Intellectual Resonance and Novelty needs.
* C_score (Float 0.0-1.0): **Conscientiousness**. Inverse correlation with external Resource/Scaffolding needs.
* E_score (Float 0.0-1.0): **Extraversion**. Correlates with Social Expansion needs.
* A_score (Float 0.0-1.0): **Agreeableness**. Correlates with Emotional Resonance needs.
* N_score (Float 0.0-1.0): **Neuroticism**. Strong correlation with Safety needs.
* Neurotype_Flags (Bitmask/Set):
  * ADHD_Trait: Modifies Novelty decay rate (boredom) and Executive Function needs.
  * ASD_Trait: Modifies Sensory Safety needs and Communication directness.

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