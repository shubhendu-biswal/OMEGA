"""
OMEGA Gen AI Training Data Seeder
Generates ~1 Million diverse records across 5 tables in Oracle DB.
"""
import os, sys, random, json, time
from sqlalchemy import create_engine, text

# Load .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", ".env")
if os.path.exists(dotenv_path):
    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

db_user = os.getenv("DB_USER", "OMEGA_user")
db_pass = os.getenv("DB_PASSWORD", "omega123")
db_url = f"oracle+oracledb://{db_user}:{db_pass}@localhost:1521/?service_name=orcl"

engine = create_engine(db_url, pool_pre_ping=True)
print(f"[OK] Connected to Oracle DB as {db_user}")

random.seed(42)

# ==================== DOMAIN DATA ====================
CATEGORIES = [
    "agriculture", "technology", "science", "health", "education",
    "finance", "environment", "cooking", "sports", "history",
    "geography", "mathematics", "programming", "music", "travel"
]
DIFFICULTIES = ["basic", "intermediate", "advanced"]
SENTIMENTS = ["positive", "negative", "neutral"]
INTENTS = [
    "crop_prediction", "fertilizer_recommendation", "pest_diagnosis",
    "weather_query", "market_price", "irrigation_advice", "soil_analysis",
    "general_greeting", "tech_support", "health_advice", "recipe_request",
    "travel_recommendation", "math_help", "coding_help", "general_knowledge"
]
DOMAINS = ["crops", "soil", "fertilizer", "pest", "weather", "tech", "science", "health", "finance", "general"]

AGRI_INSTRUCTIONS = [
    ("What is the best crop for {} soil in {} season?", "For {} soil during {} season, the recommended crops are {}. These crops thrive because {} soil provides {} nutrients and {} season offers optimal {} conditions for growth."),
    ("How to increase {} yield?", "To increase {} yield: 1) Use {} fertilizer at {} kg/hectare. 2) Ensure {} irrigation schedule. 3) Apply {} pesticide if {} infestation is detected. 4) Maintain soil pH between {} and {}."),
    ("What fertilizer is best for {}?", "For {} cultivation, {} fertilizer is recommended at {} kg/acre. Apply {} during {} stage. Supplement with {} for micronutrient deficiency. Soil testing every {} months ensures optimal dosage."),
    ("How to control {} pest in {} crop?", "To control {} in {} crop: 1) Use {} at {} ml/liter. 2) Apply {} trap crops around the field. 3) Release {} biocontrol agents. 4) Practice {} crop rotation to break pest cycle."),
    ("What is the ideal temperature for growing {}?", "The ideal temperature range for {} is {}-{}°C. Below {}°C, {} damage occurs. Above {}°C, {} stress develops. In tropical regions, {} variety is preferred for heat tolerance."),
    ("How much water does {} need per day?", "{} requires approximately {}-{} mm of water daily during {} stage. Use {} irrigation method for {} efficiency. Reduce watering during {} stage to prevent {} issues."),
    ("When is the best time to plant {}?", "The optimal planting window for {} is {} to {}. Sow seeds at {} cm depth with {} cm spacing. In {} climate zones, early {} planting gives {} better yield results."),
    ("How to prepare {} soil for planting?", "To prepare {} soil: 1) Plow to {} cm depth. 2) Add {} organic matter at {} tons/hectare. 3) Adjust pH to {} using {}. 4) Let soil rest for {} days before sowing."),
]

TECH_INSTRUCTIONS = [
    ("What is {}?", "{} is a {} technology that {}. It was developed by {} and is widely used in {}. Key features include {} and {}. It has revolutionized {} industry."),
    ("How does {} work?", "{} works by {}. The core mechanism involves {}. Input data is processed through {} layers of {}. Output is generated using {} algorithm with {} accuracy."),
    ("What are the advantages of {}?", "Advantages of {}: 1) {} performance improvement. 2) {} cost reduction. 3) {} scalability. 4) {} integration with existing systems. 5) {} security features."),
    ("Compare {} and {}", "{} and {} are both {} technologies. {} excels in {} while {} is better for {}. Performance-wise, {} offers {}x speed. Cost comparison shows {} is {}% cheaper."),
]

