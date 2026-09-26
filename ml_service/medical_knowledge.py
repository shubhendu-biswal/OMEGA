"""OMEGA Medical Science Knowledge Base - Comprehensive medical data for query routing."""

DISEASES = {
    "diabetes": {"name": "Diabetes Mellitus", "type": "Metabolic", "symptoms": "excessive thirst, frequent urination, fatigue, blurred vision, slow wound healing", "treatment": "insulin therapy, metformin, lifestyle changes, blood sugar monitoring", "specialist": "Endocrinologist", "prevalence": "537 million adults worldwide (2021)"},
    "hypertension": {"name": "Hypertension (High Blood Pressure)", "type": "Cardiovascular", "symptoms": "headaches, shortness of breath, nosebleeds, dizziness (often asymptomatic)", "treatment": "ACE inhibitors, ARBs, calcium channel blockers, diuretics, lifestyle changes", "specialist": "Cardiologist", "prevalence": "1.28 billion adults worldwide"},
    "asthma": {"name": "Asthma", "type": "Respiratory", "symptoms": "wheezing, shortness of breath, chest tightness, coughing (especially at night)", "treatment": "inhaled corticosteroids, bronchodilators, leukotriene modifiers", "specialist": "Pulmonologist", "prevalence": "262 million people worldwide"},
    "cancer": {"name": "Cancer", "type": "Oncological", "symptoms": "unexplained weight loss, fatigue, persistent pain, skin changes, unusual bleeding", "treatment": "surgery, chemotherapy, radiation therapy, immunotherapy, targeted therapy", "specialist": "Oncologist", "prevalence": "19.3 million new cases annually"},
    "heart disease": {"name": "Coronary Heart Disease", "type": "Cardiovascular", "symptoms": "chest pain (angina), shortness of breath, heart palpitations, fatigue", "treatment": "statins, beta-blockers, ACE inhibitors, angioplasty, bypass surgery", "specialist": "Cardiologist", "prevalence": "Leading cause of death globally, 17.9 million deaths/year"},
    "alzheimer": {"name": "Alzheimer's Disease", "type": "Neurological", "symptoms": "memory loss, confusion, difficulty with language, mood changes, disorientation", "treatment": "cholinesterase inhibitors (donepezil), memantine, supportive care", "specialist": "Neurologist", "prevalence": "55 million people worldwide"},
    "parkinson": {"name": "Parkinson's Disease", "type": "Neurological", "symptoms": "tremors, rigidity, slow movement (bradykinesia), balance problems", "treatment": "levodopa/carbidopa, dopamine agonists, deep brain stimulation (DBS)", "specialist": "Neurologist", "prevalence": "8.5 million people worldwide"},
    "tuberculosis": {"name": "Tuberculosis (TB)", "type": "Infectious", "symptoms": "persistent cough (3+ weeks), blood in sputum, night sweats, weight loss, fever", "treatment": "RIPE regimen: Rifampicin, Isoniazid, Pyrazinamide, Ethambutol (6-9 months)", "specialist": "Pulmonologist / Infectious Disease Specialist", "prevalence": "10.6 million new cases annually"},
    "malaria": {"name": "Malaria", "type": "Infectious (Parasitic)", "symptoms": "high fever, chills, headache, nausea, muscle pain, sweating", "treatment": "artemisinin-based combination therapy (ACT), chloroquine, primaquine", "specialist": "Infectious Disease Specialist", "prevalence": "247 million cases annually, 619,000 deaths"},
    "hiv": {"name": "HIV/AIDS", "type": "Infectious (Viral)", "symptoms": "flu-like symptoms initially, then weight loss, recurring infections, chronic diarrhea", "treatment": "antiretroviral therapy (ART) - combination of NRTIs, NNRTIs, protease inhibitors", "specialist": "Infectious Disease Specialist", "prevalence": "39 million people living with HIV globally"},
    "stroke": {"name": "Stroke (Cerebrovascular Accident)", "type": "Neurological/Cardiovascular", "symptoms": "sudden numbness (face/arm/leg), confusion, trouble speaking, severe headache, vision problems (FAST: Face drooping, Arm weakness, Speech difficulty, Time to call emergency)", "treatment": "tPA (tissue plasminogen activator) for ischemic stroke, surgery for hemorrhagic stroke, rehabilitation", "specialist": "Neurologist", "prevalence": "12.2 million new strokes annually"},
    "pneumonia": {"name": "Pneumonia", "type": "Respiratory/Infectious", "symptoms": "cough with phlegm, fever, chills, difficulty breathing, chest pain", "treatment": "antibiotics (bacterial), antivirals (viral), rest, fluids, oxygen therapy", "specialist": "Pulmonologist", "prevalence": "2.5 million deaths annually worldwide"},
    "arthritis": {"name": "Arthritis", "type": "Musculoskeletal", "symptoms": "joint pain, stiffness, swelling, reduced range of motion, redness", "treatment": "NSAIDs, DMARDs, corticosteroids, physical therapy, joint replacement surgery", "specialist": "Rheumatologist", "prevalence": "350 million people worldwide"},
    "depression": {"name": "Major Depressive Disorder", "type": "Mental Health", "symptoms": "persistent sadness, loss of interest, fatigue, sleep changes, appetite changes, difficulty concentrating, thoughts of self-harm", "treatment": "SSRIs (fluoxetine, sertraline), SNRIs, cognitive behavioral therapy (CBT), psychotherapy", "specialist": "Psychiatrist", "prevalence": "280 million people worldwide"},
    "epilepsy": {"name": "Epilepsy", "type": "Neurological", "symptoms": "recurrent seizures, temporary confusion, staring spells, uncontrollable jerking movements", "treatment": "anti-epileptic drugs (valproate, carbamazepine, levetiracetam), surgery, vagus nerve stimulation", "specialist": "Neurologist", "prevalence": "50 million people worldwide"},
    "kidney disease": {"name": "Chronic Kidney Disease (CKD)", "type": "Renal", "symptoms": "fatigue, swelling (edema), decreased urine output, nausea, shortness of breath", "treatment": "ACE inhibitors, dialysis, kidney transplant, dietary modifications", "specialist": "Nephrologist", "prevalence": "850 million people worldwide"},
    "liver disease": {"name": "Liver Disease (Hepatitis/Cirrhosis)", "type": "Hepatic", "symptoms": "jaundice, abdominal pain, swelling, dark urine, fatigue, nausea", "treatment": "antivirals (for hepatitis), liver transplant, lifestyle changes, lactulose", "specialist": "Hepatologist/Gastroenterologist", "prevalence": "1.5 billion people with chronic liver disease"},
    "thyroid": {"name": "Thyroid Disorders", "type": "Endocrine", "symptoms": "weight changes, fatigue, hair loss, temperature sensitivity, mood changes", "treatment": "levothyroxine (hypothyroidism), methimazole/radioactive iodine (hyperthyroidism)", "specialist": "Endocrinologist", "prevalence": "200 million people worldwide"},
    "covid": {"name": "COVID-19 (SARS-CoV-2)", "type": "Infectious (Viral)", "symptoms": "fever, cough, fatigue, loss of taste/smell, difficulty breathing, body aches", "treatment": "Paxlovid (nirmatrelvir/ritonavir), remdesivir, dexamethasone, supportive care, vaccination", "specialist": "Infectious Disease Specialist / Pulmonologist", "prevalence": "770+ million confirmed cases globally (cumulative)"},
    "dengue": {"name": "Dengue Fever", "type": "Infectious (Viral)", "symptoms": "high fever, severe headache, pain behind eyes, joint/muscle pain, skin rash, bleeding", "treatment": "supportive care, fluids, pain relievers (avoid aspirin), platelet monitoring", "specialist": "Infectious Disease Specialist", "prevalence": "100-400 million infections annually"},
}

