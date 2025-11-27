# **Technical Specification: Comprehensive Relationship Needs Analysis System (CRNAS)**

## **1\. Abstract**

This document outlines the algorithmic architecture for a scientifically grounded relationship needs assessment tool. Unlike traditional "Love Language" models, CRNAS utilizes a multi-layered approach, integrating the **Big Five (OCEAN)** psychometric model, **Self-Determination Theory (SDT)**, **Attachment Theory**, and the **Dual Control Model of Sexual Response**.

The system is designed using a **Composition over Inheritance** principle. It treats a user profile not as a monolithic entity, but as a composition of independent, interacting modules (Components).

## **2\. Core Methodology & Architecture**

The system operates on three distinct processing layers:

1. **The Substrate Layer (Hardware):** Biological and stable psychological traits (Big Five, Neurotype).  
2. **The Needs Layer (Interface):** The S.R.M.E. model (Safety, Resource, Resonance, Expansion).  
3. **The Context Layer (Implementation):** Specific interests, values, and defense mechanisms.

### **2.1. Compositional Structure (Data Entities)**

The UserProfile entity is composed of the following modules:

* PsychometricsComponent (The "Hardware")  
* RelationalNeedsComponent (The S.R.M.E. Engine)  
* ErosComponent (Sexual Temperament)  
* ShadowComponent (Conflict & Attachment)  
* ContextComponent (Interests & Values)

## **3\. Module Specifications & Variables**

### **3.1. Module A: PsychometricsComponent (The Hardware)**

**Purpose:** Acts as a coefficient modifier for all other modules. It represents the user's "operating system."

**Variables:**

* O\_score (Float 0.0-1.0): **Openness**. Correlates with Intellectual Resonance and Novelty needs.  
* C\_score (Float 0.0-1.0): **Conscientiousness**. Inverse correlation with external Resource/Scaffolding needs.  
* E\_score (Float 0.0-1.0): **Extraversion**. Correlates with Social Expansion needs.  
* A\_score (Float 0.0-1.0): **Agreeableness**. Correlates with Emotional Resonance needs.  
* N\_score (Float 0.0-1.0): **Neuroticism**. Strong correlation with Safety needs.  
* Neurotype\_Flags (Bitmask/Set):  
  * ADHD\_Trait: Modifies Novelty decay rate (boredom) and Executive Function needs.  
  * ASD\_Trait: Modifies Sensory Safety needs and Communication directness.

### **3.2. Module B: RelationalNeedsComponent (The S.R.M.E. Model)**

**Purpose:** Defines the core interaction style the user requires.

**Dimensions:**

1. **Safety (S):** Need for regulation, predictability, and anxiety reduction.  
2. **Resource (R):** Need for instrumental support, acts of service, and logistical scaffolding.  
3. **Resonance (M):** Need for shared meaning, cognitive or emotional synchronization.  
4. **Expansion (E):** Need for novelty, autonomy, and personal growth facilitation.

**Variables per Dimension:**

* raw\_score (Float): Self-reported importance.  
* calculated\_weight (Float): The final importance score after Big Five adjustment.  
* preferred\_channel (Enum): The mode of delivery (e.g., *Verbal, Physical, Action-based*).

### **3.3. Module C: ErosComponent (Sexual Profile)**

**Methodology:** Based on the Dual Control Model (Nagoski).

**Variables:**

* accelerator\_sensitivity (Float): Ease of arousal.  
* brake\_sensitivity (Float): Susceptibility to inhibition (stress, environment).  
* context\_dependency (Enum): *High* (needs specific conditions) vs *Low* (spontaneous).  
* erotic\_language (List\<Tags\>): Specific pathways to arousal (e.g., *Sapiosexual, Kinky, Sensory, Devotional*).

### **3.4. Module D: ShadowComponent (Defense & Trauma)**

**Methodology:** Attachment Theory & Gottman Conflict Styles.

**Variables:**

* attachment\_style (Enum): *Secure, Anxious, Avoidant, Disorganized*.  
* conflict\_response (Enum): *Fight (Attack), Flight (Withdraw), Freeze (Shut down), Fawn (Appease)*.  
* regulation\_method (Enum): *Co-regulation* (needs partner) vs *Auto-regulation* (needs solitude).

