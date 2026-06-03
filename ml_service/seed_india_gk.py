"""
OMEGA India GK Seeder
Generates and bulk-inserts 1 Million General Knowledge records about India into the database.
"""
import os, sys, random, time
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

random.seed(101)

# ==================== DATA DEFINITIONS ====================
STATES = [
    ("Andhra Pradesh", "Amaravati", "Telugu"),
    ("Arunachal Pradesh", "Itanagar", "English"),
    ("Assam", "Dispur", "Assamese"),
    ("Bihar", "Patna", "Hindi"),
    ("Chhattisgarh", "Raipur", "Hindi"),
    ("Goa", "Panaji", "Konkani"),
    ("Gujarat", "Gandhinagar", "Gujarati"),
    ("Haryana", "Chandigarh", "Hindi"),
    ("Himachal Pradesh", "Shimla", "Hindi"),
    ("Jharkhand", "Ranchi", "Hindi"),
    ("Karnataka", "Bengaluru", "Kannada"),
    ("Kerala", "Thiruvananthapuram", "Malayalam"),
    ("Madhya Pradesh", "Bhopal", "Hindi"),
    ("Maharashtra", "Mumbai", "Marathi"),
    ("Manipur", "Imphal", "Meitei"),
    ("Meghalaya", "Shillong", "English"),
    ("Mizoram", "Aizawl", "Mizo"),
    ("Nagaland", "Kohima", "English"),
    ("Odisha", "Bhubaneswar", "Odia"),
    ("Punjab", "Chandigarh", "Punjabi"),
    ("Rajasthan", "Jaipur", "Hindi"),
    ("Sikkim", "Gangtok", "Nepali"),
    ("Tamil Nadu", "Chennai", "Tamil"),
    ("Telangana", "Hyderabad", "Telugu"),
    ("Tripura", "Agartala", "Bengali"),
    ("Uttar Pradesh", "Lucknow", "Hindi"),
    ("Uttarakhand", "Dehradun", "Hindi"),
    ("West Bengal", "Kolkata", "Bengali")
]

LEADERS = [
    ("Mahatma Gandhi", "Father of the Nation", "Satyagraha movement", "1869"),
    ("Jawaharlal Nehru", "First Prime Minister of India", "Discovery of India book", "1889"),
    ("Subhas Chandra Bose", "Netaji", "Indian National Army (INA)", "1897"),
    ("Sardar Vallabhbhai Patel", "Iron Man of India", "integration of princely states", "1875"),
    ("Dr. B.R. Ambedkar", "Father of the Indian Constitution", "drafting the constitution", "1891"),
    ("Bhagat Singh", "Shaheed", "Naujawan Bharat Sabha", "1907"),
    ("Rani Lakshmibai", "Queen of Jhansi", "Rebellion of 1857", "1828"),
    ("Rabindranath Tagore", "Gurudev", "writing the national anthem Jan Gana Mana", "1861"),
    ("Dr. A.P.J. Abdul Kalam", "Missile Man of India", "development of Agni and Prithvi missiles", "1931"),
    ("Lal Bahadur Shastri", "Second Prime Minister of India", "slogan Jai Jawan Jai Kisan", "1904")
]

MONUMENTS = [
    ("Taj Mahal", "Agra, Uttar Pradesh", "Shah Jahan", "white marble"),
    ("Qutub Minar", "Delhi", "Qutb-ud-din Aibak", "red sandstone"),
    ("Red Fort", "Delhi", "Shah Jahan", "red sandstone"),
    ("Hawa Mahal", "Jaipur, Rajasthan", "Maharaja Sawai Pratap Singh", "pink sandstone"),
    ("Charminar", "Hyderabad, Telangana", "Muhammad Quli Qutb Shah", "granite and lime mortar"),
    ("Gateway of India", "Mumbai, Maharashtra", "George Wittet", "basalt"),
    ("Victoria Memorial", "Kolkata, West Bengal", "William Emerson", "Makrana marble"),
    ("Konark Sun Temple", "Konark, Odisha", "King Narasimhadeva I", "sandstone"),
    ("Sanchi Stupa", "Sanchi, Madhya Pradesh", "Emperor Ashoka", "stone"),
    ("Mysore Palace", "Mysore, Karnataka", "Henry Irwin", "granite and pink marble")
]

RIVERS = [
    ("Ganga", 2525, "Gangotri Glacier", "Bay of Bengal"),
    ("Yamuna", 1376, "Yamunotri Glacier", "Triveni Sangam at Prayagraj"),
    ("Brahmaputra", 2900, "Angsi Glacier", "Bay of Bengal"),
    ("Godavari", 1465, "Trimbakeshwar", "Bay of Bengal"),
    ("Krishna", 1400, "Mahabaleshwar", "Bay of Bengal"),
    ("Narmada", 1312, "Amarkantak", "Gulf of Khambhat"),
    ("Tapi", 724, "Multai", "Gulf of Khambhat"),
    ("Mahanadi", 858, "Sihawa", "Bay of Bengal"),
    ("Kaveri", 805, "Talakaveri", "Bay of Bengal"),
    ("Indus", 3180, "Tibetan Plateau", "Arabian Sea")
]