BODY_SYSTEMS = {
    "circulatory": {"name": "Circulatory System", "organs": "Heart, Blood vessels (arteries, veins, capillaries), Blood", "function": "Transports oxygen, nutrients, hormones, and waste products throughout the body. The heart pumps approximately 5 liters of blood per minute.", "diseases": "Heart disease, Hypertension, Atherosclerosis, Aneurysm, Deep vein thrombosis"},
    "respiratory": {"name": "Respiratory System", "organs": "Lungs, Trachea, Bronchi, Diaphragm, Alveoli", "function": "Facilitates gas exchange - oxygen intake and carbon dioxide removal. Adults breathe approximately 12-20 times per minute at rest.", "diseases": "Asthma, COPD, Pneumonia, Lung cancer, Tuberculosis, Pulmonary fibrosis"},
    "nervous": {"name": "Nervous System", "organs": "Brain, Spinal cord, Peripheral nerves, Sensory organs", "function": "Controls and coordinates body activities by transmitting electrical signals. The brain contains approximately 86 billion neurons.", "diseases": "Alzheimer's, Parkinson's, Epilepsy, Multiple sclerosis, Stroke, Meningitis"},
    "digestive": {"name": "Digestive System", "organs": "Mouth, Esophagus, Stomach, Small intestine, Large intestine, Liver, Pancreas, Gallbladder", "function": "Breaks down food into nutrients for absorption and eliminates waste. Complete digestion takes 24-72 hours.", "diseases": "GERD, Crohn's disease, Ulcerative colitis, Celiac disease, Liver cirrhosis"},
    "skeletal": {"name": "Skeletal System", "organs": "Bones (206 in adults), Cartilage, Ligaments, Joints", "function": "Provides structural support, protects internal organs, enables movement, produces blood cells in bone marrow, and stores minerals.", "diseases": "Osteoporosis, Osteoarthritis, Fractures, Scoliosis, Rickets"},
    "muscular": {"name": "Muscular System", "organs": "Skeletal muscles (600+), Smooth muscles, Cardiac muscle", "function": "Enables body movement, maintains posture, generates heat, and facilitates blood circulation.", "diseases": "Muscular dystrophy, Myasthenia gravis, Fibromyalgia, Rhabdomyolysis"},
    "endocrine": {"name": "Endocrine System", "organs": "Pituitary gland, Thyroid, Adrenal glands, Pancreas, Ovaries/Testes, Hypothalamus", "function": "Produces hormones that regulate metabolism, growth, reproduction, sleep, and mood.", "diseases": "Diabetes, Thyroid disorders, Cushing's syndrome, Addison's disease, PCOS"},
    "immune": {"name": "Immune System", "organs": "Lymph nodes, Spleen, Thymus, Bone marrow, White blood cells, Antibodies", "function": "Defends against pathogens (bacteria, viruses, parasites), removes damaged cells, and provides immunological memory.", "diseases": "HIV/AIDS, Autoimmune diseases (Lupus, Rheumatoid arthritis), Allergies, Immunodeficiency"},
    "urinary": {"name": "Urinary/Renal System", "organs": "Kidneys, Ureters, Bladder, Urethra", "function": "Filters blood, removes waste as urine, regulates fluid balance, blood pressure, and electrolyte levels. Kidneys filter ~180 liters of blood daily.", "diseases": "Chronic kidney disease, Kidney stones, Urinary tract infections, Glomerulonephritis"},
    "reproductive": {"name": "Reproductive System", "organs": "Male: Testes, Prostate, Seminal vesicles. Female: Ovaries, Uterus, Fallopian tubes", "function": "Produces gametes (sperm/eggs), facilitates fertilization, supports fetal development, and produces sex hormones.", "diseases": "Infertility, PCOS, Endometriosis, Prostate cancer, Cervical cancer"},
}

