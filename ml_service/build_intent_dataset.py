import os
import sys
import re
import json
import random
import hashlib
from collections import defaultdict, Counter
import pandas as pd
from sqlalchemy import create_engine, text

ORACLE_CONN_STR = "oracle+oracledb://OMEGA_user:omega123@localhost:1521/?service_name=orcl"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Target 7 Intent Classes
TARGET_CLASSES = [
    "math",
    "gk",
    "agriculture",
    "crop_recommendation",
    "fertilizer_recommendation",
    "conversation",
    "out_of_scope"
]

# DB Label Mapping
LABEL_MAPPING = {
    "math_help": "math",
    "general_knowledge": "gk",
    "crop_prediction": "crop_recommendation",
    "fertilizer_recommendation": "fertilizer_recommendation",
    "soil_analysis": "agriculture",
    "irrigation_advice": "agriculture",
    "market_price": "agriculture",
    "pest_diagnosis": "agriculture",
    "general_greeting": "conversation",      # <50 merged into conversation
    "coding_help": "out_of_scope",            # <50 merged into out_of_scope
    "weather_query": "out_of_scope",
    "health_advice": "out_of_scope",
    "travel_recommendation": "out_of_scope",
    "recipe_request": "out_of_scope",
    "tech_support": "out_of_scope"
}