## **4\. Algorithmic Logic**

### **4.1. The Correction Algorithm (Normalization)**

User self-reporting is often inaccurate. We use the PsychometricsComponent to adjust the raw\_score of needs.

**Pseudocode Logic:**

def calculate\_safety\_weight(raw\_safety, big\_five):  
    \# Neuroticism is the primary driver for Safety needs.  
    \# If N is high, Safety is critical regardless of what the user says.  
    n\_weight \= 0.7  
    base\_safety \= raw\_safety \* (1.0 \- n\_weight)  
    implicit\_safety \= big\_five.N\_score \* n\_weight  
      
    final\_safety \= base\_safety \+ implicit\_safety  
    return clamp(final\_safety, 0.0, 1.0)

def calculate\_resource\_weight(raw\_resource, big\_five, neurotype):  
    \# Low Conscientiousness or ADHD increases need for external scaffolding (Resource).  
    dysfunction\_penalty \= (1.0 \- big\_five.C\_score)  
      
    if "ADHD" in neurotype:  
        dysfunction\_penalty \+= 0.2  
          
    final\_resource \= max(raw\_resource, dysfunction\_penalty)  
    return final\_resource

### **4.2. The Context Interpretation Algorithm**

This algorithm maps Interests to Resonance Types based on Openness.

**Logic:**

* **Input:** User Interest (e.g., "Programming") \+ Psychometrics.  
* **Process:**  
  * IF Openness \> 0.7 (High):  
    * Map "Programming" to **Cognitive Resonance** (Deep discussion, architecture analysis).  
  * IF Agreeableness \> 0.7 AND Openness \< 0.5:  
    * Map "Programming" to **Emotional/Support Resonance** (Empathizing with coding burnout, celebrating success).  
  * IF Conscientiousness \> 0.7:  
    * Map "Programming" to **Functional Resonance** (Code reviews, productivity optimization).

### **4.3. The Compatibility Heuristic (Scoring)**

Compatibility is not about identical scores, but about **Need-Provision Fit**.

Formula:  
$$ Compatibility \= \\sum (UserA.Needs\_i \\times UserB.Capacity\_i) \\times Penalty(ShadowMismatch) $$  
**Critical Mismatch Flags (Instant Fail Conditions):**

1. **The Anxious-Avoidant Trap:**  
   * UserA.Shadow.Attachment \== Anxious AND UserB.Shadow.Attachment \== Avoidant.  
   * *Result:* Severe Penalty.  
2. **The Expansion-Safety Conflict:**  
   * UserA.Needs.Expansion \> 0.8 AND UserB.Psychometrics.Openness \< 0.3.  
   * *Result:* UserA will bore UserB, UserB will constrain UserA.

## **5\. Survey Methodology (Input Strategy)**

To populate these components, the survey must use **Scenario-Based Inquiries** rather than declarative statements.

**Example Data Collection Pattern:**

* *Do not ask:* "Do you like intellectual conversations?"  
* *Ask:* "You and your partner disagree on a complex topic. What is your ideal outcome?"  
  * A) We drop it to keep the peace. (Maps to: *Safety \> Resonance*)  
  * B) We debate until we find the logical truth, even if it gets heated. (Maps to: *Resonance (Cognitive) \> Safety*)  
  * C) My partner listens to my feelings about the topic. (Maps to: *Resonance (Emotional)*)

## **6\. Output Generation (The "User Manual")**

The final output is a structural directive, not a label.

**Output Object Structure:**

{  
  "profile\_summary": "High-Maintenance Cognitive Explorer",  
  "drivers": {  
    "primary": "Resonance (Intellectual)",  
    "secondary": "Expansion (Novelty)"  
  },  
  "constraints": {  
    "safety\_mechanism": "Requires Logic-based Reassurance",  
    "resource\_dependency": "High (Executive Dysfunction detected)"  
  },  
  "erotic\_key": "Sapiosexual / Context-Dependent",  
  "shadow\_warning": "Tendency to Intellectualize emotions (Avoidant-Dismissive)"  
}  
