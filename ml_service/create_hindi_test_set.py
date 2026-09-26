import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

test_set = [
    # ==========================================
    # 1. Math (15 queries)
    # ==========================================
    {"query": "45 aur 60 ka LCM kitna hoga?", "intent": "math", "language": "hinglish"},
    {"query": "solve karo: 3x + 12 = 36", "intent": "math", "language": "hinglish"},
    {"query": "800 rupaye ka 15 pratishat kitna hota hai?", "intent": "math", "language": "hinglish"},
    {"query": "agar 5 pen ki kimat 50 rupaye hai to 8 pen kitne ke aayenge?", "intent": "math", "language": "hinglish"},
    {"query": "ek aayat ki lambai 12 cm aur chaudai 8 cm hai, kshetraphal batao", "intent": "math", "language": "hinglish"},
    {"query": "what is 250 divided by 5 in hindi?", "intent": "math", "language": "hinglish"},
    {"query": "144 ka vargmool (square root) kya hai?", "intent": "math", "language": "hinglish"},
    {"query": "9 aur 12 ka GCD ya HCF nikalo", "intent": "math", "language": "hinglish"},
    {"query": "ek car 60 km/hr ki raftar se 3 ghante me kitni doori tay karegi?", "intent": "math", "language": "hinglish"},
    {"query": "5000 rupaye par 2 saal ke liye 10% sadharan byaj kitna hoga?", "intent": "math", "language": "hinglish"},
    {"query": "solve the equation 5x - 10 = 40", "intent": "math", "language": "hinglish"},
    {"query": "25 ko 16 se guna karne par kya aayega?", "intent": "math", "language": "hinglish"},
    {"query": "vrit ki trijya 7 cm hai to paridhi gyat kijiye", "intent": "math", "language": "hinglish"},
    {"query": "35 aur 70 ka anupat kya hoga?", "intent": "math", "language": "hinglish"},
    {"query": "1000 rupaye me 20% chhut ke baad kitne rupaye bachenge?", "intent": "math", "language": "hinglish"},

    # ==========================================
    # 2. General Knowledge (GK) (15 queries)
    # ==========================================
    {"query": "Bharat ke pratham pradhan mantri kaun the?", "intent": "gk", "language": "hinglish"},
    {"query": "Bharat ki rajdhani kahan hai?", "intent": "gk", "language": "hinglish"},
    {"query": "Taj Mahal kis shahar me sthit hai?", "intent": "gk", "language": "hinglish"},
    {"query": "Duniya ka sabse uncha parvat kaunsa hai?", "intent": "gk", "language": "hinglish"},
    {"query": "ISRO ka mukhyalaya kis shahar mein sthit hai?", "intent": "gk", "language": "hinglish"},
    {"query": "Bharat ka rashtriya geet kisne likha tha?", "intent": "gk", "language": "hinglish"},
    {"query": "Suryamandal ka sabse chhota grah kaun sa hai?", "intent": "gk", "language": "hinglish"},
    {"query": "Constitution of India kab lagu hua tha?", "intent": "gk", "language": "hinglish"},
    {"query": "Ganga nadi kahan se nikalti hai?", "intent": "gk", "language": "hinglish"},
    {"query": "Reserve Bank of India ka head office kahan hai?", "intent": "gk", "language": "hinglish"},
    {"query": "Bharat me kul kitne rajya aur kendrashasit pradesh hain?", "intent": "gk", "language": "hinglish"},
    {"query": "Nobel puraskar pane wale pehle bhartiya kaun the?", "intent": "gk", "language": "hinglish"},
    {"query": "Lal Bahadur Shastri ji ka samadhi sthal kahan hai?", "intent": "gk", "language": "hinglish"},
    {"query": "Vishwa Paryavaran Diwas kab manaya jata hai?", "intent": "gk", "language": "hinglish"},
    {"query": "Bharat ki mudra kya hai?", "intent": "gk", "language": "hinglish"},

    # ==========================================
    # 3. Agriculture (General Farming, Pests, Mandi, Soil, Irrigation) (15 queries)
    # ==========================================
    {"query": "Tamatar ke paudhe me keede lag gaye hain kya kare?", "intent": "agriculture", "language": "hinglish"},
    {"query": "Aaj mandi me gehu ka bhav kya chal raha hai?", "intent": "agriculture", "language": "hinglish"},
    {"query": "Drip sinchai lagane ke kya fayde hain?", "intent": "agriculture", "language": "hinglish"},
    {"query": "Mitti ki janch (soil test) kahan aur kaise karwaye?", "intent": "agriculture", "language": "hinglish"},
    {"query": "Dhan ki fasal me tana chhedak keet ka ilaj kya hai?", "intent": "agriculture", "language": "hinglish"},
    {"query": "Sprinkler sinchai aur drip sinchai me kya antar hai?", "intent": "agriculture", "language": "hinglish"},
    {"query": "Kisan Credit Card par byaj dar kitni hoti hai?", "intent": "agriculture", "language": "hinglish"},
    {"query": "Mitti ka pH level kaise sudhare agar mitti amliya ho?", "intent": "agriculture", "language": "hinglish"},
    {"query": "Fasal me kharpatwar niyantran ke liye konsi dawa dale?", "intent": "agriculture", "language": "hinglish"},
    {"query": "Kapas me safed makhi (whitefly) ka desi upchar kya hai?", "intent": "agriculture", "language": "hinglish"},
    {"query": "Neem ke tel ka chhidkaw khet me kaise kare?", "intent": "agriculture", "language": "hinglish"},
    {"query": "Aaj pyaj ka thok mandi bhav kya hai?", "intent": "agriculture", "language": "hinglish"},
    {"query": "Khet me organic kheti shuru karne ka sahi tarika", "intent": "agriculture", "language": "hinglish"},
    {"query": "Rainwater harvesting khet me kaise banaye?", "intent": "agriculture", "language": "hinglish"},
    {"query": "Fasal beema claim karne ke liye kin dastavejon ki jarurat hoti hai?", "intent": "agriculture", "language": "hinglish"},

    # ==========================================
    # 4. Crop Recommendation (15 queries)
    # ==========================================
    {"query": "Kali mitti me konsi fasal lagana sabse achha hota hai?", "intent": "crop_recommendation", "language": "hinglish"},
    {"query": "Sardi ke mausam me kisan ko konsi fasal boni chahiye?", "intent": "crop_recommendation", "language": "hinglish"},
    {"query": "Kam pani wale ilake me konsi daal ya anaj ugaye?", "intent": "crop_recommendation", "language": "hinglish"},
    {"query": "25 degree tapman aur loamy soil me kaun si fasal acchi hogi?", "intent": "crop_recommendation", "language": "hinglish"},
    {"query": "Balui retili mitti ke liye konsi cash crop suitable hai?", "intent": "crop_recommendation", "language": "hinglish"},
    {"query": "Kharif season ke liye sabse jyada munafa dene wali fasal kaun si hai?", "intent": "crop_recommendation", "language": "hinglish"},
    {"query": "Pahadi ilake me kis fal ya fasal ki kheti karni chahiye?", "intent": "crop_recommendation", "language": "hinglish"},
    {"query": "Alluvial soil me gehu ke baad konsi fasal lagaye crop rotation me?", "intent": "crop_recommendation", "language": "hinglish"},
    {"query": "Lal mitti me groundnut ki kheti ho sakti hai kya?", "intent": "crop_recommendation", "language": "hinglish"},
    {"query": "32 degree garmi me konsi sabzi lagana faydemand hai?", "intent": "crop_recommendation", "language": "hinglish"},
    {"query": "Suggest the best crop for clayey soil in rainy season", "intent": "crop_recommendation", "language": "hinglish"},
    {"query": "Zaid ke mausam me tarbooz aur kharbuja lagana kaisa rahega?", "intent": "crop_recommendation", "language": "hinglish"},
    {"query": "Laterite soil ke liye kaun sa bagwani crop best hai?", "intent": "crop_recommendation", "language": "hinglish"},
    {"query": "Dhan ke khet ke baad rabi me kya lagana chahiye?", "intent": "crop_recommendation", "language": "hinglish"},
    {"query": "Kisan bhaiyo ke liye kam lapat me zyada kamai wali fasal", "intent": "crop_recommendation", "language": "hinglish"},

    # ==========================================
    # 5. Fertilizer Recommendation (15 queries)
    # ==========================================
    {"query": "Gehu ki fasal me urea kitni matra me dalna chahiye?", "intent": "fertilizer_recommendation", "language": "hinglish"},
    {"query": "Dhan me DAP aur Urea ka sahi ratio kya hona chahiye?", "intent": "fertilizer_recommendation", "language": "hinglish"},
    {"query": "NPK 19 19 19 khad ka prayog kab aur kaise kare?", "intent": "fertilizer_recommendation", "language": "hinglish"},
    {"query": "Paudhon me nitrogen ki kami ke lakshan aur uski khad", "intent": "fertilizer_recommendation", "language": "hinglish"},
    {"query": "Alu ki fasal me tubers badhane ke liye konsa fertilizer dale?", "intent": "fertilizer_recommendation", "language": "hinglish"},
    {"query": "Potash khad ka chhidkaw fasal me kab karna labhkari hota hai?", "intent": "fertilizer_recommendation", "language": "hinglish"},
    {"query": "Gobar ki sadi khad khet me kitne quintal per acre dalni chahiye?", "intent": "fertilizer_recommendation", "language": "hinglish"},
    {"query": "Sugarcane me pehla fertilizer dose kitne din baad de?", "intent": "fertilizer_recommendation", "language": "hinglish"},
    {"query": "Mitti me zinc aur iron ki kami door karne ke liye konsi khad dale?", "intent": "fertilizer_recommendation", "language": "hinglish"},
    {"query": "Vermicompost khad ke prayog se paudho ko kya fayda hota hai?", "intent": "fertilizer_recommendation", "language": "hinglish"},
    {"query": "Chana ki fasal me superphosphate kitna dalna chahiye?", "intent": "fertilizer_recommendation", "language": "hinglish"},
    {"query": "Tamatar me phool aate samay konsa micronutrient spray kare?", "intent": "fertilizer_recommendation", "language": "hinglish"},
    {"query": "Sarso ki fasal me sulfur fertilizer kitna dalna jaruri hai?", "intent": "fertilizer_recommendation", "language": "hinglish"},
    {"query": "Biofertilizer jaise Rhizobium culture ka beej upchar kaise kare?", "intent": "fertilizer_recommendation", "language": "hinglish"},
    {"query": "Recommended fertilizer dose for cotton crop in black soil", "intent": "fertilizer_recommendation", "language": "hinglish"},

    # ==========================================
    # 6. Conversation (15 queries)
    # ==========================================
    {"query": "Namaste, aap kaise hain?", "intent": "conversation", "language": "hinglish"},
    {"query": "Hello bhai, kya haal chaal hai?", "intent": "conversation", "language": "hinglish"},
    {"query": "Tumhara naam kya hai aur tum kya kar sakte ho?", "intent": "conversation", "language": "hinglish"},
    {"query": "Kya aap meri thodi madad kar sakte hain?", "intent": "conversation", "language": "hinglish"},
    {"query": "Aapko kisne banaya hai?", "intent": "conversation", "language": "hinglish"},
    {"query": "Shubh prabhat! Aaj ka din shubh ho", "intent": "conversation", "language": "hinglish"},
    {"query": "Bahut bahut dhanyawad aapki sahayata ke liye", "intent": "conversation", "language": "hinglish"},
    {"query": "Aap kaun si bhasha bol sakte ho?", "intent": "conversation", "language": "hinglish"},
    {"query": "Mujhe ek hasane wala chutkula sunao", "intent": "conversation", "language": "hinglish"},
    {"query": "Aap bot ho ya insaan?", "intent": "conversation", "language": "hinglish"},
    {"query": "Alvida, baad me baat karte hain", "intent": "conversation", "language": "hinglish"},
    {"query": "Kya hum dost ban sakte hain?", "intent": "conversation", "language": "hinglish"},
    {"query": "Aap bahut acche se jawab dete ho", "intent": "conversation", "language": "hinglish"},
    {"query": "Main ek sawal puchna chahta tha", "intent": "conversation", "language": "hinglish"},
    {"query": "Hey Omega, help me please", "intent": "conversation", "language": "hinglish"},

    # ==========================================
    # 7. Out of Scope (10 queries)
    # ==========================================
    {"query": "Python me list ko sort karne ka code likhiye", "intent": "out_of_scope", "language": "hinglish"},
    {"query": "Mujhe do din se sir dard aur bukhar hai, konsi dawai lu?", "intent": "out_of_scope", "language": "hinglish"},
    {"query": "Ghar par chicken biryani banane ki simple recipe batao", "intent": "out_of_scope", "language": "hinglish"},
    {"query": "Goa ghumne ke liye saste hotels aur package kahan milenge?", "intent": "out_of_scope", "language": "hinglish"},
    {"query": "Laptop ki screen black ho gayi hai, start nahi ho raha", "intent": "out_of_scope", "language": "hinglish"},
    {"query": "React me useEffect hook kaise kaam karta hai?", "intent": "out_of_scope", "language": "hinglish"},
    {"query": "Khansi aur gale me jalan ke liye best syrup", "intent": "out_of_scope", "language": "hinglish"},
    {"query": "Paneer butter masala banane ka tareeka kya hai?", "intent": "out_of_scope", "language": "hinglish"},
    {"query": "Delhi se Shimla jane ke liye train ticket kaise book kare?", "intent": "out_of_scope", "language": "hinglish"},
    {"query": "Mobile phone ka password bhool gaye to unlock kaise kare?", "intent": "out_of_scope", "language": "hinglish"}
]

out_path = os.path.join(DATA_DIR, "intent_hindi_hinglish_100.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(test_set, f, indent=2, ensure_ascii=False)

print(f"Saved {len(test_set)} Hindi/Hinglish test samples to {out_path}")
counts = {}
for item in test_set:
    counts[item["intent"]] = counts.get(item["intent"], 0) + 1
for k, v in counts.items():
    print(f"  {k}: {v}")
assert len(test_set) == 100, f"Expected 100 samples, got {len(test_set)}"
