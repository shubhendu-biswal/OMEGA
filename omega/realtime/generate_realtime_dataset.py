import os
import sys
import json
import random
import re
from collections import defaultdict, Counter

random.seed(42)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Base locations, commodities, exams, topics, currencies
INDIAN_CITIES = [
    "Delhi", "Mumbai", "Bengaluru", "Chennai", "Kolkata", "Hyderabad",
    "Ahmedabad", "Pune", "Jaipur", "Lucknow", "Patna", "Bhopal", "Chandigarh",
    "Kochi", "Shimla", "Srinagar", "Varanasi", "Surat", "Nagpur", "Indore",
    "Ranchi", "Guwahati", "Bhubaneswar", "Amritsar", "Dehradun", "Raipur",
    "Gwalior", "Jodhpur", "Coimbatore", "Visakhapatnam"
]
INDIAN_DISTRICTS = [
    "Nashik", "Guntur", "Karnal", "Bhatinda", "Ludhiana", "Bareilly",
    "Warangal", "Mandya", "Kolhapur", "Meerut", "Unjha", "Ganganagar",
    "Rajkot", "Mandsaur", "Kota", "Khanna", "Hapur", "Alwar", "Muzaffarnagar"
]
WORLD_CITIES = [
    "New York", "London", "Tokyo", "Paris", "Dubai", "Singapore",
    "Sydney", "Toronto", "Berlin", "San Francisco"
]

COMMODITIES = [
    ("onion", "pyaj", "प्याज"),
    ("potato", "aloo", "आलू"),
    ("tomato", "tamatar", "टमाटर"),
    ("wheat", "gehu", "गेहूं"),
    ("rice", "chawal", "चावल"),
    ("mustard", "sarson", "सरसों"),
    ("cotton", "kapas", "कपास"),
    ("soybean", "soyabean", "सोयाबीन"),
    ("garlic", "lahsun", "लहसुन"),
    ("ginger", "adrak", "अदरक"),
    ("chilli", "mirchi", "मिर्च"),
    ("turmeric", "haldi", "हल्दी"),
    ("cumin", "jeera", "जीरा"),
    ("chana", "chana", "चना"),
    ("maize", "makka", "मक्का"),
    ("sugarcane", "ganna", "गन्ना")
]

MANDIS = [
    "Azadpur", "Nashik", "Lasalgaon", "Vashi", "Indore", "Khanna",
    "Ganganagar", "Unjha", "Rajkot", "Guntur", "Nizamabad", "Kota",
    "Mandsaur", "Hapur", "Karnal", "Agra", "Kanpur", "Bhatinda"
]

SPORTS_TEAMS = [
    ("India", "Australia"), ("India", "England"), ("India", "Pakistan"),
    ("CSK", "MI"), ("RCB", "KKR"), ("GT", "RR"), ("Real Madrid", "Barcelona"),
    ("Arsenal", "Manchester City"), ("Liverpool", "Chelsea")
]

CURRENCIES = [
    ("USD", "dollar", "डॉलर"),
    ("EUR", "euro", "यूरो"),
    ("GBP", "pound", "पाउंड"),
    ("AED", "dirham", "दिरहम"),
    ("CAD", "Canadian dollar", "कैनेडियन डॉलर"),
    ("AUD", "Australian dollar", "ऑस्ट्रेलियाई डॉलर")
]

EXAMS = [
    "UPSC Civil Services", "NEET UG", "JEE Main", "CBSE 10th", "CBSE 12th",
    "UGC NET", "SSC CGL", "IBPS PO", "CTET", "NDA", "GATE 2026", "ICSE Board"
]

GOVT_SCHEMES = [
    "PM Kisan Samman Nidhi 17th installment", "Kisan Credit Card interest subvention",
    "PM Fasal Bima Yojana claim", "MSP procurement rates 2026", "LPG cylinder subsidy",
    "income tax return filing deadline", "RBI repo rate policy decision",
    "fertilizer subsidy allocation", "Aadhaar PAN linking status"
]

NEWS_TOPICS = [
    "Union Budget announcements", "ISRO Gaganyaan mission", "monsoon forecast in India",
    "crude oil prices", "parliament session debate", "Supreme Court verdict",
    "semiconductor plant in Gujarat", "electric vehicle policy", "stock market rally",
    "international trade agreements", "national highway expansion", "AI regulation bill"
]

def mask_digits(text: str) -> str:
    t = re.sub(r'\b\d+(?:\.\d+)?\b', '<N>', text.lower())
    t = re.sub(r'#<N>', '#<N>', t)
    return re.sub(r'\s+', ' ', t).strip()

