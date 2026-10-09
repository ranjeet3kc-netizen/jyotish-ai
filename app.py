import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta, date, time, timezone
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import zoneinfo

# ---------------------------------------------------------------
# Swiss Ephemeris (Lahiri Ayanamsha)
# ---------------------------------------------------------------
swe.set_sid_mode(swe.SIDM_LAHIRI)

SIGNS = ["Mesh", "Vrishabh", "Mithun", "Kark", "Singh", "Kanya",
         "Tula", "Vrishchik", "Dhanu", "Makar", "Kumbh", "Meen"]
SIGNS_HI = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या",
            "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

PLANETS = {
    "Surya": swe.SUN, "Chandra": swe.MOON, "Mangal": swe.MARS,
    "Budh": swe.MERCURY, "Guru": swe.JUPITER, "Shukra": swe.VENUS,
    "Shani": swe.SATURN, "Rahu": swe.MEAN_NODE,
}

DASHA_LORDS = ["Ketu", "Shukra", "Surya", "Chandra", "Mangal",
               "Rahu", "Guru", "Shani", "Budh"]
DASHA_YEARS = {"Ketu": 7, "Shukra": 20, "Surya": 6, "Chandra": 10, "Mangal": 7,
               "Rahu": 18, "Guru": 16, "Shani": 19, "Budh": 17}
YEAR_DAYS = 365.25

RASHI_LORDS = {0: "Mangal", 1: "Shukra", 2: "Budh", 3: "Chandra", 4: "Surya",
               5: "Budh", 6: "Shukra", 7: "Mangal", 8: "Guru", 9: "Shani",
               10: "Shani", 11: "Guru"}

OWN_SIGNS = {"Mangal": [0, 7], "Shukra": [1, 6], "Budh": [2, 5],
             "Guru": [8, 11], "Shani": [9, 10]}
EXALT_SIGN = {"Mangal": 9, "Shukra": 11, "Budh": 5, "Guru": 3, "Shani": 6}
MAHAPURUSHA = {"Mangal": "रुचक योग", "Budh": "भद्र योग", "Guru": "हंस योग",
               "Shukra": "मालव्य योग", "Shani": "शश योग"}

GEMSTONES = {
    "Surya": "माणिक्य (Ruby)", "Chandra": "मोती (Pearl)",
    "Mangal": "मूँगा (Red Coral)", "Budh": "पन्ना (Emerald)",
    "Guru": "पुखराज (Yellow Sapphire)", "Shukra": "हीरा / ओपल (Diamond / Opal)",
    "Shani": "नीलम (Blue Sapphire)",
    "Rahu": "गोमेद (Hessonite) - केवल विद्वान की सलाह से",
    "Ketu": "लहसुनिया (Cat's Eye) - केवल विद्वान की सलाह से",
}

RUDRAKSHA = {
    "Surya": "1 मुखी या 12 मुखी रुद्राक्ष", "Chandra": "2 मुखी रुद्राक्ष",
    "Mangal": "3 मुखी रुद्राक्ष", "Budh": "4 मुखी रुद्राक्ष",
    "Guru": "5 मुखी रुद्राक्ष", "Shukra": "6 मुखी रुद्राक्ष",
    "Shani": "7 मुखी रुद्राक्ष", "Rahu": "8 मुखी रुद्राक्ष",
    "Ketu": "9 मुखी रुद्राक्ष",
}

HEALTH_MAP = {
    "Surya": "अस्थि स्वास्थ्य, नेत्र दृष्टि, हृदय प्रणाली, एवं पित्त संबंधी संतुलन पर विशेष ध्यान दें।",
    "Chandra": "मानसिक शांति, अनिद्रा, कफ/जल जनित समस्याएं, एवं श्वसन तंत्र की देखभाल आवश्यक है।",
    "Mangal": "रक्तचाप, एसिडिटी, चोट-चपेट से सावधानी, एवं पाचन अग्नि को संतुलित रखना हितकर है।",
    "Budh": "त्वचा स्वास्थ्य, स्नायु तंत्र (Nervous System), वाणी एवं गले की देखभाल पर ध्यान दें।",
    "Guru": "यकृत (Liver) स्वास्थ्य, कोलेस्ट्रॉल, शुगर/डायबिटीज प्रबंधन, एवं पाचन तंत्र पर ध्यान दें।",
    "Shukra": "वृक्क (Kidney) स्वास्थ्य, हार्मोनल संतुलन, एवं शरीर में शर्करा स्तर की नियमित जांच रखें।",
    "Shani": "अस्थि संधि (Joints), वात संतुलन, दांतों की देखभाल, एवं शारीरिक दिनचर्या में अनुशासन रखें।",
    "Rahu": "अचानक स्वास्थ्य उतार-चढ़ाव, मानसिक तनाव, एलर्जी, एवं एंग्जाइटी से बचाव के लिए योग करें।",
    "Ketu": "त्वचा संबंधी संवेदनशीलता, उदर स्वास्थ्य, एवं शारीरिक ऊर्जा स्तर को बनाए रखने के उपाय करें।",
}