MEDICAL_SPECIALTIES = {
    "cardiology": ("Cardiology", "Diagnosis and treatment of heart and cardiovascular diseases", "ECG, Echocardiography, Angiography, Cardiac catheterization"),
    "neurology": ("Neurology", "Diagnosis and treatment of nervous system disorders", "EEG, MRI, CT scan, Lumbar puncture, Nerve conduction studies"),
    "oncology": ("Oncology", "Diagnosis and treatment of cancer", "Biopsy, PET scan, Chemotherapy, Radiation therapy, Immunotherapy"),
    "orthopedics": ("Orthopedics", "Treatment of musculoskeletal system disorders", "X-ray, MRI, Joint replacement, Arthroscopy, Fracture fixation"),
    "dermatology": ("Dermatology", "Treatment of skin, hair, and nail conditions", "Skin biopsy, Dermoscopy, Patch testing, Phototherapy"),
    "pediatrics": ("Pediatrics", "Medical care of infants, children, and adolescents", "Growth monitoring, Vaccination, Developmental screening"),
    "psychiatry": ("Psychiatry", "Diagnosis and treatment of mental health disorders", "Psychotherapy, CBT, Medication management, Electroconvulsive therapy"),
    "ophthalmology": ("Ophthalmology", "Diagnosis and treatment of eye disorders", "Slit-lamp exam, Tonometry, LASIK, Cataract surgery"),
    "gastroenterology": ("Gastroenterology", "Treatment of digestive system disorders", "Endoscopy, Colonoscopy, ERCP, Liver biopsy"),
    "pulmonology": ("Pulmonology", "Treatment of respiratory/lung disorders", "Spirometry, Bronchoscopy, Chest X-ray, Pulmonary function tests"),
    "nephrology": ("Nephrology", "Treatment of kidney diseases", "Kidney biopsy, Dialysis, GFR testing, Urinalysis"),
    "endocrinology": ("Endocrinology", "Treatment of hormone-related disorders", "Thyroid function tests, HbA1c, Hormone panels, Glucose tolerance test"),
}

