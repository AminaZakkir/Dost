import streamlit as st
from groq import Groq
import pandas as pd
import os

# Your Groq API Key
API_KEY = "API_KEY = st.secrets[GROQ_API_KEY]"
client = Groq(api_key=API_KEY)

# ── User Database Functions ──────────────────────
def load_users():
    if os.path.exists('data/users.csv'):
        return pd.read_csv('data/users.csv')
    return pd.DataFrame(columns=[
        'username', 'password', 'name', 'stream',
        'year', 'state', 'category', 'income', 'language'
    ])

def save_user(username, password, name, stream,
              year, state, category, income, language):
    df = load_users()
    new_user = pd.DataFrame([{
        'username': username, 'password': password,
        'name': name, 'stream': stream, 'year': year,
        'state': state, 'category': category,
        'income': income, 'language': language
    }])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv('data/users.csv', index=False)

def check_login(username, password):
    df = load_users()
    user = df[
        (df['username'] == username) &
        (df['password'] == password)
    ]
    if not user.empty:
        return user.iloc[0]
    return None

def username_exists(username):
    df = load_users()
    return username in df['username'].values

# ── Admin Functions ───────────────────────────────
def load_admins():
    if os.path.exists('data/admin.csv'):
        return pd.read_csv('data/admin.csv')
    else:
        df = pd.DataFrame([{'username': 'admin', 'password': 'admin123'}])
        df.to_csv('data/admin.csv', index=False)
        return df

def check_admin_login(username, password):
    df = load_admins()
    match = df[(df['username'] == username) & (df['password'] == password)]
    return not match.empty

# ── Applications (History) Functions ─────────────
def load_applications():
    if os.path.exists('data/applications.csv'):
        return pd.read_csv('data/applications.csv')
    return pd.DataFrame(columns=[
        'username', 'type', 'name', 'amount_or_stipend',
        'deadline', 'status'
    ])

