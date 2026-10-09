import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta, date, time
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import zoneinfo
from fpdf import FPDF

# Initialize Swiss Ephemeris Settings
swe.set_sid_mode(swe.SIDM_LAHIRI)

SIGNS = [
    "Mesh", "Vrishabh", "Mithun", "Kark",
    "Singh", "Kanya", "Tula", "Vrishchik",
    "Dhanu", "Makar", "Kumbh", "Meen"
]

SIGNS_HI = [
    "मेष", "वृषभ", "मिथुन", "कर्क",
    "सिंह", "कन्या", "तुला", "वृश्चिक",
    "धनु", "मकर", "कुंभ", "मीन"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini",
    "Mrigashira", "Ardra", "Punarvasu", "Pushya",
    "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula",
    "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

PLANETS = {
    "Surya": swe.SUN,
    "Chandra": swe.MOON,
    "Mangal": swe.MARS,
    "Budh": swe.MERCURY,
    "Guru": swe.JUPITER,
    "Shukra": swe.VENUS,
    "Shani": swe.SATURN,
    "Rahu": swe.MEAN_NODE
}

DASHA_LORDS = [
    "Ketu", "Shukra", "Surya", "Chandra",
    "Mangal", "Rahu", "Guru", "Shani", "Budh"
]

DASHA_YEARS = {
    "Ketu": 7, "Shukra": 20, "Surya": 6,
    "Chandra": 10, "Mangal": 7, "Rahu": 18,
    "Guru": 16, "Shani": 19, "Budh": 17
}

RASHI_LORDS = {
    0: "Mangal", 1: "Shukra", 2: "Budh", 3: "Chandra",
    4: "Surya", 5: "Budh", 6: "Shukra", 7: "Mangal",
    8: "Guru", 9: "Shani", 10: "Shani", 11: "Guru"
}

GEMSTONES = {
    "Mangal": "मूंगा (Red Coral)",
    "Shukra": "हीरा / ओपल (Diamond / Opal)",
    "Budh": "पन्ना (Emerald)",
    "Chandra": "मोती (Pearl)",
    "Surya": "माणिक्य (Ruby)",
    "Guru": "पुखराज (Yellow Sapphire)",
    "Shani": "नीलम (Blue Sapphire)"
}

RUDRAKSHA = {
    "Surya": "1 मुखी या 12 मुखी रुद्राक्ष",
    "Chandra": "2 मुखी रुद्राक्ष",
    "Mangal": "3 मुखी रुद्राक्ष",
    "Budh": "4 मुखी रुद्राक्ष",
    "Guru": "5 मुखी रुद्राक्ष",
    "Shukra": "6 मुखी रुद्राक्ष",
    "Shani": "7 मुखी रुद्राक्ष",
    "Rahu": "8 मुखी रुद्राक्ष",
    "Ketu": "9 मुखी रुद्राक्ष"
}

CAREER_MAP = {
    "Surya": "प्रशासनिक सेवाएं, सरकारी क्षेत्र, उच्च प्रबंधन, चिकित्सा, राजनीति, एवं नेतृत्वकारी पद।",
    "Chandra": "जल व्यवसाय, हॉस्पिटैलिटी, ट्रैवल एवं टूरिज्म, नर्सिंग, डेयरी, साहित्य, कला एवं लेखन।",
    "Mangal": "इंजीनियरिंग, रक्षा बल/पुलिस, रियल एस्टेट, निर्माण कार्य, खेलकूद, एवं तकनीकी क्षेत्र।",
    "Budh": "व्यापार, बैंकिंग, चार्टर्ड अकाउंटेंसी (CA), सॉफ्टवेयर/आईटी, मीडिया, पत्रकारिता, एवं अनुवाद।",
    "Guru": "शिक्षा व अध्यापन, कानून व वकालत, वित्तीय परामर्श, ज्योतिष, धार्मिक संस्थान, एवं रिसर्च।",
    "Shukra": "फैशन डिजाइनिंग, सौंदर्य उत्पाद, फिल्म व मीडिया, लग्जरी उद्योग, आभूषण, एवं हॉस्पिटैलिटी।",
    "Shani": "इन्फ्रास्ट्रक्चर, माइनिंग, भारी मशीनरी, लॉजिस्टिक्स, श्रम प्रबंधन, कानून, एवं कृषि।",
    "Rahu": "आईटी व सॉफ्टवेयर, डिजिटल मार्केटिंग, साइबर सुरक्षा, आयात-निर्यात, शेयर बाजार, एवं इलेक्ट्रॉनिक्स।",
    "Ketu": "सॉफ्टवेयर कोडिंग, डेटा साइंस, बायोटेक्नोलॉजी, शोध कार्य, फार्मास्यूटिकल्स, एवं वैकल्पिक चिकित्सा।"
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
    "Ketu": "त्वचा संबंधी संवेदनशीलता, उदर स्वास्थ्य, एवं शारीरिक ऊर्जा स्तर को बनाए रखने के उपाय करें।"
}

MAHADASHA_PREDICTIONS = {
    "Surya": """
    सूर्य की महादशा जीवन में एक नया प्रभात लेकर आती है। यह समय आपके आत्मबल, अधिकार, और सामाजिक प्रतिष्ठा में अप्रत्याशित वृद्धि का कारक बनता है। इस अवधि में राजकीय या प्रशासनिक कार्यों में सफलता प्राप्त होती है। समाज में आपका प्रभाव बढ़ता है और उच्च अधिकारियों का सहयोग मिलता है। यदि आप नौकरी या व्यवसाय में हैं, तो पदोन्नति और नेतृत्व के अवसर प्राप्त होते हैं। हालांकि, इस दौरान अहंकार और पित्त संबंधी स्वास्थ्य समस्याओं से बचना आवश्यक है।
    """,
    "Chandra": """
    चंद्रमा की महादशा मन की संवेदनशीलता, रचनात्मकता और मानसिक परिवर्तनों का काल होती है। इस समय आपकी कल्पनाशक्ति और बौद्धिक क्षमता चरम पर रहती है। कला, साहित्य, जल संबंधी व्यवसाय, या यात्राओं से जुड़े कार्यों में विशेष लाभ प्राप्त होता है। माता से संबंध प्रगाढ़ होते हैं और उनका आशीर्वाद प्राप्त होता है। हालांकि, चंद्रमा के उतार-चढ़ाव के कारण मन में कभी-कभी चंचलता या मानसिक तनाव आ सकता है, जिसके लिए ध्यान और योग अत्यंत लाभप्रद रहेगा।
    """,
    "Mangal": """
    मंगल की महादशा असीम ऊर्जा, साहस, और निर्णय क्षमता का काल है। यह समय भूमि, भवन, प्रॉपर्टी, और तकनीकी कार्यों में बड़ी सफलता दिलाने वाला होता है। यदि आप इंजीनियरिंग, सुरक्षा, खेलकूद, या निर्माण कार्य से जुड़े हैं, तो यह दशा आपके लिए स्वर्णिम सिद्ध हो सकती है। आप कठिन से कठिन चुनौतियों का सामना करने के लिए तैयार रहते हैं। हालांकि, जल्दबाजी में निर्णय लेने या क्रोध पर नियंत्रण न रखने से विवाद हो सकते हैं, इसलिए धैर्य बनाए रखना आवश्यक है।
    """,
    "Budh": """
    बुध की महादशा बुद्धि, ज्ञान, संचार और व्यावसायिक कुशाग्रता का काल मानी जाती है। इस अवधि में आपकी वाक्-पटुता और तार्किक क्षमता में जबर्दस्त सुधार आता है। व्यापार, बैंकिंग, फाइनेंस, आईटी, मीडिया और लेखन से जुड़े जातकों को अभूतपूर्व सफलता मिलती है। नए व्यावसायिक संबंध बनते हैं जो दीर्घकालिक लाभ प्रदान करते हैं। वित्तीय स्थिति में मजबूती आती है और पढ़ाई या शोध से जुड़े लोगों के लिए यह समय अत्यंत फलदायी सिद्ध होता है।
    """,
    "Guru": """
    बृहस्पति (गुरु) की महादशा जीवन में सुख, समृद्धि, ज्ञान और धार्मिक चेतना का प्रसार करती है। यह दशा वैदिक ज्योतिष में सबसे शुभ मानी जाती है। इस दौरान विवाह, संतान सुख, घर में मांगलिक कार्य और उच्च शिक्षा के योग बनते हैं। समाज में आपका सम्मान बढ़ता है और बड़ों का आशीर्वाद प्राप्त होता है। आर्थिक दृष्टिकोण से यह कालखंड अत्यंत फलदायी रहता है। अध्यात्म और दर्शन की ओर रुझान बढ़ता है, जिससे जीवन में आंतरिक शांति मिलती है।
    """,
    "Shukra": """
    शुक्र की महादशा जीवन में भौतिक सुख-सुविधाओं, ऐश्वर्य, और कलात्मक उपलब्धियों का स्वर्णिम काल होती है। इस दौरान वाहन सुख, नए वस्त्र, आभूषण और अचल संपत्ति की प्राप्ति होती है। प्रेम संबंधों और वैवाहिक जीवन में मधुरता आती है। कला, फैशन, मीडिया, हॉस्पिटैलिटी या सौंदर्य प्रसाधनों के व्यापार से जुड़े जातकों को बड़ी सफलता मिलती है। सामाजिक आकर्षण बढ़ता है और जीवन में आनंद का वातावरण बना रहता है।
    """,
    "Shani": """
    शनि की महादशा कड़े परिश्रम, अनुशासन, और आत्म-मंथन का काल होती है। शनि देव जातक को व्यावहारिक और परिपक्व बनाते हैं। इस अवधि में किए गए सतत प्रयास से मिलने वाली सफलता अत्यंत स्थायी और दीर्घकालिक होती है। निर्माण कार्य, मशीनरी, ट्रांसपोर्ट, कानून या जनसेवा से जुड़े कार्यों में बड़ा लाभ होता है। हालांकि, शुरुआती दौर में कुछ विलंब या संघर्ष का सामना करना पड़ सकता है, लेकिन धैर्य रखने पर यह दशा जीवन को मजबूत आधार देती है।
    """,
    "Rahu": """
    राहु की महादशा जीवन में अचानक और अप्रत्याशित बदलाव लाती है। यह आउट-ऑफ-द-बॉक्स सोच और आधुनिक तकनीकों में सफलता की सूचक है। आईटी, सॉफ्टवेयर, विदेशी व्यापार, आयात-निर्यात, और डिजिटल मीडिया से जुड़े लोगों के लिए यह कालखंड असीम संभावनाएं लेकर आता है। आप स्थापित सीमाओं से बाहर निकलकर नए कीर्तिमान स्थापित करते हैं। हालांकि, इस दौरान भ्रम या अति-उत्साह में गलत निर्णय लेने से बचना चाहिए और यथार्थवादी दृष्टिकोण रखना चाहिए।
    """,
    "Ketu": """
    केतु की महादशा अध्यात्म, शोध, और आत्म-साक्षात्कार का काल मानी जाती है। यह समय सांसारिक मोह-माया से थोड़ा हटकर गूढ़ विद्याओं, कोडिंग, डेटा साइंस, और मौलिक शोध में गहराई से उतरने का अवसर देता है। आपकी अंतर्दृष्टि (Intuition) बहुत मजबूत हो जाती है। यह कालखंड पुरानी मानसिक उलझनों को समाप्त कर जीवन में एक नया और स्पष्ट दृष्टिकोण प्रदान करता है। ध्यान और योग के माध्यम से यह दशा परम शांति देती है।
    """
}

def section_heading(title, icon="✨"):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #4A0000 0%, #1A0000 100%);
            padding: 14px 22px;
            border-radius: 10px;
            margin-top: 28px;
            margin-bottom: 18px;
            border-left: 6px solid #FFD700;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
        ">
            <h3 style="color: #FFD700; margin:0; padding:0; font-family: 'Segoe UI', sans-serif; font-weight: 700; font-size: 20px;">
                {icon} {title}
            </h3>
        </div>
        """,
        unsafe_allow_html=True
)
def get_navamsha_sign(abs_degree):
    abs_degree = abs_degree % 360
    d1_sign = int(abs_degree // 30)
    sign_degree = abs_degree % 30
    navamsha_num = int(sign_degree // (30 / 9))

    if d1_sign in [0, 4, 8]:
        start_sign = 0
    elif d1_sign in [1, 5, 9]:
        start_sign = 9
    elif d1_sign in [2, 6, 10]:
        start_sign = 6
    else:
        start_sign = 3

    return (start_sign + navamsha_num) % 12

def render_north_indian_chart(asc_sign, planet_signs, title):
    fig, ax = plt.subplots(figsize=(5, 5))

    ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color="maroon", lw=2)
    ax.plot([0, 0.5, 1, 0.5, 0], [0.5, 1, 0.5, 0, 0.5], color="maroon", lw=1.5)
    ax.plot([0, 1], [0, 1], color="maroon", lw=1.5)
    ax.plot([0, 1], [1, 0], color="maroon", lw=1.5)

    positions = [
        (0.50, 0.75), (0.25, 0.88), (0.12, 0.70),
        (0.25, 0.50), (0.12, 0.30), (0.25, 0.12),
        (0.50, 0.25), (0.75, 0.12), (0.88, 0.30),
        (0.75, 0.50), (0.88, 0.70), (0.75, 0.88)
    ]

    for i, (x, y) in enumerate(positions):
        sign_index = (asc_sign + i) % 12
        planets_in_house = planet_signs.get(SIGNS[sign_index], [])
        p_str = "\n".join(planets_in_house) if planets_in_house else ""

        ax.text(x, y + 0.05, f"{sign_index + 1}", color="darkred", fontsize=10, weight="bold", ha="center")
        if p_str:
            ax.text(x, y - 0.05, p_str, color="navy", fontsize=8, ha="center")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(title, fontsize=12, pad=10, color="maroon", weight="bold")
    return fig

def generate_pdf_report(name, dob_str, place_str, asc_sign_name, moon_sign_name, active_md, active_ad, yoga_list):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Jyotish AI - Detailed Horoscope Report", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Name: {name}", ln=True)
    pdf.cell(0, 8, f"Date of Birth: {dob_str}", ln=True)
    pdf.cell(0, 8, f"Place: {place_str}", ln=True)
    pdf.cell(0, 8, f"Lagna Rashi: {asc_sign_name}", ln=True)
    pdf.cell(0, 8, f"Moon Rashi: {moon_sign_name}", ln=True)
    pdf.cell(0, 8, f"Active Mahadasha: {active_md}", ln=True)
    pdf.cell(0, 8, f"Active Antardasha: {active_ad}", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Key Yogas & Analysis:", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for y in yoga_list:
        pdf.cell(0, 7, f"- {y}", ln=True)

    return pdf.output()

# --- Page Setup ---
st.set_page_config(page_title="Jyotish AI - विस्तृत महा जन्मपत्री", page_icon="🔱", layout="wide")

st.markdown(
    """
    <div style="text-align: center; background: linear-gradient(90deg, #3A0007 0%, #8A1C1C 50%, #3A0007 100%); padding: 25px; border-radius: 12px; border-bottom: 4px solid #FFD700; margin-bottom: 25px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3);">
        <h1 style="color: #FFD700; font-size: 34px; font-weight: 800; margin:0;">🔱 JYOTISH AI — अति-विस्तृत महा जन्मपत्री</h1>
        <p style="color: #FFF8DC; font-size: 16px; margin-top: 8px;">Comprehensive Vedic Astrology Engine | गहन विश्लेषण एवं सम्पूर्ण जीवन फलादेश</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.subheader("📋 Birth Details / जन्म विवरण दर्ज करें")

col_a, col_b = st.columns(2)
with col_a:
    name = st.text_input("Name / नाम", value="", placeholder="अपना नाम लिखें")
    gender = st.selectbox("Gender / लिंग", ["Male (पुरुष)", "Female (महिला)", "Other (अन्य)"])
    dob = st.date_input("Date of birth / जन्म तिथि", value=None, min_value=date(1900, 1, 1))
    
    st.write("**Birth Time / जन्म समय (AM / PM के साथ):**")
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        hour12 = st.number_input("Hour (घंटा)", min_value=1, max_value=12, value=1)
    with t_col2:
        minute = st.number_input("Minute (मिनट)", min_value=0, max_value=59, value=0)
    with t_col3:
        ampm = st.selectbox("AM / PM", ["AM (सुबह/रात)", "PM (दोपहर/शाम)"])

with col_b:
    place = st.text_input("Birth place & Country / जन्म स्थान व देश", value="", placeholder="जैसे: Dang Nepal, Delhi India, London UK, New York USA")

submitted = st.button("🚀 Generate Full Detailed Report / संपूर्ण विस्तृत महा-रिपोर्ट देखें", type="primary")
if submitted:
    if not name or not dob or not place:
        st.warning("कृपया सभी विवरण (नाम, लिंग, जन्म तिथि, समय और जन्म स्थान) भरें!")
    else:
        try:
            hour24 = hour12 % 12
            if "PM" in ampm:
                hour24 += 12
            bt = time(hour24, minute)

            geolocator = Nominatim(user_agent="jyotish_app_v13")
            location = geolocator.geocode(place)

            if not location:
                st.error("जन्म स्थान नहीं मिल सका! कृपया स्थान और देश का नाम सही से लिखें।")
            else:
                lat = location.latitude
                lon = location.longitude

                tf = TimezoneFinder()
                tz_str = tf.timezone_at(lng=lon, lat=lat)
                
                if tz_str:
                    tz_obj = zoneinfo.ZoneInfo(tz_str)
                    local_dt_naive = datetime.combine(dob, bt)
                    local_dt_aware = local_dt_naive.replace(tzinfo=tz_obj)
                    utc_offset_hours = local_dt_aware.utcoffset().total_seconds() / 3600.0
                    utc_dt = local_dt_aware.astimezone(zoneinfo.ZoneInfo("UTC"))
                else:
                    tz_str = "UTC Offset (+5.75 Default)"
                    utc_offset_hours = 5.75
                    local_dt_naive = datetime.combine(dob, bt)
                    utc_dt = local_dt_naive - timedelta(hours=5, minutes=45)

                st.success(f"📍 स्थान मिला: **{location.address}** | टाइमज़ोन: **{tz_str} (UTC {utc_offset_hours:+.2f} hrs)** | समय: **{hour12}:{minute:02d} {ampm[:2]}**")

                jd = swe.julday(
                    utc_dt.year,
                    utc_dt.month,
                    utc_dt.day,
                    utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
                )

                flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

                # 1. PLANETARY POSITIONS
                section_heading("1. ग्रह स्थिति एवं नवमांश विवरण (Planetary Positions)", "🪐")

                rows = []
                d1_planet_signs = {}
                d9_planet_signs = {}
                planet_positions_map = {}

                for planet, code in PLANETS.items():
                    res = swe.calc_ut(jd, code, flags)
                    degree = res[0][0] % 360
                    speed = res[0][3]

                    is_retro = speed < 0 and planet not in ["Surya", "Chandra", "Rahu"]
                    planet_display = f"{planet} (R)" if is_retro else planet

                    sign_index = int(degree // 30)
                    sign_degree = degree % 30
                    nak_index = int(degree / (360 / 27))

                    planet_positions_map[planet] = sign_index
                    d9_sign_index = get_navamsha_sign(degree)

                    rows.append({
                        "Planet": planet_display,
                        "D1 Rashi": SIGNS[sign_index],
                        "Degree": round(sign_degree, 2),
                        "Nakshatra": NAKSHATRAS[nak_index],
                        "D9 Navamsha Rashi": SIGNS[d9_sign_index],
                        "Status": "Retrograde" if is_retro else "Direct"
                    })

                    d1_planet_signs.setdefault(SIGNS[sign_index], []).append(planet_display)
                    d9_planet_signs.setdefault(SIGNS[d9_sign_index], []).append(planet_display)

                rahu_res = swe.calc_ut(jd, swe.MEAN_NODE, flags)
                rahu_deg = rahu_res[0][0] % 360
                ketu_degree = (rahu_deg + 180) % 360
                ketu_sign = int(ketu_degree // 30)
                ketu_nak = int(ketu_degree / (360 / 27))
                ketu_d9_sign = get_navamsha_sign(ketu_degree)

                planet_positions_map["Ketu"] = ketu_sign

                rows.append({
                    "Planet": "Ketu",
                    "D1 Rashi": SIGNS[ketu_sign],
                    "Degree": round(ketu_degree % 30, 2),
                    "Nakshatra": NAKSHATRAS[ketu_nak],
                    "D9 Navamsha Rashi": SIGNS[ketu_d9_sign],
                    "Status": "Retrograde"
                })
                d1_planet_signs.setdefault(SIGNS[ketu_sign], []).append("Ketu")
                d9_planet_signs.setdefault(SIGNS[ketu_d9_sign], []).append("Ketu")

                st.dataframe(rows, use_container_width=True)

                # 2. CHARTS
                res_houses = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
                cusps, ascmc = res_houses[0], res_houses[1]
                
                asc_degree = ascmc[0] % 360
                asc_sign = int(asc_degree // 30)
                d9_asc_sign = get_navamsha_sign(asc_degree)

                section_heading("2. D1 (जन्म) एवं D9 (नवमांश) चक्र", "📊")
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**D1 लग्न राशि:** {SIGNS[asc_sign]} ({SIGNS_HI[asc_sign]}) — {round(asc_degree % 30, 2)}°")
                    fig_d1 = render_north_indian_chart(asc_sign, d1_planet_signs, "D1 - जन्म कुंडली")
                    st.pyplot(fig_d1)
                    plt.close(fig_d1)

                with col2:
                    st.write(f"**D9 नवमांश लग्न राशि:** {SIGNS[d9_asc_sign]} ({SIGNS_HI[d9_asc_sign]})")
                    fig_d9 = render_north_indian_chart(d9_asc_sign, d9_planet_signs, "D9 - नवमांश कुंडली")
                    st.pyplot(fig_d9)
                    plt.close(fig_d9)

                # 3. HEALTH & WELLNESS DEEP ANALYSIS
                section_heading("3. स्वास्थ्य एवं शारीरिक आरोग्य का विस्तृत विश्लेषण (Health Report)", "🏥")

                sixth_sign_idx = (asc_sign + 5) % 12
                sixth_lord = RASHI_LORDS[sixth_sign_idx]
                planets_in_6th = [p for p, s_idx in planet_positions_map.items() if s_idx == sixth_sign_idx]

                with st.expander("🏥 रोग प्रतिरोधक क्षमता, संभावित स्वास्थ्य चुनौतियां एवं विस्तृत उपाय", expanded=True):
                    st.write(f"• **षष्ठ भाव (रोग व प्रतिरोधक क्षमता):** आपकी कुंडली में षष्ठ भाव में **{SIGNS[sixth_sign_idx]} ({SIGNS_HI[sixth_sign_idx]})** राशि स्थित है, जिसके स्वामी **{sixth_lord}** हैं।")
                    st.write(f"• **प्राकृतिक स्वास्थ्य प्रवृत्तियां:** {HEALTH_MAP.get(sixth_lord, 'सामान्य स्वास्थ्य उत्तम रहेगा।')}")
                    st.write("""
                    वैदिक सिद्धांत के अनुसार प्रथम भाव (शरीर व आत्मबल) और षष्ठ भाव (रोग व प्रतिरोधकता) का संतुलन स्वास्थ्य को निर्धारित करता है। यदि आप संतुलित जीवनशैली अपनाते हैं, नित्य प्रातः प्राणायाम करते हैं और आहार में ताजे फलों व जल का उचित समावेश रखते हैं, तो आपकी शारीरिक ऊर्जा हमेशा उच्च स्तर पर बनी रहेगी।
                    """)
                    if planets_in_6th:
                        st.write(f"• **षष्ठ भाव में स्थित ग्रह (`{', '.join(planets_in_6th)}`):** इस भाव में ग्रहों की उपस्थिति आपको स्वास्थ्य के प्रति अधिक सतर्क रहने का संकेत देती है। मौसमी बदलाव के समय विशेष सावधानी बरतें।")

                # 4. LOVE, AFFAIRS & RELATIONSHIPS DEEP ANALYSIS
                section_heading("4. प्रेम, लव-अफेयर्स एवं संबंधों का विस्तृत विश्लेषण (Love & Relationships)", "❤️")

                fifth_sign_idx = (asc_sign + 4) % 12
                fifth_lord = RASHI_LORDS[fifth_sign_idx]
                planets_in_5th = [p for p, s_idx in planet_positions_map.items() if s_idx == fifth_sign_idx]

                with st.expander("❤️ प्रेम संबंध, भावनात्मक जुड़ाव एवं विवाह संभावनाओं का गहन विश्लेषण", expanded=True):
                    st.write(f"• **पंचम भाव (प्रेम व भावुकता):** पंचम भाव में **{SIGNS[fifth_sign_idx]} ({SIGNS_HI[fifth_sign_idx]})** राशि है, जिसके स्वामी **{fifth_lord}** हैं।")
                    st.write(f"""
                    आपके जीवन में प्रेम संबंधों का आधार भावनात्मक गहराई और परस्पर विश्वास रहेगा। आप अपने साथी के प्रति समर्पित और निष्ठावान रहने वाले व्यक्ति हैं। जब भी आप किसी रिश्ते में प्रवेश करते हैं, तो उसे केवल अल्पकालिक न मानकर गंभीरता से निभाते हैं।
                    """)
                    if planets_in_5th:
                        st.write(f"• **पंचम भाव में स्थित ग्रहों का प्रभाव (`{', '.join(planets_in_5th)}`):** ये ग्रह आपकी लव-लाइफ़ में भावनात्मक मोड़ और आकर्षण को बढ़ाते हैं। संवाद में स्पष्टता बनाए रखना आपके रिश्ते को और मजबूत करेगा।")
                    
                    if fifth_lord in [RASHI_LORDS[(asc_sign + 6) % 12], "Shukra", "Rahu"] or "Rahu" in planets_in_5th:
                        st.write("• **विवाह स्वरूप योग:** आपकी कुंडली में प्रेम (5th) और विवाह (7th) स्थानों के बीच शुभ संबंध बनता दिख रहा है, जो यह दर्शाता है कि आपकी अपनी पसंद या प्रेम विवाह होने की प्रबल संभावनाएं हैं।")
                    else:
                        st.write("• **विवाह स्वरूप योग:** आपकी कुंडली में पारिवारिक सहमति और पारंपरिक रीति-रिवाजों द्वारा तय संबंध (Arranged Marriage) अत्यंत सुखद, स्थायी और भाग्योदय करने वाला सिद्ध होगा।")

                # 5. YOGAS & RAJYOGA ANALYSIS
                section_heading("5. कुंडली में स्थित प्रमुख राजयोग एवं धनयोग (Yogas & Rajyoga)", "👑")

                detected_yogas = []
                if planet_positions_map.get("Surya") == planet_positions_map.get("Budh"):
                    detected_yogas.append("बुधादित्य योग (Budhaditya Yoga): सूर्य और बुध की युति से कुशाग्र बुद्धि, तीक्ष्ण निर्णय क्षमता, और समाज में प्रतिष्ठित स्थान प्राप्त होता है।")

                guru_p = planet_positions_map.get("Guru")
                chandra_p = planet_positions_map.get("Chandra")
                if guru_p is not None and chandra_p is not None:
                    diff = abs(guru_p - chandra_p) % 12
                    if diff in [0, 3, 6, 9]:
                        detected_yogas.append("गजकेसरी योग (Gajakesari Yoga): गुरु और चंद्रमा का केंद्र योग। यह योग जातक को असीम ज्ञान, धन, यश और स्थायी समृद्धि प्रदान करता है।")

                mangal_p = planet_positions_map.get("Mangal")
                mangal_house = ((mangal_p - asc_sign) % 12) + 1
                if mangal_house in [1, 4, 7, 10] and mangal_p in [0, 7, 9]:
                    detected_yogas.append("रूचक महापुरुष योग (Ruchaka Yoga): मंगल का केंद्र में बलवान होना। असीम पराक्रम, अचल संपत्ति, और नेतृत्व क्षमता प्रदान करता है।")

                if not detected_yogas:
                    detected_yogas.append("आपकी कुंडली में कर्मेश और भाग्येश का शुभ संबंध निर्मित हो रहा है, जो सतत परिश्रम से धन और मान-सम्मान दिलाता है।")

                for y in detected_yogas:
                    st.success(f"• {y}")

                # 6. DASHA & ANTARDASHA
                section_heading("6. महादशा एवं अंतर्दशा का अति-विस्तृत फलादेश (Dasha Analysis)", "⏳")

                moon_res = swe.calc_ut(jd, swe.MOON, flags)
                moon_degree = moon_res[0][0] % 360
                moon_sign_idx = int(moon_degree // 30)
                moon_nak_idx = int(moon_degree / nak_span)

                deg_in_nak = moon_degree % nak_span
                balance_fraction = 1.0 - (deg_in_nak / nak_span)

                first_md_lord_idx = moon_nak_idx % 9
                first_md_lord = DASHA_LORDS[first_md_lord_idx]
                first_md_years = DASHA_YEARS[first_md_lord]
                remaining_first_md_years = first_md_years * balance_fraction

                now_dt = datetime.now()
                current_start_date = local_dt_naive
                active_md = ""
                active_ad = ""

                all_md_rows = []

                for m_idx in range(9):
                    md_lord_i = (first_md_lord_idx + m_idx) % 9
                    md_name = DASHA_LORDS[md_lord_i]
                    md_total_years = DASHA_YEARS[md_name]

                    md_duration_years = remaining_first_md_years if m_idx == 0 else md_total_years
                    md_end_date = current_start_date + timedelta(days=md_duration_years * 365.25)

                    is_active_md = current_start_date <= now_dt <= md_end_date
                    if is_active_md:
                        active_md = md_name
                        ad_start = current_start_date
                        for a_idx in range(9):
                            ad_lord_i = (md_lord_i + a_idx) % 9
                            ad_name = DASHA_LORDS[ad_lord_i]
                            ad_years = (md_total_years * DASHA_YEARS[ad_name]) / 120.0
                            ad_end = ad_start + timedelta(days=ad_years * 365.25)
                            if ad_start <= now_dt <= ad_end:
                                active_ad = ad_name
                                break
                            ad_start = ad_end

                    all_md_rows.append({
                        "महादशा (Mahadasha)": md_name,
                        "प्रारंभ तिथि": current_start_date.strftime("%Y-%m-%d"),
                        "समाप्ति तिथि": md_end_date.strftime("%Y-%m-%d"),
                        "अवधि (वर्ष)": round(md_duration_years, 2),
                        "स्थिति": "🔥 वर्तमान में सक्रिय" if is_active_md else "-"
                    })
                    current_start_date = md_end_date

                st.dataframe(all_md_rows, use_container_width=True)

                if active_md and active_ad:
                    with st.expander(f"🌟 वर्तमान सक्रिय महादशा ({active_md}) एवं अंतर्दशा ({active_ad}) का विस्तृत प्रभाव", expanded=True):
                        st.write(f"• **महादशापति ({active_md}) का प्रभाव:** {MAHADASHA_PREDICTIONS.get(active_md, 'यह कालखंड आपके जीवन में नए अवसर लाएगा।')}")
                        st.write(f"• **अंतर्दशापति ({active_ad}) का प्रभाव:** वर्तमान समय में आपके दैनिक निर्णयों, मानसिक रुझान, और अल्पकालिक परिणामों पर {active_ad} का मुख्य प्रभाव है।")

                # 7. AGE-WISE PREDICTIONS
                section_heading("7. जीवन कालखंड अनुसार अति-विस्तृत महा-फलादेश (Age-wise Horoscope)", "🔮")

                with st.expander("🎓 20 से 30 वर्ष की आयु: शिक्षा, कौशल विकास एवं आजीविका का निर्माण", expanded=True):
                    st.write("""
                    • **करियर एवं कार्यक्षेत्र की नींव:** यह दशक आपके जीवन की दिशा तय करने वाला सबसे महत्वपूर्ण कालखंड है। इस अवधि में आपका मुख्य ध्यान अपने कौशल (Skill Set), व्यावहारिक ज्ञान, और तकनीकी दक्षता को निखारने पर होना चाहिए। शुरुआती वर्षों (20-23 वर्ष) में अत्यधिक प्रयास और अपेक्षाकृत धीमा परिणाम देखने को मिल सकता है, परंतु 24 से 27 वर्ष की आयु के मध्य करियर में पहला बड़ा ब्रेक या स्थायी अवसर प्राप्त होता है।
                    
                    • **आर्थिक प्रगति व परिपक्वता:** 26 वर्ष की आयु के पश्चात आपकी कमाई में निरंतरता और आर्थिक निर्णय लेने में स्पष्ट परिपक्वता आने लगेगी। इस समय में वित्तीय अनुशासन बनाए रखना आपके भविष्य के लिए वरदान सिद्ध होगा।
                    """)

                with st.expander("💍 25 से 35 वर्ष की आयु: विवाह, दांपत्य जीवन एवं पारिवारिक जिम्मेदारियां", expanded=True):
                    st.write("""
                    • **विवाह एवं दांपत्य सुख:** यह कालखंड गृहस्थ जीवन में प्रवेश करने और नए पारिवारिक संबंधों को स्थापित करने का उत्तम समय है। कुंडली के शुभ योगों के प्रभाव से आपका जीवनसाथी समझदार, जिम्मेदार, और व्यावहारिक दृष्टिकोण वाला होगा।
                    
                    • **भाग्योदय व सामाजिक मान-प्रतिष्ठा:** विवाह के पश्चात आपके भाग्य की गति में तीव्रता आएगी। जीवनसाथी का सहयोग आपको न केवल मानसिक शांति देगा बल्कि आर्थिक फैसलों में भी सही राह दिखाएगा। घर में मांगलिक कार्य और नए सदस्यों का आगमन होगा।
                    """)

                with st.expander("🏢 35 से 50 वर्ष की आयु: स्व-अर्जित संपत्ति, अचल संपत्ति एवं स्थायी सफलता", expanded=True):
                    st.write("""
                    • **अचल संपत्ति व भूमि-भवन योग:** यह आपके जीवन का सबसे समृद्ध और फलदायी दौर सिद्ध होगा। वर्षों के अनुभव, कड़ी मेहनत और सूझबूझ के बल पर आप अपनी खुद की संपत्ति (मकान, भूमि, या व्यावसायिक स्थान) का निर्माण करने में सफल होंगे।
                    
                    • **स्थायी सफलता व नेतृत्व:** इस उम्र में आप दूसरों के अधीन काम करने की बजाय स्वतंत्र रूप से निर्णय लेने और बड़े प्रोजेक्ट्स को संभालने की स्थिति में होंगे। समाज और व्यापारिक क्षेत्र में आपका कद और प्रतिष्ठा चरम पर रहेगी।
                    """)

                # 8. GEMSTONE & RUDRAKSHA SUGGESTIONS
                section_heading("8. शुभ रत्न, रुद्राक्ष एवं भाग्यशाली समाधान (Remedies)", "💎")

                lagna_lord = RASHI_LORDS[asc_sign]
                fifth_sign = (asc_sign + 4) % 12
                fifth_lord = RASHI_LORDS[fifth_sign]
                ninth_sign = (asc_sign + 8) % 12
                ninth_lord = RASHI_LORDS[ninth_sign]

                col_g1, col_g2, col_g3 = st.columns(3)
                with col_g1:
                    st.info(f"**जीवनरत्न (Lagna Stone):**\n\n`{GEMSTONES.get(lagna_lord, 'नेचुरल ओपल')}`\n\n(स्वास्थ्य, व्यक्तित्व व आत्मबल हेतु)")
                with col_g2:
                    st.success(f"**ज्ञान व बुद्धि रत्न (5th Stone):**\n\n`{GEMSTONES.get(fifth_lord, 'पुखराज')}`\n\n(शिक्षा, निर्णय शक्ति व संतान सुख हेतु)")
                with col_g3:
                    st.warning(f"**भाग्यरत्न (9th Lucky Stone):**\n\n`{GEMSTONES.get(ninth_lord, 'माणिक्य')}`\n\n(किस्मत, पद-प्रतिष्ठा व भाग्यवृद्धि हेतु)")

                st.write(f"• **उपयुक्त रुद्राक्ष:** आपकी कुंडली के अनुसार आपके लिए **{RUDRAKSHA.get(lagna_lord, '5 मुखी रुद्राक्ष')}** धारण करना मानसिक शांति और सकारात्मक ऊर्जा के लिए सर्वोत्तम रहेगा।")

                # 9. CAREER & MARRIAGE PREDICTIONS
                section_heading("9. ग्रहों के अनुसार उपयुक्त करियर एवं विवाह फलादेश", "💼")

                karma_sign_idx = (asc_sign + 9) % 12
                karma_lord = RASHI_LORDS[karma_sign_idx]

                with st.expander("💼 आपके लिए उपयुक्त काम/बिज़नेस क्षेत्र", expanded=True):
                    st.write(f"• **कर्मेश ({karma_lord}) के अनुसार सबसे सफल क्षेत्र:** {CAREER_MAP.get(karma_lord, 'व्यापार व स्वतंत्र रोजगार')}")

                partner_label = "पत्नी (Wife)" if "Male" in gender else "पति (Husband)"
                marriage_sign_idx = (asc_sign + 6) % 12
                marriage_lord = RASHI_LORDS[marriage_sign_idx]

                with st.expander(f"💍 {gender} विशेष — विवाह एवं {partner_label} का स्वभाव", expanded=True):
                    st.write(f"• **सप्तमेश ({marriage_lord}) का प्रभाव:** आपका जीवनसाथी सुलझा हुआ, व्यावहारिक और पारिवारिक जिम्मेदारियों को कुशलता से निभाने वाला होगा।")

                # 10. ALL 12 HOUSES ANALYSIS
                section_heading("10. समस्त 12 भावों का अति-विस्तृत फलादेश (12 Bhav Analysis)", "🏛️")

                house_details = [
                    ("प्रथम भाव (तनु भाव)", "व्यक्तित्व, शारीरिक सौष्ठव, आत्मबल, विचार और स्वास्थ्य का प्रतिनिधित्व करता है।"),
                    ("द्वितीय भाव (धन भाव)", "कुटुंब, वाणी, प्रारंभिक शिक्षा, संचित धन और संपत्ति का भाव है।"),
                    ("तृतीय भाव (सहज भाव)", "पराक्रम, कार्यक्षमता, साहस, संचार और भाई-बहनों का स्थान है।"),
                    ("चतुर्थ भाव (सुख भाव)", "माता का सुख, घर का वातावरण, वाहन, भूमि और अचल संपत्ति का प्रतीक है।"),
                    ("पंचम भाव (बुद्धि/प्रेम भाव)", "सोचने की क्षमता, बौद्धिक ज्ञान, प्रेम संबंध और संतान का भाव है।"),
                    ("षष्ठ भाव (रिपु/रोग भाव)", "प्रतिस्पर्धा, दैनिक कार्यशैली, ऋण और स्वास्थ्य/रोग से निपटने का भाव है।"),
                    ("सप्तम भाव (जाया भाव)", "वैवाहिक जीवन, जीवनसाथी का स्वभाव, साझेदारी और सामाजिक संबंध का भाव है।"),
                    ("अष्टम भाव (आयु भाव)", "आयु, अचानक होने वाले परिवर्तन, शोध और गुप्त विद्याओं का स्थान है।"),
                    ("नवम भाव (भाग्य भाव)", "भाग्योदय, धार्मिक आस्था, उच्च विचार और बड़ों के मार्गदर्शन का भाव है।"),
                    ("दशम भाव (कर्म भाव)", "करियर, आजीविका, सामाजिक पद-प्रतिष्ठा और अधिकारों का मुख्य केंद्र है।"),
                    ("एकदश भाव (लाभ भाव)", "आय के स्रोत, वित्तीय लाभ, मित्रों का सहयोग और मनोकामना पूर्ति का भाव है।"),
                    ("द्वादश भाव (व्यय भाव)", "विदेश/दूरस्थ स्थानों से संबंध, खर्चे, आत्म-साक्षात्कार और बचत का भाव है।")
                ]

                for house_num in range(1, 13):
                    h_sign_idx = (asc_sign + house_num - 1) % 12
                    h_sign_name = SIGNS[h_sign_idx]
                    h_lord = RASHI_LORDS[h_sign_idx]
                    planets_here = [p for p, s_idx in planet_positions_map.items() if s_idx == h_sign_idx]
                    h_title, h_desc = house_details[house_num - 1]

                    with st.expander(f"📍 {house_num}. {h_title} — राशि: {h_sign_name} ({SIGNS_HI[h_sign_idx]})", expanded=False):
                        st.write(f"• **भाव का महत्व:** {h_desc}")
                        st.write(f"• **भाव स्वामी (House Lord):** `{h_lord}`")
                        st.write(f"• **स्थित ग्रह:** `{', '.join(planets_here) if planets_here else 'खाली भाव (कोई ग्रह नहीं)'}`")

                # 11. VEDIC & LAL KITAB REMEDIES
                section_heading("11. वैदिक एवं लाल किताब उपाय (Vedic & Lal Kitab Remedies)", "🌿")

                with st.expander("🌿 ग्रह शांति एवं भाग्योदय के मुख्य उपाय", expanded=True):
                    st.write("""
                    1. **आत्मबल व आरोग्य हेतु:** नित्य प्रातः सूर्य देव को तांबे के पात्र से जल अर्पित करें एवं 'ओम् नमः शिवाय' का ध्यानपूर्वक जप करें।
                    2. **कार्यक्षेत्र में उन्नति हेतु:** प्रत्येक शनिवार को हनुमान चालीसा का पाठ करें एवं पीपल के वृक्ष के समीप दीपक प्रज्वलित करें।
                    3. **भाग्यवृद्धि व सुख-समृद्धि हेतु:** माता-पिता व वयोवृद्धों का सदैव सम्मान करें तथा अपनी क्षमतानुसार अन्न या वस्त्र का दान करें।
                    """)

                # PDF DOWNLOAD BUTTON
                st.markdown("---")
                pdf_bytes = generate_pdf_report(
                    name, dob.strftime("%Y-%m-%d"), location.address,
                    SIGNS[asc_sign], SIGNS[moon_sign_idx],
                    active_md, active_ad, detected_yogas
                )
                st.download_button(
                    label="📄 Download Complete Kundli PDF Report",
                    data=bytes(pdf_bytes),
                    file_name=f"{name}_Jyotish_AI_Detailed_Report.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"Calculation error: {e}")