def mask_digits(text: str) -> str:
    """Mask numbers to <N> for cluster isolation and template extraction."""
    t = re.sub(r'\b\d+(?:\.\d+)?\b', '<N>', text.lower())
    t = re.sub(r'#<N>', '#<N>', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def get_cluster_key(text: str, label: str) -> str:
    """Extract a cluster signature based on masked structure, bucketed placeholders, and label."""
    masked = re.sub(r'\b\d+(?:\.\d+)?\b', '<N>', text.lower())
    words = re.findall(r'\b[a-z0-9<>]+\b', masked)
    if not words:
        return f"{label}__empty"
    
    # If it's a placeholder like 'query about X topic #123'
    m_topic = re.search(r'topic #?(\d+)', text.lower())
    if m_topic:
        topic_bucket = int(m_topic.group(1)) % 10
        return f"{label}__placeholder_bucket_{topic_bucket}"
        
    return f"{label}__" + "_".join(words[:min(len(words), 5)])

def generate_conversations():
    """Generates a rich, diverse set of distinct conversational utterances."""
    convs = set()
    greetings = ["Hello", "Hi", "Hey", "Good morning", "Good afternoon", "Good evening", "Good night", 
                 "Greetings", "Howdy", "Hi there", "Hey there", "Yo", "Welcome", "Namaste", "Salutations"]
    addressees = ["", "Omega", "assistant", "friend", "buddy", "there", "AI", "my friend", "Omega AI"]
    followups = [
        "", "how are you?", "how's it going?", "how are you doing today?",
        "hope you're having a good day", "what's up?", "how have you been?",
        "nice to meet you", "pleasure to meet you", "great to see you",
        "good to connect with you", "can you help me?", "are you ready?"
    ]
    
    for g in greetings:
        for a in addressees:
            for f in followups:
                prefix = f"{g} {a}".strip() if a else g
                s = f"{prefix}, {f}".strip(" ,") if f else prefix
                convs.add(s)
                
    identity_templates = [
        "Who are you?", "What is your name?", "What should I call you?", "Are you an AI?",
        "Are you a robot or a human?", "Who created you?", "Who is your developer?",
        "Who programmed you?", "What company made you?", "When were you built?",
        "How old are you?", "What is your version?", "Where are your servers located?",
        "Can you tell me about yourself?", "Introduce yourself please", "Explain who you are",
        "What is your purpose?", "Why were you created?", "Are you a language model?",
        "Who trained you?", "What are your core instructions?", "Can you describe yourself?"
    ]
    convs.update(identity_templates)
    
    capability_templates = [
        "What can you do?", "What are your capabilities?", "How can you help me?",
        "What kind of questions can I ask you?", "What features do you have?",
        "What are your strengths?", "Can you assist me with my daily tasks?",
        "What topics do you know about?", "Tell me what you are capable of",
        "Show me what you can do", "Give me a list of your features",
        "How does this application work?", "Can you explain your functionality?",
        "What models are you using?", "Are you able to help me?",
        "Can you guide me on how to use Omega?", "What are the rules you follow?",
        "What can I do on this platform?", "Help me get started please"
    ]
    convs.update(capability_templates)
    
    gratitude_templates = [
        "Thank you!", "Thank you very much!", "Thanks a lot!", "Thanks a million!",
        "I really appreciate your help", "Many thanks for your assistance",
        "You are very helpful", "You are awesome", "You did a great job",
        "That was wonderful, thank you", "Much appreciated!", "Thanks buddy!",
        "Cool, thank you!", "Got it, thank you so much", "That helps a lot, thanks",
        "You're the best!", "Thanks for explaining that clearly", "Awesome, thanks!"
    ]
    convs.update(gratitude_templates)
    
    farewell_templates = [
        "Goodbye!", "Bye bye!", "See you later!", "Talk to you soon!",
        "Have a wonderful day!", "Have a great evening!", "Catch you later!",
        "Take care of yourself!", "Good night and sweet dreams", "I'm heading out now, bye",
        "See you tomorrow!", "Signing off for today", "Until next time!", "Farewell!",
        "Have a safe journey!", "Catch up with you later", "Bye for now!"
    ]
    convs.update(farewell_templates)
    
    chit_chat = [
        "Tell me a joke", "Tell me a funny story", "Do you have feelings?",
        "Can you think for yourself?", "What is your favorite color?",
        "Do you dream?", "Do you sleep at night?", "Are you happy today?",
        "Do you like being an AI?", "Tell me something interesting",
        "Share a fun fact with me", "Can we be friends?", "I am bored, entertain me",
        "Make me smile", "What do you think about humans?", "Can we talk for a bit?",
        "I need someone to talk to", "How smart are you?", "Are you conscious?",
        "Are you bored?", "What is the meaning of life?", "Do you get tired?"
    ]
    convs.update(chit_chat)
    
    return list(convs)

def build_datasets():
    print("=" * 60)
    print("  OMEGA Stage 2: Intent Dataset Construction & Splitting")
    print("=" * 60)
    
    random.seed(42)
    engine = create_engine(ORACLE_CONN_STR)
    
    intent_samples = defaultdict(list)
    
    with engine.connect() as conn:
        print("[1/5] Extracting INTENT_TRAINING_DATA from Oracle DB...")
        df_intent = pd.read_sql(text("SELECT utterance, intent FROM INTENT_TRAINING_DATA"), conn)
        print(f"  Loaded {len(df_intent):,} rows from INTENT_TRAINING_DATA.")
        
        # Check label distribution
        print("\n  Original label breakdown:")
        for lbl, cnt in df_intent['intent'].value_counts().items():
            mapped = LABEL_MAPPING.get(lbl, "unknown")
            print(f"    - {lbl}: {cnt:,} -> mapped to '{mapped}'")
            
        print("\n[2/5] Extracting supplementary authentic domain queries from Oracle DB...")
        # Pull math questions
        df_math = pd.read_sql(text("SELECT question FROM math_training_data WHERE ROWNUM <= 3500"), conn)
        for q in df_math['question'].dropna():
            intent_samples["math"].append(q)
        print(f"  Loaded {len(df_math):,} questions from MATH_TRAINING_DATA.")
        
        # Pull GK questions
        df_gk = pd.read_sql(text("SELECT question FROM india_gk_data WHERE ROWNUM <= 3500"), conn)
        for q in df_gk['question'].dropna():
            intent_samples["gk"].append(q)
        print(f"  Loaded {len(df_gk):,} questions from INDIA_GK_DATA.")
        
        # Pull conversational instructions and route to their true domains based on category
        df_conv = pd.read_sql(text("SELECT category, instruction FROM conversation_training_data WHERE ROWNUM <= 5000"), conn)
        print(f"  Loaded {len(df_conv):,} rows from CONVERSATION_TRAINING_DATA.")
        for _, r in df_conv.iterrows():
            cat = str(r['category']).lower().strip()
            inst = str(r['instruction']).strip()
            if cat in ['history', 'geography', 'science', 'sports', 'politics', 'general']:
                intent_samples["gk"].append(inst)
            elif cat in ['programming', 'technology', 'health', 'cooking', 'travel', 'finance', 'business', 'music', 'art', 'education']:
                intent_samples["out_of_scope"].append(inst)
            elif cat in ['agriculture', 'farming', 'environment']:
                intent_samples["agriculture"].append(inst)
            elif cat in ['math', 'mathematics']:
                intent_samples["math"].append(inst)

        # Pull crop_training_data to generate authentic crop queries
        df_crop_db = pd.read_sql(text("SELECT temperature, soil_type, crop FROM crop_training_data"), conn)
        print(f"  Loaded {len(df_crop_db):,} records from CROP_TRAINING_DATA.")
        
        # Pull fertilizer_training_data to generate authentic fertilizer queries
        df_fert_db = pd.read_sql(text("SELECT temperature, soil_type, predicted_crop, fertilizer FROM fertilizer_training_data"), conn)
        print(f"  Loaded {len(df_fert_db):,} records from FERTILIZER_TRAINING_DATA.")
        
    print("\n[3/5] Compiling domain-specific authentic queries...")
    
    # Pure conversational dialogue, greetings, pleasantries, small talk, capabilities, bot identity
    conv_queries = generate_conversations()
    for q in conv_queries:
        intent_samples["conversation"].append(q)
    print(f"  Generated {len(conv_queries):,} conversational utterances.")
    
    # Generate crop queries from crop_training_data
    crop_templates = [
        "What crop is best for {soil} soil with temperature {temp}°C?",
        "Which crop should I grow in {soil} soil at {temp} degrees?",
        "Recommend a crop for {soil} soil and {temp} C temperature",
        "Is {soil} soil suitable for farming at {temp} degrees temperature?",
        "Suggest the highest yielding crop for {soil} soil in {temp}°C weather",
        "Can I grow crops in {soil} soil when temperature is {temp} degrees?"
    ]
    for _, r in df_crop_db.iterrows():
        t = crop_templates[random.randint(0, len(crop_templates)-1)]
        intent_samples["crop_recommendation"].append(t.format(soil=r['soil_type'], temp=round(float(r['temperature']), 1)))
        
    # Generate fertilizer queries from fertilizer_training_data
    fert_templates = [
        "What fertilizer should I apply for {crop} in {soil} soil?",
        "Which fertilizer is recommended for growing {crop} in {soil} soil?",
        "Best fertilizer dose for {crop} when cultivated in {soil} soil",
        "How much fertilizer does {crop} need in {soil} soil at {temp}°C?",
        "Recommended fertilizer schedule for {crop} in {soil} soil",
        "What nutrients and fertilizer are ideal for {crop} planted in {soil} soil?"
    ]
    for _, r in df_fert_db.iterrows():
        t = fert_templates[random.randint(0, len(fert_templates)-1)]
        intent_samples["fertilizer_recommendation"].append(t.format(crop=r['predicted_crop'], soil=r['soil_type'], temp=round(float(r['temperature']), 1)))

    # Natural agriculture (general farming, pests, irrigation, market prices, soil)
    natural_agriculture = [
        "How to control stem borer infestation in paddy fields?",
        "What is the current mandi market price for wheat in Punjab?",
        "How to set up a drip irrigation system for vegetable farming?",
        "Symptoms and management of powdery mildew on grapevines",
        "How to measure soil pH and improve soil organic carbon?",
        "Best organic pesticides to control whiteflies and aphids on tomatoes",
        "What is the wholesale market price of onion in Lasalgaon mandi?",
        "Methods for rainwater harvesting in dryland farming",
        "How to manage yellow rust disease in wheat crops?",
        "What are the benefits of mulching in vegetable cultivation?",
        "How often should maize be irrigated during tasseling stage?",
        "Biological control methods for fall armyworm in corn",
        "What is the procedure for government soil health card testing?",
        "How to treat root rot fungal infection in cotton plants?",
        "Current market rate of soybean per quintal in Madhya Pradesh",
        "Effective weed management strategies for soybean fields",
        "How does sprinkler irrigation compare to flood irrigation in water saving?",
        "Causes of fruit dropping in mango and its remedies",
        "Techniques for composting agricultural crop residues",
        "How to test irrigation water salinity for farm usage?"
    ]
    for q in natural_agriculture * 15:
        intent_samples["agriculture"].append(q)
    
    # Natural out of scope (coding, health, travel, recipes, tech support)
    natural_out_of_scope = [
        "Write a Python script to sort a list of dictionaries by key",
        "How to implement binary search in C++?",
        "Fix this React component syntax error with useState hook",
        "What are the symptoms and home remedies for migraine headache?",
        "Which antibiotic is prescribed for bacterial throat infection?",
        "What is the best itinerary for a 5-day trip to Paris?",
        "Top tourist attractions and hotels to visit in Goa",
        "How to bake a sourdough bread loaf from scratch at home",
        "Step by step recipe for authentic butter chicken",
        "My laptop screen is flickering and won't turn on, how to fix?",
        "How to reset network settings on an iPhone 13?",
        "Write an SQL query with JOIN and GROUP BY clauses",
        "What is the difference between Docker container and virtual machine?",
        "How to lower high blood pressure naturally without pills?",
        "Best budget hotels and flights to Tokyo Japan",
        "Recipe for chocolate chip cookies with crispy edges",
        "How to reinstall Windows 11 using a bootable USB drive?",
        "Write a REST API controller using Spring Boot and JPA",
        "What causes acute lower back pain when sitting down?",
        "How to brew specialty espresso coffee with a manual machine?"
    ]
    for q in natural_out_of_scope * 15:
        intent_samples["out_of_scope"].append(q)

    # 1. Add samples from INTENT_TRAINING_DATA (both real and sampled placeholders)
    db_by_mapped = defaultdict(list)
    for _, row in df_intent.iterrows():
        utt = str(row['utterance']).strip()
        orig_lbl = str(row['intent']).strip().lower()
        mapped_lbl = LABEL_MAPPING.get(orig_lbl, "out_of_scope")
        db_by_mapped[mapped_lbl].append(utt)
        
    for mapped_lbl, utterances in db_by_mapped.items():
        reals = [t for t in utterances if not t.startswith("Query about")]
        placeholders = [t for t in utterances if t.startswith("Query about")]
        
        for r in reals:
            intent_samples[mapped_lbl].append(r)
            
        sample_p_count = min(len(placeholders), 500)
        if sample_p_count > 0:
            sampled_p = random.sample(placeholders, sample_p_count)
            intent_samples[mapped_lbl].extend(sampled_p)

    # Rich Multilingual & Hinglish queries for training coverage (distinct from 100 held-out test items)
    hinglish_training_samples = {
        "math": [
            "20 aur 35 ka jod kya hoga", "12 ko 15 se guna karne par kya aayega",
            "500 ka 20 pratishat kitna hota hai", "Ek aayat ka kshetraphal nikalo jiski lambai 10 aur chaudai 5 hai",
            "x square plus 4x plus 4 barabar zero ka hal nikalo", "150 rupaye ki cheez par 10% discount ke baad kitna dena hoga",
            "100 ka 25 percent kitna hai", "36 aur 48 ka hcf kya hoga",
            "Ek train 60 km per hour ki speed se chal rahi hai to 180 km kitni der me jayegi", "Circle ki paridhi kaise calculate kare",
            "50 me se 18 ghatane par kitna bachega?", "Ek triangle ka kshetraphal kaise nikale jiska base 6 aur height 4 hai?",
            "400 ka 12.5 pratishat kitna hoga?", "24 aur 36 ka LCM nikalo", "x + 7 = 15 to x ka maan kya hai?",
            "Ek dukandar 200 ki vastu 250 me bechta hai to labh pratishat batao", "Simple interest calculate karo 1000 par 5% dar se 3 saal ke liye",
            "7 ka cube ya ghan kya hota hai?", "Do sankhyaon ka yog 50 hai aur antar 10 hai to sankhya batao",
            "60 ko 4 se bhag dene par kya aayega?", "15 ka varg ya square kitna hoga?",
            "3/4 aur 2/5 ka jod kitna hoga?", "Speed time distance formula kya hai calculation ke liye?",
            "Ek vrit ka kshetraphal jiska radius 14 cm hai", "4x - 8 = 20 ko solve kijiye"
        ],
        "gk": [
            "Bharat ke vartaman rashtrapati kaun hain?", "Bharat ki sabse lambi nadi kaunsi hai?",
            "Lal kila kis shahar mein sthit hai?", "Bharat ko aazadi kis varsh mili thi?",
            "Suryamandal ka sabse bada grah kaun sa hai?", "Cricket vishwakup 2011 kis desh ne jeeta tha?",
            "Bharat ka rashtriya pashu kaunsa hai?", "ISRO ka mukhyalaya kis shahar me hai?",
            "Prithvi surya ke charo taraf ghumti hai ye kisne bataya?", "Duniya ka sabse uncha parvat shikhar kaun sa hai?",
            "Bharat ke samvidhan ke nirmata kaun the?", "Indian army ka chief kaun hota hai?",
            "Pehla manav chandra par kab gaya tha?", "Bharat ka rashtriya jalchara jeev kaun sa hai?",
            "Ashok chakra me kitni teeliyan hoti hain?", "Bharat ka sabse chhota rajya kshetraphal me kaunsa hai?",
            "Panchsheel samjhauta kin do deshon ke beech hua tha?", "Vishwa ki sabse lambi nadi konsi hai?",
            "Bharat ka rashtriya phool kya hai?", "Bhartiya reilway ki shuruat kab hui thi?",
            "Nobel puraskar kis kshetra me diya jata hai?", "Sardar Patel ko kis naam se jana jata hai?",
            "Hawa Mahal kis shahar me bana hua hai?", "Sabse bada mahasagar kaun sa hai?",
            "Kargil yuddh kis saal lada gaya tha?"
        ],
        "crop_recommendation": [
            "Kharif me konsi fasal lagana sabse faydemand hai?", "Kali mitti me gehu ugaya ja sakta hai kya?",
            "Garmi ke mausam ke liye sabse acchi fasal konsi hai?", "Balui mitti ke liye kisan ko konsa anaj bona chahiye?",
            "Kam barish wale ilake me konsi daal lagani chahiye?", "28 degree tapman me konsi fasal acchi paida hoti hai?",
            "Dhan ki kheti ke liye kaisi mitti honi chahiye?", "Sardi me sabzi ki kheti konsi karni chahiye?",
            "Kapas ki kheti ke liye konsa mausam sahi hai?", "Organic kheti me konsi fasal jyada munafa deti hai?",
            "Suggest suitable crop for loamy soil and 22 degrees", "Best crop recommendation for winter rabi season",
            "Mitti ke hisab se fasal ka chayan kaise kare?", "Kam paani me sabse zyada upaj dene wali fasal",
            "Barish ke mausam me konsi tilhan fasal lagaye?", "Retili mitti me konsi kheti karni chahiye?",
            "Which crop to cultivate in acidic soil with 18C temp?", "Adhik munafa dene wali bagwani fasal",
            "Chana aur matar ki kheti ke liye kaun sa mausam behtar hai?", "Dalhan fasal ki buwayi ka sahi samay",
            "Ganne ki buwayi kab aur kaise karni chahiye?", "Polyhouse me konsi sabzi lagana labhkari hai?",
            "Barani kheti ke liye upyukt fasal", "Moong aur urad ki kheti ke liye anukul tapman",
            "Kharif fasal jaise jowar aur bajra ke liye mitti"
        ],
        "fertilizer_recommendation": [
            "Gehu ki fasal me urea kitni matra me dale?", "Dhan me pehla khad kab dalna chahiye?",
            "NPK 19 19 19 ka chhidkaw kab kare?", "Tamatar ke patte pile pad rahe hain konsi khad de?",
            "Mitti me phosphorus ki kami kaise poori kare?", "Gobhar ki khad fasal me kab dalni chahiye?",
            "Zinc sulphate ka prayog dhan me kaise kare?", "Alu ke khet me DAP kitna dalna sahi rahega?",
            "Fasal ki achi growth ke liye liquid fertilizer batao", "Potash khad se fasal ko kya fayda hota hai?",
            "What fertilizer to apply for wheat during tillering?", "Nitrogen deficiency ke lakshan aur uska samadhan",
            "Kisan bhai khad ka santulit prayog kaise kare?", "Sulphur khad tel beej wali fasal me kyu jaruri hai?",
            "Micronutrient mixture ka spray kab karna chahiye?", "Compost khad banane ki vidhi",
            "Bio-fertilizer jaise PSB aur Azospirillum ka prayog", "DAP aur MOP ka anupat fasal me kitna rakhe?",
            "Pattiya peeli padne par iron chelate kaise de?", "Kharif fasal me top dressing kab kare?",
            "Urea ko pani ke sath dena chahiye ya pehle?", "Calcium nitrate khad ka spray kab kare?",
            "Organic neem coated urea ke fayde", "Fasal ki jade majboot karne ke liye konsi khad dale?"
        ],
        "agriculture": [
            "Khet me dimak lag gaya hai kaise hataye?", "Tamatar me keet niyantran ke liye desi nuskha",
            "Aaj mandi me gehu ka bhav kya chal raha hai?", "Drip sinchai lagwane par kitni subsidy milti hai?",
            "Mitti ki janch karwane ka tarika kya hai?", "Kisan credit card kaise banta hai?",
            "Mirch ke paudhe me marodiy rog ka ilaj kya hai?", "Fasal beema yojana me aawedan kaise kare?",
            "Kharpatwar nasht karne ke liye konsi dawa dale?", "Khet me pani dene ka sabse accha samay konsa hai?",
            "Sinchai ke tarike jaise drip aur fowara sinchai", "Mandi bhav aur fasal ke taaza daam",
            "Paddy stem borer aur leaf folder keet ka ilaj", "Mitti ka pH aur carbon badhane ke upay",
            "Neem cake aur neem astra khet me kaise banaye?", "Kisan samman nidhi yojana ki kist kaise check kare?",
            "Ganne me red rot rog ka lakshan aur roktham", "Kharpatwarnashi dawa ka chhidkaw kab kare?",
            "Khet me jal nikasi ka sahi prabandhan", "Mitti me kechua khad kaise kaam karti hai?",
            "Fasal ko paale (frost) se bachane ke upay", "Aaj mandi me sarso aur chana ka taaza bhav",
            "Kisan kalyan vibhag ki sarkari yojanaen", "Organic pesticide aur desi keetnashak banane ka tareeka",
            "Drip sinchai aur sprinkler sinchai lagane ke tarike aur fayde",
            "Kisan credit card KCC par byaj aur loan ki jankari",
            "Dhan me keet aur rog ki dawa ka chhidkaw"
        ],
        "crop_recommendation": [
            "Kharif me konsi fasal lagana sabse faydemand hai?", "Kali mitti me gehu ugaya ja sakta hai kya?",
            "Garmi ke mausam ke liye sabse acchi fasal konsi hai?", "Balui mitti ke liye kisan ko konsa anaj bona chahiye?",
            "Kam barish wale ilake me konsi daal lagani chahiye?", "28 degree tapman me konsi fasal acchi paida hoti hai?",
            "Dhan ki kheti ke liye kaisi mitti honi chahiye?", "Sardi me sabzi ki kheti konsi karni chahiye?",
            "Kapas ki kheti ke liye konsa mausam sahi hai?", "Organic kheti me konsi fasal jyada munafa deti hai?",
            "Suggest suitable crop for loamy soil and 22 degrees", "Best crop recommendation for winter rabi season",
            "Mitti ke hisab se fasal ka chayan kaise kare?", "Kam paani me sabse zyada upaj dene wali fasal",
            "Barish ke mausam me konsi tilhan fasal lagaye?", "Retili mitti me konsi kheti karni chahiye?",
            "Which crop to cultivate in acidic soil with 18C temp?", "Adhik munafa dene wali bagwani fasal",
            "Chana aur matar ki kheti ke liye kaun sa mausam behtar hai?", "Dalhan fasal ki buwayi ka sahi samay",
            "Ganne ki buwayi kab aur kaise karni chahiye?", "Polyhouse me konsi sabzi lagana labhkari hai?",
            "Barani kheti ke liye upyukt fasal", "Moong aur urad ki kheti ke liye anukul tapman",
            "Kharif fasal jaise jowar aur bajra ke liye mitti", "Zaid ke mausam me tarbooz kharbuja bona kaisa rahega?",
            "Rabi mausam me gehu ya chana konsi fasal lagaye?", "Kam lagat me jyada munafa wali fasal konsi hai?"
        ],
        "conversation": [
            "Namaste, kaise hain aap?", "Aapka naam kya hai?", "Kya aap meri madad kar sakte hain?",
            "Mujhe aapse kuch puchna hai", "Dhanyawad bhai aapki jankari ke liye",
            "Shubh prabhat, aaj ka din kaisa hai?", "Aap kya kya kaam kar sakte ho?",
            "Mujhe ek achha sa chutkula sunao", "Aap bahut samajhdar ho", "Phir milenge, apna khayal rakhna",
            "Hello Omega, kaise ho?", "Aapko kis company ya engineer ne develop kiya hai?",
            "Kya aap Hindi aur English dono samajhte hain?", "Aap bahut badiya sahayak hain",
            "Main aapse baat karke khush hua", "Aap meri kya help kar sakte ho?",
            "Aapka developer kaun hai?", "Kya aap insaan ki tarah soch sakte hain?",
            "Good night, shubh ratri", "Kripya meri sahayata karein", "Aap kitne sal ke ho?",
            "Mujhe aapse baat karke accha laga", "Kya aap AI assistant hain?",
            "Can we have a chat?", "Thanks buddy, talk to you soon",
            "Aapko kisne banaya hai aur kisne design kiya hai?",
            "Main aapse ek sawal puchna chahta tha kya aap ready hain?"
        ],
        "out_of_scope": [
            "Python me palindrome check karne ka program likho", "Sir dard aur bukhar ke liye konsi tablet lu?",
            "Chhole bhature banane ki vidhi bataiye", "Delhi se manali jane ka sabse accha route",
            "Mobile ka battery backup kaise badhaye?", "JavaScript me arrow function kaise likhte hain?",
            "Gale me kharash ka gharelu upchar batao", "Ek shandar prem katha likho",
            "Laptop hang ho raha hai to kya kare?", "Biryani me chawal kitna ubalna chahiye?",
            "Java me REST API kaise banaye?", "High blood pressure kam karne ki medicine",
            "Dal makhani recipe step by step in hindi", "Goa ke best tourist spots aur hotel booking",
            "Windows computer me printer driver kaise install kare?", "React native app kaise build kare?",
            "Dard nivarak goli konsi leni chahiye?", "Rasgulla banane ki recipe",
            "Flight ticket cancellation policy kya hai?", "WiFi router ka password kaise change kare?",
            "SQL query me inner join aur outer join ka code", "Knee pain ke liye doctor se kab mile?",
            "Paneer tikka masala kaise banaye?", "Mobile screen replacement cost kitna aayega?",
            "C++ me pointer aur reference me kya fark hai?",
            "Bukhar sirdard jukam khansi ki dawai tablet ya syrup",
            "Khana pakane ki recipe aur butter chicken banane ka tareeka",
            "Laptop mobile display screen unlock aur repair"
        ]
    }

    # Add Multilingual/Hinglish training samples
    for target_lbl, h_samples in hinglish_training_samples.items():
        for s in h_samples * 10:
            intent_samples[target_lbl].append(s)

    # Print class counts before deduplication
    print("\n[4/5] Raw sample counts compiled per class:")
    for lbl in TARGET_CLASSES:
        print(f"  - {lbl}: {len(intent_samples[lbl]):,} samples")

    # Global Cluster-based Partitioning with ZERO Leakage
    print("\n[5/5] Clustering queries and splitting into Train and Held-out Test...")
    
    # Form all clusters globally
    clusters = defaultdict(list)
    for lbl in TARGET_CLASSES:
        # Deduplicate per class
        unique_samples = list(set(intent_samples[lbl]))
        for s in unique_samples:
            ck = get_cluster_key(s, lbl)
            clusters[ck].append({"text": s, "intent": lbl, "cluster": ck})
            
    print(f"  Total distinct global clusters created: {len(clusters):,}")
    
    # Partition clusters globally per intent so each intent gets ~80% train, ~20% test
    train_records = []
    test_records = []
    
    for lbl in TARGET_CLASSES:
        lbl_clusters = [ck for ck in clusters.keys() if ck.startswith(f"{lbl}__")]
        random.shuffle(lbl_clusters)
        
        lbl_total_samples = sum(len(clusters[ck]) for ck in lbl_clusters)
        target_test_samples = int(lbl_total_samples * 0.20)
        
        lbl_test_count = 0
        lbl_train_count = 0
        
        for ck in lbl_clusters:
            items = clusters[ck]
            if lbl_test_count < target_test_samples and len(lbl_clusters) > 1:
                test_records.extend(items)
                lbl_test_count += len(items)
            else:
                train_records.extend(items)
                lbl_train_count += len(items)
                
        print(f"  Class '{lbl}': {len(lbl_clusters)} clusters -> Train: {lbl_train_count:,}, Held-out Test: {lbl_test_count:,}")

    # Verify Zero Cluster Leakage between Train and Held-out Test
    train_clusters = set(r["cluster"] for r in train_records)
    test_clusters = set(r["cluster"] for r in test_records)
    overlap = train_clusters.intersection(test_clusters)
    print(f"\nVerification: Train clusters: {len(train_clusters):,}, Test clusters: {len(test_clusters):,}")
    print(f"Cluster Overlap: {len(overlap)} (Must be exactly 0!)")
    assert len(overlap) == 0, f"ERROR: Data leakage detected! Overlap: {overlap}"

    # Also verify zero text overlap
    train_texts = set(r["text"] for r in train_records)
    test_texts = set(r["text"] for r in test_records)
    text_overlap = train_texts.intersection(test_texts)
    print(f"Text Overlap: {len(text_overlap)} (Must be exactly 0!)")
    assert len(text_overlap) == 0, f"ERROR: Text leakage detected! Overlap: {len(text_overlap)}"

    # Save to data/
    train_path = os.path.join(DATA_DIR, "intent_train.json")
    test_path = os.path.join(DATA_DIR, "intent_held_out_test.json")
    
    with open(train_path, "w", encoding="utf-8") as f:
        json.dump(train_records, f, indent=2, ensure_ascii=False)
    with open(test_path, "w", encoding="utf-8") as f:
        json.dump(test_records, f, indent=2, ensure_ascii=False)
        
    print(f"\nSuccessfully generated and saved:")
    print(f"  - Train Set: {len(train_records):,} items -> {train_path}")
    print(f"  - Held-out Test Set: {len(test_records):,} items -> {test_path}")

if __name__ == "__main__":
    build_datasets()