def save_application(username, item_type, name, amount_or_stipend, deadline):
    df = load_applications()
    already_applied = df[
        (df['username'] == username) & (df['name'] == name)
    ]
    if not already_applied.empty:
        return False
    new_row = pd.DataFrame([{
        'username': username, 'type': item_type, 'name': name,
        'amount_or_stipend': amount_or_stipend, 'deadline': deadline,
        'status': 'Ongoing'
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv('data/applications.csv', index=False)
    return True

def update_application_status(username, name, new_status):
    df = load_applications()
    df.loc[(df['username'] == username) & (df['name'] == name), 'status'] = new_status
    df.to_csv('data/applications.csv', index=False)
def clear_user_history(username):
    df = load_applications()
    df = df[df['username'] != username]
    df.to_csv('data/applications.csv', index=False)

def delete_single_application(username, name):
    df = load_applications()
    df = df[~((df['username'] == username) & (df['name'] == name))]
    df.to_csv('data/applications.csv', index=False)

# ── Page Setup ───────────────────────────────────
st.set_page_config(
    page_title="Dost — Your College Senior",
    page_icon="🎓",
    layout="wide"
)

# ── Styling ──────────────────────────────────────
st.markdown("""
    <style>
    .main { background-color: #f0f4ff; }
    </style>
""", unsafe_allow_html=True)

# ── Greeting Function ────────────────────────────
def get_greeting(name, language):
    if language == "Malayalam":
        return f"ഹായ് {name}! 👋 ഞാൻ ഡോസ്റ്റ് ആണ് — നിങ്ങളുടെ സ്വന്തം കോളേജ് സീനിയർ! നിങ്ങളുടെ പ്രൊഫൈൽ അനുസരിച്ച് scholarships കണ്ടെത്തി. എന്തും ചോദിക്കൂ! 😊"
    elif language == "Hindi":
        return f"नमस्ते {name}! 👋 मैं Dost हूं — आपका अपना कॉलेज सीनियर! आपकी प्रोफाइल के अनुसार scholarships मिली हैं। कुछ भी पूछो! 😊"
    elif language == "Tamil":
        return f"வணக்கம் {name}! 👋 நான் Dost — உங்கள் சொந்த கல்லூரி சீனியர்! உங்கள் profile க்கு ஏற்ற scholarships கண்டுபிடித்தேன். எதுவும் கேளுங்கள்! 😊"
    else:
        return f"Hi {name}! 👋 I am Dost — your personal college senior! I found scholarships matching your profile. Ask me anything about scholarships, internships, branch selection or college life. I am always here! 😊"

# ── Scholarship About ────────────────────────────
def get_scholarship_about(name):
    about = {
        "Kerala HEC UG Scholarship": "Kerala Higher Education Council scholarship for meritorious UG students with low family income.",
        "Kerala DCE SC Scholarship": "Department of Collegiate Education Kerala — supports SC students in government and aided colleges.",
        "Kerala Minority Scholarship": "Kerala government scheme supporting Muslim, Christian, Buddhist, Sikh and Jain students.",
        "Kerala eGrantz SC ST Scholarship": "Online scholarship portal by Kerala government for SC/ST students covering full fee reimbursement.",
        "KSFDC Scholarship": "Kerala Scheduled Castes Development Corporation scholarship for SC students.",
        "Prof Joseph Mundassery Scholarship": "Named after Kerala's first Education Minister — awarded to outstanding minority students.",
        "CH Muhammedkoya Scholarship": "Kerala Minority Welfare scholarship named after former Chief Minister for minority girl students.",
        "APJ Abdul Kalam Scholarship": "Named after India's Missile Man — Kerala scholarship for minority students in technical education.",
        "Bhinnaseshy Souhrida Scholarship": "Kerala government scholarship supporting differently abled students in higher education.",
        "Kerala State Merit Scholarship": "Merit-based scholarship by Kerala DCE rewarding top-scoring students from low income families.",
        "TN Post Matric SC ST Scholarship": "Tamil Nadu government full financial support for SC/ST students in post-matriculation education.",
        "TN BC MBC Scholarship": "Tamil Nadu scholarship for Backward Class and Most Backward Class students in higher education.",
        "TN First Graduate Scholarship": "Tamil Nadu special scheme for students who are the first in their family to attend college!",
        "TN Pudhumai Penn Scholarship": "Tamil Nadu CM scheme giving ₹1000 monthly to all girl students in government colleges.",
        "TN EVR Nagammai Scholarship": "Named after Periyar's wife — Tamil Nadu scholarship empowering women in postgraduate education.",
        "TN Differently Abled Scholarship": "Tamil Nadu government support for differently abled students across all streams.",
        "TN Minority Post Matric Scholarship": "Tamil Nadu Minority Welfare Department scholarship for Muslim, Christian and other minority students.",
        "TN Perarignar Anna Award": "Prestigious merit award named after former CM C.N. Annadurai for top BC/MBC students.",
        "TN SC ST Overseas Scholarship": "Tamil Nadu scheme funding SC/ST students to study abroad at top universities.",
        "TN Chief Minister Fellowship": "Tamil Nadu CM's flagship scholarship for highly meritorious students across all disciplines.",
        "TN Tamil Pudhalvan Scheme": "Tamil Nadu monthly support scheme for boy students entering government colleges.",
        "TN Merit Cum Means Scholarship": "Tamil Nadu scholarship combining merit and financial need for minority students.",
        "TN Pre Matric Minority Scholarship": "Tamil Nadu Minority Welfare support for minority students in school and college.",
        "TN Adi Dravidar Welfare Scholarship": "Tamil Nadu Adi Dravidar Welfare Department scholarship for SC students.",
        "TN Tribal Welfare Scholarship": "Tamil Nadu Tribal Welfare Department scholarship for ST students in higher education.",
        "TN Girl Student Nursing Scholarship": "Tamil Nadu special scholarship encouraging girl students to pursue nursing.",
        "TN Engineering First Graduate Scholarship": "Tamil Nadu scheme for first-generation engineering students.",
        "TN Law Students Scholarship": "Tamil Nadu government support for students pursuing law education.",
        "TN Sports Scholarship": "Tamil Nadu scholarship recognising talented sports students in higher education.",
        "TN BC Muslim Scholarship": "Tamil Nadu scholarship for BC Muslim community students in higher education.",
    }
    return about.get(name, "Government scholarship supporting students in higher education.")

# ── Internship About ─────────────────────────────
def get_internship_about(name):
    about = {
        "PM Internship Scheme": "Prime Minister's flagship scheme — 12-month paid internship at top Indian companies for youth aged 18-24.",
        "AICTE National Internship Portal": "Free national portal connecting students with 200+ domains including AI, data science and government projects.",
        "Digital India Internship NIC MeitY": "Ministry of Electronics and IT internship on e-governance, cybersecurity and software development.",
        "NITI Aayog Internship": "Work with India's top policy think tank on national-level IT, data and governance projects.",
        "IBM SkillsBuild Virtual Internship": "Free 8-week online internship by IBM covering AI, Cybersecurity, Data Analytics and Front-End Development.",
        "TCS iON Virtual Internship": "100% free internship by Tata Consultancy Services covering IT and business analytics from home.",
        "Google STEP Internship": "Google's paid internship program for 1st and 2nd year CS/IT students.",
        "Microsoft Explore Internship": "Microsoft's paid internship for early college students interested in software engineering.",
        "Tata Global Internship": "Tata Group's structured paid internship across IT, finance and operations sectors.",
        "Reliance Foundation Internship": "Reliance Foundation paid internship across technology and social impact domains.",
        "Internshala": "India's largest internship platform with thousands of paid and unpaid opportunities.",
        "LinkedIn Jobs": "World's largest professional network with internship listings from companies across India.",
        "ISRO Internship": "Indian Space Research Organisation internship for CS/IT students with CGPA 7+ on space projects.",
        "Skill India Digital": "Government of India free internship and training portal with certificates across skill domains.",
        "YBI Foundation Bootcamp": "Short 15-45 day project-based internships with certificates for IT students.",
        "ASAP Kerala Internship": "Additional Skill Acquisition Programme — Kerala government paid internship for graduates.",
        "KSUM Student Programs": "Kerala Startup Mission internship in Kerala's growing startup ecosystem.",
        "Technopark Trivandrum": "India's first IT park in Trivandrum — 300+ companies offering student internships.",
        "Infopark Kochi": "Kerala's premier IT park in Kochi with major IT companies for BCA/CS students.",
        "Cyberpark Calicut": "North Kerala's IT hub in Calicut with software development internship opportunities.",
        "Nestsoft Technologies": "Kochi-based IT company offering free certificate internships for BCA/BSc CS students.",
        "SMEClabs Internship": "Kerala technical training institute offering short internships with certificates.",
        "TIDEL Park Chennai": "Tamil Nadu's top IT park in Chennai hosting major companies with student internships.",
        "SIPCOT IT Park": "State Industries Promotion Corporation of Tamil Nadu IT park with internship opportunities.",
        "TN e-Governance Internship": "Tamil Nadu government internship on digital governance and e-services projects.",
        "ELCOT Tamil Nadu": "Electronics Corporation of Tamil Nadu internship for CS/IT students in government tech.",
    }
    return about.get(name, "A great internship opportunity to build your skills and resume.")

    # ── Card Renderers ────────────────────────────────
def render_scholarship_card(row, username, key_prefix="", language="English"):
    L = get_labels(language)
    st.markdown(f"**🎓 {row['name']}**")
    st.markdown(f"{L['deadline']}: {row['deadline']}  \n{L['amount']}: ₹{row['amount']}")
    with st.expander(L['view_details']):
        st.markdown(f"📌 {get_scholarship_about(row['name'])}")
        st.markdown(f"**{L['amount']}:** ₹{row['amount']}")
        st.markdown(f"**{L['deadline']}:** {row['deadline']}")
        docs = row['documents'].split('+')
        st.markdown(f"**{L['documents']}:**")
        for doc in docs:
            st.markdown(f"- {doc.strip()}")
        st.markdown(f"**{L['apply']}:** [{row['link']}]({row['link']})")
        if st.button(L['mark_applied'], key=f"apply_schol_{key_prefix}_{row['name']}"):
            saved = save_application(username, "Scholarship", row['name'], f"₹{row['amount']}", row['deadline'])
            if saved:
                st.success("Marked as applied! Check your History page.")
            else:
                st.info("You already marked this as applied.")
    st.divider()

def render_internship_card(row, username, key_prefix="", language="English"):
    L = get_labels(language)
    st.markdown(f"**💼 {row['name']}**")
    st.markdown(f"{L['location']}: {row['location']}  \n{L['duration']}: {row['duration']}")
    with st.expander(L['view_details']):
        st.markdown(f"📌 {get_internship_about(row['name'])}")
        st.markdown(f"**{L['location']}:** {row['location']}")
        st.markdown(f"**{L['duration']}:** {row['duration']}")
        st.markdown(f"**{L['eligibility']}:** {row['eligibility']}")
        st.markdown(f"**{L['stipend']}:** {row['stipend']}")
        st.markdown(f"**{L['how_to_apply']}:** {row['how_to_apply']}")
        st.markdown(f"**{L['apply']}:** [{row['link']}]({row['link']})")
        if st.button(L['mark_applied'], key=f"apply_intern_{key_prefix}_{row['name']}"):
            saved = save_application(username, "Internship", row['name'], row['stipend'], "N/A")
            if saved:
                st.success("Marked as applied! Check your History page.")
            else:
                st.info("You already marked this as applied.")
    st.divider()

def get_scholarship_cards_data(category, income, state, stream, filter_type="all"):
    df = pd.read_csv('data/scholarships.csv')
    df['stream'] = df['stream'].fillna('All').str.strip()
    if filter_type == "kerala":
        results = df[df['state'].str.strip() == 'Kerala']
    elif filter_type == "tn":
        results = df[df['state'].str.strip() == 'Tamil Nadu']
    else:
        results = df[(df['category'] == category) | (df['category'] == 'General')]
        results = results[results['income_limit'] >= income]
        results = results[(results['state'] == state) | (results['state'] == 'All India')]
    results = results[(results['stream'] == stream) | (results['stream'] == 'All')]
    return results

# ── Label Translations ───────────────────────────
def get_labels(language):
    if language == "Malayalam":
        return {
            "amount": "💰 തുക",
            "deadline": "📅 അവസാന തീയതി",
            "documents": "📄 ആവശ്യമായ രേഖകൾ",
            "apply": "🔗 ഇവിടെ അപേക്ഷിക്കൂ",
            "location": "📍 സ്ഥലം",
            "duration": "⏱️ ദൈർഘ്യം",
            "eligibility": "✅ യോഗ്യത",
            "stipend": "💰 സ്റ്റൈപ്പൻഡ്",
            "how_to_apply": "📝 എങ്ങനെ അപേക്ഷിക്കാം",
            "mark_applied": "✅ അപേക്ഷിച്ചതായി രേഖപ്പെടുത്തുക",
            "view_details": "വിശദാംശങ്ങൾ കാണുക",
            "scholarships_title": "നിങ്ങൾക്കുള്ള സ്കോളർഷിപ്പുകൾ",
            "internships_title": "നിങ്ങൾക്കുള്ള ഇന്റേൺഷിപ്പുകൾ",
        }
    elif language == "Hindi":
        return {
            "amount": "💰 राशि",
            "deadline": "📅 अंतिम तिथि",
            "documents": "📄 आवश्यक दस्तावेज़",
            "apply": "🔗 यहाँ आवेदन करें",
            "location": "📍 स्थान",
            "duration": "⏱️ अवधि",
            "eligibility": "✅ पात्रता",
            "stipend": "💰 वजीफा",
            "how_to_apply": "📝 आवेदन कैसे करें",
            "mark_applied": "✅ आवेदन किया हुआ चिह्नित करें",
            "view_details": "विवरण देखें",
            "scholarships_title": "आपके लिए छात्रवृत्तियाँ",
            "internships_title": "आपके लिए इंटर्नशिप",
        }
    elif language == "Tamil":
        return {
            "amount": "💰 தொகை",
            "deadline": "📅 கடைசி தேதி",
            "documents": "📄 தேவையான ஆவணங்கள்",
            "apply": "🔗 இங்கே விண்ணப்பிக்கவும்",
            "location": "📍 இடம்",
            "duration": "⏱️ காலம்",
            "eligibility": "✅ தகுதி",
            "stipend": "💰 உதவித்தொகை",
            "how_to_apply": "📝 விண்ணப்பிப்பது எப்படி",
            "mark_applied": "✅ விண்ணப்பித்ததாக குறிக்கவும்",
            "view_details": "விவரங்களைக் காண்க",
            "scholarships_title": "உங்களுக்கான கல்வி உதவித்தொகைகள்",
            "internships_title": "உங்களுக்கான பயிற்சி வாய்ப்புகள்",
        }
    else:
        return {
            "amount": "💰 Amount",
            "deadline": "📅 Last Date",
            "documents": "📄 Documents Required",
            "apply": "🔗 Apply Here",
            "location": "📍 Location",
            "duration": "⏱️ Duration",
            "eligibility": "✅ Eligibility",
            "stipend": "💰 Stipend",
            "how_to_apply": "📝 How to Apply",
            "mark_applied": "✅ Mark as Applied",
            "view_details": "View Details",
            "scholarships_title": "Scholarships for you",
            "internships_title": "Internships for you",
        }


def get_internship_cards_data(stream, filter_type="all"):
    df = pd.read_csv('data/internships.csv')
    df['stream'] = df['stream'].fillna('All').str.strip()
    if filter_type == "kerala":
        results = df[df['state'] == 'Kerala']
    elif filter_type == "tn":
        results = df[df['state'] == 'Tamil Nadu']
    else:
        results = df
    results = results[(results['stream'] == stream) | (results['stream'] == 'All')]
    return results
def render_cards_grid(data, render_func, username, key_prefix="", cols_per_row=2, language="English"):
    rows_list = list(data.iterrows())
    for i in range(0, len(rows_list), cols_per_row):
        chunk = rows_list[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for col_idx, (_, row) in enumerate(chunk):
            with cols[col_idx]:
                render_func(row, username, key_prefix, language)

# ── Scholarship Filter ───────────────────────────
def get_scholarships(category, income, state, stream="All"):
    try:
        df = pd.read_csv('data/scholarships.csv')
        eligible = df[
            (df['category'] == category) |
            (df['category'] == 'General')
        ]
        eligible = eligible[eligible['income_limit'] >= income]
        eligible = eligible[
            (eligible['state'] == state) |
            (eligible['state'] == 'All India')
        ]
        # Filter by stream
        if 'stream' in df.columns:
            eligible = eligible[
                (eligible['stream'] == stream) |
                (eligible['stream'] == 'All')
            ]
        if eligible.empty:
            return "No scholarships found for this profile."
        result = ""
        for _, row in eligible.iterrows():
            result += f"""
SCHOLARSHIP_START
Name: {row['name']}
Amount: ₹{row['amount']}
Deadline: {row['deadline']}
Documents: {row['documents']}
Link: {row['link']}
SCHOLARSHIP_END
"""
        return result
    except Exception as e:
        return f"Error loading scholarships: {e}"
# ── AI Response ──────────────────────────────────
def get_response(user_message, profile, scholarships):
    msg = user_message.lower()
# Resume template request
    resume_keywords = ["resume", "cv", "write a resume",
                       "help me write a resume", "resume template",
                       "make a resume", "create a resume"]
    if any(kw in msg for kw in resume_keywords):
        return f"""Here is a professional resume template for you, {profile['name']}! 📄

---

### {profile['name'].upper()}
📍 City, State  |  📧 email@gmail.com  |  📱 +91 XXXXXXXXXX

---

### 🎓 EDUCATION
- Degree | College Name | Year | CGPA/Percentage

---

### 💻 SKILLS
- Technical Skills: Python, Java, HTML, MySQL
- Soft Skills: Communication, Teamwork, Problem Solving

---

### 📁 PROJECTS
- Project Name | Brief Description | Tech Used

---

### 🏆 ACHIEVEMENTS
- Achievement 1
- Achievement 2

---

### 🌐 LANGUAGES
- Malayalam | English | Hindi

---

### 📌 DECLARATION
I declare that all information is true to the best of my knowledge.

**{profile['name']}** | Date: ___________

---

💪 **Quick Tips:**
- Keep it ONE page only
- Save as PDF before sending
- Add your Dost project — it shows real AI skills!
"""
    # Check internship FIRST before state filters
    # Specific advice questions — check BEFORE internship list
    advice_keywords = [
        "prepare", "how to prepare", "interview tips",
        "resume", "cv", "how to apply", "application letter",
        "email to professor", "how to write email",
        "what documents", "documents needed", "documents required",
        "cgpa", "backlog", "career", "job after",
        "which branch", "branch selection", "skills needed",
        "tips for", "guide me", "help me write",
        "interview", "how do i prepare"
    ]
    if any(kw in msg for kw in advice_keywords):
        prompt = f"""
You are Dost — a warm helpful AI college senior
guiding first-generation college students in India.

STUDENT PROFILE:
Name: {profile['name']}
Stream: {profile['stream']}
Year: {profile['year']}
State: {profile['state']}

RULES:
- Answer ONLY the specific question asked
- Do NOT show scholarship or internship lists
- Give practical step by step advice
- Keep answer clear and simple
- Respond in {profile['language']} language
- End with one encouraging tip

Student asks: {user_message}
Dost responds:"""
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            return {"type": "text", "content": response.choices[0].message.content}
        except Exception as e:
            return f"Oops! Sorry {profile['name']}, something went wrong. Please try again! 😊"

    internship_keywords = ["internship", "intern", "training",
                           "work experience", "ഇന്റേൺഷിപ്പ്",
                           "इंटर्नशिप", "பயிற்சி", "placement"]

    if any(kw in msg for kw in internship_keywords):
        f = "kerala" if ("kerala" in msg or "കേരള" in msg) else \
            "tn" if ("tamil" in msg) else "all"
        results = get_internship_cards_data(profile['stream'], f)
        return {"type": "internship_cards", "data": results, "name": profile['name']}

    # Kerala scholarships AFTER internship check
    kerala_keywords = ["kerala", "കേരള", "keralam", "kerala scholarships", "kerala scholarship"]
    scholarship_keywords = ["scholarship", "scholarships"]
    if any(kw in msg for kw in scholarship_keywords):
        f = "kerala" if ("kerala" in msg or "കേരള" in msg) else \
            "tn" if ("tamil" in msg) else "all"
        results = get_scholarship_cards_data(
            profile['category'], profile['income'], profile['state'], profile['stream'], f)
        return {"type": "scholarship_cards", "data": results, "name": profile['name']}
    

    # if any(kw in msg for kw in internship_keywords):
    #     try:
    #         df = pd.read_csv('data/internships.csv')

    #         student_stream = profile['stream']
    #         st.write(f"DEBUG: Filtering for stream = {student_stream}")

    # if any(kw in msg for kw in internship_keywords):
    #     try:
    #         df = pd.read_csv('data/internships.csv')
    #         df['stream'] = df['stream'].fillna('All').str.strip()
    #         student_stream = str(profile['stream']).strip()

    #         if "kerala" in msg or "കേരള" in msg:
    #             filtered = df[
    #                 (df['state'] == 'Kerala') &
    #                 ((df['stream'] == student_stream) | (df['stream'] == 'All'))
    #             ]
    #             header = f"Here are Kerala internships for {student_stream} students, {profile['name']}! 🌴"
    #         elif "tamil nadu" in msg or "tamilnadu" in msg or "tamil" in msg:
    #             filtered = df[
    #                 (df['state'] == 'Tamil Nadu') &
    #                 ((df['stream'] == student_stream) | (df['stream'] == 'All'))
    #             ]
    #             header = f"Here are Tamil Nadu internships for {student_stream} students, {profile['name']}! 🌟"
    #         else:
    #             filtered = df[
    #                 (df['stream'] == student_stream) |
    #                 (df['stream'] == 'All')
    #             ]
    #             header = f"Here are internships for {student_stream} students, {profile['name']}! 💼"

    #         if filtered.empty:
    #             filtered = df[df['stream'] == 'All']
    #             header = f"Here are general internships for you, {profile['name']}! 💼"

    #         lines = [header, ""]
    #         for _, row in filtered.iterrows():
    #             lines.append("---")
    #             lines.append(f"### • {row['name']}")
    #             lines.append(f"📌 {get_internship_about(row['name'])}")
    #             lines.append(f"📍 **Location:** {row['location']}")
    #             lines.append(f"⏱️ **Duration:** {row['duration']}")
    #             lines.append(f"✅ **Eligibility:** {row['eligibility']}")
    #             lines.append(f"💰 **Stipend:** {row['stipend']}")
    #             lines.append(f"📝 **How to Apply:** {row['how_to_apply']}")
    #             lines.append(f"🔗 **Apply Here:** [{row['link']}]({row['link']})")
    #             lines.append("")

    #         lines.append(f"💪 {profile['name']}, apply to at least 3 internships this week! 🌟")
    #         return "\n".join(lines)

        # except Exception as e:
        #     return f"Error: {e}"
    # Internship recommendations
    if any(kw in msg for kw in internship_keywords):
        try:
            df = pd.read_csv("data/internships.csv")

            # Clean stream column
            df["stream"] = df["stream"].fillna("All").str.strip()
            student_stream = str(profile["stream"]).strip()

            st.write(f"DEBUG: Filtering internships for stream = {student_stream}")

            # Filter based on state
            if "kerala" in msg or "കേരള" in msg:
                filtered = df[
                    (df["state"] == "Kerala") &
                    ((df["stream"] == student_stream) | (df["stream"] == "All"))
                ]
                header = (
                    f"Here are Kerala internships for {student_stream} students, "
                    f"{profile['name']}! 🌴"
                )

            elif (
                "tamil nadu" in msg
                or "tamilnadu" in msg
                or "tamil" in msg
            ):
                filtered = df[
                    (df["state"] == "Tamil Nadu") &
                    ((df["stream"] == student_stream) | (df["stream"] == "All"))
                ]
                header = (
                    f"Here are Tamil Nadu internships for {student_stream} students, "
                    f"{profile['name']}! 🌟"
                )

            else:
                filtered = df[
                    (df["stream"] == student_stream)
                    | (df["stream"] == "All")
                ]
                header = (
                    f"Here are internships for {student_stream} students, "
                    f"{profile['name']}! 💼"
                )

            # If no stream-specific internships, show general internships
            if filtered.empty:
                filtered = df[df["stream"] == "All"]
                header = (
                    f"Here are general internships for you, "
                    f"{profile['name']}! 💼"
                )

            lines = [header, ""]

            for _, row in filtered.iterrows():
                lines.append("---")
                lines.append(f"### • {row['name']}")
                lines.append(f"📌 {get_internship_about(row['name'])}")
                lines.append(f"📍 **Location:** {row['location']}")
                lines.append(f"⏱️ **Duration:** {row['duration']}")
                lines.append(f"✅ **Eligibility:** {row['eligibility']}")
                lines.append(f"💰 **Stipend:** {row['stipend']}")
                lines.append(f"📝 **How to Apply:** {row['how_to_apply']}")
                lines.append(f"🔗 **Apply Here:** [{row['link']}]({row['link']})")
                lines.append("")

            lines.append(
                f"💪 {profile['name']}, apply to at least 3 internships this week! 🌟"
            )

            return "\n".join(lines)

        except Exception as e:
            return f"Error loading internships: {e}"

    # Tamil Nadu specific
    tn_keywords = ["tamil nadu", "tamilnadu", "தமிழ்நாடு", "tamil"]
    if any(kw in msg for kw in tn_keywords):
        try:
            df = pd.read_csv('data/scholarships.csv')
            tn_only = df[df['state'] == 'Tamil Nadu']
            if tn_only.empty:
                return f"Sorry {profile['name']}, no Tamil Nadu scholarships found."
            result = f"Here are Tamil Nadu specific scholarships for you, {profile['name']}! 🌟\n\n"
            for _, row in tn_only.iterrows():
                docs = row['documents'].split('+')
                doc_list = "\n".join([f"   - {d.strip()}" for d in docs])
                result += f"""---

## • {row['name']}

📌 {get_scholarship_about(row['name'])}

💰 **Amount:** ₹{row['amount']}
📅 **Last Date:** {row['deadline']}
📄 **Documents Required:**
{doc_list}
🔗 **Apply Here:** [{row['link']}]({row['link']})

"""
            result += f"\n\n💪 {profile['name']}, apply before deadlines and verify at official websites! 🌟"
            result += f"""

---
🤔 **Want to know more?** You can ask me:
- *"How do I apply for these scholarships?"*
- *"What documents do I need?"*
- *"Which scholarship gives the most money?"*
- *"Help me write an application letter"*
"""
            return result
        
        except Exception as e:
            return f"Error: {e}"

    # Internship specific
    internship_keywords = ["internship", "intern", "training",
                           "work experience", "ഇന്റേൺഷിപ്പ്",
                           "इंटर्नशिप", "பயிற்சி", "placement"]

    if any(kw in msg for kw in internship_keywords):
        try:
            df = pd.read_csv('data/internships.csv')

            # Check for state specific request
            if "kerala" in msg or "കേരള" in msg:
                filtered = df[df['state'] == 'Kerala']
                title = f"Here are Kerala internship opportunities for you, {profile['name']}! 🌴\n\n"
            elif "tamil nadu" in msg or "tamilnadu" in msg or "tamil" in msg:
                filtered = df[df['state'] == 'Tamil Nadu']
                title = f"Here are Tamil Nadu internship opportunities for you, {profile['name']}! 🌟\n\n"
            else:
                # Filter by year recommendation
                year_num = profile['year'].replace('st Year','').replace('nd Year','').replace('rd Year','').replace('th Year','').strip()
                filtered = df[
                    df['year_recommended'].str.contains('1st Year', na=False) |
                    (profile['year'] == '2nd Year') & df['year_recommended'].str.contains('2nd Year', na=False) |
                    (profile['year'] == '3rd Year') & df['year_recommended'].str.contains('3rd Year', na=False) |
                    (profile['year'] == '4th Year') & df['year_recommended'].str.contains('3rd Year', na=False)
                ]
                title = f"Here are internship opportunities recommended for {profile['year']} students like you, {profile['name']}! 💼\n\n"

            if filtered.empty:
                filtered = df
                title = f"Here are all internship opportunities for you, {profile['name']}! 💼\n\n"

            result = title
            for _, row in filtered.iterrows():
                result += f"\n\n---\n\n### • {row['name']}\n\n"
                result += f"📍 **Location:** {row['location']}\n\n"
                result += f"⏱️ **Duration:** {row['duration']}\n\n"
                result += f"✅ **Eligibility:** {row['eligibility']}\n\n"
                result += f"💰 **Stipend:** {row['stipend']}\n\n"
                result += f"📝 **How to Apply:** {row['how_to_apply']}\n\n"
                result += f"🔗 **Apply Here:** [{row['link']}]({row['link']})\n\n"
                
            result += f"\n\n💪 {profile['name']}, apply to at least 3 internships this week! 🌟"
            result += f"""

---
🤔 **Want to know more?** You can ask me:
- *"Kerala internships"*
- *"Tamil Nadu internships"*
- *"How do I prepare for internship interview?"*
- *"Help me write a resume"*
"""
            return result
        except Exception as e:
            return f"Error: {e}"

# Kerala scholarships
    kerala_keywords = ["kerala", "കേരള", "keralam",
                       "kerala scholarships", "kerala scholarship"]
    if any(kw in msg for kw in kerala_keywords):
        try:
            df = pd.read_csv('data/scholarships.csv')
            kerala_only = df[df['state'].str.strip() == 'Kerala']
            if kerala_only.empty:
                return f"Sorry {profile['name']}, no Kerala scholarships found."
            result = f"Here are Kerala specific scholarships for you, {profile['name']}! 🌴\n\n"
            for _, row in kerala_only.iterrows():
                docs = row['documents'].split('+')
                doc_list = "\n".join([f"   - {d.strip()}" for d in docs])
                result += f"""---

## • {row['name']}

📌 {get_scholarship_about(row['name'])}

💰 **Amount:** ₹{row['amount']}
📅 **Last Date:** {row['deadline']}
📄 **Documents Required:**
{doc_list}
🔗 **Apply Here:** [{row['link']}]({row['link']})

"""
            result += f"\n\n💪 {profile['name']}, apply before deadlines and verify at official websites! 🌟"
            return result
        except Exception as e:
            return f"Error: {e}"

    # Tamil Nadu scholarships
    tn_keywords = ["tamil nadu", "tamilnadu", "தமிழ்நாடு",
                   "tamil nadu scholarships", "tn scholarships"]
    if any(kw in msg for kw in tn_keywords):
        try:
            df = pd.read_csv('data/scholarships.csv')
            tn_only = df[df['state'].str.strip() == 'Tamil Nadu']
            if tn_only.empty:
                return f"Sorry {profile['name']}, no Tamil Nadu scholarships found."
            result = f"Here are Tamil Nadu specific scholarships for you, {profile['name']}! 🌟\n\n"
            for _, row in tn_only.iterrows():
                docs = row['documents'].split('+')
                doc_list = "\n".join([f"   - {d.strip()}" for d in docs])
                result += f"""---

## • {row['name']}

💰 **Amount:** ₹{row['amount']}
📅 **Last Date:** {row['deadline']}
📄 **Documents Required:**
{doc_list}
🔗 **Apply Here:** [{row['link']}]({row['link']})

"""
            result += f"\n\n💪 {profile['name']}, apply before deadlines and verify at official websites! 🌟"
            return result
        except Exception as e:
            return f"Error: {e}"

    

    # All other questions
    prompt = f"""
You are Dost — a warm, helpful AI college senior
guiding first-generation college students in India.

STUDENT PROFILE:
Name: {profile['name']}
Stream: {profile['stream']}
Year: {profile['year']}
State: {profile['state']}
Category: {profile['category']}
Income: ₹{profile['income']}

SCHOLARSHIPS THIS STUDENT QUALIFIES FOR:
{scholarships}

STRICT FORMAT RULES — FOLLOW EXACTLY:
When showing scholarships, use THIS EXACT format.
Each part MUST be on a NEW LINE.
Do NOT merge name and description together.

## **• [Scholarship Name]**

[Write 2-3 warm sentences about this scholarship addressing student by name]

💰 **Amount:** ₹[amount]
📅 **Last Date:** [deadline]
📄 **Documents Required:**
- [document 1]
- [document 2]
- [document 3]
🔗 **Apply Here:** [exact link from database]

---

IMPORTANT RULES:
RULES:
- If student asks about scholarships → show ALL scholarships 
  from the database with full details
- If student asks about specific topic like documents, 
  eligibility, how to apply → answer ONLY that specific topic
- If student asks for resume → give full resume template
- If student asks about career → give career guidance
- If student asks something you don't know → reply:
  "Oops! Sorry, I am still working on that! 
   You can ask me about scholarships, internships, 
   documents needed, resume tips, or career guidance! 😊"
- Respond in {profile['language']} language
- End with one helpful follow up suggestion
- Never cut short scholarship information
- Always show complete scholarship details when asked

Student says: {user_message}
Dost responds:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content
        if not reply or len(reply.strip()) < 10:
            return {"type": "text", "content": f"Oops! Sorry {profile['name']}, I am still working on that. You can ask me about scholarships, internships, documents needed, resume tips, or career guidance! 😊"}
        return {"type": "text", "content": reply}
    except Exception as e:
        return {"type": "text", "content": f"Oops! Sorry {profile['name']}, something went wrong. Please try asking again! 😊"}

# ── Login Page ───────────────────────────────────
def show_login_page():
    st.markdown("""
        <style>
        @keyframes bounce {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-15px); }
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.15); }
        }
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(30px); }
            100% { opacity: 1; transform: translateY(0px); }
        }
        .login-icon {
            font-size: 80px;
            text-align: center;
            animation: bounce 2s ease-in-out infinite;
            display: block;
            margin: 20px auto;
        }
        .login-title {
            text-align: center;
            font-size: 42px;
            font-weight: 800;
            color: #1565C0;
            animation: fadeIn 1s ease-in-out;
            margin: 0;
        }
        .login-caption {
            text-align: center;
            color: #666;
            font-style: italic;
            animation: fadeIn 1.5s ease-in-out;
            margin-bottom: 20px;
        }
        .login-box {
            animation: fadeIn 1s ease-in-out;
        }
        </style>

        <div class="login-icon">🎓</div>
        <p class="login-title">Dost</p>
        <p class="login-caption">
            The college senior every first-generation student deserves
        </p>
    """, unsafe_allow_html=True)

    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Welcome to Dost!")
        tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Register", "🛡️ Admin"])

        with tab1:
            st.markdown("#### Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input(
                "Password", type="password", key="login_password")
            if st.button("Login →", key="login_btn"):
                if username and password:
                    user = check_login(username, password)
                    if user is not None:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.messages = []
                        st.session_state.greeted = False
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Wrong username or password!")
                else:
                    st.warning("⚠️ Please enter username and password!")

        with tab2:
            st.markdown("#### Create New Account")
            new_name = st.text_input("Your Full Name", key="reg_name")
            new_username = st.text_input(
                "Choose Username", key="reg_username")
            new_password = st.text_input(
                "Choose Password", type="password", key="reg_password")
            confirm_password = st.text_input(
                "Confirm Password", type="password", key="reg_confirm")
            new_stream = st.selectbox("Your Stream", [
                "BCA", "Engineering", "BSc",
                "BCom", "Arts", "Medicine"
            ], key="reg_stream")
            new_year = st.selectbox("Your Year", [
                "1st Year", "2nd Year",
                "3rd Year", "4th Year"
            ], key="reg_year")
            new_state = st.selectbox("Your State", [
                "Kerala", "Tamil Nadu", "Karnataka",
                "Maharashtra", "Bihar", "Other"
            ], key="reg_state")
            new_category = st.selectbox("Your Category", [
                "General", "OBC", "SC", "ST", "Minority"
            ], key="reg_category")
            new_income = st.number_input(
                "Family Annual Income (₹)",
                min_value=0, max_value=1500000,
                value=250000, step=10000, key="reg_income"
            )
            new_language = st.selectbox("Preferred Language", [
                "English", "Malayalam", "Hindi", "Tamil"
            ], key="reg_language")

            if st.button("Create Account →", key="register_btn"):
                if new_name and new_username and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("❌ Passwords do not match!")
                    elif username_exists(new_username):
                        st.error("❌ Username already taken!")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters!")
                    else:
                        save_user(
                            new_username, new_password,
                            new_name, new_stream, new_year,
                            new_state, new_category,
                            new_income, new_language
                        )
                        st.success("✅ Account created! Please login now.")
                else:
                    st.warning("⚠️ Please fill all fields!")
        with tab3:
            st.markdown("#### 🛡️ Admin Login")
            admin_username = st.text_input("Admin Username", key="admin_username")
            admin_password = st.text_input("Admin Password", type="password", key="admin_password")
            if st.button("Admin Login →", key="admin_login_btn"):
                if check_admin_login(admin_username, admin_password):
                    st.session_state.is_admin = True
                    st.session_state.logged_in = True
                    st.session_state.page = "admin_dashboard"
                    st.success("✅ Admin login successful!")
                    st.rerun()
                else:
                    st.error("❌ Wrong admin username or password!")

# ── Initialize Login State ───────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "chat"

# ── Main App ─────────────────────────────────────
if not st.session_state.logged_in:
    show_login_page()

elif st.session_state.get("is_admin", False):
    # Admin Dashboard
    st.title("🛡️ Admin Dashboard")
    st.caption("Private analytics — visible only to admin")
    st.divider()

    users_df = load_users()
    apps_df = load_applications()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", len(users_df))
    col2.metric("Total Applications", len(apps_df))
    col3.metric("Completed", len(apps_df[apps_df['status'] == 'Completed']) if not apps_df.empty else 0)

    st.divider()

    if not apps_df.empty:
        st.subheader("📈 Most Applied For")
        top_items = apps_df['name'].value_counts().head(10)
        st.bar_chart(top_items)

        st.divider()
        st.subheader("🗺️ Users by State")
        if 'state' in users_df.columns:
            state_counts = users_df['state'].value_counts()
            st.bar_chart(state_counts)

        st.divider()
        st.subheader("📋 All Applications")
        for idx, row in apps_df.iterrows():
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"**{row['username']}** — {row['name']} ({row['type']}) — *{row['status']}*")
            with col_b:
                if st.button("🗑️", key=f"admin_del_{idx}"):
                    delete_single_application(row['username'], row['name'])
                    st.rerun()
    else:
        st.info("No application data yet.")

    st.divider()
    if st.button("🚪 Admin Logout"):
        st.session_state.is_admin = False
        st.session_state.logged_in = False
        st.session_state.page = "chat"
        st.rerun()

else:
    user = st.session_state.user
    name = str(user['name'])
    stream = str(user['stream'])
    year = str(user['year'])
    state = str(user['state'])
    category = str(user['category'])
    income = int(user['income'])
    language = str(user['language'])

    # ── Sidebar ──────────────────────────────────
    # ── Sidebar ──────────────────────────────────
    with st.sidebar:

        # Profile Button
        if st.button(f"👤 {name} — My Profile", key="btn_profile"):
            st.session_state.page = "profile"
            st.rerun()
        st.divider()

        
        # Quick Ask Buttons
        st.markdown("### 💬 Ask Dost About")
        if st.button("🎓 My Scholarships", key="btn_scholar"):
            st.session_state.page = "chat"
            st.session_state.auto_query = "What scholarships can I get?"
            st.rerun()
        if st.button("🌴 Kerala Scholarships", key="btn_kerala"):
            st.session_state.page = "chat"
            st.session_state.auto_query = "Kerala scholarships"
            st.rerun()
        if st.button("🌟 Tamil Nadu Scholarships", key="btn_tn"):
            st.session_state.page = "chat"
            st.session_state.auto_query = "Tamil Nadu scholarships"
            st.rerun()
        if st.button("💼 Internships", key="btn_intern"):
            st.session_state.page = "chat"
            st.session_state.auto_query = "What internships can I get?"
            st.rerun()
        if st.button("📊 History", key="btn_history"):
            st.session_state.page = "history"
            st.rerun()
        st.divider()

        if st.button("🔄 New Chat", key="btn_newchat"):
            st.session_state.messages = []
            st.session_state.greeted = False
            st.session_state.page = "chat"
            st.rerun()
        if st.button("🚪 Logout", key="btn_logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.messages = []
            st.session_state.greeted = False
            st.session_state.page = "chat"
            st.rerun()

# ── Header ───────────────────────────────────
    # ── Page Router ──────────────────────────────
    if st.session_state.get("is_admin", False):
        st.title("🛡️ Admin Dashboard")
        st.caption("Private analytics — visible only to admin")
        st.divider()

        users_df = load_users()
        apps_df = load_applications()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Users", len(users_df))
        col2.metric("Total Applications", len(apps_df))
        col3.metric("Completed", len(apps_df[apps_df['status'] == 'Completed']) if not apps_df.empty else 0)

        st.divider()

        if not apps_df.empty:
            st.subheader("📈 Most Applied For")
            top_items = apps_df['name'].value_counts().head(10)
            st.bar_chart(top_items)

            st.divider()
            st.subheader("🗺️ Users by State")
            if 'state' in users_df.columns:
                state_counts = users_df['state'].value_counts()
                st.bar_chart(state_counts)

            st.divider()
            st.subheader("📋 All Applications (All Users)")
            for idx, row in apps_df.iterrows():
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.markdown(f"**{row['username']}** — {row['name']} ({row['type']}) — *{row['status']}*")
                with col_b:
                    if st.button("🗑️", key=f"admin_del_{idx}"):
                        delete_single_application(row['username'], row['name'])
                        st.rerun()
        else:
            st.info("No application data yet.")

        st.divider()
        if st.button("🚪 Admin Logout"):
            st.session_state.is_admin = False
            st.session_state.logged_in = False
            st.session_state.page = "chat"
            st.rerun()

    if st.session_state.page == "history":
        st.title("📊 My History")
        st.caption("Track your scholarship and internship applications")
        st.divider()

        apps_df = load_applications()
        my_apps = apps_df[apps_df['username'] == user['username']]

        if my_apps.empty:
            st.info("You haven't marked any applications yet. Go to Scholarships or Internships and click 'Mark as Applied'!")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Applications", len(my_apps))
            col2.metric("Ongoing", len(my_apps[my_apps['status'] == 'Ongoing']))
            col3.metric("Completed", len(my_apps[my_apps['status'] == 'Completed']))

            st.divider()
            st.subheader("📈 Status Overview")
            status_counts = my_apps['status'].value_counts()
            st.bar_chart(status_counts)

            st.divider()
            st.subheader("📋 All Applications")
            if st.button("🗑️ Clear All History", key="clear_all_history"):
                clear_user_history(user['username'])
                st.success("History cleared!")
                st.rerun()

            for _, row in my_apps.iterrows():
                icon = "🎓" if row['type'] == "Scholarship" else "💼"
                with st.expander(f"{icon} {row['name']}  |  {row['status']}"):
                    st.markdown(f"**Type:** {row['type']}")
                    st.markdown(f"**Amount/Stipend:** {row['amount_or_stipend']}")
                    st.markdown(f"**Deadline:** {row['deadline']}")
                    new_status = st.selectbox(
                        "Update Status", ["Ongoing", "Completed"],
                        index=0 if row['status'] == 'Ongoing' else 1,
                        key=f"status_{row['name']}"
                    )
                    if st.button("Update", key=f"update_{row['name']}"):
                        update_application_status(user['username'], row['name'], new_status)
                        st.success("Status updated!")
                        st.rerun()
                    if st.button("🗑️ Delete", key=f"delete_{row['name']}"):
                        delete_single_application(user['username'], row['name'])
                        st.success("Deleted!")
                        st.rerun()

        st.divider()
        if st.button("⬅️ Back to Chat"):
            st.session_state.page = "chat"
            st.rerun()

    elif st.session_state.page == "profile":

        # Profile Page
        st.title("👤 My Profile")
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📋 Current Details")
            st.markdown(f"**📛 Name:** {name}")
            st.markdown(f"**🎓 Stream:** {stream}")
            st.markdown(f"**📅 Year:** {year}")
            st.markdown(f"**📍 State:** {state}")
            st.markdown(f"**🏷️ Category:** {category}")
            st.markdown(f"**💰 Income:** ₹{income}")
            st.markdown(f"**🌐 Language:** {language}")

        with col2:
            st.markdown("### ✏️ Update Your Details")
            new_stream = st.selectbox("Your Stream", [
                "BCA", "Engineering", "BSc",
                "BCom", "Arts", "Medicine"
            ], index=["BCA", "Engineering", "BSc",
                      "BCom", "Arts", "Medicine"].index(stream))
            new_year = st.selectbox("Your Year", [
                "1st Year", "2nd Year",
                "3rd Year", "4th Year"
            ], index=["1st Year", "2nd Year",
                      "3rd Year", "4th Year"].index(year))
            new_state = st.selectbox("Your State", [
                "Kerala", "Tamil Nadu", "Karnataka",
                "Maharashtra", "Bihar", "Other"
            ], index=["Kerala", "Tamil Nadu", "Karnataka",
                      "Maharashtra", "Bihar", "Other"].index(state))
            new_category = st.selectbox("Your Category", [
                "General", "OBC", "SC", "ST", "Minority"
            ], index=["General", "OBC", "SC",
                      "ST", "Minority"].index(category))
            new_income = st.number_input(
                "Family Annual Income (₹)",
                min_value=0, max_value=1500000,
                value=income, step=10000)
            new_language = st.selectbox("Your Language", [
                "English", "Malayalam", "Hindi", "Tamil"
            ], index=["English", "Malayalam",
                      "Hindi", "Tamil"].index(language))

            if st.button("💾 Save Changes"):
                updated_user = st.session_state.user.copy()
                updated_user['stream'] = new_stream
                updated_user['year'] = new_year
                updated_user['state'] = new_state
                updated_user['category'] = new_category
                updated_user['income'] = new_income
                updated_user['language'] = new_language
                st.session_state.user = updated_user
                st.success("✅ Profile updated successfully!")

        st.divider()
        if st.button("⬅️ Back to Chat"):
            st.session_state.page = "chat"
            st.rerun()

    else:
        # ── Chat Page ─────────────────────────────
        st.title("🎓 Dost")
        st.caption("*The college senior every first-generation student deserves*")
        st.divider()

        scholarships = get_scholarships(str(category), int(income), str(state), str(stream))

        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.greeted = False

            # Handle auto query from sidebar buttons
        if "auto_query" in st.session_state and st.session_state.auto_query:
            auto_msg = st.session_state.auto_query
            st.session_state.auto_query = ""
            st.session_state.messages.append({
                "role": "user",
                "content": auto_msg
            })
            profile = {
                "name": name,
                "stream": stream,
                "year": year,
                "state": state,
                "category": category,
                "income": income,
                "language": language
            }
            scholarships = get_scholarships(
                str(category), int(income), str(state))
            auto_reply = get_response(
                auto_msg, profile, scholarships)
            st.session_state.messages.append({
                "role": "assistant",
                "content": auto_reply
            })

        if not st.session_state.get("greeted", False):
            st.session_state.messages = [{
                "role": "assistant",
                "content": get_greeting(name, language)
            }]
            st.session_state.greeted = True

        for msg_idx, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                content = msg["content"]
                if isinstance(content, dict):
                    if content["type"] == "scholarship_cards":
                        st.markdown(f"Here are scholarships for you, {content['name']}! 🎓")
                        if content["data"].empty:
                            st.markdown("No scholarships found for your profile right now.")
                        else:
                            render_cards_grid(content["data"], render_scholarship_card, user['username'], key_prefix=f"m{msg_idx}", cols_per_row=2, language=language)
                    elif content["type"] == "internship_cards":
                        st.markdown(f"Here are internships for you, {content['name']}! 💼")
                        if content["data"].empty:
                            st.markdown("No internships found for your profile right now.")
                        else:
                            render_cards_grid(content["data"], render_internship_card, user['username'], key_prefix=f"m{msg_idx}", cols_per_row=2, language=language)
                    else:
                        st.markdown(content["content"])
                else:
                    st.markdown(content)

        if prompt := st.chat_input("Ask Dost anything..."):
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Dost is thinking... 🤔"):
                    try:
                        profile = {
                            "name": name,
                            "stream": stream,
                            "year": year,
                            "state": state,
                            "category": category,
                            "income": income,
                            "language": language
                        }

                        reply = get_response(
                            prompt, profile, scholarships)
                        for line in reply.split('\n'):
                            st.markdown(line)

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": reply
                        })
                    except Exception as e:
                        st.error(f"Error: {e}")