def get_cluster_key(text: str, label: str) -> str:
    masked = mask_digits(text)
    words = re.findall(r'\b[a-z0-9<>]+\b', masked)
    if not words:
        return f"{label}__empty"
    return f"{label}__" + "_".join(words[:min(len(words), 4)])

def generate_realtime_examples():
    """Generates 3,600+ labeled examples for the 'realtime' intent across EN, HI, Hinglish."""
    examples = set()

    # 1. Weather Queries (~800)
    for city in INDIAN_CITIES + INDIAN_DISTRICTS + WORLD_CITIES:
        examples.add(f"What is the weather in {city} today?")
        examples.add(f"Current temperature in {city} right now")
        examples.add(f"Is it raining in {city} at the moment?")
        examples.add(f"Weather forecast for {city} this weekend")
        examples.add(f"Will it rain today in {city}?")
        examples.add(f"What is the humidity and wind speed in {city} now?")
        examples.add(f"Check air quality index AQI in {city} today")
        examples.add(f"Is there a heatwave warning in {city} today?")
        examples.add(f"Minimum and maximum temperature in {city} today")
        # Hindi / Hinglish
        examples.add(f"{city} mein aaj ka mausam kaisa hai?")
        examples.add(f"{city} me aaj barish hogi kya?")
        examples.add(f"Aaj {city} ka tapman kitna chal raha hai?")
        examples.add(f"{city} ka live weather update do")
        examples.add(f"Kya {city} me aaj dhoop niklegi ya badal rahenge?")
        examples.add(f"{city} ka current temperature batao")
        examples.add(f"Aaj {city} me mausam kaisa rahega?")
        examples.add(f"{city} ka AQI kitna hai aaj?")

    # 2. Market & Mandi Prices (~900)
    for c_en, c_hing, c_hi in COMMODITIES:
        for m in MANDIS:
            examples.add(f"What is the mandi price of {c_en} in {m} today?")
            examples.add(f"Current wholesale rate of {c_en} per quintal in {m} mandi")
            examples.add(f"Today's modal price for {c_en} in {m} APMC")
            examples.add(f"Latest {c_en} market price today in {m}")
            examples.add(f"How much is {c_en} selling for in {m} mandi right now?")
            # Hinglish & Hindi
            examples.add(f"Aaj {m} mandi me {c_hing} ka bhav kya hai?")
            examples.add(f"{m} mandi mein {c_hing} ka taaza rate bataiye")
            examples.add(f"Aaj {c_hing} ka rate kitna chal raha hai {m} me?")
            examples.add(f"{m} me {c_hi} ka aaj ka mandi bhav kya hai?")
            examples.add(f"Latest {c_hing} price in {m} mandi today")

    # 3. Sports Scores & Live Games (~600)
    for t1, t2 in SPORTS_TEAMS:
        examples.add(f"What is the live score of {t1} vs {t2} today?")
        examples.add(f"Who won the match between {t1} and {t2} today?")
        examples.add(f"Current match score between {t1} and {t2} right now")
        examples.add(f"Live cricket score {t1} against {t2} today")
        examples.add(f"Who is batting right now in {t1} vs {t2}?")
        examples.add(f"How many runs has {t1} scored so far against {t2}?")
        # Hinglish & Hindi
        examples.add(f"Aaj ke match me {t1} vs {t2} ka live score kya hai?")
        examples.add(f"{t1} aur {t2} ke match me kaun jeeta aaj?")
        examples.add(f"Aaj ka IPL match kaun jeet raha hai?")
        examples.add(f"{t1} ka score kitna hua hai abhi?")
        examples.add(f"Live match score batao {t1} aur {t2} ka")

    sports_extras = [
        "What is the current medal tally of India in Olympic games today?",
        "Live football score Premier League match today",
        "Who is leading in today's Formula 1 Grand Prix race?",
        "Aaj ke test match ka live score update do",
        "Who scored the goal in today's Champions League match?",
        "T20 World Cup points table latest update today",
        "Aaj ka football match kaun jeeta?",
        "Who won yesterday's cricket match between India and Australia?"
    ]
    for s in sports_extras:
        examples.add(s)

    # 4. Exchange Rates, Financial Live Prices & Crypto (~600)
    for code, name_en, name_hi in CURRENCIES:
        examples.add(f"What is the exchange rate of {code} to INR today?")
        examples.add(f"Current price of 1 {name_en} in Indian rupees right now")
        examples.add(f"How much is 100 {code} in INR today?")
        examples.add(f"Live currency rate for {code} against Indian rupee")
        examples.add(f"Aaj 1 {name_en} kitne rupaye ka hai?")
        examples.add(f"{code} to INR ka aaj ka conversion rate kya hai?")
        examples.add(f"Rupaye ke mukable {name_hi} ka current bhav kitna hai?")

    finance_extras = [
        "What is the gold price per 10 grams in Delhi today?",
        "Current 24K and 22K gold rate today in Mumbai",
        "Silver price per kg in India today",
        "Current price of Bitcoin in USD right now",
        "What is the live price of Ethereum today?",
        "Nifty 50 and Sensex current live index value today",
        "Is the stock market up or down right now?",
        "Crude oil price per barrel in international market today",
        "Aaj sone ka taaza bhav kya hai Delhi mein?",
        "Aaj chandi ka rate kitna chal raha hai?",
        "Bitcoin ka live price kitna hai abhi?",
        "Aaj share market me Nifty ka current level kya hai?",
        "Sensex kitne point upar ya niche hai aaj?"
    ]
    for fe in finance_extras:
        examples.add(fe)

    # 5. Government Announcements & Schemes (~500)
    for sch in GOVT_SCHEMES:
        examples.add(f"What is the latest government announcement on {sch}?")
        examples.add(f"Has the government released new update on {sch} today?")
        examples.add(f"Latest circular and notification regarding {sch}")
        examples.add(f"Current status of {sch} update today")
        examples.add(f"Sarkar ne aaj {sch} par kya announcement kiya?")
        examples.add(f"{sch} ki latest news aur update kya hai?")
        examples.add(f"Kya {sch} ki tarikh aage badha di gayi hai aaj?")

    # 6. Exam Results & Education Notifications (~400)
    for ex in EXAMS:
        examples.add(f"Is {ex} result declared today?")
        examples.add(f"Latest update on {ex} answer key release date")
        examples.add(f"When will {ex} cutoff be announced officially today?")
        examples.add(f"Direct link to check {ex} score card today active?")
        examples.add(f"Kya {ex} ka result aaj aa gaya hai?")
        examples.add(f"{ex} pariksha ka parinaam kab ghoshit hoga latest news")
        examples.add(f"{ex} ki answer key aaj jaari hui kya?")
        examples.add(f"{ex} cutoff marks ka current update kya hai?")

    # 7. General News & Time-Sensitive Queries (~500)
    for top in NEWS_TOPICS:
        examples.add(f"What is the latest news about {top} today?")
        examples.add(f"Breaking news updates on {top} right now")
        examples.add(f"What happened today regarding {top}?")
        examples.add(f"Aaj ki taaza khabar on {top}")
        examples.add(f"{top} par aaj ki breaking news kya hai?")
        examples.add(f"Latest developments in {top} today")

    general_realtime = [
        "What are the top breaking news headlines in India today?",
        "What is currently trending on Twitter / X in India right now?",
        "Who is the current Prime Minister of the United Kingdom right now?",
        "Who is the current President of France in 2026?",
        "What is the present situation at the border today?",
        "Is there a nationwide strike or bandh declared today in India?",
        "Are banks open today or is it a holiday?",
        "Current petrol and diesel price in Delhi today",
        "LPG cylinder price in Mumbai today",
        "Aaj ki sabse badi taaza khabar kya hai?",
        "Abhi desh me kya trending chal raha hai?",
        "Aaj petrol diesel ka rate kya hai Delhi me?",
        "Kya aaj bank band hain ya khule hain?",
        "Aaj public holiday hai kya?",
        "Breaking news batao abhi ki",
        "Aaj ka taaza samachar sunao"
    ]
    for gr in general_realtime:
        examples.add(gr)

    print(f"Generated {len(examples)} unique 'realtime' examples.")
    return list(examples)