MAHADASHA_PREDICTIONS = {
    "Surya": "सूर्य की महादशा आत्मबल, अधिकार, सामाजिक प्रतिष्ठा और प्रशासनिक कार्यों में सफलता प्रदान करती है। अहंकार से बचें।",
    "Chandra": "चंद्रमा की महादशा मन की संवेदनशीलता, रचनात्मकता और मानसिक सुख लाती है। माता का सहयोग मिलता है।",
    "Mangal": "मंगल की महादशा असीम ऊर्जा, साहस, पराक्रम, भूमि और तकनीकी कार्यों में बड़ी सफलता का काल है।",
    "Budh": "बुध की महादशा बुद्धि, ज्ञान, संचार, बैंकिंग, लेखन और व्यापारिक कुशाग्रता का काल मानी जाती है।",
    "Guru": "बृहस्पति की महादशा सुख, समृद्धि, उच्च शिक्षा, आध्यात्मिक ज्ञान और दांपत्य जीवन में वृद्धि लाती है।",
    "Shukra": "शुक्र की महादशा भौतिक सुख-सुविधाओं, वाहन, आभूषण, कला और विलासिता का स्वर्णिम काल होती है।",
    "Shani": "शनि की महादशा कड़े परिश्रम, अनुशासन और परिपक्वता का काल है। यह स्थायी और दीर्घकालिक फल देती है।",
    "Rahu": "राहु की महादशा अचानक बदलाव, आधुनिक तकनीक, विदेशी व्यापार और लीक से हटकर सोचने का अवसर देती है।",
    "Ketu": "केतु की महादशा आध्यात्म, गुप्त विद्याओं, शोध और आत्म-साक्षात्कार का काल है। अंतर्दृष्टि मजबूत होती है।",
}


# ---------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------

