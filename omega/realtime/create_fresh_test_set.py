import json
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")

# Load existing files to guarantee ZERO overlap
train_v4_path = os.path.join(DATA_DIR, "intent_train_v4.json")
mandi_150_path = os.path.join(DATA_DIR, "mandi_handcrafted_150.json")
hw_100_path = os.path.join(DATA_DIR, "handwritten_test_100.json")
gap_75_path = os.path.join(DATA_DIR, "targeted_gap_75.json")
strengthening_path = os.path.join(DATA_DIR, "domain_strengthening_train.json")
held_out_path = os.path.join(DATA_DIR, "intent_held_out_test_v3.json")

all_seen_texts = set()
for path in [train_v4_path, mandi_150_path, hw_100_path, gap_75_path, strengthening_path, held_out_path]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for r in data:
                all_seen_texts.add(r["text"].strip().lower())

print(f"Total existing unique texts across all datasets: {len(all_seen_texts)}")

# 150 Fresh, untouched test queries specifically targeting mandi/market rates
fresh_queries = [
    # 1-15: Onion (Pyaz / Kanda) - different mandis, units, phrasings
    "aaj subah vashi APMC me pyaz kitne me bika",
    "lasalgaon kanda auction rate per quintal this morning",
    "delhi azadpur wholesale mandi me onion 50 kg sack price",
    "pyaaz bhao aajka pune market",
    "solapur mandi onion arrival and minimum rate today",
    "kisan bhaiyo mahuva mandi me pyaz ka kya rate nikla",
    "hubli market red onion modal price right now",
    "yeotmal APMC pyaz thok rate live",
    "bhavnagar mandi white onion prevailing rate",
    "kurnool APMC summer onion auction price",
    "aaj alwar mandi me fresh pyaz ki boli kitne pe shuru hui",
    "khandwa mandi pyaz rate per kg today",
    "ahmednagar kanda bazaar live rates",
    "satara mandi onion modal price per bag",
    "dindori APMC onion daily rate sheet",

    # 16-30: Wheat (Gehu / Sharbati / Durum)
    "bhai aaj ujjain mandi me gehu ka kya rate chal raha hai",
    "sehore mandi sharbati gehu ka live auction bhav",
    "kota mandi durum wheat modal price per quintal",
    "khanna mandi gehu arrival rate morning session",
    "sirsa grain market wheat per quintal today",
    "harda mandi gehu ka taaza rate kitna hai",
    "baran mandi wheat mill quality price",
    "vidisha mandi lokwan wheat rate per quintal",
    "shahjahanpur gehu market rate live update",
    "dabwali mandi gehu ka taza bhav bataiye",
    "bikaner mandi gehu standard lot price",
    "patiala grain market wheat wholesale rate today",
    "ratlam APMC gehu modal bhav live",
    "hathras mandi gehu purchase price",
    "gehu bhao karnal grain market",

    # 31-45: Tomato (Tamatar) - crate rates, wholesale auctions
    "tamatar 25 kg crate rate in kolar market today",
    "tamater bhav deesa vegetable market",
    "pimpalgaon tomato auction average price per crate",
    "madannapalle mandi tamatar wholesale rate morning",
    "chittoor tomato market price per kg live",
    "nashik tomato yard modal rate per box",
    "aaj ranchi mandi me tamatar ka kya wholesale bhav hai",
    "solan mandi hybrid tomato crate price",
    "lucknow dubagga mandi tamatar ka taaza rate",
    "varanasi pahariya mandi tomato prevailing price",
    "sangamner tomato auction rate sheet",
    "jabalpur krishi mandi tamatar bhav per crate",
    "agra mandi deshi tamatar rate",
    "ahmedabad APMC hybrid tamatar daily rate",
    "tamatar crate price shivaji market",

    # 46-60: Cotton (Kapas / Ru) - quality grades, bail prices
    "kapas rate rajkot commodity yard today",
    "surendranagar mandi shankar-6 cotton spot rate",
    "yeotmal APMC cotton medium staple per quintal",
    "kadi mandi kapas auction price live",
    "adilabad cotton market modal rate per quintal",
    "amreli mandi desi kapas rate morning",
    "jalna APMC ru kapas wholesale price",
    "bhatinda mandi narma kapas rate today",
    "sirsa mandi long staple cotton price update",
    "mansa market narma kapas live rate",
    "warangal cotton yard prevailing auction rate",
    "khammam kapas rate per quintal",
    "hinganghat APMC cotton price sheet",
    "dharwad cotton spot market price",
    "kapas ka taaja dam botad mandi",

    # 61-75: Soybean
    "indore mandi yellow soybean modal rate today per quintal",
    "latur APMC soyabean auction rate morning",
    "neemuch mandi soybean rate per quintal live",
    "akola market soybean commercial quality price",
    "dewas mandi soybean ka taaza bhav kitna chal raha hai",
    "amravati APMC soybean spot delivery price",
    "nagpur mandi refined soybean lot rate",
    "ujjain APMC soyabean modal price today",
    "washim APMC soybean arrival and auction rate",
    "kota mandi soyabean seed rate per quintal",
    "seoni mandi soybean modal price list",
    "betul krishi upaj mandi soybean bhav",
    "mandsaur mandi black soybean rate",
    "hingoli mandi soybean wholesale price",
    "soyabean bhav baramati yard",

    # 76-90: Garlic & Ginger (Lahsun & Adrak)
    "lahsun mandy rat mandsaur today",
    "neemuch mandi ooti garlic modal price per quintal",
    "kota mandi desi lahsun per bag auction rate",
    "hassan APMC ginger wholesale price per bag",
    "wayanad fresh green ginger mandi price today",
    "shimoga adrak market price per quintal",
    "pipariya mandi lahsun arrival and modal rate",
    "chhindwara mandi adrak wholesale rate",
    "jaipur terminal market garlic box rate",
    "bhopal mandi lahsun wholesale price per kg",
    "lahsun grade 1 rate pratapgarh mandi",
    "adrak goli quality price siliguri mandi",
    "alwar mandi garlic loose price",
    "shimla ginger wet lot mandi price",
    "garlic mandi price indore krishi upaj",

    # 91-105: Potato & Vegetables (Alu, Mirch, Matar)
    "delhi azadpur mandi potato rate per bag today",
    "farrukhabad alu mandi bhav per quintal",
    "agra cold storage alu market release price",
    "hapur mandi pukhraj potato modal rate",
    "guntur dry red chilli teja variety live rate per quintal",
    "byadgi chilli auction price in karnataka today",
    "khammam red chilli fatki quality mandi price",
    "jabalpur mandi fresh green peas matar per kg rate",
    "aligarh alu mandi rate 50 kg packet",
    "sambhal potato wholesale yard price",
    "warangal red chilli modal rate live",
    "nashik cauliflower gobhi crate rate APMC",
    "bengaluru market green chilli per kg price",
    "kolhapur yard potato chipsona rate",
    "alu ka wholesale rate kanpur mandi",

    # 106-120: Mustard, Maize & Pulses (Sarso, Makka, Chana, Moong)
    "bharatpur mandi sarso spot price per quintal",
    "jaipur mandi mustard seed 42 condition rate",
    "alwar oilseed mandi sarso live rate",
    "gulabbagh purnea makka corn modal rate today",
    "chhindwara mandi maize poultry grade price",
    "davangere APMC maize per quintal morning price",
    "bikaner mandi chana dal wholesale rate",
    "latur mandi red gram tur tur dal auction price",
    "gulbarga tur dal mandi modal price today",
    "jalgaon chana auction rate per quintal",
    "akola moong dal wholesale mandi rate",
    "kota mandi black urad per quintal price",
    "hindaun mandi sarso mustard auction price",
    "makka bhav bihar gulabbagh live",
    "sarson ka daam mandi morena",

    # 121-135: Spices, Oilseeds & Commercial (Jeera, Dhaniya, Haldi, Groundnut)
    "unjha mandi jeera cumin seed auction rate today",
    "rajkot APMC jeera quality 1 modal price",
    "gondal mandi moongfali groundnut pod rate per 20 kg",
    "junagadh APMC groundnut bold variety rate",
    "ramganj mandi dhaniya coriander spot rate",
    "kumbhraj mandi green coriander seed rate",
    "erode mandi finger turmeric live auction price",
    "nizamabad turmeric farmers yard modal rate",
    "sangli haldi market rajapore turmeric rate",
    "dharapuram groundnut kernel market rate",
    "patan mandi castor seed erand rate today",
    "deesa mandi sesamum til white rate",
    "bodeli castor seed APMC wholesale price",
    "jeera bhav unjha live trading session",
    "haldi ka mandi rate duggirala",

    # 136-150: Precious Metals & Financial Commodity Rates in Mandis
    "gold 24k bullion spot rate in zaveri bazaar mumbai today",
    "silver 999 wholesale price per kg mcx live right now",
    "delhi bullion market 22 carat gold rate per 10 grams",
    "sona chandi ka taaza bhav sarafa market indore",
    "chennai gold rate sovereign today live",
    "kolkata sarafa bazaar silver bar price today",
    "jaipur sarafa mandal gold hallmarked rate",
    "ahmedabad gold 99.9 purity spot cash price",
    "crude oil barrel price on mcx commodity exchange now",
    "natural gas mcx spot contract rate today",
    "copper lot price commodity market live",
    "mentha oil spot price sambhal market",
    "guar gum seed rate jodhpur commodity yard today",
    "guar split rate bikaner mandi morning session",
    "rubber rss-4 kottayam spot market auction rate"
]

print(f"Candidate fresh queries count: {len(fresh_queries)}")

# Verify NO overlap
overlaps = []
for q in fresh_queries:
    norm = q.strip().lower()
    if norm in all_seen_texts:
        overlaps.append(q)

if overlaps:
    print(f"ERROR: Found {len(overlaps)} overlapping queries!")
    for o in overlaps:
        print(f"  - {o}")
    raise ValueError("Overlap detected!")
else:
    print("SUCCESS: EXACTLY ZERO OVERLAP with any existing dataset!")

fresh_dataset = [{"text": q, "intent": "realtime"} for q in fresh_queries]

out_file = os.path.join(DATA_DIR, "fresh_mandi_test_150.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(fresh_dataset, f, indent=2, ensure_ascii=False)

print(f"Saved {len(fresh_dataset)} fresh queries to: {out_file}")