SCIENCE_INSTRUCTIONS = [
    ("Explain the process of {}", "{} is a {} process that occurs in {}. It involves {} stages: First, {}. Then, {}. Finally, {}. This process is crucial for {} in nature."),
    ("What causes {}?", "{} is caused by {} interacting with {}. The primary mechanism involves {}. Contributing factors include {} and {}. Scientists discovered this in {} through {} experiments."),
]

HEALTH_INSTRUCTIONS = [
    ("What are the benefits of eating {}?", "{} is rich in {} and provides {} calories per serving. Health benefits include: 1) {} improvement. 2) {} prevention. 3) {} support. Recommended daily intake is {} grams."),
    ("How to prevent {}?", "Prevention of {} involves: 1) {} diet changes. 2) {} minutes of daily exercise. 3) {} hours of sleep. 4) Regular {} checkups. 5) Avoiding {} and {} habits."),
]

SOILS = ["Sandy", "Clayey", "Loamy", "Black", "Red", "Alluvial", "Laterite", "Peaty", "Saline", "Silty"]
SEASONS = ["summer", "winter", "monsoon", "spring", "autumn", "kharif", "rabi", "zaid"]
CROPS = ["Rice", "Wheat", "Maize", "Cotton", "Sugarcane", "Potato", "Tomato", "Onion", "Soybean", "Groundnut",
         "Banana", "Mango", "Coffee", "Tea", "Jute", "Barley", "Chickpea", "Lentil", "Mustard", "Sunflower",
         "Coconut", "Rubber", "Pepper", "Turmeric", "Ginger", "Cardamom", "Cashew", "Arecanut", "Papaya", "Grapes"]
FERTILIZERS = ["Urea", "DAP", "MOP", "NPK 19-19-19", "Superphosphate", "Ammonium Sulphate", "Vermicompost",
               "Organic Compost", "Bone Meal", "Neem Cake", "Potash", "Zinc Sulphate"]
PESTS = ["aphids", "bollworm", "stem borer", "leaf miner", "whitefly", "thrips", "mealybug", "fruit fly",
         "army worm", "root grub", "caterpillar", "spider mite", "nematode", "locust"]
PESTICIDES = ["Neem oil", "Chlorpyrifos", "Imidacloprid", "Spinosad", "Bt spray", "Malathion", "Cypermethrin"]
TECH_TERMS = ["Machine Learning", "Blockchain", "IoT", "Cloud Computing", "5G", "Quantum Computing",
              "Neural Networks", "Docker", "Kubernetes", "GraphQL", "WebAssembly", "Edge Computing",
              "Artificial Intelligence", "Deep Learning", "Natural Language Processing", "Computer Vision"]
SCIENCE_TOPICS = ["photosynthesis", "nitrogen cycle", "water cycle", "cell division", "DNA replication",
                  "protein synthesis", "osmosis", "fermentation", "decomposition", "pollination"]
HEALTH_FOODS = ["spinach", "almonds", "blueberries", "salmon", "quinoa", "avocado", "broccoli", "turmeric",
                "green tea", "yogurt", "lentils", "sweet potato", "garlic", "oats", "walnuts"]
DISEASES = ["diabetes", "hypertension", "heart disease", "obesity", "anemia", "vitamin D deficiency"]

def rand_num(a, b): return round(random.uniform(a, b), 1)