VITAMINS_NUTRIENTS = {
    "vitamin a": ("Vitamin A (Retinol)", "Vision, immune function, skin health, cell growth", "Carrots, sweet potatoes, spinach, liver, eggs", "900 mcg (men), 700 mcg (women)", "Night blindness, dry skin, immune weakness"),
    "vitamin b12": ("Vitamin B12 (Cobalamin)", "Red blood cell formation, nerve function, DNA synthesis", "Meat, fish, dairy, eggs, fortified cereals", "2.4 mcg", "Anemia, nerve damage, fatigue, memory problems"),
    "vitamin c": ("Vitamin C (Ascorbic Acid)", "Immune support, collagen synthesis, antioxidant, wound healing", "Citrus fruits, strawberries, bell peppers, broccoli", "90 mg (men), 75 mg (women)", "Scurvy, poor wound healing, weakened immunity"),
    "vitamin d": ("Vitamin D (Cholecalciferol)", "Calcium absorption, bone health, immune function, mood regulation", "Sunlight, fatty fish, fortified milk, egg yolks", "600-800 IU", "Rickets, osteomalacia, bone weakness, depression"),
    "iron": ("Iron", "Oxygen transport in blood (hemoglobin), energy production", "Red meat, spinach, lentils, fortified cereals, beans", "8 mg (men), 18 mg (women)", "Iron-deficiency anemia, fatigue, weakness, pale skin"),
    "calcium": ("Calcium", "Bone and teeth health, muscle contraction, nerve signaling", "Dairy, leafy greens, almonds, fortified foods", "1000-1200 mg", "Osteoporosis, muscle cramps, numbness"),
    "zinc": ("Zinc", "Immune function, wound healing, DNA synthesis, taste/smell", "Oysters, beef, pumpkin seeds, lentils, chickpeas", "11 mg (men), 8 mg (women)", "Impaired immunity, hair loss, delayed wound healing"),
    "omega 3": ("Omega-3 Fatty Acids", "Heart health, brain function, anti-inflammatory", "Salmon, mackerel, walnuts, flaxseeds, chia seeds", "250-500 mg EPA+DHA", "Inflammation, cognitive decline, dry eyes"),
}

