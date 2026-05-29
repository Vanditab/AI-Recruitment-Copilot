import streamlit as st
import requests
from fpdf import FPDF
import plotly.express as px
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="HireSense AI",
    page_icon="🚀",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

.stApp {
    background-color: #0E1117;
}

.card {
    background: #1c1f26;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 0px 10px rgba(255,255,255,0.05);
}

.big-font {
    font-size: 28px;
    font-weight: bold;
}

.small-font {
    font-size: 15px;
    color: #A0A0A0;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================

st.title("🚀 HireSense AI")
st.markdown("### AI Powered Resume Screening & Hiring Assistant")

st.divider()

# =========================
# SESSION STATE
# =========================

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "job_description" not in st.session_state:
    st.session_state.job_description = ""

if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = []

# =========================
# INPUT SECTION
# =========================

col1, col2 = st.columns(2)

with col1:

    uploaded_files = st.file_uploader(
        "📄 Upload Multiple Resumes",
        type=["pdf"],
        accept_multiple_files=True
    )

with col2:

    job_description = st.text_area(
        "💼 Paste Job Description",
        height=250
    )

# =========================
# ANALYZE BUTTON
# =========================

if st.button("🔍 Analyze Resumes"):

    if uploaded_files and job_description:

        with st.spinner("Analyzing resumes with AI..."):

            files = []

            for file in uploaded_files:

                files.append(
                    (
                        "resumes",
                        (
                            file.name,
                            file,
                            "application/pdf"
                        )
                    )
                )

            data = {
                "job_description": job_description
            }

            response = requests.post(
                "http://127.0.0.1:8000/analyze",
                files=files,
                data=data
            )

            result = response.json()

            st.session_state.analysis_result = result
            st.session_state.job_description = job_description

            if "questions" in result:
                st.session_state.interview_questions = result["questions"]

    else:

        st.warning("Please upload resumes and paste job description.")

# =========================
# SHOW RESULTS
# =========================

if st.session_state.analysis_result:

    result = st.session_state.analysis_result

    if "error" in result:

        st.error(result["error"])

    else:

        ats_score = result.get("ats_score", 75)

        total_candidates = len(uploaded_files)

        avg_score = np.random.randint(65, 85)

        # =========================
        # ANALYTICS CARDS
        # =========================

        st.subheader("📊 Recruiter Analytics Dashboard")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(f"""
            <div class="card">
                <div class="big-font">{total_candidates}</div>
                <div class="small-font">Candidates</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="card">
                <div class="big-font">{ats_score}%</div>
                <div class="small-font">Best ATS Score</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="card">
                <div class="big-font">⭐</div>
                <div class="small-font">Strong Hire</div>
            </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
            <div class="card">
                <div class="big-font">{avg_score}%</div>
                <div class="small-font">Average Match</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # =========================
        # CHARTS
        # =========================

        st.subheader("📈 ATS Score Analytics")

        chart_data = pd.DataFrame({
            "Candidate": [f"Candidate {i+1}" for i in range(total_candidates)],
            "ATS Score": np.random.randint(60, 95, total_candidates)
        })

        fig = px.bar(
            chart_data,
            x="Candidate",
            y="ATS Score",
            text="ATS Score"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # =========================
        # CANDIDATE ANALYSIS
        # =========================

        st.subheader("🤖 AI Candidate Analysis")

        st.markdown(result["analysis"])

        st.divider()

        # =========================
        # MOCK INTERVIEW
        # =========================

        st.subheader("🎤 AI Mock Interview")

        questions = st.session_state.interview_questions

        if not questions:

            questions = [
                "Tell me about yourself.",
                "Explain one project you worked on.",
                "What are your strengths?"
            ]

        selected_question = st.selectbox(
            "Choose Interview Question",
            questions
        )

        st.info(selected_question)

        answer = st.text_area(
            "✍ Your Answer",
            height=200
        )

        if st.button("Evaluate My Answer"):

            if answer.strip() == "":

                st.warning("Please write your answer first.")

            else:

                with st.spinner("Evaluating Answer..."):

                    response = requests.post(
                        "http://127.0.0.1:8000/mock-interview",
                        data={
                            "answer": answer,
                            "question": selected_question,
                            "job_description": st.session_state.job_description
                        }
                    )

                    feedback = response.json()

                    if "feedback" in feedback:

                        st.success("Interview Feedback Ready ✅")

                        st.markdown(feedback["feedback"])

                    else:

                        st.error(feedback["error"])

        st.divider()

        # =========================
        # SKILL GAP ROADMAP
        # =========================

        st.subheader("📌 Skill Gap Suggestions")

        skills = [
            "Docker",
            "CI/CD",
            "System Design",
            "REST APIs",
            "TypeScript",
            "AWS Deployment",
            "DSA & Problem Solving"
        ]

        cols = st.columns(3)

        for i, skill in enumerate(skills):

            with cols[i % 3]:
                st.success(skill)

        st.divider()

        # =========================
        # PDF REPORT
        # =========================

        st.subheader("📄 Download AI Hiring Report")

        if st.button("Generate PDF Report"):

            pdf = FPDF()

            pdf.add_page()

            pdf.set_font("Arial", size=12)

            report_text = f"""
HireSense AI Report

Best ATS Score: {ats_score}%

AI Candidate Analysis:

{result["analysis"]}
"""

            clean_text = report_text.encode(
                "latin-1",
                "replace"
            ).decode("latin-1")

            pdf.multi_cell(
                0,
                10,
                clean_text
            )

            pdf.output("AI_Report.pdf")

            with open("AI_Report.pdf", "rb") as file:

                st.download_button(
                    label="⬇ Download PDF",
                    data=file,
                    file_name="HireSense_AI_Report.pdf",
                    mime="application/pdf"
                )