def gen_conversation(idx):
    cat = random.choice(CATEGORIES)
    diff = random.choice(DIFFICULTIES)
    soil = random.choice(SOILS)
    season = random.choice(SEASONS)
    crop = random.choice(CROPS)
    fert = random.choice(FERTILIZERS)
    pest = random.choice(PESTS)
    tech = random.choice(TECH_TERMS)
    food = random.choice(HEALTH_FOODS)
    disease = random.choice(DISEASES)
    topic = random.choice(SCIENCE_TOPICS)

    if cat == "agriculture":
        templates = [
            (f"What is the best crop for {soil} soil in {season} season?",
             f"For {soil} soil during {season} season, {crop} is highly recommended. {soil} soil provides ideal nutrients and {season} offers optimal conditions. Apply {fert} at {rand_num(20,50)} kg/hectare for best results."),
            (f"How to increase {crop} yield?",
             f"To increase {crop} yield: 1) Use {fert} at {rand_num(15,40)} kg/hectare. 2) Follow {random.choice(['drip','flood','sprinkler'])} irrigation. 3) Apply {random.choice(PESTICIDES)} if {pest} appears. 4) Maintain soil pH {rand_num(5.5,7.5)}."),
            (f"What fertilizer is best for {crop}?",
             f"For {crop}, {fert} is recommended at {rand_num(10,50)} kg/acre. Apply during {random.choice(['sowing','flowering','fruiting'])} stage. Supplement with {random.choice(FERTILIZERS)} for micronutrients. Test soil every {random.randint(3,6)} months."),
            (f"How to control {pest} in {crop}?",
             f"To control {pest} in {crop}: 1) Spray {random.choice(PESTICIDES)} at {rand_num(1,5)} ml/liter. 2) Use trap crops. 3) Release biocontrol agents. 4) Practice crop rotation with {random.choice(CROPS)}."),
        ]
        instr, resp = random.choice(templates)
    elif cat == "technology":
        templates = [
            (f"What is {tech}?",
             f"{tech} is a transformative technology used in modern computing. It enables automation and optimization across {random.randint(5,15)} industries. Key features include scalability, {rand_num(90,99)}% accuracy, and real-time processing capabilities."),
            (f"How does {tech} work?",
             f"{tech} works by processing data through multiple computational layers. The core mechanism involves {random.choice(['neural networks','distributed systems','cloud infrastructure'])}. It achieves {rand_num(85,99)}% efficiency in production environments."),
        ]
        instr, resp = random.choice(templates)
    elif cat == "science":
        instr = f"Explain the process of {topic}"
        resp = f"{topic.title()} is a fundamental {cat} process. It involves multiple stages of molecular interaction. First, initial reactants combine. Then, energy transformation occurs. Finally, products are formed. This process is essential for life on Earth."
    elif cat == "health":
        templates = [
            (f"What are the benefits of eating {food}?",
             f"{food.title()} is rich in vitamins and minerals, providing {rand_num(50,300)} calories per serving. Benefits include immune support, heart health improvement, and {disease} prevention. Recommended intake: {rand_num(50,200)}g daily."),
            (f"How to prevent {disease}?",
             f"Prevention of {disease} involves: 1) Balanced diet with {food}. 2) {random.randint(20,60)} minutes daily exercise. 3) {random.randint(7,9)} hours sleep. 4) Regular medical checkups. 5) Stress management techniques."),
        ]
        instr, resp = random.choice(templates)
    else:
        instr = f"Explain the concept of {cat} topic #{idx} in detail"
        resp = f"This is a comprehensive explanation about {cat} concept #{idx}. It covers fundamentals, applications, and advanced aspects with {rand_num(3,10)} practical examples across {random.randint(5,20)} industries."
    return cat, instr, resp, diff

def gen_knowledge(idx):
    domain = random.choice(DOMAINS)
    if domain == "crops":
        crop = random.choice(CROPS)
        topic = f"{crop} Cultivation Guide"
        content = f"{crop} is a major crop grown in tropical and subtropical regions. Optimal temperature: {rand_num(15,35)}°C. Soil: {random.choice(SOILS)}. Water requirement: {rand_num(400,1200)}mm annually. Growth period: {random.randint(60,180)} days. Major producing states include various regions across India. Yield potential: {rand_num(2,8)} tons/hectare with proper management practices including timely sowing, adequate fertilization with {random.choice(FERTILIZERS)}, and integrated pest management."
        keywords = f"{crop.lower()},cultivation,farming,agriculture"
    elif domain == "tech":
        tech = random.choice(TECH_TERMS)
        topic = f"{tech} Overview"
        content = f"{tech} is a transformative technology reshaping modern industries. It enables {random.choice(['automation','optimization','prediction','analysis'])} of complex systems. Adoption rate has grown {rand_num(15,45)}% annually. Key applications span {random.randint(5,15)} sectors including healthcare, finance, and agriculture. Implementation requires understanding of core algorithms and infrastructure with {rand_num(85,99)}% uptime requirements."
        keywords = f"{tech.lower().replace(' ','_')},technology,innovation"
    else:
        topic = f"{domain.title()} Knowledge Article #{idx}"
        content = f"Comprehensive article about {domain} covering {random.randint(5,12)} key aspects. This knowledge base entry provides detailed information for training generative AI models. Coverage includes theoretical foundations, practical applications, case studies from {random.randint(3,8)} regions, and expert recommendations based on {random.randint(10,50)} years of research data."
        keywords = f"{domain},knowledge,training,ai"
    return topic, domain, content, keywords