COMMON_DRUGS = {
    "paracetamol": ("Paracetamol (Acetaminophen)", "Analgesic/Antipyretic", "Pain relief, fever reduction", "500-1000 mg every 4-6 hours, max 4g/day", "Liver damage in overdose, rare allergic reactions"),
    "ibuprofen": ("Ibuprofen", "NSAID (Non-Steroidal Anti-Inflammatory Drug)", "Pain, inflammation, fever", "200-400 mg every 4-6 hours", "Stomach ulcers, kidney problems, increased bleeding risk"),
    "amoxicillin": ("Amoxicillin", "Antibiotic (Penicillin-type)", "Bacterial infections (ear, throat, urinary, skin)", "250-500 mg every 8 hours", "Allergic reactions, diarrhea, rash"),
    "metformin": ("Metformin", "Antidiabetic (Biguanide)", "Type 2 diabetes - lowers blood sugar", "500-2000 mg daily", "GI upset, lactic acidosis (rare), vitamin B12 deficiency"),
    "omeprazole": ("Omeprazole", "Proton Pump Inhibitor (PPI)", "Acid reflux, GERD, stomach ulcers", "20-40 mg once daily", "Headache, vitamin B12/magnesium deficiency with long-term use"),
    "aspirin": ("Aspirin (Acetylsalicylic Acid)", "NSAID/Antiplatelet", "Pain, fever, heart attack/stroke prevention", "75-325 mg daily (cardiac), 300-600 mg (pain)", "Stomach bleeding, Reye's syndrome in children"),
    "atorvastatin": ("Atorvastatin (Lipitor)", "Statin", "High cholesterol, cardiovascular risk reduction", "10-80 mg once daily", "Muscle pain, liver enzyme elevation, rare rhabdomyolysis"),
    "amlodipine": ("Amlodipine", "Calcium Channel Blocker", "Hypertension, angina", "2.5-10 mg once daily", "Ankle swelling, dizziness, flushing"),
    "cetirizine": ("Cetirizine (Zyrtec)", "Antihistamine", "Allergies, hay fever, hives", "10 mg once daily", "Drowsiness, dry mouth, headache"),
    "insulin": ("Insulin", "Hormone/Antidiabetic", "Type 1 diabetes, advanced Type 2 diabetes", "Individualized dosing based on blood sugar", "Hypoglycemia, weight gain, injection site reactions"),
}

FIRST_AID = {
    "burns": "For burns: 1) Cool the burn under cool running water for at least 20 minutes. 2) Remove jewelry/clothing near the burn. 3) Cover with a sterile non-stick bandage. 4) Take pain relievers if needed. 5) Do NOT apply ice, butter, or toothpaste. Seek medical help for severe/large burns.",
    "choking": "For choking (Heimlich Maneuver): 1) Stand behind the person. 2) Place fist just above the navel. 3) Grasp fist with other hand. 4) Perform quick upward thrusts. 5) Repeat until object is dislodged. For infants: 5 back blows + 5 chest thrusts. Call emergency services if unsuccessful.",
    "cpr": "CPR (Cardiopulmonary Resuscitation): 1) Check responsiveness. 2) Call emergency services. 3) Place heel of hand on center of chest. 4) Push hard and fast (100-120 compressions/min, 2 inches deep). 5) Give 2 rescue breaths after every 30 compressions. Continue until help arrives.",
    "bleeding": "For severe bleeding: 1) Apply firm direct pressure with a clean cloth. 2) Keep the injured area elevated above the heart. 3) Apply a pressure bandage. 4) Do NOT remove blood-soaked dressings, add more on top. 5) Apply tourniquet only as last resort for life-threatening limb bleeding. Call emergency services.",
    "fracture": "For suspected fractures: 1) Immobilize the injured area - do NOT try to realign. 2) Apply ice wrapped in cloth to reduce swelling. 3) Splint the area if trained. 4) Elevate the limb if possible. 5) Seek immediate medical attention. Do NOT move if spinal injury suspected.",
    "heart attack": "Heart attack signs: Chest pain/pressure, arm/jaw pain, shortness of breath, cold sweat. Action: 1) Call emergency (112/911). 2) Chew aspirin (300mg) if not allergic. 3) Rest in comfortable position. 4) Loosen tight clothing. 5) Be ready to perform CPR if person becomes unresponsive.",
    "snake bite": "For snake bites: 1) Move away from the snake. 2) Keep the bitten limb still and below heart level. 3) Remove jewelry/watches. 4) Do NOT cut, suck, or apply tourniquet. 5) Clean wound gently. 6) Rush to hospital for antivenom. Try to remember snake appearance.",
    "drowning": "For drowning: 1) Call emergency services. 2) If safe, pull person from water. 3) Check breathing. 4) If not breathing, begin CPR immediately (start with 5 rescue breaths). 5) Continue CPR until help arrives. 6) Place in recovery position if breathing resumes.",
}


