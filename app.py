import streamlit as st
import os
import PyPDF2
from dotenv import load_dotenv
from groq import Groq


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Career & Resume Agent",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# 2. LOAD API KEY
# =========================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY is missing. Please check your .env file.")
    st.stop()

client = Groq(api_key=api_key)


# =========================================================
# 3. PROFESSIONAL UI
# =========================================================

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #666;
    margin-bottom: 30px;
}

.card {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #ddd;
    margin-bottom: 15px;
}

.stButton > button {
    width: 100%;
    border-radius: 8px;
    font-weight: 600;
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 4. TITLE
# =========================================================

st.markdown(
    '<div class="main-title">🤖 AI Career & Resume Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Upload your resume and get personalized AI-powered career guidance'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# 5. LOAD CAREER KNOWLEDGE BASE - RAG
# =========================================================

try:

    with open("career_knowledge.txt", "r", encoding="utf-8") as file:
        career_knowledge = file.read()

except FileNotFoundError:

    st.error(
        "career_knowledge.txt file was not found. "
        "Please create it in the same folder as app.py."
    )

    st.stop()


# =========================================================
# 6. CAREER KNOWLEDGE SEARCH TOOL
# =========================================================

def search_career_knowledge(query):

    """
    Search the career knowledge base
    and return relevant information.
    """

    query_words = query.lower().split()

    lines = career_knowledge.split("\n")

    relevant_lines = []

    for line in lines:

        line_lower = line.lower()

        if any(word in line_lower for word in query_words):

            relevant_lines.append(line)

    if relevant_lines:

        return "\n".join(relevant_lines[:10])

    return "No relevant career information found."


# =========================================================
# 7. CAREER INFORMATION
# =========================================================

st.markdown("## 💼 Career Information")

st.write(
    "Enter your details to get personalized career guidance."
)

name = st.text_input(
    "Your Name",
    placeholder="Enter your name"
)

skills = st.text_input(
    "Your Skills",
    placeholder="Example: Python, JavaScript, HTML, CSS, React"
)

target_role = st.text_input(
    "Target Job Role",
    placeholder="Example: Software Developer"
)

job_description = st.text_area(
    "Job Description",
    placeholder="Paste the job description here..."
)


# =========================================================
# 8. RESUME UPLOAD
# =========================================================

st.markdown("---")

st.markdown("## 📄 Resume Upload")

uploaded_file = st.file_uploader(
    "Upload your Resume (PDF or TXT)",
    type=["pdf", "txt"]
)


# =========================================================
# 9. RESUME ANALYSIS
# =========================================================

if uploaded_file is not None:

    st.success("Resume uploaded successfully!")

    if st.button("🔍 Analyze Resume"):

        with st.spinner("Analyzing your resume..."):

            # ---------------------------------------------
            # Read TXT
            # ---------------------------------------------

            if uploaded_file.name.lower().endswith(".txt"):

                resume_text = uploaded_file.read().decode(
                    "utf-8",
                    errors="ignore"
                )

            # ---------------------------------------------
            # Read PDF
            # ---------------------------------------------

            else:

                pdf_reader = PyPDF2.PdfReader(uploaded_file)

                resume_text = ""

                for page in pdf_reader.pages:

                    page_text = page.extract_text()

                    if page_text:
                        resume_text += page_text + "\n"


            # =================================================
            # 10. SEARCH KNOWLEDGE BASE
            # =================================================

            search_query = f"""
            {skills}
            {target_role}
            {job_description}
            {resume_text[:2000]}
            """

            knowledge_result = search_career_knowledge(
                search_query
            )


            # =================================================
            # 11. AI PROMPT
            # =================================================

            prompt = f"""

You are an AI Career and Resume Agent.

Your job is to analyze a candidate's resume and
provide personalized career guidance.

You have access to a career knowledge base.

Use the knowledge base when relevant.

==================================================
CAREER KNOWLEDGE BASE
==================================================

{career_knowledge}

==================================================
RELEVANT KNOWLEDGE FOUND BY TOOL
==================================================

{knowledge_result}

==================================================
CANDIDATE INFORMATION
==================================================

Name:
{name}

Skills entered by candidate:
{skills}

Target Job Role:
{target_role}

Job Description:
{job_description}

==================================================
RESUME
==================================================

{resume_text}

==================================================
TASK
==================================================

Analyze the resume and provide the following:

1. Candidate's Main Skills

Identify the important technical and professional skills
found in the resume.

2. Suitable Job Roles

Suggest suitable entry-level job roles based on the
candidate's skills and resume.

3. Missing or Weak Skills

Identify important skills that are missing or need
improvement for the target role.

4. Recommended Learning Roadmap

Create a simple step-by-step learning roadmap.

5. Interview Preparation

Give important interview topics and questions
the candidate should prepare.

6. Career Recommendation

Give a short explanation of what the candidate
should focus on next.

Keep the answer simple, clear and practical.

Use headings and bullet points.

Do not invent information that is not supported
by the resume or career knowledge base.

"""


            # =================================================
            # 12. GROQ LLM CALL
            # =================================================

            try:

                response = client.chat.completions.create(

                    model="openai/gpt-oss-20b",

                    messages=[

                        {
                            "role": "system",
                            "content": (
                                "You are a helpful AI Career "
                                "and Resume Agent."
                            )
                        },

                        {
                            "role": "user",
                            "content": prompt
                        }

                    ],

                    temperature=0.2

                )


                result = response.choices[0].message.content


                # =================================================
                # 13. DISPLAY RESULT
                # =================================================

                st.success("✅ Analysis completed!")

                st.markdown("---")

                st.markdown("## 🤖 AI Career Analysis")

                st.markdown(result)


                # =================================================
                # 14. TOOL INFORMATION
                # =================================================

                with st.expander("🔧 Tool / RAG Information"):

                    st.write(
                        "The agent searched the career "
                        "knowledge base before generating "
                        "the recommendation."
                    )

                    st.write(
                        "This demonstrates a simple "
                        "RAG + tool-based workflow."
                    )


            except Exception as e:

                st.error(
                    f"Something went wrong while analyzing "
                    f"the resume: {e}"
                )