def gen_intent(idx):
    intent = random.choice(INTENTS)
    if intent == "crop_prediction":
        crop = random.choice(CROPS)
        soil = random.choice(SOILS)
        u = random.choice([f"What crop grows best in {soil} soil?", f"Suggest a crop for {rand_num(15,40)} degrees temperature",
                           f"Which crop is suitable for {random.choice(SEASONS)} season?", f"Best crop for {soil} soil in {random.choice(SEASONS)}?"])
        e = json.dumps({"soil": soil, "crop": crop})
    elif intent == "pest_diagnosis":
        crop = random.choice(CROPS)
        pest = random.choice(PESTS)
        u = random.choice([f"My {crop} has {pest} problem", f"{crop} leaves are damaged by insects",
                           f"How to get rid of {pest} in {crop} field?", f"Yellow spots on {crop} leaves"])
        e = json.dumps({"crop": crop, "pest": pest})
    elif intent == "coding_help":
        lang = random.choice(["Python", "Java", "JavaScript", "C++", "SQL", "React", "Spring Boot"])
        u = random.choice([f"How to write a loop in {lang}?", f"Fix this {lang} error", f"Best practices for {lang} development"])
        e = json.dumps({"language": lang})
    elif intent == "general_greeting":
        u = random.choice(["Hello", "Hi there", "Good morning", "Hey", "What can you do?", "Help me please"])
        e = json.dumps({})
    else:
        u = f"Query about {intent.replace('_',' ')} topic #{idx}"
        e = json.dumps({"topic": intent})
    return u, intent, e

def gen_feedback(idx):
    cat = random.choice(CATEGORIES)
    rating = random.choices([1,2,3,4,5], weights=[5,10,15,35,35])[0]
    sentiment = "positive" if rating >= 4 else ("negative" if rating <= 2 else "neutral")
    query = f"User question about {cat} - query #{idx}"
    response = f"AI response providing {random.choice(['detailed','brief','comprehensive','expert'])} {cat} guidance with {random.randint(3,8)} actionable recommendations and {rand_num(85,99)}% confidence score."
    return query, response, rating, sentiment

def gen_dialog(dialog_idx):
    turns = random.randint(3, 6)
    cat = random.choice(CATEGORIES)
    did = f"DLG-{dialog_idx:06d}"
    rows = []
    for t in range(1, turns + 1):
        if t % 2 == 1:
            role = "user"
            msg = f"User message about {cat} in dialog {did}, turn {t}: {random.choice(['Can you explain','Tell me about','How does','What is','Help me with'])} {cat} concept #{random.randint(1,1000)}?"
        else:
            role = "assistant"
            msg = f"Assistant response for {cat}: Here is a {random.choice(['detailed','comprehensive','concise'])} explanation covering {random.randint(3,7)} key points about {cat}. This includes practical examples and {rand_num(2,5)} case studies with {rand_num(90,99)}% accuracy metrics."
        rows.append((did, t, role, msg))
    return rows

# ==================== SEEDER ====================
BATCH = 1000