def lookup_medical(prompt_lower):
    """Route medical queries to appropriate answers. Returns answer string or None."""
    
    # Disease lookups
    for key, info in DISEASES.items():
        if key in prompt_lower:
            if "symptom" in prompt_lower or "sign" in prompt_lower:
                return f"Symptoms of {info['name']}: {info['symptoms']}. Specialist: {info['specialist']}. If you experience these symptoms, consult a doctor immediately."
            elif "treatment" in prompt_lower or "cure" in prompt_lower or "medicine" in prompt_lower or "drug" in prompt_lower:
                return f"Treatment for {info['name']}: {info['treatment']}. Specialist: {info['specialist']}. Always consult a qualified medical professional before starting any treatment."
            elif "cause" in prompt_lower or "why" in prompt_lower or "reason" in prompt_lower:
                return f"{info['name']} is a {info['type']} condition. Symptoms include: {info['symptoms']}. Treatment: {info['treatment']}. Global prevalence: {info['prevalence']}."
            else:
                return f"{info['name']} ({info['type']})\n\nSymptoms: {info['symptoms']}\n\nTreatment: {info['treatment']}\n\nSpecialist: {info['specialist']}\n\nGlobal Prevalence: {info['prevalence']}"

    # Body system lookups
    for key, info in BODY_SYSTEMS.items():
        if key in prompt_lower and ("system" in prompt_lower or "body" in prompt_lower or "organ" in prompt_lower or "function" in prompt_lower):
            return f"{info['name']}\n\nKey Organs: {info['organs']}\n\nFunction: {info['function']}\n\nCommon Diseases: {info['diseases']}"

    # Specialty lookups
    specialist_map = {
        "neurologist": "neurology", "neurology": "neurology",
        "cardiologist": "cardiology", "cardiology": "cardiology",
        "oncologist": "oncology", "oncology": "oncology",
        "orthopedist": "orthopedics", "orthopedic": "orthopedics", "orthopedics": "orthopedics",
        "dermatologist": "dermatology", "dermatology": "dermatology",
        "pediatrician": "pediatrics", "pediatric": "pediatrics", "pediatrics": "pediatrics",
        "psychiatrist": "psychiatry", "psychiatry": "psychiatry",
        "ophthalmologist": "ophthalmology", "ophthalmology": "ophthalmology",
        "gastroenterologist": "gastroenterology", "gastroenterology": "gastroenterology",
        "pulmonologist": "pulmonology", "pulmonology": "pulmonology",
        "nephrologist": "nephrology", "nephrology": "nephrology",
        "endocrinologist": "endocrinology", "endocrinology": "endocrinology"
    }
    for spec_word, key in specialist_map.items():
        if spec_word in prompt_lower:
            name, desc, procedures = MEDICAL_SPECIALTIES[key]
            return f"{name}: {desc}.\n\nCommon Procedures: {procedures}."

    # Vitamin/nutrient lookups
    for key, (name, function, sources, rda, deficiency) in VITAMINS_NUTRIENTS.items():
        if key in prompt_lower:
            return f"{name}\n\nFunction: {function}\n\nBest Sources: {sources}\n\nRecommended Daily Intake: {rda}\n\nDeficiency Symptoms: {deficiency}"

    # Drug lookups
    for key, (name, drug_class, uses, dosage, side_effects) in COMMON_DRUGS.items():
        if key in prompt_lower:
            return f"{name} ({drug_class})\n\nUses: {uses}\n\nTypical Dosage: {dosage}\n\nSide Effects: {side_effects}\n\nAlways consult a doctor before taking any medication."

    # First aid lookups
    for key, answer in FIRST_AID.items():
        if key in prompt_lower and ("first aid" in prompt_lower or "emergency" in prompt_lower or "how to" in prompt_lower or "what to do" in prompt_lower or "help" in prompt_lower):
            return answer

    # General medical topic detection
    if "blood pressure" in prompt_lower:
        return "Normal blood pressure is below 120/80 mmHg.\n- Elevated: 120-129/<80\n- Stage 1 Hypertension: 130-139/80-89\n- Stage 2 Hypertension: 140+/90+\n- Crisis: 180+/120+ (seek emergency care)\n\nManagement: Low-sodium diet, regular exercise, stress management, medication if prescribed."
    
    if "blood group" in prompt_lower or "blood type" in prompt_lower:
        return "Human Blood Groups (ABO System):\n- Type A: Has A antigens, can receive A and O\n- Type B: Has B antigens, can receive B and O\n- Type C: Has both A and B antigens (Universal Recipient: AB+)\n- Type O: Has no antigens (Universal Donor: O-)\n\nRh Factor: Positive (+) or Negative (-). Blood typing is critical for transfusions and pregnancy."

    if "bmi" in prompt_lower or "body mass index" in prompt_lower:
        return "Body Mass Index (BMI) = Weight(kg) / Height(m)²\n\nCategories:\n- Underweight: <18.5\n- Normal: 18.5-24.9\n- Overweight: 25-29.9\n- Obese Class I: 30-34.9\n- Obese Class II: 35-39.9\n- Obese Class III: 40+\n\nBMI is a screening tool; consult a doctor for full health assessment."

    if "vaccine" in prompt_lower or "vaccination" in prompt_lower or "immunization" in prompt_lower:
        return "Essential Vaccines:\n- BCG (Tuberculosis) - at birth\n- Hepatitis B - at birth, 6 weeks, 6 months\n- DPT (Diphtheria, Pertussis, Tetanus) - 6, 10, 14 weeks\n- Polio (OPV/IPV) - at birth, 6, 10, 14 weeks\n- MMR (Measles, Mumps, Rubella) - 9-12 months\n- HPV - 9-14 years\n- COVID-19 - as recommended\n- Influenza - annually\n\nVaccines work by training the immune system to recognize and fight specific pathogens."

    return None