FESTIVALS = [
    ("Diwali", "Festival of Lights", "victory of light over darkness"),
    ("Holi", "Festival of Colors", "arrival of spring and victory of good over evil"),
    ("Eid-ul-Fitr", "Islamic Festival", "breaking of the month-long Ramadan fast"),
    ("Durga Puja", "Bengali Festival", "worship of Goddess Durga and victory over Mahishasura"),
    ("Pongal", "Harvest Festival of Tamil Nadu", "thanking the Sun God for abundant crops"),
    ("Onam", "Harvest Festival of Kerala", "homecoming of the legendary King Mahabali"),
    ("Bihu", "Assamese Festival", "marking the change of seasons and agricultural cycles"),
    ("Ganesh Chaturthi", "Maharashtrian Festival", "celebrating the birth of Lord Ganesha"),
    ("Chhath Puja", "Bihari Festival", "worship of the Sun God and Chhathi Maiya"),
    ("Lohri", "Punjabi Harvest Festival", "marking the end of the winter solstice")
]

DANCES = [
    ("Bharatanatyam", "Tamil Nadu", "classical"),
    ("Kathak", "Northern India (Uttar Pradesh)", "classical"),
    ("Kathakali", "Kerala", "classical"),
    ("Kuchipudi", "Andhra Pradesh", "classical"),
    ("Odissi", "Odisha", "classical"),
    ("Manipuri", "Manipur", "classical"),
    ("Sattriya", "Assam", "classical"),
    ("Mohiniyattam", "Kerala", "classical"),
    ("Bhangra", "Punjab", "folk"),
    ("Garba", "Gujarat", "folk")
]

DIFFICULTIES = ["basic", "intermediate", "advanced"]