def generate_hard_negatives():
    """
    Generates hard negatives that look time-related or contain temporal keywords
    (first, history, when, year, date, was, ancient, past) but are strictly STATIC.
    """
    gk_hard_negatives = [
        "Who was the first Prime Minister of India?",
        "Who was the first President of India?",
        "When did India gain independence?",
        "In which year was the Constitution of India adopted?",
        "When did the Battle of Plassey take place?",
        "Who was the first Indian in space?",
        "What was the capital of India before New Delhi in 1911?",
        "Who invented the telephone in 1876?",
        "In which year was the Reserve Bank of India established?",
        "Who won the Cricket World Cup in 1983?",
        "Who was the first Mughal emperor of India?",
        "When did World War 2 end?",
        "What was the currency of France before the Euro?",
        "Who was the first woman President of India?",
        "Who discovered penicillin in 1928?",
        "In which year was ISRO founded?",
        "Who was the ruler of Delhi during the 16th century?",
        "When was the Quit India Movement launched?",
        "Who was the first woman governor of an Indian state?",
        "What was the duration of the First World War?",
        "Who was the first Viceroy of British India in 1858?",
        "When was Mahatma Gandhi born?",
        "In which year was the Indian National Congress founded?",
        "Who was the first Indian to win a Nobel Prize in 1913?",
        "When did the Taj Mahal construction complete?",
        "Who won the 2011 ICC Cricket World Cup?",
        "Who was the first Law Minister of Independent India?",
        "When was the first Five Year Plan launched in India?",
        "What was the name of the first satellite launched by India in 1975?",
        "Who was the prime minister of India during the 1971 war?",
        "When was the State Bank of India established in 1955?",
        "Who discovered gravity in the 17th century?",
        "What was the original name of Kolkata before 2001?",
        "When was the railway line first opened in India in 1853?",
        "Who was the first chief justice of independent India?",
        "In which century was the Qutub Minar built?",
        "Who was the captain of the Indian cricket team in 1983?",
        "When did Neil Armstrong land on the moon in 1969?",
        "Who was the president of the Constituent Assembly in 1946?",
        "What was the exchange rate of Indian rupee against US dollar in 1947?",
        # Hindi / Hinglish hard negatives
        "Bharat ke pehle pradhan mantri kaun the?",
        "Bharat ke pehle rashtrapati kaun the?",
        "India kis varsh azaad hua tha?",
        "Bharat ka samvidhan kab lagu hua tha?",
        "Pehla vishva yuddh kis varsh shuru hua tha?",
        "ISRO ki sthapna kis varsh hui thi?",
        "1983 ka cricket world cup kisne jeeta tha?",
        "Bharat me pehli train kab chali thi?",
        "Mahatma Gandhi ka janm kab hua tha?",
        "Pehla upagrah Aryabhata kab launch kiya gaya tha?",
        "Congress party ki sthapna kab hui thi?",
        "Bharat ratna sabse pehle kise mila tha?",
        "Quit India movement kis saal shuru hua tha?",
        "Pehli baar Chandrama par insaan kab gaya tha?",
        "2011 ka world cup final kis stadium me khela gaya tha?",
        "Harit kranti ke janak kaun the Bharat mein?",
        "Ancient India me Takshashila kahan sthit tha?",
        "Mughal samrajya ka sansthapak kaun tha?"
    ]

    agri_hard_negatives = [
        "What was the history of the Green Revolution in India in the 1960s?",
        "Who was known as the father of Green Revolution in India?",
        "How has drip irrigation historically evolved in arid regions?",
        "When was the Indian Council of Agricultural Research (ICAR) founded?",
        "What is the botanical history of wheat domestication?",
        "Ancient agricultural practices used in the Indus Valley Civilization",
        "Who introduced chemical fertilizers to Indian agriculture in the 20th century?",
        "When was the first agriculture university established in Pantnagar in 1960?",
        "Bharat mein harit kranti ke janak kaun mane jate hain?",
        "ICAR ki sthapna kis varsh hui thi?",
        "Prachin Bharat mein krishi ki kya padhhati thi?"
    ]

    math_hard_negatives = [
        "If a train started 3 hours ago at 60 km/h, what distance did it cover?",
        "What is the mathematical formula for compound interest after t years?",
        "Calculate the speed when distance is 150 km and time is 2.5 hours.",
        "A car took 4 hours to complete a journey. Find the average velocity.",
        "If yesterday was Tuesday, what day was it 45 days ago?",
        "5 saal me 10000 rupaye par 8% ki dar se simple interest kitna hoga?",
        "Ek train 4 ghante me 240 km chalti hai, uski speed kya hai?"
    ]

    print(f"Generated {len(gk_hard_negatives)} GK hard negatives, {len(agri_hard_negatives)} Agri hard negatives, {len(math_hard_negatives)} Math hard negatives.")
    return gk_hard_negatives, agri_hard_negatives, math_hard_negatives

