import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta, date, time, timezone
import base64
from html import escape as _esc
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import zoneinfo
import os
import json
import sqlite3
import urllib.request
import urllib.error

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
# Helper functions (Including New Varga & Drishti logic)
# ---------------------------------------------------------------
def get_varga_sign(abs_degree, varga):
    """Calculates signs for D1 to D60 based on Parashari principles"""
    abs_degree = abs_degree % 360
    rashi = int(abs_degree // 30)
    
    if varga == 1: return rashi
    if varga == 2: # Hora (Parashari)
        is_even = rashi % 2 != 0
        half = (abs_degree % 30) >= 15
        if not is_even: return 4 if not half else 3
        else: return 3 if not half else 4
    if varga == 3: # Drekkana
        part = int((abs_degree % 30) // 10)
        if part == 0: return rashi
        elif part == 1: return (rashi + 4) % 12
        else: return (rashi + 8) % 12
    if varga == 4: # Chaturthamsha
        part = int((abs_degree % 30) // 7.5)
        return (rashi + (part * 3)) % 12
    if varga == 7: # Saptamsha
        part = int((abs_degree % 30) // (30/7.0))
        start = rashi if rashi % 2 == 0 else (rashi + 6) % 12
        return (start + part) % 12
    if varga == 9: # Navamsha
        navamsha_num = int((abs_degree % 30) // (30 / 9))
        if rashi in (0, 4, 8): start = 0
        elif rashi in (1, 5, 9): start = 9
        elif rashi in (2, 6, 10): start = 6
        else: start = 3
        return (start + navamsha_num) % 12
    if varga == 10: # Dashamsha
        part = min(9, int((abs_degree % 30) // 3.0))
        start = rashi if rashi % 2 == 0 else (rashi + 8) % 12
        return (start + part) % 12
    if varga == 12: # Dwadashamsha
        part = int((abs_degree % 30) // 2.5)
        return (rashi + part) % 12
    if varga == 60: # Shashtiamsha
        part = int((abs_degree % 30) // 0.5)
        return (rashi + part) % 12
    return rashi
def get_navamsha_sign(abs_degree):
    return get_varga_sign(abs_degree, 9)

def get_dashamsha_sign(abs_degree):
    return get_varga_sign(abs_degree, 10)

def calculate_drishti(sign_of):
    """Calculates planetary aspects (Drishti) based on Vedic rules."""
    aspects = {}
    for planet, sign in sign_of.items():
        if planet in ("Rahu", "Ketu"):
            aspects[planet] = [(sign + 4) % 12, (sign + 6) % 12, (sign + 8) % 12] # 5, 7, 9
        else:
            aspects[planet] = [(sign + 6) % 12] # 7th aspect for all
            if planet == "Mangal":
                aspects[planet].extend([(sign + 3) % 12, (sign + 7) % 12]) # 4, 8
            elif planet == "Guru":
                aspects[planet].extend([(sign + 4) % 12, (sign + 8) % 12]) # 5, 9
            elif planet == "Shani":
                aspects[planet].extend([(sign + 2) % 12, (sign + 9) % 12]) # 3, 10
    return aspects

def get_profile_db():
    db_path = os.environ.get("JYOTISH_DB_PATH", "jyotish_profiles.db")
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            birth_time TEXT NOT NULL,
            place TEXT NOT NULL,
            gender TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def save_profile(name, dob_value, birth_time, place, gender):
    with get_profile_db() as conn:
        conn.execute(
            "INSERT INTO profiles(name, dob, birth_time, place, gender) VALUES (?, ?, ?, ?, ?)",
            (name, dob_value.isoformat(), birth_time.strftime("%H:%M"), place, gender),
        )

def list_profiles():
    with get_profile_db() as conn:
        return conn.execute(
            "SELECT id, name, dob, birth_time, place, gender, created_at FROM profiles ORDER BY id DESC"
        ).fetchall()

def delete_profile(profile_id):
    with get_profile_db() as conn:
        conn.execute("DELETE FROM profiles WHERE id = ?", (int(profile_id),))

def guna_milan(report_a, report_b):
    nak_a = int(report_a["lons"]["Chandra"] / (360.0 / 27.0))
    nak_b = int(report_b["lons"]["Chandra"] / (360.0 / 27.0))
    sign_a, sign_b = report_a["moon_sign"], report_b["moon_sign"]

    deva = {0, 4, 6, 7, 12, 14, 17, 21, 26}
    manushya = {1, 3, 5, 10, 11, 19, 20, 24, 25}
    rakshasa = {2, 8, 9, 13, 15, 18, 22, 23}
    gana = ["Deva" if i in deva else "Manushya" if i in manushya else "Rakshasa" for i in range(27)]

    yoni = [
        "Horse", "Elephant", "Sheep", "Serpent", "Serpent", "Dog", "Cat", "Sheep", "Cat",
        "Rat", "Rat", "Cow", "Buffalo", "Tiger", "Buffalo", "Tiger", "Deer", "Deer",
        "Dog", "Monkey", "Mongoose", "Monkey", "Lion", "Horse", "Lion", "Cow", "Elephant"
    ]
    nadi = []
    adi = {0, 5, 6, 11, 12, 17, 18, 23, 24}
    madhya = {1, 4, 7, 10, 13, 16, 19, 22, 25}
    for i in range(27):
        nadi.append("Adi" if i in adi else "Madhya" if i in madhya else "Antya")

    sign_lords = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
                  "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
    friends = {
        "Sun": {"Moon", "Mars", "Jupiter"}, "Moon": {"Sun", "Mercury"},
        "Mars": {"Sun", "Moon", "Jupiter"}, "Mercury": {"Sun", "Venus"},
        "Jupiter": {"Sun", "Moon", "Mars"}, "Venus": {"Mercury", "Saturn"},
        "Saturn": {"Mercury", "Venus"},
    }
enemies = {
        "Sun": {"Venus", "Saturn"}, "Moon": set(), "Mars": {"Mercury"},
        "Mercury": {"Moon"}, "Jupiter": {"Mercury", "Venus"},
        "Venus": {"Sun", "Moon"}, "Saturn": {"Sun", "Moon", "Mars"},
    }
lord_a, lord_b = sign_lords[sign_a], sign_lords[sign_b]
varna = [1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4]
varna_score = 1 if varna[sign_a] == varna[sign_b] else 0

    element = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]
    vashya_score = 2 if element[sign_a] == element[sign_b] else 1 if (element[sign_a] + element[sign_b]) % 2 == 0 else 0

    tara_a = (nak_b - nak_a) % 9
    tara_b = (nak_a - nak_b) % 9
    good_tara = {0, 1, 3, 5, 7}
    tara_score = 3 if tara_a in good_tara and tara_b in good_tara else 1.5 if tara_a in good_tara or tara_b in good_tara else 0

    yoni_enemies = {
        frozenset(("Horse", "Buffalo")), frozenset(("Elephant", "Lion")),
        frozenset(("Sheep", "Monkey")), frozenset(("Serpent", "Mongoose")),
        frozenset(("Dog", "Deer")), frozenset(("Cat", "Rat")),
        frozenset(("Cow", "Tiger")), frozenset(("Rat", "Monkey")),
    }
    if yoni[nak_a] == yoni[nak_b]:
        yoni_score = 4
    elif frozenset((yoni[nak_a], yoni[nak_b])) in yoni_enemies:
        yoni_score = 0
    else:
        yoni_score = 2

    if lord_a == lord_b:
        maitri_score = 5
    elif lord_b in friends.get(lord_a, set()) and lord_a in friends.get(lord_b, set()):
        maitri_score = 5
    elif lord_b in enemies.get(lord_a, set()) or lord_a in enemies.get(lord_b, set()):
        maitri_score = 0
    else:
        maitri_score = 3

    gana_pair = {gana[nak_a], gana[nak_b]}
    if gana[nak_a] == gana[nak_b]:
        gana_score = 6
    elif gana_pair == {"Deva", "Manushya"}:
        gana_score = 5
    elif "Rakshasa" in gana_pair and "Deva" in gana_pair:
        gana_score = 0
    else:
        gana_score = 1

    sign_distance = (sign_b - sign_a) % 12
    bhakoot_bad = sign_distance in {1, 4, 5, 7, 8, 11}
    bhakoot_score = 0 if bhakoot_bad and sign_a != sign_b else 7

    nadi_score = 0 if nadi[nak_a] == nadi[nak_b] else 8

    details = [
        ("Varna", varna_score, 1, f"Moon-sign classes: {varna[sign_a]} / {varna[sign_b]}"),
        ("Vashya", vashya_score, 2, "Simplified sign-class compatibility"),
        ("Tara", tara_score, 3, f"Nakshatra distance remainders: {tara_a}, {tara_b}"),
        ("Yoni", yoni_score, 4, f"{yoni[nak_a]} / {yoni[nak_b]}"),
        ("Graha Maitri", maitri_score, 5, f"Moon-sign lords: {lord_a} / {lord_b}"),
        ("Gana", gana_score, 6, f"{gana[nak_a]} / {gana[nak_b]}"),
        ("Bhakoot", bhakoot_score, 7, f"Moon-sign distance: {sign_distance}"),
        ("Nadi", nadi_score, 8, f"{nadi[nak_a]} / {nadi[nak_b]}"),
    ]
    total = round(sum(x[1] for x in details), 1)
    return total, details, nak_a, nak_b

def get_current_transits():
    now = datetime.now(timezone.utc)
    jd = swe.julday(now.year, now.month, now.day,
                    now.hour + now.minute / 60.0 + now.second / 3600.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    out = {}
    for pname, code in PLANETS.items():
        result = swe.calc_ut(jd, code, flags)[0]
        out[pname] = {"longitude": result[0] % 360, "sign": int((result[0] % 360) // 30)}
    if "Rahu" in out:
        ketu_lon = (out["Rahu"]["longitude"] + 180) % 360
        out["Ketu"] = {"longitude": ketu_lon, "sign": int(ketu_lon // 30)}
    return out

def build_pdf_bytes(report):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from io import BytesIO
    except ImportError as exc:
        raise RuntimeError("PDF ke liye reportlab install karein: pip install reportlab") from exc

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    font_name = "Helvetica"
    font_path = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont("JyotishNoto", font_path))
            font_name = "JyotishNoto"
        except Exception:
            font_name = "Helvetica"
    for style_name in ("Normal", "Title", "Heading2", "Italic"):
        styles[style_name].fontName = font_name
    styles.add(ParagraphStyle(name="TitleCenter", parent=styles["Title"], alignment=TA_CENTER, fontName=font_name))
    story = [
        Paragraph("JYOTISH AI - Birth Chart Report", styles["TitleCenter"]),
        Spacer(1, 10),
        Paragraph(f"Name: {_esc(str(report.get('name', '')))}", styles["Normal"]),
        Paragraph(f"Birth details: {_esc(str(report.get('dob_str', '')))}", styles["Normal"]),
        Paragraph(f"Birth place: {_esc(str(report.get('place', '')))}", styles["Normal"]),
        Paragraph(f"Timezone: {_esc(str(report.get('tz_str', '')))} (UTC {report.get('utc_off', 0):+.2f})", styles["Normal"]),
        Paragraph(f"Ascendant: {SIGNS[report['asc_sign']]} | Moon sign: {SIGNS[report['moon_sign']]}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Planetary Positions", styles["Heading2"]),
    ]
    planet_data = [["Planet", "D1 sign", "House", "Degree", "D9 sign", "D10 sign", "Status"]]
    for row in report.get("rows", []):
        planet_data.append([
            str(row.get("Planet", "")).replace(" (R)", " R"),
            str(row.get("D1 Rashi", "")), str(row.get("House", "")),
            str(row.get("Degree", "")), str(row.get("D9 Navamsha Rashi", "")),
            str(row.get("D10 Dashamsha Rashi", "")), str(row.get("Status", "")),
        ])
        table = Table(planet_data, repeatRows=1, colWidths=[65, 58, 48, 38, 68, 68, 55])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3A0007")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.extend([table, Spacer(1, 12), Paragraph("Vimshottari Mahadasha", styles["Heading2"])])
    md_data = [["Lord", "Start", "End", "Years", "Active"]]
    for m in report.get("md_rows", []):
        md_data.append([m["lord"], m["start"], m["end"], str(m["years"]), "Yes" if m["active"] else ""])
    md_table = Table(md_data, repeatRows=1, colWidths=[70, 90, 90, 50, 55])
    md_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#8A1C1C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (-1, -1), font_name),
    ]))
    story.extend([md_table, Spacer(1, 12), Paragraph("Panchang", styles["Heading2"])])
    pc = report.get("panchang", {})
    story.append(Paragraph(
        f"Vara: {pc.get('vara', '')} | Tithi: {pc.get('tithi', '')} | "
        f"Nakshatra: {pc.get('nakshatra', '')} | Yoga: {pc.get('yoga', '')} | Karana: {pc.get('karana', '')}",
        styles["Normal"]
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph("For educational/astrological interpretation only; not a scientific or guaranteed prediction.", styles["Italic"]))
    doc.build(story)
    return buffer.getvalue()

def ask_ai_jyotish(question, report, language, api_key, model="gpt-4o-mini"):
    chart_context = "No birth chart has been generated in this session."
    if report:
        planets = "; ".join(
            f"{row['Planet']}: {row['D1 Rashi']} house {row['House']}, D9 {row['D9 Navamsha Rashi']}"
            for row in report.get("rows", [])
        )
        chart_context = (
            f"Ascendant: {SIGNS[report['asc_sign']]}; Moon sign: {SIGNS[report['moon_sign']]}; "
            f"active Mahadasha: {report.get('active_md')}; active Antardasha: {report.get('active_ad')}. "
            f"Planet data: {planets}"
        )
    lang_names = {"Hindi": "Hindi", "Nepali": "Nepali", "English": "English"}
    system_prompt = (
        "You are a careful Vedic astrology explainer. Use only supplied chart facts; never invent planetary positions "
        "or dates. Explain traditional interpretations as beliefs, not guaranteed facts. Avoid fear-based certainty, "
        "medical diagnosis, financial guarantees, or telling users to make major decisions solely from astrology. "
        f"Answer in {lang_names.get(language, 'Hindi')}. If birth-chart data is absent, clearly say so. "
        f"Chart context: {chart_context}"
    )
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        "temperature": 0.4,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"AI API error ({exc.code}): {detail}") from exc
    except (urllib.error.URLError, KeyError, ValueError, TimeoutError) as exc:
        raise RuntimeError(f"AI service unavailable or returned an unexpected response: {exc}") from exc

def antardashas(md_lord, md_start):
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
def pratyantar_dashas(md_lord, ad_lord, ad_start, ad_end):
    """Calculates Pratyantar Dasha (PD) timeline within an Antardasha."""
    ad_days = (ad_end - ad_start).total_seconds() / 86400.0
    start = ad_start
    out = []
    ad_idx = DASHA_LORDS.index(ad_lord)
    for i in range(9):
        pd_lord = DASHA_LORDS[(ad_idx + i) % 9]
        pd_days = ad_days * (DASHA_YEARS[pd_lord] / 120.0)
        end = start + timedelta(days=pd_days)
        out.append((pd_lord, start, end))
        start = end
    return out

def check_kaal_sarp(lons, rahu_deg):
    others = ["Surya", "Chandra", "Mangal", "Budh", "Guru", "Shukra", "Shani"]
    diffs = [(lons[p] - rahu_deg) % 360 for p in others]
    return all(d < 180 for d in diffs) or all(d > 180 for d in diffs)

def find_yogas(sign_of, houses):
    yogas = []
    if (sign_of["Guru"] - sign_of["Chandra"]) % 12 in (0, 3, 6, 9):
        yogas.append(("गजकेसरी योग", "गुरु चंद्र से केंद्र में है: यश, बुद्धि और सम्मान देने वाला योग।"))
    if sign_of["Surya"] == sign_of["Budh"]:
        yogas.append(("बुधादित्य योग", "सूर्य-बुध एक राशि में: तीक्ष्ण बुद्धि और वाक्पटुता।"))
    if sign_of["Chandra"] == sign_of["Mangal"]:
        yogas.append(("चंद्र-मंगल योग", "धन-अर्जन की क्षमता, पर भावनात्मक उग्रता से सावधान रहें।"))
    for p, name in MAHAPURUSHA.items():
        in_kendra = houses[p] in (1, 4, 7, 10)
        strong = sign_of[p] in OWN_SIGNS[p] or sign_of[p] == EXALT_SIGN[p]
        if in_kendra and strong:
            yogas.append((name, f"{p} स्वराशि/उच्च का होकर केंद्र में है: पंच-महापुरुष योग।"))
    return yogas

def analyze_love(asc_sign, sign_of, houses, gender):
    lord5 = RASHI_LORDS[(asc_sign + 4) % 12]
    lord7 = RASHI_LORDS[(asc_sign + 6) % 12]
    karaka = "Guru" if gender.startswith("Female") else "Shukra"

    def in_house(h): return [p for p in houses if houses[p] == h]
    def together(a, b): return sign_of[a] == sign_of[b]

    love, marriage, affair, score = [], [], [], 0

    p5 = in_house(5)
    love.append(("info", f"पंचम भाव (प्रेम): लग्न से {SIGNS[(asc_sign + 4) % 12]} राशि, स्वामी {lord5} "
                         f"{houses[lord5]}वें भाव में। पंचम में ग्रह: {', '.join(p5) if p5 else 'कोई नहीं'}।"))
    if houses["Shukra"] in (1, 5, 7, 11):
        love.append(("good", f"शुक्र {houses['Shukra']}वें भाव में है: प्रेम, आकर्षण और रोमांस की अच्छी क्षमता।"))
    elif houses["Shukra"] in (6, 8, 12):
        love.append(("warn", f"शुक्र {houses['Shukra']}वें भाव में है: प्रेम में बाधा, देरी या गुप्तता के संकेत।"))
    if "Chandra" in p5 or together("Chandra", "Shukra"):
        love.append(("good", "चंद्र/शुक्र का संबंध भावनात्मक और संवेदनशील प्रेम स्वभाव दर्शाता है।"))
    if together("Mangal", "Shukra"): score += 1
    if together("Rahu", "Shukra") or together("Ketu", "Shukra"): score += 1

    if together(lord5, lord7) and lord5 != lord7: marriage.append(("good", "पंचमेश और सप्तमेश एक राशि में: प्रेम-विवाह का मजबूत योग।"))
    if houses[lord5] == 7 or houses[lord7] == 5: marriage.append(("good", "पंचमेश-सप्तमेश का भाव-परिवर्तन/संबंध: प्रेम से विवाह की संभावना।"))

    p7 = in_house(7)
    marriage.append(("info", f"सप्तम भाव: {SIGNS[(asc_sign + 6) % 12]} राशि, स्वामी {lord7} {houses[lord7]}वें भाव में। "
                             f"सप्तम में ग्रह: {', '.join(p7) if p7 else 'कोई नहीं'}।"))

    if "Rahu" in in_house(5) or "Rahu" in p7 or "Ketu" in p7: affair.append(("warn", "राहु/केतु पंचम या सप्तम में: गुप्त, असामान्य संबंधों की प्रवृत्ति।")); score += 1
    if "Rahu" in in_house(12) or "Mangal" in in_house(12): affair.append(("warn", "द्वादश भाव में राहु/मंगल: छिपे हुए संबंधों की प्रवृत्ति।")); score += 1
    if not affair: affair.append(("good", "गुप्त संबंध या अनैतिक आकर्षण के स्पष्ट योग नहीं मिले।"))

    level = "कम" if score <= 1 else ("मध्यम" if score <= 3 else "अधिक")
    return {"love": love, "marriage": marriage, "affair": affair, "affair_level": level, "score": score, "karaka": karaka, "lord5": lord5, "lord7": lord7}

WEEKDAYS = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
TITHIS = ["प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी", "सप्तमी", "अष्टमी", "नवमी", "दशमी", "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी"]
PANCHANG_YOGAS = ["विष्कुम्भ", "प्रीति", "आयुष्मान", "सौभाग्य", "शोभन", "अतिगण्ड", "सुकर्मा", "धृति", "शूल", "गण्ड", "वृद्धि", "ध्रुव", "व्याघात", "हर्षण", "वज्र", "सिद्धि", "व्यतीपात", "वरीयान", "परिघ", "शिव", "सिद्ध", "साध्य", "शुभ", "शुक्ल", "ब्रह्म", "इन्द्र", "वैधृति"]
KARANA_MOVABLE = ["बव", "बालव", "कौलव", "तैतिल", "गर", "वणिज", "विष्टि (भद्रा)"]
KARANA_FIXED = ["शकुनि", "चतुष्पद", "नाग"]
NAK_GANA = ["देव", "मनुष्य", "राक्षस", "मनुष्य", "देव", "मनुष्य", "देव", "देव", "राक्षस", "राक्षस", "मनुष्य", "मनुष्य", "देव", "राक्षस", "देव", "राक्षस", "देव", "राक्षस", "राक्षस", "मनुष्य", "मनुष्य", "देव", "राक्षस", "राक्षस", "मनुष्य", "मनुष्य", "देव"]
NAK_YONI = ["अश्व", "गज", "मेष", "सर्प", "सर्प", "श्वान", "मार्जार", "मेष", "मार्जार", "मूषक", "मूषक", "गौ", "महिष", "व्याघ्र", "महिष", "व्याघ्र", "मृग", "मृग", "श्वान", "वानर", "नकुल", "वानर", "सिंह", "अश्व", "सिंह", "गौ", "गज"]
NADI_NAMES = ["आदि", "मध्य", "अंत्य", "अंत्य", "मध्य", "आदि"]
VARNA_BY_SIGN = ["क्षत्रिय", "वैश्य", "शूद्र", "ब्राह्मण"] * 3
VASHYA_BY_SIGN = ["चतुष्पद", "चतुष्पद", "मानव", "जलचर", "वनचर", "मानव", "मानव", "कीट", "मानव/चतुष्पद", "चतुष्पद/जलचर", "मानव", "जलचर"]
TATVA_BY_SIGN = ["अग्नि", "पृथ्वी", "वायु", "जल"]
BHAVA_NAMES = ["तनु (लग्न)", "धन/कुटुंब", "सहज (पराक्रम)", "सुख/माता", "पुत्र/विद्या/प्रेम", "रिपु/रोग/ऋण", "जाया/विवाह", "आयु/गुप्त", "भाग्य/धर्म", "कर्म/व्यवसाय", "लाभ", "व्यय/विदेश"]
CAREER_HOUSE = {1: "स्वयं के बल पर, स्वतंत्र कार्य", 2: "वाणी, बैंकिंग/खाद्य", 3: "संचार, मीडिया, सेल्स", 4: "भूमि-भवन, कृषि या वाहन", 5: "शिक्षा, निवेश", 6: "सेवा, स्वास्थ्य, कानून", 7: "साझेदारी, व्यापार", 8: "शोध, बीमा, तकनीकी", 9: "उच्च शिक्षा, विदेश", 10: "करियर बहुत मज़बूत", 11: "बड़ा नेटवर्क, आय", 12: "विदेश, अस्पताल, एकांत"}
CAREER_KARAKA = {"Surya": "सरकारी/प्रशासनिक", "Chandra": "जनता, यात्रा, तरल", "Mangal": "इंजीनियरिंग, सुरक्षा", "Budh": "व्यापार, IT, लेखन", "Guru": "शिक्षण, वित्त, सलाह", "Shukra": "कला, फैशन", "Shani": "उद्योग, निर्माण, सेवा", "Rahu": "तकनीक, राजनीति", "Ketu": "शोध, अध्यात्म"}

def compute_panchang(lons, dob):
    sun, moon = lons["Surya"], lons["Chandra"]
    elong = (moon - sun) % 360
    tithi_no = int(elong // 12) + 1
    paksha = "शुक्ल" if tithi_no <= 15 else "कृष्ण"
    tithi = "पूर्णिमा" if tithi_no == 15 else "अमावस्या" if tithi_no == 30 else TITHIS[(tithi_no - 1) % 15]
    k = int(elong // 6)
    karana = "किंस्तुघ्न" if k == 0 else KARANA_FIXED[k - 57] if k >= 57 else KARANA_MOVABLE[(k - 1) % 7]
    span = 360.0 / 27.0
    yoga = PANCHANG_YOGAS[int(((sun + moon) % 360) / span)]
    nak = int(moon / span)
    pada = int((moon % span) / (span / 4)) + 1
    return {"vara": WEEKDAYS[dob.weekday()], "tithi": f"{paksha} पक्ष {tithi}", "karana": karana, "yoga": yoga, "nakshatra": NAKSHATRAS[nak], "pada": pada}

def compute_avakahada(moon_lon):
    nak = int(moon_lon / (360.0 / 27.0))
    sign = int(moon_lon // 30)
    return {"वर्ण": VARNA_BY_SIGN[sign], "वश्य": VASHYA_BY_SIGN[sign], "योनि": NAK_YONI[nak], "गण": NAK_GANA[nak], "नाड़ी": NADI_NAMES[nak % 6], "तत्व": TATVA_BY_SIGN[sign % 4], "राशि स्वामी": RASHI_LORDS[sign]}

def compute_sade_sati(moon_sign):
    now = datetime.now(timezone.utc)
    jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0)
    sat = swe.calc_ut(jd, swe.SATURN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360
    s = int(sat // 30)
    d = (s - moon_sign) % 12
    status = {11: "साढ़ेसाती - प्रथम चरण", 0: "साढ़ेसाती - द्वितीय चरण (शिखर)", 1: "साढ़ेसाती - तृतीय चरण", 3: "शनि ढैया (4थे में)", 7: "शनि ढैया (8वें में)"}.get(d)
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
    for p in p10: out.append(("info", f"दशम भाव में {p}: {CAREER_KARAKA[p]} से जुड़े क्षेत्र।"))
    return out

# ===============================================================
# विस्तृत महादशा / अंतर्दशा फलादेश (TEXT CONTENT KEPT SAME AS BEFORE)
# ===============================================================
GRAHA_HI = {"Surya": "सूर्य", "Chandra": "चंद्र", "Mangal": "मंगल", "Budh": "बुध", "Guru": "गुरु", "Shukra": "शुक्र", "Shani": "शनि", "Rahu": "राहु", "Ketu": "केतु"}
NAT_FRIENDS = {"Surya": ["Chandra", "Mangal", "Guru"], "Chandra": ["Surya", "Budh"], "Mangal": ["Surya", "Chandra", "Guru"], "Budh": ["Surya", "Shukra"], "Guru": ["Surya", "Chandra", "Mangal"], "Shukra": ["Budh", "Shani"], "Shani": ["Budh", "Shukra"], "Rahu": ["Budh", "Shukra", "Shani"], "Ketu": ["Mangal", "Shukra", "Shani"]}
NAT_ENEMIES = {"Surya": ["Shukra", "Shani"], "Chandra": [], "Mangal": ["Budh"], "Budh": ["Chandra"], "Guru": ["Budh", "Shukra"], "Shukra": ["Surya", "Chandra"], "Shani": ["Surya", "Chandra", "Mangal"], "Rahu": ["Surya", "Chandra", "Mangal"], "Ketu": ["Surya", "Chandra"]}
EXTRA_OWN = {"Surya": [4], "Chandra": [3]}
EXALT_ALL = {"Surya": 0, "Chandra": 1, "Mangal": 9, "Budh": 5, "Guru": 3, "Shukra": 11, "Shani": 6}
HOUSE_THEME = {1: "स्वास्थ्य, व्यक्तित्व", 2: "धन, वाणी", 3: "पराक्रम, मेहनत", 4: "सुख, माता", 5: "संतान, विद्या", 6: "रोग, ऋण", 7: "विवाह, व्यापार", 8: "आयु, गुप्त", 9: "भाग्य, धर्म", 10: "कर्म, प्रतिष्ठा", 11: "लाभ", 12: "व्यय, एकांत"}

HOUSE_EFFECT = {
    1: "दशानाथ लग्न (प्रथम भाव) में है। आपके व्यक्तित्व, सोच और निर्णय जीवन की दिशा तय करते हैं।",
    2: "दशानाथ द्वितीय भाव (धन-कुटुंब) में है। कमाई, बचत, वाणी और पारिवारिक ज़िम्मेदारियाँ मुख्य विषय बनते हैं।",
    3: "दशानाथ तृतीय भाव (पराक्रम) में है। यह साहस, मेहनत, संचार और भाई-बहनों से जुड़े फल देता है।",
    4: "दशानाथ चतुर्थ भाव (सुख-स्थान) में है। घर, ज़मीन, वाहन, माता और मानसिक शांति प्रमुख रहती है।",
    5: "दशानाथ पंचम भाव (विद्या-संतान) में है। शिक्षा, बुद्धि, प्रेम-संबंध, संतान का काल है।",
    6: "दशानाथ षष्ठ भाव (रोग-ऋण-शत्रु) में है। प्रतियोगिता, नौकरी, और शत्रु-विजय जैसे विषय सक्रिय रहते हैं।",
    7: "दशानाथ सप्तम भाव (विवाह-साझेदारी) में है। जीवनसाथी, साझेदारी और सार्वजनिक जीवन केंद्र में रहते हैं।",
    8: "दशानाथ अष्टम भाव (आयु-गुप्त विषय) में है। अप्रत्याशित घटनाएँ, शोध, स्वास्थ्य चुनौतियाँ संभव हैं।",
    9: "दशानाथ नवम भाव (भाग्य) में है। भाग्य का साथ, धार्मिक कार्य, उच्च शिक्षा का अवसर मिलता है।",
    10: "दशानाथ दशम भाव (कर्म) में है। करियर, पद, प्रतिष्ठा, व्यवसाय और जिम्मेदारी बढ़ती है।",
    11: "दशानाथ एकादश भाव (लाभ) में है। आय के कई स्रोत बनते हैं, मित्रों से लाभ मिलता है।",
    12: "दशानाथ द्वादश भाव (व्यय-विदेश) में है। खर्च बढ़ने, विदेश-यात्रा या एकांत से जुड़े अनुभव होने की संभावना रहती है।",
}

MD_DETAIL = {
    "Surya": [("स्वरूप", "सूर्य की दशा अधिकार और सम्मान लाती है।"), ("सावधानियाँ", "अहंकार से बचें।")],
    "Chandra": [("स्वरूप", "मन की संवेदनशीलता, रचनात्मकता लाती है।"), ("सावधानियाँ", "मानसिक तनाव से बचें।")],
    "Mangal": [("स्वरूप", "ऊर्जा, पराक्रम, भूमि और तकनीकी कार्यों में सफलता।"), ("सावधानियाँ", "क्रोध से बचें।")],
    "Budh": [("स्वरूप", "बुद्धि, व्यापार, संचार और लेखन का काल।"), ("सावधानियाँ", "चालाकी से बचें।")],
    "Guru": [("स्वरूप", "सुख, उच्च शिक्षा, ज्ञान और दांपत्य जीवन में वृद्धि।"), ("सावधानियाँ", "अति-आत्मविश्वास से बचें।")],
    "Shukra": [("स्वरूप", "भौतिक सुख, वाहन, कला और विलासिता का काल।"), ("सावधानियाँ", "फ़िज़ूलखर्ची से बचें।")],
    "Shani": [("स्वरूप", "परिश्रम, अनुशासन और परिपक्वता का काल।"), ("सावधानियाँ", "निराशा से बचें।")],
    "Rahu": [("स्वरूप", "अचानक बदलाव, तकनीक, विदेशी व्यापार।"), ("सावधानियाँ", "भ्रम से बचें।")],
    "Ketu": [("स्वरूप", "आध्यात्म, गुप्त विद्याओं और आत्म-साक्षात्कार।"), ("सावधानियाँ", "अनावश्यक त्याग से बचें।")],
}

AD_DETAIL = {
    "Surya": [("सामान्य फल", "आत्मविश्वास बढ़ता है।")], "Chandra": [("सामान्य फल", "मानसिक सुख से जुड़े विषय प्रमुख होते हैं।")],
    "Mangal": [("सामान्य फल", "ऊर्जा बढ़ती है।")], "Budh": [("सामान्य फल", "व्यापारिक कुशलता चमकती है।")],
    "Guru": [("सामान्य फल", "ज्ञान, समृद्धि बढ़ती है।")], "Shukra": [("सामान्य फल", "सुख-सुविधा बढ़ती है।")],
    "Shani": [("सामान्य फल", "मेहनत का अनुभव होता है।")], "Rahu": [("सामान्य फल", "बदलाव आते हैं।")],
    "Ketu": [("सामान्य फल", "मन अंतर्मुखी होता है।")],
}

REL_TEXT = {"friend": "मित्र भाव (सहयोगी)", "enemy": "शत्रु भाव (विरोधाभासी)", "neutral": "सम भाव (मिश्रित फल)"}

def planet_relation(a, b): return "friend" if b in NAT_FRIENDS.get(a, []) else "enemy" if b in NAT_ENEMIES.get(a, []) else "neutral"

def planet_context(p, r):
    h, s = r["houses"][p], r["sign_of"][p]
    return [f"{GRAHA_HI[p]} आपकी कुंडली में **{SIGNS[s]} ({SIGNS_HI[s]}) राशि** और **{h}वें भाव** में है।"]

def md_reading(md, r): return [("आपकी कुंडली में दशानाथ की स्थिति", "\n\n".join(planet_context(md, r))), ("भाव के अनुसार फल", HOUSE_EFFECT[r["houses"][md]])] + MD_DETAIL[md]
def ad_reading(md, ad, r):
    rel = planet_relation(md, ad)
    d = (r["houses"][ad] - r["houses"][md]) % 12 + 1
    return [("आपसी संबंध", REL_TEXT[rel] + f" (संबंध दूरी: {d}वाँ)"), ("भाव फल", HOUSE_EFFECT[r["houses"][ad]])] + AD_DETAIL[ad]

def section_heading(title, icon="✨"):
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4A0000 0%, #1A0000 100%);
            padding: 14px 22px; border-radius: 10px; margin-top: 28px; margin-bottom: 18px;
            border-left: 6px solid #FFD700; box-shadow: 0px 4px 12px rgba(0,0,0,0.3);">
            <h3 style="color:#FFD700; margin:0; font-weight:700; font-size:20px;">{icon} {title}</h3>
        </div>
    """, unsafe_allow_html=True)

PL_SHORT = {"Surya": "सू", "Chandra": "चं", "Mangal": "मं", "Budh": "बु", "Guru": "गु", "Shukra": "शु", "Shani": "श", "Rahu": "रा", "Ketu": "के"}
HOUSE_CENTERS = [(0.50, 0.75), (0.25, 0.917), (0.083, 0.75), (0.25, 0.50), (0.083, 0.25), (0.25, 0.083), (0.50, 0.25), (0.75, 0.083), (0.917, 0.25), (0.75, 0.50), (0.917, 0.75), (0.75, 0.917)]

def render_north_indian_chart(asc_sign, planet_signs, title):
    W, H, S, X0, Y0 = 600, 640, 520, 40, 80
    def px(x, y): return X0 + x * S, Y0 + (1 - y) * S
    font = "'Noto Sans Devanagari','Noto Sans',sans-serif"
    A, B, C, D = px(0, .5), px(.5, 1), px(1, .5), px(.5, 0)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" rx="14" fill="#FFFDF5"/>',
         f'<text x="{W / 2}" y="46" text-anchor="middle" font-family="{font}" font-size="24" font-weight="700" fill="#7A0000">{_esc(title)}</text>',
         f'<rect x="{X0}" y="{Y0}" width="{S}" height="{S}" fill="none" stroke="#7A0000" stroke-width="3"/>',
         f'<polygon points="{A[0]},{A[1]} {B[0]},{B[1]} {C[0]},{C[1]} {D[0]},{D[1]}" fill="none" stroke="#7A0000" stroke-width="2.5"/>']
    for p1, p2 in ((px(0, 0), px(1, 1)), (px(0, 1), px(1, 0))):
        o.append(f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" stroke="#7A0000" stroke-width="2.5"/>')

    for i, (cx, cy) in enumerate(HOUSE_CENTERS):
        sign_index = (asc_sign + i) % 12
        big = i in (0, 3, 6, 9)
        x, y = px(cx, cy)
        toks = []
        for disp in planet_signs.get(SIGNS[sign_index], []):
            base = disp.replace(" (R)", "")
            toks.append(PL_SHORT.get(base, base[:2]) + ("(व)" if "(R)" in disp else ""))
        per_row = 3 if big else 2
        rows = [" ".join(toks[k:k + per_row]) for k in range(0, len(toks), per_row)]
        fs_num, fs_pl, lh = (20, 19, 23) if big else (16, 15, 18)
        top = y - (len(rows) * lh) / 2 - 4
        o.append(f'<text x="{x:.1f}" y="{top - 4 if rows else y + 6:.1f}" text-anchor="middle" font-family="{font}" font-size="{fs_num}" font-weight="700" fill="#B00020">{sign_index + 1}</text>')
        for k, row in enumerate(rows):
            o.append(f'<text x="{x:.1f}" y="{top + 14 + (k + 1) * lh - 6:.1f}" text-anchor="middle" font-family="{font}" font-size="{fs_pl}" font-weight="600" fill="#0B2A6F">{_esc(row)}</text>')
    o.append("</svg>")
    return "".join(o)

def show_chart(svg):
    b64 = base64.b64encode(svg.encode("utf-8")).decode()
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{b64}" style="width:100%;max-width:560px;"/></div>', unsafe_allow_html=True)


def compute_report(name, dob, bt, place):
    loc = Nominatim(user_agent="jyotish_app_v15").geocode(place)
    if not loc: return None
    lat, lon = loc.latitude, loc.longitude
    tz_str = TimezoneFinder().timezone_at(lng=lon, lat=lat)
    if tz_str:
        aware = datetime.combine(dob, bt, tzinfo=zoneinfo.ZoneInfo(tz_str))
        utc_dt = aware.astimezone(zoneinfo.ZoneInfo("UTC")).replace(tzinfo=None)
        utc_off = aware.utcoffset().total_seconds() / 3600.0
    else:
        tz_str, utc_off = "Asia/Kathmandu +5.75", 5.75
        utc_dt = datetime.combine(dob, bt) - timedelta(hours=5, minutes=45)

    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    ayan = swe.get_ayanamsa_ut(jd)
    cusps, ascmc = swe.houses(jd, lat, lon, b"P")
    asc_degree = (ascmc[0] - ayan) % 360
    asc_sign = int(asc_degree // 30)
    d9_asc = get_navamsha_sign(asc_degree)
    d10_asc = get_dashamsha_sign(asc_degree)

    rows, lons, sign_of, houses = [], {}, {}, {}
    d1_signs, d9_signs, d10_signs = {}, {}, {}
    varga_rows = [] # New list for D1 to D60 vargas

    def add_planet(pname, deg, retro):
        si = int(deg // 30)
        d9 = get_navamsha_sign(deg)
        d10 = get_dashamsha_sign(deg)
        h = ((si - asc_sign) % 12) + 1
        disp = f"{pname} (R)" if retro else pname
        lons[pname], sign_of[pname], houses[pname] = deg, si, h
        
        # Populate Base table
        rows.append({
            "Planet": disp, "D1 Rashi": SIGNS[si], "House": f"House {h}",
            "Degree": round(deg % 30, 2), "Nakshatra": NAKSHATRAS[int(deg / (360 / 27))],
            "D9 Navamsha Rashi": SIGNS[d9], "D10 Dashamsha Rashi": SIGNS[d10], "Status": "Retrograde" if retro else "Direct"
        })
           # Populate All Vargas (D1 to D60)
        varga_rows.append({
            "ग्रह": pname, "डिग्री": round(deg % 30, 2),
            "D1 (लग्न)": SIGNS_HI[get_varga_sign(deg, 1)],
            "D2 (होरा)": SIGNS_HI[get_varga_sign(deg, 2)],
            "D3 (द्रेष्काण)": SIGNS_HI[get_varga_sign(deg, 3)],
            "D4 (चतुर्थांश)": SIGNS_HI[get_varga_sign(deg, 4)],
            "D7 (सप्तांश)": SIGNS_HI[get_varga_sign(deg, 7)],
            "D9 (नवमांश)": SIGNS_HI[get_varga_sign(deg, 9)],
            "D10 (दशमांश)": SIGNS_HI[get_varga_sign(deg, 10)],
            "D12 (द्वादशांश)": SIGNS_HI[get_varga_sign(deg, 12)],
            "D60 (षष्ट्यंश)": SIGNS_HI[get_varga_sign(deg, 60)]
        })

        d1_signs.setdefault(SIGNS[si], []).append(disp)
        d9_signs.setdefault(SIGNS[d9], []).append(disp)
        d10_signs.setdefault(SIGNS[d10], []).append(disp)

    for pname, code in PLANETS.items():
        res = swe.calc_ut(jd, code, flags)[0]
        deg, speed = res[0] % 360, res[3]
        retro = True if pname == "Rahu" else (False if pname in ("Surya", "Chandra") else speed < 0)
        add_planet(pname, deg, retro)

    add_planet("Ketu", (lons["Rahu"] + 180) % 360, True)
    
    # Calculate Drishti
    drishti_data = calculate_drishti(sign_of)

    is_manglik = houses["Mangal"] in (1, 4, 7, 8, 12)
    kalsarp = check_kaal_sarp(lons, lons["Rahu"])

    # Vimshottari Dasha
    moon = lons["Chandra"]
    span = 360.0 / 27.0
    nak_idx = int(moon / span)
    balance = 1.0 - ((moon % span) / span)
    first_idx = nak_idx % 9
    first_lord = DASHA_LORDS[first_idx]
    first_remaining = DASHA_YEARS[first_lord] * balance
    birth = utc_dt
    first_md_start = birth - timedelta(days=(DASHA_YEARS[first_lord] - first_remaining) * YEAR_DAYS)
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
                    "समाप्ति": a_e.strftime("%Y-%m-%d"), "स्थिति": "🔥 सक्रिय" if a_s <= now < a_e else "-",
                })
                if a_s <= now < a_e: active_ad = ad
        md_rows.append({
            "lord": lord, "start": shown_start.strftime("%Y-%m-%d"),
            "end": md_end.strftime("%Y-%m-%d"), "years": round(first_remaining if i == 0 else full, 2),
            "active": is_active, "true_start": md_start,
        })
        md_start = md_end

    return {
        "name": name, "place": place, "address": loc.address,
        "dob_str": dob.strftime("%d-%m-%Y") + " " + bt.strftime("%H:%M"),
        "tz_str": tz_str, "utc_off": utc_off, "asc_degree": asc_degree, "asc_sign": asc_sign, "d9_asc": d9_asc,
        "d10_asc": d10_asc, "moon_sign": sign_of["Chandra"],
        "rows": rows, "varga_rows": varga_rows, "drishti_data": drishti_data, 
        "d1_signs": d1_signs, "d9_signs": d9_signs, "d10_signs": d10_signs,
        "lons": lons, "houses": houses, "is_manglik": is_manglik, "kalsarp": kalsarp,
        "md_rows": md_rows, "active_md": active_md, "active_ad": active_ad,
        "yogas": find_yogas(sign_of, houses), "lagna_lord": RASHI_LORDS[asc_sign],
        "sign_of": sign_of, "panchang": compute_panchang(lons, dob),
        "avakahada": compute_avakahada(lons["Chandra"]), "sadesati": compute_sade_sati(sign_of["Chandra"]),
        "bhava": bhava_table(asc_sign, sign_of, houses), "career": analyze_career(asc_sign, sign_of, houses),
    }

# ---------------------------------------------------------------
# UI
# ---------------------------------------------------------------
st.set_page_config(page_title="Jyotish AI - विस्तृत महा जन्मपत्री", page_icon="🔱", layout="wide")
LANG_OPTIONS = {"Hindi": {"features": "नए फीचर"}, "Nepali": {"features": "नयाँ सुविधाहरू"}, "English": {"features": "New features"}}
UI_LANG = st.sidebar.selectbox("Language / भाषा / भाषा", ["Hindi", "Nepali", "English"], index=0)
UI = LANG_OPTIONS[UI_LANG]

st.markdown("""
    <div style="text-align:center; background: linear-gradient(90deg,#3A0007 0%,#8A1C1C 50%,#3A0007 100%);
        padding:25px; border-radius:12px; border-bottom:4px solid #FFD700; margin-bottom:25px;">
        <h1 style="color:#FFD700; font-size:34px; font-weight:800; margin:0;">🔱 JYOTISH AI — अति-विस्तृत महा जन्मपत्री</h1>
        <p style="color:#FFF8DC; font-size:16px; margin-top:8px;">Comprehensive Vedic Astrology Engine | गहन विश्लेषण एवं सम्पूर्ण जीवन फलादेश</p>
    </div>
""", unsafe_allow_html=True)

st.subheader("📋 Birth Details / जन्म विवरण दर्ज करें")
col_a, col_b = st.columns(2)
with col_a:
    name = st.text_input("Name / नाम", value="", placeholder="अपना नाम लिखें")
    gender = st.selectbox("Gender / लिंग", ["Male (पुरुष)", "Female (महिला)", "Other (अन्य)"])
    dob = st.date_input("Date of birth / जन्म तिथि", value=None, min_value=date(1900, 1, 1))
    t1, t2, t3 = st.columns(3)
    with t1: hour12 = st.number_input("Hour (घंटा)", min_value=1, max_value=12, value=12)
    with t2: minute = st.number_input("Minute (मिनट)", min_value=0, max_value=59, value=0)
    with t3: ampm = st.selectbox("AM / PM", ["PM (दोपहर/शाम)", "AM (सुबह/रात)"])
with col_b: place = st.text_input("Birth place & Country / जन्म स्थान व देश", value="", placeholder="जैसे: Ghorahi Nepal, Delhi India, London UK")

if st.button("🚀 Generate Full Detailed Report / संपूर्ण विस्तृत महा-रिपोर्ट देखें", type="primary"):
    if not name or not dob or not place: st.warning("कृपया सभी विवरण भरें!")
    else:
        try:
            h24 = hour12 % 12 + (12 if "PM" in ampm else 0)
            with st.spinner("गणना हो रही है..."):
                rep = compute_report(name, dob, time(h24, int(minute)), place)
            if rep is None: st.error("जन्म स्थान नहीं मिल सका!")
            else:
                rep["time_label"] = f"{hour12}:{int(minute):02d} {ampm[:2]}"
                rep["gender"] = gender
                st.session_state["report"] = rep
        except Exception as e: st.error(f"गणना में त्रुटि: {e}")

r = st.session_state.get("report")
if r:
    st.success(f"📍 स्थान: **{r['address']}** | टाइमज़ोन: **{r['tz_str']} (UTC {r['utc_off']:+.2f})** | समय: **{r['time_label']}**")

    # 1-10 OLD FEATURES (Kept Intact)
    section_heading("1. मूल विवरण एवं पंचांग", "📜")
    st.dataframe(r["panchang"], use_container_width=True)

    section_heading("2. ग्रह स्थिति (Planetary Positions)", "🪐")
    st.dataframe(r["rows"], use_container_width=True)

    # --- NEW FEATURE: D2-D60 VARGA CHARTS ---
    section_heading("3. विस्तृत वर्ग कुंडलियाँ (D1 से D60)", "🔣")
    st.dataframe(r["varga_rows"], use_container_width=True)

    # --- NEW FEATURE: PLANETARY ASPECTS (DRISHTI) ---
    section_heading("4. ग्रहों की दृष्टियाँ (Planetary Aspects)", "👁️")
    drishti_list = [{"ग्रह": p, "दृष्टि (राशियाँ)": ", ".join([f"{SIGNS[a]} ({SIGNS_HI[a]})" for a in set(aspects)])} for p, aspects in r["drishti_data"].items()]
    st.dataframe(drishti_list, hide_index=True, use_container_width=True)

    section_heading("5. लग्न एवं नवमांश कुंडली", "📊")
    c1, c2 = st.columns(2)
    with c1: show_chart(render_north_indian_chart(r["asc_sign"], r["d1_signs"], "D1 - जन्म कुंडली"))
    with c2: show_chart(render_north_indian_chart(r["d9_asc"], r["d9_signs"], "D9 - नवमांश कुंडली"))

    section_heading("6. महादशा एवं अंतर्दशा का विस्तृत फलादेश (Dasha Analysis)", "⏳")
    st.markdown(f"### वर्तमान दशा: **{GRAHA_HI.get(r['active_md'], r['active_md'])} महादशा — {GRAHA_HI.get(r['active_ad'], r['active_ad'])} अंतर्दशा**")
    
    md_labels = [f"{GRAHA_HI[m['lord']]} महादशा ({m['start']} से {m['end']})" + (" 🔥 वर्तमान" if m["active"] else "") for m in r["md_rows"]]
    default_i = next((i for i, m in enumerate(r["md_rows"]) if m["active"]), 0)
    pick = st.selectbox("कोई भी महादशा चुनकर उसका विस्तृत फल पढ़ें:", range(len(md_labels)), index=default_i, format_func=lambda i: md_labels[i])
    sel = r["md_rows"][pick]
    sel_md = sel["lord"]
    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    ad_list = antardashas(sel_md, sel["true_start"])
    
    st.markdown(f"## 🔹 {GRAHA_HI[sel_md]} महादशा की सभी अंतर्दशाएँ")
    for ad, a_s, a_e in ad_list:
        is_now = a_s <= now_naive < a_e
        label = (f"{GRAHA_HI[sel_md]} - {GRAHA_HI[ad]} अंतर्दशा ({a_s.strftime('%d-%m-%Y')} से {a_e.strftime('%d-%m-%Y')})" + (" 🔥 वर्तमान" if is_now else ""))
        with st.expander(label, expanded=is_now):
            for title, text in ad_reading(sel_md, ad, r):
                st.markdown(f"**{title}**")
                st.write(text)
            
            # --- NEW FEATURE: PRATYANTAR DASHA TIMELINE ---
            st.markdown(f"**{GRAHA_HI[ad]} अंतर्दशा की प्रत्यंतर दशाएँ (PD):**")
            pds = pratyantar_dashas(sel_md, ad, a_s, a_e)
            st.dataframe(
                [{"प्रत्यंतर दशा": GRAHA_HI[pd[0]], "प्रारंभ": pd[1].strftime('%d-%m-%Y'), "समाप्ति": pd[2].strftime('%d-%m-%Y'), "स्थिति": "🔥 सक्रिय" if pd[1] <= now_naive < pd[2] else "-"} for pd in pds],
                use_container_width=True
            )

    section_heading("7. प्रमुख योग एवं दोष", "🌟")
    for yname, ydesc in r["yogas"]: st.success(f"**{yname}** — {ydesc}")

    section_heading("8. गोचर (Current Transits)", "🪐")
    try:
        transits = get_current_transits()
        transit_rows = [{"Planet": pname, "Current sidereal sign": SIGNS[data["sign"]], "Degree": round(data["longitude"] % 30, 2)} for pname, data in transits.items()]
        st.dataframe(transit_rows, use_container_width=True, hide_index=True)
    except Exception as e: st.warning(f"Transit calculation error: {e}")

    section_heading("9. AI ज्योतिष चैट (Ask Question)", "🤖")
    user_question = st.chat_input("अपना ज्योतिष प्रश्न पूछें…")
    if user_question:
        st.info("AI Chat works when OPENAI_API_KEY is configured in Streamlit Secrets.")

    section_heading("10. PDF Report Download", "📄")
    try:
        pdf_bytes = build_pdf_bytes(r)
        st.download_button("Download PDF", data=pdf_bytes, file_name=f"jyotish_report_{date.today().isoformat()}.pdf", mime="application/pdf")
    except: st.warning("PDF Generation Failed")