def gen_gk_record(idx):
    diff = random.choice(DIFFICULTIES)
    cat_selector = idx % 7

    seq_idx = idx // 7
    if cat_selector == 0:  # Geography (States & Capitals)
        state, cap, lang = STATES[seq_idx % len(STATES)]
        templates = [
            (f"What is the capital of {state}?",
             f"The capital of {state} is {cap}. The official language of the state is {lang}."),
            (f"Which Indian state has {cap} as its capital?",
             f"{cap} is the capital of {state}. It is one of the key political and cultural hubs in India, where {lang} is widely spoken."),
            (f"What is the official language of {state}?",
             f"The official language of {state} is {lang}. Its capital city is {cap}.")
        ]
        q, a = random.choice(templates)
        cat = "Geography"
    
    elif cat_selector == 1:  # History (Leaders & Freedom Struggle)
        name, desc, contribution, birth = LEADERS[seq_idx % len(LEADERS)]
        templates = [
            (f"Who is known as the '{desc}'?",
             f"{name} is famously referred to as the '{desc}'. He was born in the year {birth} and is widely recognized for his role in the {contribution}."),
            (f"In which year was {name} born?",
             f"{name} was born in the year {birth}. He is known as the '{desc}' and played a significant role in {contribution}."),
            (f"What was the main contribution of {name} in the freedom struggle?",
             f"{name} (born {birth}), famously known as the '{desc}', led the {contribution} to help secure India's independence.")
        ]
        q, a = random.choice(templates)
        cat = "History"
        
    elif cat_selector == 2:  # Culture (Monuments)
        name, loc, builder, material = MONUMENTS[seq_idx % len(MONUMENTS)]
        templates = [
            (f"Where is the historical monument '{name}' located?",
             f"The historical monument '{name}' is located in {loc}. It was commissioned by {builder} and constructed primarily using {material}."),
            (f"Who built the '{name}'?",
             f"The '{name}' was built by {builder}. It is situated in {loc} and features architecture constructed from {material}."),
            (f"Which materials were used to construct '{name}'?",
             f"The '{name}' in {loc} was built using {material} under the patronage of {builder}.")
        ]
        q, a = random.choice(templates)
        cat = "Art & Culture"

    elif cat_selector == 3:  # Geography (Rivers)
        name, length, origin, mouth = RIVERS[seq_idx % len(RIVERS)]
        templates = [
            (f"What is the total length of the {name} river in India?",
             f"The total length of the {name} river is approximately {length} kilometers. It originates from the {origin} and flows into the {mouth}."),
            (f"Where does the {name} river originate?",
             f"The {name} river originates from the {origin}. It flows across various regions for {length} km before emptying into the {mouth}."),
            (f"Which body of water does the {name} river flow into?",
             f"The {name} river drains into the {mouth}. It has a length of {length} km and starts at {origin}.")
        ]
        q, a = random.choice(templates)
        cat = "Geography"

    elif cat_selector == 4:  # Culture (Festivals & Customs)
        name, desc, meaning = FESTIVALS[seq_idx % len(FESTIVALS)]
        templates = [
            (f"What is the significance of the festival '{name}'?",
             f"'{name}' is a famous {desc} in India. It symbolizes the {meaning} and is celebrated with great devotion across the country."),
            (f"How is the festival '{name}' characterized?",
             f"'{name}' is celebrated as the {desc}, signifying the {meaning}.")
        ]
        q, a = random.choice(templates)
        cat = "Art & Culture"

    elif cat_selector == 5:  # Culture (Dance Forms)
        name, origin, dtype = DANCES[seq_idx % len(DANCES)]
        templates = [
            (f"Which state does the dance form '{name}' originate from?",
             f"'{name}' is a traditional {dtype} dance originating from the state of {origin}."),
            (f"Is '{name}' a classical or folk dance form?",
             f"'{name}' is recognized as a traditional {dtype} dance form, originating from {origin}.")
        ]
        q, a = random.choice(templates)
        cat = "Art & Culture"

    else:  # Polity, Sports, Economy & Science (General Trivia)
        general_trivia = [
            ("Who was the first President of India?", "Dr. Rajendra Prasad served as the first President of India from 1950 to 1962.", "Polity"),
            ("When did the Indian Constitution come into force?", "The Constitution of India came into force on January 26, 1950, celebrated annually as Republic Day.", "Polity"),
            ("What is the national animal of India?", "The Royal Bengal Tiger is the national animal of India, known for its grace, strength, and agility.", "Geography"),
            ("What is the national bird of India?", "The Indian Peacock (Pavo cristatus) is the national bird of India, representing beauty and cultural heritage.", "Geography"),
            ("Which is the national sport of India?", "While India has no official national sport declared by law, Field Hockey is traditionally considered the national sport due to its rich history of Olympic success.", "Sports"),
            ("Who was the first Indian to win a Nobel Prize?", "Rabindranath Tagore won the Nobel Prize in Literature in 1913 for his poetry collection 'Gitanjali'.", "History"),
            ("What is the national currency of India?", "The Indian Rupee (INR) is the official currency, symbolized by the sign ₹.", "Economy"),
            ("Which Indian space agency launched the Chandrayaan missions?", "ISRO (Indian Space Research Organisation) launched the Chandrayaan lunar exploration missions.", "Science & Tech"),
            ("Which city is known as the Silicon Valley of India?", "Bengaluru (formerly Bangalore) is known as the Silicon Valley of India because of its role as the nation's leading IT exporter.", "Economy"),
            ("Where is the Reserve Bank of India (RBI) headquartered?", "The Reserve Bank of India is headquartered in Mumbai, Maharashtra.", "Economy")
        ]
        q, a, trivia_cat = general_trivia[seq_idx % len(general_trivia)]
        q = f"{q} (QID: {idx})"
        a = f"{a} This is catalogued under general facts about India."
        cat = trivia_cat

    # Ensure uniqueness across questions by appending ID if necessary
    if idx >= 100:
        q = f"{q} [ID: {idx}]"

    return cat, q, a, diff

# ==================== SEEDER ====================
BATCH = 2000

def seed_india_gk(conn, count=1000000):
    print(f"\nSeeding INDIA_GK_DATA ({count:,} records)...")
    conn.execute(text("DELETE FROM india_gk_data"))
    conn.commit()
    
    t0 = time.time()
    for start in range(0, count, BATCH):
        end = min(start + BATCH, count)
        params = []
        for i in range(start, end):
            cat, q, a, diff = gen_gk_record(i)
            params.append({"c": cat, "q": q, "a": a, "d": diff})
        
        # Use bulk insert
        conn.execute(
            text("INSERT INTO india_gk_data (category,question,answer,difficulty) VALUES (:c,:q,:a,:d)"),
            params
        )
        conn.commit()
        
        if (start // BATCH) % 50 == 0:
            elapsed = time.time() - t0
            rate = end / elapsed if elapsed > 0 else 0
            print(f"  {end:,}/{count:,} inserted (Rate: {rate:.1f} rows/sec)...")
            
    print(f"  [OK] {count:,} India GK records seeded successfully.")

if __name__ == "__main__":
    print("=" * 60)
    print("  OMEGA India GK Seeder")
    print("  Target: 1,000,000 records of India GK")
    print("=" * 60)
    t0 = time.time()
    with engine.connect() as conn:
        seed_india_gk(conn, 1000000)
    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"  COMPLETE: 1,000,000 records seeded in {elapsed:.1f}s")
    print(f"{'=' * 60}")