def seed_conversations(conn, count=300000):
    print(f"\n[1/5] Seeding CONVERSATION_TRAINING_DATA ({count:,} records)...")
    conn.execute(text("DELETE FROM conversation_training_data"))
    conn.commit()
    for start in range(0, count, BATCH):
        end = min(start + BATCH, count)
        for i in range(start, end):
            cat, instr, resp, diff = gen_conversation(i)
            conn.execute(text("INSERT INTO conversation_training_data (category,instruction,response,difficulty) VALUES (:c,:i,:r,:d)"),
                         {"c": cat, "i": instr, "r": resp, "d": diff})
        conn.commit()
        if (start // BATCH) % 50 == 0:
            print(f"  {end:,}/{count:,} inserted...")
    print(f"  [OK] {count:,} conversation records seeded.")

def seed_knowledge(conn, count=200000):
    print(f"\n[2/5] Seeding AGRI_KNOWLEDGE_BASE ({count:,} records)...")
    conn.execute(text("DELETE FROM agri_knowledge_base"))
    conn.commit()
    for start in range(0, count, BATCH):
        end = min(start + BATCH, count)
        for i in range(start, end):
            topic, domain, content, kw = gen_knowledge(i)
            conn.execute(text("INSERT INTO agri_knowledge_base (topic,domain,content,keywords) VALUES (:t,:d,:c,:k)"),
                         {"t": topic, "d": domain, "c": content, "k": kw})
        conn.commit()
        if (start // BATCH) % 50 == 0:
            print(f"  {end:,}/{count:,} inserted...")
    print(f"  [OK] {count:,} knowledge records seeded.")

def seed_intents(conn, count=200000):
    print(f"\n[3/5] Seeding INTENT_TRAINING_DATA ({count:,} records)...")
    conn.execute(text("DELETE FROM intent_training_data"))
    conn.commit()
    for start in range(0, count, BATCH):
        end = min(start + BATCH, count)
        for i in range(start, end):
            u, intent, e = gen_intent(i)
            conn.execute(text("INSERT INTO intent_training_data (utterance,intent,entities) VALUES (:u,:i,:e)"),
                         {"u": u, "i": intent, "e": e})
        conn.commit()
        if (start // BATCH) % 50 == 0:
            print(f"  {end:,}/{count:,} inserted...")
    print(f"  [OK] {count:,} intent records seeded.")

def seed_feedback(conn, count=200000):
    print(f"\n[4/5] Seeding FEEDBACK_TRAINING_DATA ({count:,} records)...")
    conn.execute(text("DELETE FROM feedback_training_data"))
    conn.commit()
    for start in range(0, count, BATCH):
        end = min(start + BATCH, count)
        for i in range(start, end):
            q, r, rating, sent = gen_feedback(i)
            conn.execute(text("INSERT INTO feedback_training_data (user_query,ai_response,rating,sentiment) VALUES (:q,:r,:ra,:s)"),
                         {"q": q, "r": r, "ra": rating, "s": sent})
        conn.commit()
        if (start // BATCH) % 50 == 0:
            print(f"  {end:,}/{count:,} inserted...")
    print(f"  [OK] {count:,} feedback records seeded.")

def seed_dialogs(conn, count=25000):
    print(f"\n[5/5] Seeding DIALOG_TRAINING_DATA (~{count*4:,} records from {count:,} dialogs)...")
    conn.execute(text("DELETE FROM dialog_training_data"))
    conn.commit()
    total = 0
    for start in range(0, count, BATCH):
        end = min(start + BATCH, count)
        for i in range(start, end):
            rows = gen_dialog(i)
            for did, tn, role, msg in rows:
                conn.execute(text("INSERT INTO dialog_training_data (dialog_id,turn_number,role,message) VALUES (:d,:t,:r,:m)"),
                             {"d": did, "t": tn, "r": role, "m": msg})
                total += 1
        conn.commit()
        if (start // BATCH) % 50 == 0:
            print(f"  {total:,} rows inserted...")
    print(f"  [OK] {total:,} dialog records seeded from {count:,} dialogs.")
    return total

# ==================== MAIN ====================
if __name__ == "__main__":
    print("=" * 60)
    print("  OMEGA Gen AI Training Data Seeder")
    print("  Target: ~1,000,000 diverse records")
    print("=" * 60)
    t0 = time.time()
    with engine.connect() as conn:
        seed_conversations(conn, 300000)
        seed_knowledge(conn, 200000)
        seed_intents(conn, 200000)
        seed_feedback(conn, 200000)
        dialog_rows = seed_dialogs(conn, 25000)
    elapsed = time.time() - t0
    total = 300000 + 200000 + 200000 + 200000 + dialog_rows
    print(f"\n{'=' * 60}")
    print(f"  COMPLETE: {total:,} total records seeded in {elapsed:.1f}s")
    print(f"{'=' * 60}")