def main():
    print("=" * 65)
    print("  OMEGA Realtime Intent Dataset Generation")
    print("=" * 65)

    realtime_samples = generate_realtime_examples()
    gk_hn, agri_hn, math_hn = generate_hard_negatives()

    # Load existing train and held-out test splits
    base_train_path = os.path.join(CURRENT_DIR, "..", "..", "ml_service", "data", "intent_train.json")
    base_test_path = os.path.join(CURRENT_DIR, "..", "..", "ml_service", "data", "intent_held_out_test.json")

    with open(base_train_path, "r", encoding="utf-8") as f:
        existing_train = json.load(f)
    with open(base_test_path, "r", encoding="utf-8") as f:
        existing_test = json.load(f)

    print(f"Existing train size: {len(existing_train)}, test size: {len(existing_test)}")

    # Cluster-based partitioning for realtime samples (Zero cluster overlap)
    cluster_groups = defaultdict(list)
    for text in realtime_samples:
        key = get_cluster_key(text, "realtime")
        cluster_groups[key].append(text)

    all_keys = list(cluster_groups.keys())
    random.shuffle(all_keys)

    # 80/20 train/test cluster split
    split_idx = int(0.80 * len(all_keys))
    train_keys = set(all_keys[:split_idx])
    test_keys = set(all_keys[split_idx:])

    realtime_train = []
    realtime_test = []

    for k in train_keys:
        for t in cluster_groups[k]:
            realtime_train.append({"text": t, "intent": "realtime"})
    for k in test_keys:
        for t in cluster_groups[k]:
            realtime_test.append({"text": t, "intent": "realtime"})

    print(f"Realtime Partitioning:")
    print(f"  Total clusters: {len(all_keys)} (Train clusters: {len(train_keys)}, Test clusters: {len(test_keys)})")
    print(f"  Cluster overlap: {len(train_keys.intersection(test_keys))}")
    print(f"  Realtime train samples: {len(realtime_train)}, test samples: {len(realtime_test)}")

    # Add Hard Negatives to train and test
    random.shuffle(gk_hn)
    gk_split = int(0.75 * len(gk_hn))
    for t in gk_hn[:gk_split]:
        existing_train.append({"text": t, "intent": "gk"})
    for t in gk_hn[gk_split:]:
        existing_test.append({"text": t, "intent": "gk"})

    for t in agri_hn[:int(0.75 * len(agri_hn))]:
        existing_train.append({"text": t, "intent": "agriculture"})
    for t in agri_hn[int(0.75 * len(agri_hn)):]:
        existing_test.append({"text": t, "intent": "agriculture"})

    for t in math_hn[:int(0.75 * len(math_hn))]:
        existing_train.append({"text": t, "intent": "math"})
    for t in math_hn[int(0.75 * len(math_hn)):]:
        existing_test.append({"text": t, "intent": "math"})

    # Combine datasets
    new_train = existing_train + realtime_train
    new_test = existing_test + realtime_test

    random.shuffle(new_train)
    random.shuffle(new_test)

    # Save to omega/realtime/data/
    out_train_path = os.path.join(DATA_DIR, "intent_train_v3.json")
    out_test_path = os.path.join(DATA_DIR, "intent_held_out_test_v3.json")

    with open(out_train_path, "w", encoding="utf-8") as f:
        json.dump(new_train, f, indent=2, ensure_ascii=False)
    with open(out_test_path, "w", encoding="utf-8") as f:
        json.dump(new_test, f, indent=2, ensure_ascii=False)

    print(f"\nFinal Dataset Statistics:")
    print(f"  Total Train Samples: {len(new_train):,}")
    print(f"    Train distribution: {Counter(r['intent'] for r in new_train)}")
    print(f"  Total Test Samples: {len(new_test):,}")
    print(f"    Test distribution: {Counter(r['intent'] for r in new_test)}")
    print(f"  Saved train data to: {out_train_path}")
    print(f"  Saved test data to:  {out_test_path}")

    # Also save dedicated test suite of 50 static GK queries for hard negative verification
    gk_test_sample = [r["text"] for r in new_test if r["intent"] == "gk"]
    static_gk_test_file = os.path.join(DATA_DIR, "static_gk_eval_50.json")
    random.seed(123)
    eval_gk_50 = random.sample(gk_test_sample, min(50, len(gk_test_sample)))
    with open(static_gk_test_file, "w", encoding="utf-8") as f:
        json.dump(eval_gk_50, f, indent=2, ensure_ascii=False)
    print(f"  Saved 50 static GK evaluation samples to: {static_gk_test_file}")

if __name__ == "__main__":
    main()