def predict_disease_and_medicine(symptom_query):
    if not symptom_query:
        return None
    query_lower = symptom_query.lower()

    scored_diseases = []
    for key, data in DISEASES.items():
        symptoms = [s.strip() for s in data["symptoms"].split(",")]
        matched = [s for s in symptoms if any(word in query_lower for word in s.split())]
        match_count = len(matched)
        if match_count > 0 or key in query_lower:
            score = match_count * 2.0
            if key in query_lower:
                score += 3.0
            confidence = min(98.5, round((score / (len(symptoms) * 2.0 + 3.0)) * 100.0, 1))
            if confidence < 30.0:
                confidence = round(35.0 + match_count * 15.0, 1)
            scored_diseases.append({
                "disease_key": key,
                "name": data["name"],
                "type": data["type"],
                "matched_symptoms": matched if matched else [data["symptoms"].split(",")[0]],
                "all_symptoms": data["symptoms"],
                "treatment": data["treatment"],
                "specialist": data["specialist"],
                "confidence": min(98.0, confidence)
            })

    scored_diseases.sort(key=lambda x: x["confidence"], reverse=True)

    if not scored_diseases:
        return None

    top_disease = scored_diseases[0]

    # Find relevant common drugs
    matching_drugs = []
    for d_key, (d_name, d_class, d_uses, d_dosage, d_side) in COMMON_DRUGS.items():
        if any(w in top_disease["treatment"].lower() for w in d_key.split()) or any(w in top_disease["all_symptoms"].lower() for w in d_key.split()):
            matching_drugs.append({
                "name": d_name,
                "class": d_class,
                "dosage": d_dosage,
                "uses": d_uses
            })

    return {
        "status": "success",
        "predicted_disease": top_disease["name"],
        "disease_type": top_disease["type"],
        "confidence": top_disease["confidence"],
        "matched_symptoms": top_disease["matched_symptoms"],
        "recommended_treatment": top_disease["treatment"],
        "recommended_specialist": top_disease["specialist"],
        "matching_drugs": matching_drugs[:3],
        "top_predictions": scored_diseases[:3]
    }