def get_navamsha_sign(abs_degree):
    abs_degree = abs_degree % 360
    d1_sign = int(abs_degree // 30)
    navamsha_num = int((abs_degree % 30) / (30.0 / 9.0))

    if d1_sign in (0, 3, 6, 9):
        start = d1_sign
    elif d1_sign in (1, 4, 7, 10):
        start = (d1_sign + 8) % 12
    else:
        start = (d1_sign + 4) % 12

    return (start + navamsha_num) % 12

def antardashas(md_lord, md_start):
    """Full 9 antardashas of a mahadasha. md_start must be the *true* start
    of the mahadasha (for the first MD this is before birth)."""
    md_idx = DASHA_LORDS.index(md_lord)
    md_years = DASHA_YEARS[md_lord]
    out, start = [], md_start
    for i in range(9):
        lord = DASHA_LORDS[(md_idx + i) % 9]
        yrs = md_years * DASHA_YEARS[lord] / 120.0
        end = start + timedelta(days=yrs * YEAR_DAYS)
        out.append((lord, start, end))
        start = end
    return out


def check_kaal_sarp(lons, rahu_deg):
    """All 7 planets on one side of the Rahu-Ketu axis."""
    others = ["Surya", "Chandra", "Mangal", "Budh", "Guru", "Shukra", "Shani"]
    diffs = [(lons[p] - rahu_deg) % 360 for p in others]
    return all(d < 180 for d in diffs) or all(d > 180 for d in diffs)


def find_yogas(sign_of, houses):
    yogas = []
    # Gajakesari: Guru in kendra from Chandra
    if (sign_of["Guru"] - sign_of["Chandra"]) % 12 in (0, 3, 6, 9):
        yogas.append(("गजकेसरी योग", "गुरु चंद्र से केंद्र में है: यश, बुद्धि और सम्मान देने वाला योग।"))
    # Budhaditya
    if sign_of["Surya"] == sign_of["Budh"]:
        yogas.append(("बुधादित्य योग", "सूर्य-बुध एक राशि में: तीक्ष्ण बुद्धि और वाक्पटुता।"))
    # Chandra-Mangal
    if sign_of["Chandra"] == sign_of["Mangal"]:
        yogas.append(("चंद्र-मंगल योग", "धन-अर्जन की क्षमता, पर भावनात्मक उग्रता से सावधान रहें।"))
    # Panch Mahapurusha
    for p, name in MAHAPURUSHA.items():
        in_kendra = houses[p] in (1, 4, 7, 10)
        strong = sign_of[p] in OWN_SIGNS[p] or sign_of[p] == EXALT_SIGN[p]
        if in_kendra and strong:
            yogas.append((name, f"{p} स्वराशि/उच्च का होकर केंद्र में है: पंच-महापुरुष योग।"))
    return yogas


def analyze_love(asc_sign, sign_of, houses, gender):
    """Love / marriage / affair tendencies from 5th, 7th, 12th houses,
    their lords, Venus (or Jupiter for women), Mars, Rahu, Ketu, Shani."""
    lord5 = RASHI_LORDS[(asc_sign + 4) % 12]
    lord7 = RASHI_LORDS[(asc_sign + 6) % 12]
    karaka = "Guru" if gender.startswith("Female") else "Shukra"

    def in_house(h):
        return [p for p in houses if houses[p] == h]

    def together(a, b):
        return sign_of[a] == sign_of[b]

    love, marriage, affair = [], [], []
    score = 0

    # --- Prem (5th house)
    p5 = in_house(5)
    love.append(("info", f"पंचम भाव (प्रेम): लग्न से {SIGNS[(asc_sign + 4) % 12]} राशि, स्वामी {lord5} "
                         f"{houses[lord5]}वें भाव में। पंचम में ग्रह: {', '.join(p5) if p5 else 'कोई नहीं'}।"))
    if houses["Shukra"] in (1, 5, 7, 11):
        love.append(("good", f"शुक्र {houses['Shukra']}वें भाव में है: प्रेम, आकर्षण और रोमांस की अच्छी क्षमता।"))
    elif houses["Shukra"] in (6, 8, 12):
        love.append(("warn", f"शुक्र {houses['Shukra']}वें भाव में है: प्रेम में बाधा, देरी या गुप्तता के संकेत।"))
    if "Chandra" in p5 or together("Chandra", "Shukra"):
        love.append(("good", "चंद्र/शुक्र का संबंध भावनात्मक और संवेदनशील प्रेम स्वभाव दर्शाता है।"))
    if together("Shani", "Shukra"):
        love.append(("warn", "शनि-शुक्र एक राशि में: प्रेम देर से मिलता है, रिश्ते में गंभीरता और दूरी दोनों रह सकती हैं।"))
    if together("Mangal", "Shukra"):
        love.append(("warn", "मंगल-शुक्र एक राशि में: तीव्र आकर्षण और जुनून, पर संयम की आवश्यकता।"))
        score += 1
    if together("Rahu", "Shukra") or together("Ketu", "Shukra"):
        love.append(("warn", "राहु/केतु-शुक्र संबंध: असामान्य या अचानक आकर्षण, भ्रम की संभावना।"))
        score += 1

    # --- Prem vivah (love marriage)
    if together(lord5, lord7) and lord5 != lord7:
        marriage.append(("good", "पंचमेश और सप्तमेश एक राशि में: प्रेम-विवाह का मजबूत योग।"))
    if houses[lord5] == 7 or houses[lord7] == 5:
        marriage.append(("good", "पंचमेश-सप्तमेश का भाव-परिवर्तन/संबंध: प्रेम से विवाह की संभावना।"))
    if lord5 == lord7:
        marriage.append(("good", f"{lord5} पंचम और सप्तम दोनों का स्वामी है: प्रेम और विवाह एक-दूसरे से जुड़े रहते हैं।"))
    if houses[karaka] in (5, 7):
        marriage.append(("good", f"विवाह कारक {karaka} {houses[karaka]}वें भाव में है: साथी से अच्छा जुड़ाव।"))
    if not marriage:
        marriage.append(("info", "प्रेम-विवाह के स्पष्ट शास्त्रीय योग नहीं मिले; विवाह पारंपरिक या मिश्रित रूप से संभव।"))

    # --- Saptam (7th house)
    p7 = in_house(7)
    marriage.append(("info", f"सप्तम भाव: {SIGNS[(asc_sign + 6) % 12]} राशि, स्वामी {lord7} {houses[lord7]}वें भाव में। "
                             f"सप्तम में ग्रह: {', '.join(p7) if p7 else 'कोई नहीं'}।"))
    if houses[lord7] in (6, 8, 12):
        marriage.append(("warn", f"सप्तमेश {houses[lord7]}वें (दुःस्थान) भाव में: वैवाहिक जीवन में उतार-चढ़ाव, दूरी या विलंब।"))
        score += 1
    if houses[lord7] in (1, 4, 5, 7, 9, 10, 11):
        marriage.append(("good", f"सप्तमेश {houses[lord7]}वें भाव में: वैवाहिक सुख के लिए अनुकूल स्थिति।"))
    if "Shani" in p7 or "Mangal" in p7:
        marriage.append(("warn", "सप्तम में शनि/मंगल: विवाह में देरी या स्वभाव-भेद; धैर्य ज़रूरी।"))
    if "Guru" in p7 or "Shukra" in p7:
        marriage.append(("good", "सप्तम में गुरु/शुक्र: सुखद और सहयोगी जीवनसाथी का संकेत।"))

    # --- Affair / secret relationship tendencies
    if "Rahu" in in_house(5) or "Rahu" in p7 or "Ketu" in p7:
        affair.append(("warn", "राहु/केतु पंचम या सप्तम में: गुप्त, असामान्य या अचानक बनने-टूटने वाले संबंधों की प्रवृत्ति।"))
        score += 1
    if "Rahu" in in_house(12) or "Mangal" in in_house(12):
        affair.append(("warn", "द्वादश भाव (शय्या सुख/गुप्त बातें) में राहु/मंगल: छिपे हुए संबंधों की प्रवृत्ति।"))
        score += 1
    if houses[lord5] in (6, 8, 12) or houses[lord7] == 12:
        affair.append(("warn", "पंचमेश/सप्तमेश का दुःस्थान या द्वादश से संबंध: संबंधों में गोपनीयता या बाधा।"))
        score += 1
    if together("Mangal", "Shukra") or together("Rahu", "Shukra"):
        affair.append(("warn", "शुक्र पर मंगल/राहु का प्रभाव: आकर्षण में अधिक तीव्रता, इच्छाओं पर संयम की आवश्यकता।"))
        score += 1
    if houses["Shukra"] == 12:
        affair.append(("info", "शुक्र द्वादश में: भोग-विलास और निजी जीवन में गोपनीयता की प्रवृत्ति।"))
    if "Shani" in in_house(7) or "Guru" in in_house(7):
        affair.append(("good", "सप्तम में शनि/गुरु: मर्यादा और निष्ठा की प्रवृत्ति को बल।"))
        score -= 1
    if not affair:
        affair.append(("good", "गुप्त संबंध या अनैतिक आकर्षण के स्पष्ट योग नहीं मिले।"))

    level = "कम" if score <= 1 else ("मध्यम" if score <= 3 else "अधिक")
    return {"love": love, "marriage": marriage, "affair": affair,
            "affair_level": level, "score": score, "karaka": karaka,
            "lord5": lord5, "lord7": lord7}


WEEKDAYS = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
TITHIS = ["प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी", "सप्तमी", "अष्टमी",
          "नवमी", "दशमी", "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी"]
PANCHANG_YOGAS = ["विष्कुम्भ", "प्रीति", "आयुष्मान", "सौभाग्य", "शोभन", "अतिगण्ड", "सुकर्मा", "धृति",
                  "शूल", "गण्ड", "वृद्धि", "ध्रुव", "व्याघात", "हर्षण", "वज्र", "सिद्धि", "व्यतीपात",
                  "वरीयान", "परिघ", "शिव", "सिद्ध", "साध्य", "शुभ", "शुक्ल", "ब्रह्म", "इन्द्र", "वैधृति"]
KARANA_MOVABLE = ["बव", "बालव", "कौलव", "तैतिल", "गर", "वणिज", "विष्टि (भद्रा)"]
KARANA_FIXED = ["शकुनि", "चतुष्पद", "नाग"]

NAK_GANA = ["देव", "मनुष्य", "राक्षस", "मनुष्य", "देव", "मनुष्य", "देव", "देव", "राक्षस", "राक्षस",
            "मनुष्य", "मनुष्य", "देव", "राक्षस", "देव", "राक्षस", "देव", "राक्षस", "राक्षस", "मनुष्य",
            "मनुष्य", "देव", "राक्षस", "राक्षस", "मनुष्य", "मनुष्य", "देव"]
NAK_YONI = ["अश्व", "गज", "मेष", "सर्प", "सर्प", "श्वान", "मार्जार", "मेष", "मार्जार", "मूषक",
            "मूषक", "गौ", "महिष", "व्याघ्र", "महिष", "व्याघ्र", "मृग", "मृग", "श्वान", "वानर",
            "नकुल", "वानर", "सिंह", "अश्व", "सिंह", "गौ", "गज"]
NADI_NAMES = ["आदि", "मध्य", "अंत्य", "अंत्य", "मध्य", "आदि"]       # index % 6
VARNA_BY_SIGN = ["क्षत्रिय", "वैश्य", "शूद्र", "ब्राह्मण"] * 3          # index % 4
VASHYA_BY_SIGN = ["चतुष्पद", "चतुष्पद", "मानव", "जलचर", "वनचर", "मानव", "मानव", "कीट",
                  "मानव/चतुष्पद", "चतुष्पद/जलचर", "मानव", "जलचर"]
TATVA_BY_SIGN = ["अग्नि", "पृथ्वी", "वायु", "जल"]                      # index % 4
BHAVA_NAMES = ["तनु (लग्न)", "धन/कुटुंब", "सहज (पराक्रम)", "सुख/माता", "पुत्र/विद्या/प्रेम",
               "रिपु/रोग/ऋण", "जाया/विवाह", "आयु/गुप्त", "भाग्य/धर्म", "कर्म/व्यवसाय", "लाभ", "व्यय/विदेश"]

CAREER_HOUSE = {
    1: "स्वयं के बल पर, स्वतंत्र कार्य या नेतृत्व वाली भूमिका।",
    2: "वाणी, परिवार या धन-संबंधी कारोबार; बैंकिंग/खाद्य क्षेत्र में लाभ।",
    3: "मेहनत, संचार, मीडिया, सेल्स या छोटी यात्राओं वाले कार्य।",
    4: "घर के पास या घर से काम; भूमि-भवन, कृषि या वाहन संबंधी क्षेत्र।",
    5: "शिक्षा, रचनात्मक कार्य, सलाह या निवेश से जुड़े क्षेत्र।",
    6: "सेवा, स्वास्थ्य, कानून, प्रतियोगिता या नौकरी में सफलता।",
    7: "साझेदारी, व्यापार और जनसंपर्क वाले कार्य में सफलता।",
    8: "शोध, बीमा, गुप्त/तकनीकी कार्य; करियर में अचानक बदलाव संभव।",
    9: "भाग्य का साथ; उच्च शिक्षा, विदेश या धर्म/कानून से जुड़े क्षेत्र।",
    10: "करियर बहुत मज़बूत; पद, प्रतिष्ठा और स्थिरता।",
    11: "बड़ा नेटवर्क और कई स्रोतों से आय।",
    12: "विदेश, अस्पताल/आश्रम या पर्दे के पीछे वाले कार्य; खर्च अधिक।",
}
CAREER_KARAKA = {
    "Surya": "सरकारी/प्रशासनिक कार्य", "Chandra": "जनता, आतिथ्य, यात्रा, तरल पदार्थ",
    "Mangal": "इंजीनियरिंग, तकनीकी, सुरक्षा, भूमि", "Budh": "व्यापार, IT, लेखा, लेखन",
    "Guru": "शिक्षण, कानून, वित्त, सलाह", "Shukra": "कला, मीडिया, फैशन, सौंदर्य",
    "Shani": "उद्योग, निर्माण, खेती, सेवा", "Rahu": "विदेशी/आधुनिक तकनीक, राजनीति",
    "Ketu": "शोध, अध्यात्म, गुप्त विद्या",
}


def compute_panchang(lons, dob):
    sun, moon = lons["Surya"], lons["Chandra"]
    elong = (moon - sun) % 360
    tithi_no = int(elong // 12) + 1                       # 1..30
    paksha = "शुक्ल" if tithi_no <= 15 else "कृष्ण"
    if tithi_no == 15:
        tithi = "पूर्णिमा"
    elif tithi_no == 30:
        tithi = "अमावस्या"
    else:
        tithi = TITHIS[(tithi_no - 1) % 15]
    k = int(elong // 6)                                    # 0..59
    if k == 0:
        karana = "किंस्तुघ्न"
    elif k >= 57:
        karana = KARANA_FIXED[k - 57]
    else:
        karana = KARANA_MOVABLE[(k - 1) % 7]
    span = 360.0 / 27.0
    yoga = PANCHANG_YOGAS[int(((sun + moon) % 360) / span)]
    nak = int(moon / span)
    pada = int((moon % span) / (span / 4)) + 1
    return {"vara": WEEKDAYS[dob.weekday()], "tithi": f"{paksha} पक्ष {tithi}", "karana": karana,
            "yoga": yoga, "nakshatra": NAKSHATRAS[nak], "pada": pada}


def compute_avakahada(moon_lon):
    nak = int(moon_lon / (360.0 / 27.0))
    sign = int(moon_lon // 30)
    return {"वर्ण": VARNA_BY_SIGN[sign], "वश्य": VASHYA_BY_SIGN[sign], "योनि": NAK_YONI[nak],
            "गण": NAK_GANA[nak], "नाड़ी": NADI_NAMES[nak % 6], "तत्व": TATVA_BY_SIGN[sign % 4],
            "राशि स्वामी": RASHI_LORDS[sign]}


def compute_sade_sati(moon_sign):
    now = datetime.now(timezone.utc)
    jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0)
    sat = swe.calc_ut(jd, swe.SATURN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360
    s = int(sat // 30)
    d = (s - moon_sign) % 12
    status = {11: "साढ़ेसाती - प्रथम चरण (चंद्र से 12वें में शनि)",
              0: "साढ़ेसाती - द्वितीय चरण (चंद्र राशि में शनि, शिखर)",
              1: "साढ़ेसाती - तृतीय चरण (चंद्र से 2रे में शनि)",
              3: "शनि ढैया (चंद्र से 4थे में शनि)",
              7: "शनि ढैया (चंद्र से 8वें में शनि)"}.get(d)
    return {"saturn_sign": SIGNS[s], "status": status}


def bhava_table(asc_sign, sign_of, houses):
    rows = []
    for h in range(1, 13):
        sign = (asc_sign + h - 1) % 12
        lord = RASHI_LORDS[sign]
        rows.append({
            "भाव": f"{h} - {BHAVA_NAMES[h - 1]}", "राशि": f"{SIGNS[sign]} ({SIGNS_HI[sign]})",
            "भावेश": f"{lord} ({houses[lord]}वें भाव में)",
            "ग्रह": ", ".join(p for p in houses if houses[p] == h) or "-",
        })
    return rows


def analyze_career(asc_sign, sign_of, houses):
    out = []
    lord10 = RASHI_LORDS[(asc_sign + 9) % 12]
    out.append(("info", f"दशमेश {lord10} {houses[lord10]}वें भाव में: {CAREER_HOUSE[houses[lord10]]}"))
    p10 = [p for p in houses if houses[p] == 10]
    for p in p10:
        out.append(("info", f"दशम भाव में {p}: {CAREER_KARAKA[p]} से जुड़े क्षेत्र।"))
    # wealth
    lord2, lord11 = RASHI_LORDS[(asc_sign + 1) % 12], RASHI_LORDS[(asc_sign + 10) % 12]
    good = (1, 2, 5, 9, 10, 11)
    if houses[lord2] in good:
        out.append(("good", f"धनेश {lord2} {houses[lord2]}वें भाव में: धन संचय के लिए अनुकूल।"))
    else:
        out.append(("warn", f"धनेश {lord2} {houses[lord2]}वें भाव में: खर्च या धन में उतार-चढ़ाव; बचत पर ध्यान दें।"))
    if houses[lord11] in good:
        out.append(("good", f"लाभेश {lord11} {houses[lord11]}वें भाव में: आय के अच्छे स्रोत।"))
    else:
        out.append(("warn", f"लाभेश {lord11} {houses[lord11]}वें भाव में: आय में अस्थिरता संभव।"))
    if lord2 != lord11 and sign_of[lord2] == sign_of[lord11]:
        out.append(("good", "धनेश और लाभेश एक राशि में: धन योग।"))
    return out


def section_heading(title, icon="✨"):
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #4A0000 0%, #1A0000 100%);
            padding: 14px 22px; border-radius: 10px; margin-top: 28px; margin-bottom: 18px;
            border-left: 6px solid #FFD700; box-shadow: 0px 4px 12px rgba(0,0,0,0.3);">
            <h3 style="color:#FFD700; margin:0; padding:0; font-weight:700; font-size:20px;">
                {icon} {title}
            </h3>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_north_indian_chart(asc_sign, planet_signs, title):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color="maroon", lw=2)
    ax.plot([0, 0.5, 1, 0.5, 0], [0.5, 1, 0.5, 0, 0.5], color="maroon", lw=1.5)
    ax.plot([0, 1], [0, 1], color="maroon", lw=1.5)
    ax.plot([0, 1], [1, 0], color="maroon", lw=1.5)

    positions = [(0.50, 0.72), (0.25, 0.85), (0.15, 0.68), (0.25, 0.50),
                 (0.15, 0.32), (0.25, 0.15), (0.50, 0.28), (0.75, 0.15),
                 (0.85, 0.32), (0.75, 0.50), (0.85, 0.68), (0.75, 0.85)]

    for i, (x, y) in enumerate(positions):
        sign_index = (asc_sign + i) % 12
        pl = planet_signs.get(SIGNS[sign_index], [])
        if len(pl) > 3:
            p_str, fs = ", ".join(pl[:2]) + "\n" + ", ".join(pl[2:]), 6
        elif len(pl) > 1:
            p_str, fs = ", ".join(pl), 7
        else:
            p_str, fs = ("\n".join(pl) if pl else ""), 7.5
        ax.text(x, y + 0.08, f"H{i + 1} [{SIGNS[sign_index][:3]}]",
                color="darkred", fontsize=8.5, weight="bold", ha="center")
        if p_str:
            ax.text(x, y - 0.04, p_str, color="navy", fontsize=fs, ha="center", va="center")

    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.axis("off")
    ax.set_title(title, fontsize=13, pad=12, color="maroon", weight="bold")
    return fig


# ---------------------------------------------------------------
# Core calculation (no Streamlit calls -> easy to test)
# ---------------------------------------------------------------
def compute_report(name, dob, bt, place):
    loc = Nominatim(user_agent="jyotish_app_v15").geocode(place)
    if not loc:
        return None
    lat, lon = loc.latitude, loc.longitude

    tz_str = TimezoneFinder().timezone_at(lng=lon, lat=lat)
    if tz_str:
        aware = datetime.combine(dob, bt, tzinfo=zoneinfo.ZoneInfo(tz_str))
        utc_dt = aware.astimezone(zoneinfo.ZoneInfo("UTC")).replace(tzinfo=None)
        utc_off = aware.utcoffset().total_seconds() / 3600.0
    else:
        tz_str, utc_off = "Default +5.75", 5.75
        utc_dt = datetime.combine(dob, bt) - timedelta(hours=5, minutes=45)

    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                    utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0)

    # FLG_SPEED is required to get a valid speed (retrograde detection)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    ayan = swe.get_ayanamsa_ut(jd)
    cusps, ascmc = swe.houses(jd, lat, lon, b"P")
    asc_degree = (ascmc[0] - ayan) % 360
    asc_sign = int(asc_degree // 30)
    d9_asc = get_navamsha_sign(asc_degree)

    rows, lons, sign_of, houses = [], {}, {}, {}
    d1_signs, d9_signs = {}, {}

    def add_planet(pname, deg, retro):
        si = int(deg // 30)
        d9 = get_navamsha_sign(deg)
        h = ((si - asc_sign) % 12) + 1
        disp = f"{pname} (R)" if retro else pname
        lons[pname], sign_of[pname], houses[pname] = deg, si, h
        rows.append({
            "Planet": disp, "D1 Rashi": SIGNS[si], "House": f"House {h}",
            "Degree": round(deg % 30, 2),
            "Nakshatra": NAKSHATRAS[int(deg / (360 / 27))],
            "D9 Navamsha Rashi": SIGNS[d9],
            "Status": "Retrograde" if retro else "Direct",
        })
        d1_signs.setdefault(SIGNS[si], []).append(disp)
        d9_signs.setdefault(SIGNS[d9], []).append(disp)

    for pname, code in PLANETS.items():
        res = swe.calc_ut(jd, code, flags)[0]
        deg, speed = res[0] % 360, res[3]
        if pname == "Rahu":
            retro = True                       # mean node is always retrograde
        elif pname in ("Surya", "Chandra"):
            retro = False
        else:
            retro = speed < 0
        add_planet(pname, deg, retro)

    add_planet("Ketu", (lons["Rahu"] + 180) % 360, True)

    # ---- Doshas
    is_manglik = houses["Mangal"] in (1, 4, 7, 8, 12)
    kalsarp = check_kaal_sarp(lons, lons["Rahu"])

    # ---- Vimshottari Dasha
    moon = lons["Chandra"]
    span = 360.0 / 27.0
    nak_idx = int(moon / span)
    balance = 1.0 - ((moon % span) / span)
    first_idx = nak_idx % 9
    first_lord = DASHA_LORDS[first_idx]
    first_full = DASHA_YEARS[first_lord]
    first_remaining = first_full * balance

    # birth moment (UTC, naive) and the *virtual* start of the first MD
    birth = utc_dt
    first_md_start = birth - timedelta(days=(first_full - first_remaining) * YEAR_DAYS)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    md_rows, active_md, active_ad = [], "", ""
    active_ad_rows = []
    md_start = first_md_start
    for i in range(10):
        lord = DASHA_LORDS[(first_idx + i) % 9]
        full = DASHA_YEARS[lord]
        md_end = md_start + timedelta(days=full * YEAR_DAYS)
        shown_start = birth if i == 0 else md_start
        is_active = md_start <= now < md_end
        if is_active:
            active_md = lord
            for ad, a_s, a_e in antardashas(lord, md_start):
                active_ad_rows.append({
                    "अंतर्दशा": ad, "प्रारंभ": a_s.strftime("%Y-%m-%d"),
                    "समाप्ति": a_e.strftime("%Y-%m-%d"),
                    "स्थिति": "🔥 सक्रिय" if a_s <= now < a_e else "-",
                })
                if a_s <= now < a_e:
                    active_ad = ad
        md_rows.append({
            "lord": lord, "start": shown_start.strftime("%Y-%m-%d"),
            "end": md_end.strftime("%Y-%m-%d"),
            "years": round(first_remaining if i == 0 else full, 2),
            "active": is_active,
        })
        md_start = md_end

    return {
        "name": name, "place": place, "address": loc.address,
        "dob_str": dob.strftime("%d-%m-%Y") + " " + bt.strftime("%H:%M"),
        "tz_str": tz_str, "utc_off": utc_off,
        "asc_degree": asc_degree, "asc_sign": asc_sign, "d9_asc": d9_asc,
        "moon_sign": sign_of["Chandra"],
        "rows": rows, "d1_signs": d1_signs, "d9_signs": d9_signs,
        "houses": houses, "is_manglik": is_manglik, "kalsarp": kalsarp,
        "md_rows": md_rows, "active_md": active_md, "active_ad": active_ad,
        "ad_rows": active_ad_rows,
        "yogas": find_yogas(sign_of, houses),
        "lagna_lord": RASHI_LORDS[asc_sign],
        "sign_of": sign_of,
        "panchang": compute_panchang(lons, dob),
        "avakahada": compute_avakahada(lons["Chandra"]),
        "sadesati": compute_sade_sati(sign_of["Chandra"]),
        "bhava": bhava_table(asc_sign, sign_of, houses),
        "career": analyze_career(asc_sign, sign_of, houses),
    }


# ---------------------------------------------------------------
# UI
# ---------------------------------------------------------------
st.set_page_config(page_title="Jyotish AI - विस्तृत महा जन्मपत्री", page_icon="🔱", layout="wide")

st.markdown(
    """
    <div style="text-align:center; background: linear-gradient(90deg,#3A0007 0%,#8A1C1C 50%,#3A0007 100%);
        padding:25px; border-radius:12px; border-bottom:4px solid #FFD700; margin-bottom:25px;">
        <h1 style="color:#FFD700; font-size:34px; font-weight:800; margin:0;">🔱 JYOTISH AI — अति-विस्तृत महा जन्मपत्री</h1>
        <p style="color:#FFF8DC; font-size:16px; margin-top:8px;">Comprehensive Vedic Astrology Engine | गहन विश्लेषण एवं सम्पूर्ण जीवन फलादेश</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("📋 Birth Details / जन्म विवरण दर्ज करें")
col_a, col_b = st.columns(2)
with col_a:
    name = st.text_input("Name / नाम", value="", placeholder="अपना नाम लिखें")
    gender = st.selectbox("Gender / लिंग", ["Male (पुरुष)", "Female (महिला)", "Other (अन्य)"])
    dob = st.date_input("Date of birth / जन्म तिथि", value=None, min_value=date(1900, 1, 1))
    st.write("**Birth Time / जन्म समय (AM / PM के साथ):**")
    t1, t2, t3 = st.columns(3)
    with t1:
        hour12 = st.number_input("Hour (घंटा)", min_value=1, max_value=12, value=12)
    with t2:
        minute = st.number_input("Minute (मिनट)", min_value=0, max_value=59, value=0)
    with t3:
        ampm = st.selectbox("AM / PM", ["PM (दोपहर/शाम)", "AM (सुबह/रात)"])
with col_b:
    place = st.text_input("Birth place & Country / जन्म स्थान व देश", value="",
                          placeholder="जैसे: Ghorahi Nepal, Delhi India, London UK")

if st.button("🚀 Generate Full Detailed Report / संपूर्ण विस्तृत महा-रिपोर्ट देखें", type="primary"):
    if not name or not dob or not place:
        st.warning("कृपया सभी विवरण (नाम, जन्म तिथि, समय और जन्म स्थान) भरें!")
    else:
        try:
            h24 = hour12 % 12 + (12 if "PM" in ampm else 0)
            with st.spinner("गणना हो रही है..."):
                rep = compute_report(name, dob, time(h24, int(minute)), place)
            if rep is None:
                st.error("जन्म स्थान नहीं मिल सका! कृपया स्थान और देश का नाम सही से लिखें।")
            else:
                rep["time_label"] = f"{hour12}:{int(minute):02d} {ampm[:2]}"
                rep["gender"] = gender
                st.session_state["report"] = rep   # survives reruns
        except Exception as e:
            st.error(f"गणना में त्रुटि: {e}")

# ---------------------------------------------------------------
# Render (outside the button block so it persists across reruns)
# ---------------------------------------------------------------
r = st.session_state.get("report")
if r:
    st.success(f"📍 स्थान: **{r['address']}** | टाइमज़ोन: **{r['tz_str']} (UTC {r['utc_off']:+.2f})** "
               f"| समय: **{r['time_label']}**")

    section_heading("1. मूल विवरण, पंचांग एवं अवकहड़ा (Basic Details)", "📜")
    pc, av = r["panchang"], r["avakahada"]
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown("**जन्म विवरण**")
        st.dataframe([
            {"विवरण": "नाम", "मान": r["name"]},
            {"विवरण": "जन्म तिथि/समय", "मान": r["dob_str"]},
            {"विवरण": "जन्म स्थान", "मान": r["place"]},
            {"विवरण": "लग्न", "मान": f"{SIGNS[r['asc_sign']]} ({SIGNS_HI[r['asc_sign']]})"},
            {"विवरण": "चंद्र राशि", "मान": f"{SIGNS[r['moon_sign']]} ({SIGNS_HI[r['moon_sign']]})"},
            {"विवरण": "सूर्य राशि", "मान": f"{SIGNS[r['sign_of']['Surya']]} ({SIGNS_HI[r['sign_of']['Surya']]})"},
            {"विवरण": "लग्नेश", "मान": r["lagna_lord"]},
            {"विवरण": "अयनांश", "मान": "लाहिरी (चित्रपक्ष)"},
        ], hide_index=True, use_container_width=True)
    with b2:
        st.markdown("**पंचांग (जन्म के समय)**")
        st.dataframe([
            {"विवरण": "वार", "मान": pc["vara"]},
            {"विवरण": "तिथि", "मान": pc["tithi"]},
            {"विवरण": "नक्षत्र", "मान": f"{pc['nakshatra']} (चरण {pc['pada']})"},
            {"विवरण": "योग", "मान": pc["yoga"]},
            {"विवरण": "करण", "मान": pc["karana"]},
        ], hide_index=True, use_container_width=True)
        st.caption("वार स्थानीय तारीख़ से है; सूर्योदय से पहले के जन्म में पिछला वार माना जाता है।")
    with b3:
        st.markdown("**अवकहड़ा चक्र**")
        st.dataframe([{"विवरण": k, "मान": v} for k, v in av.items()],
                     hide_index=True, use_container_width=True)

    section_heading("2. ग्रह स्थिति एवं नवमांश विवरण (Planetary Positions)", "🪐")
    st.dataframe(r["rows"], use_container_width=True)

    section_heading("3. लग्न, चंद्र एवं नवमांश कुंडली", "📊")
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**D1 लग्न:** {SIGNS[r['asc_sign']]} ({SIGNS_HI[r['asc_sign']]}) — {round(r['asc_degree'] % 30, 2)}°")
        fig = render_north_indian_chart(r["asc_sign"], r["d1_signs"], "D1 - जन्म कुंडली")
        st.pyplot(fig)
        plt.close(fig)
    with c2:
        st.write(f"**D9 नवमांश लग्न:** {SIGNS[r['d9_asc']]} ({SIGNS_HI[r['d9_asc']]})")
        fig = render_north_indian_chart(r["d9_asc"], r["d9_signs"], "D9 - नवमांश कुंडली")
        st.pyplot(fig)
        plt.close(fig)

    mc1, mc2 = st.columns(2)
    with mc1:
        st.write(f"**चंद्र कुंडली (चंद्र लग्न):** {SIGNS[r['moon_sign']]} ({SIGNS_HI[r['moon_sign']]})")
        fig = render_north_indian_chart(r["moon_sign"], r["d1_signs"], "चंद्र कुंडली")
        st.pyplot(fig)
        plt.close(fig)
    with mc2:
        section_heading("4. भाव विवरण (Bhava Table)", "🏠")
        st.dataframe(r["bhava"], hide_index=True, use_container_width=True)

    section_heading("5. दोष विचार (Manglik, Kaal Sarp, Sade Sati)", "⚠️")
    d1, d2 = st.columns(2)
    with d1:
        with st.expander("🔥 मांगलिक दोष", expanded=True):
            mh = r["houses"]["Mangal"]
            if r["is_manglik"]:
                st.error(f"मंगल **{mh}वें भाव** में है, इसलिए **मांगलिक दोष** बनता है। विवाह से पूर्व कुंडली मिलान आवश्यक है।")
            else:
                st.success(f"मंगल **{mh}वें भाव** में है। मांगलिक दोष नहीं पाया गया।")
    with d2:
        with st.expander("🐍 कालसर्प दोष", expanded=True):
            if r["kalsarp"]:
                st.error("सभी सातों ग्रह राहु-केतु अक्ष के एक ही ओर हैं, इसलिए **कालसर्प दोष** बनता है। विद्वान ज्योतिषी से शांति उपाय पूछें।")
            else:
                st.success("कालसर्प दोष नहीं पाया गया।")

    ss = r["sadesati"]
    with st.expander(f"🪐 साढ़ेसाती / ढैया (वर्तमान शनि: {ss['saturn_sign']} राशि में)", expanded=True):
        if ss["status"]:
            st.error(f"वर्तमान में **{ss['status']}** चल रही है। धैर्य, अनुशासन और शनिवार को सेवा/दान लाभकारी माना जाता है।")
        else:
            st.success("वर्तमान में साढ़ेसाती या शनि ढैया नहीं है।")

    section_heading("6. महादशा एवं अंतर्दशा (Dasha Analysis)", "⏳")
    st.markdown(f"**वर्तमान दशा:** {r['active_md']} महादशा — {r['active_ad']} अंतर्दशा")
    st.dataframe(
        [{"महादशा": m["lord"], "प्रारंभ": m["start"], "समाप्ति": m["end"],
          "अवधि (वर्ष)": m["years"], "स्थिति": "🔥 वर्तमान में सक्रिय" if m["active"] else "-"}
         for m in r["md_rows"]],
        use_container_width=True,
    )
    if r["active_md"]:
        st.info(MAHADASHA_PREDICTIONS[r["active_md"]])
        st.write(f"**{r['active_md']} महादशा की अंतर्दशाएँ:**")
        st.dataframe(r["ad_rows"], use_container_width=True)

    section_heading("7. प्रमुख योग (Yogas)", "🌟")
    if r["yogas"]:
        for yname, ydesc in r["yogas"]:
            st.success(f"**{yname}** — {ydesc}")
    else:
        st.info("कोई प्रमुख शास्त्रीय योग नहीं मिला।")

    section_heading("8. रत्न, रुद्राक्ष एवं स्वास्थ्य (Remedies & Health)", "💎")
    ll, md = r["lagna_lord"], r["active_md"]
    st.markdown(f"**लग्नेश:** {ll}")
    g1, g2 = st.columns(2)
    with g1:
        st.write(f"💎 **लग्नेश रत्न:** {GEMSTONES[ll]}")
        st.write(f"📿 **लग्नेश रुद्राक्ष:** {RUDRAKSHA[ll]}")
        st.write(f"🩺 **स्वास्थ्य ({ll}):** {HEALTH_MAP[ll]}")
    with g2:
        if md:
            st.write(f"💎 **दशानाथ ({md}) रत्न:** {GEMSTONES[md]}")
            st.write(f"📿 **दशानाथ रुद्राक्ष:** {RUDRAKSHA[md]}")
            st.write(f"🩺 **स्वास्थ्य ({md}):** {HEALTH_MAP[md]}")
    st.caption("रत्न धारण से पहले किसी योग्य ज्योतिषी से परामर्श अवश्य लें।")

    section_heading("9. प्रेम, विवाह एवं संबंध (Love, Relationship & Affair)", "❤️")
    love = analyze_love(r["asc_sign"], r["sign_of"], r["houses"], r.get("gender", "Male"))

    def show(items):
        for kind, txt in items:
            if kind == "good":
                st.success(txt)
            elif kind == "warn":
                st.warning(txt)
            else:
                st.info(txt)

    st.markdown(f"**पंचमेश:** {love['lord5']} | **सप्तमेश:** {love['lord7']} | **विवाह कारक:** {love['karaka']}")
    with st.expander("💕 प्रेम स्वभाव (Love Nature)", expanded=True):
        show(love["love"])
    with st.expander("💍 प्रेम-विवाह एवं वैवाहिक जीवन (Marriage)", expanded=True):
        show(love["marriage"])
    with st.expander("🕵️ गुप्त संबंध / अफेयर की प्रवृत्ति (Affair Tendency)", expanded=True):
        show(love["affair"])
        st.markdown(f"**कुल प्रवृत्ति स्तर: {love['affair_level']}**")
    st.caption("यह केवल कुंडली के ग्रह-योगों पर आधारित सामान्य संकेत है, निश्चित भविष्यवाणी नहीं। "
               "असल जीवन में व्यक्ति के कर्म, संस्कार और निर्णय सबसे ज़्यादा मायने रखते हैं।")

    section_heading("10. करियर एवं धन (Career & Wealth)", "💼")
    for kind, txt in r["career"]:
        (st.success if kind == "good" else st.warning if kind == "warn" else st.info)(txt)
    st.caption("सभी फल कुंडली के सामान्य ग्रह-योगों पर आधारित हैं; निर्णय सोच-समझकर और योग्य सलाह से लें।")
                 
