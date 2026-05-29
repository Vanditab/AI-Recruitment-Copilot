from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from openai import OpenAI
import tempfile
import re
from typing import List

# =========================
# OPENROUTER CLIENT
# =========================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
     api_key=os.getenv("OPENROUTER_API_KEY")
)

# =========================
# FASTAPI APP
# =========================

app = FastAPI()

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# PDF TEXT EXTRACTION
# =========================

def extract_text_from_pdf(pdf_path):

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted

    return text


# =========================
# EXTRACT ATS SCORE
# =========================

def extract_score(text):

    match = re.search(r'(\d+)%', text)

    if match:
        return int(match.group(1))

    return 65


# =========================
# HOME
# =========================

@app.get("/")
def home():

    return {
        "message": "AI Recruitment Copilot Running 🚀"
    }


# =========================
# ANALYZE RESUMES
# =========================

@app.post("/analyze")
async def analyze_resume(
    resumes: List[UploadFile] = File(...),
    job_description: str = Form(...)
):

    try:

        all_analysis = []

        best_score = 0

        interview_questions = []

        for resume in resumes:

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:

                temp_file.write(await resume.read())

                temp_path = temp_file.name

            resume_text = extract_text_from_pdf(temp_path)

            prompt = f"""
You are an expert AI Hiring Manager.

Analyze this resume according to the given Job Description.

Resume:
{resume_text}

Job Description:
{job_description}

Give detailed response in this format:

ATS Match Percentage: XX%

Matching Skills:
- skill 1
- skill 2

Missing Skills:
- skill 1
- skill 2

Relevant Projects:
- project 1
- project 2

Weak Areas:
- weakness 1
- weakness 2

Fraud Detection:
(Is resume exaggerated or genuine?)

Salary Prediction:
(Expected salary range)

Behavior Analysis:
(Confidence, communication, leadership)

Technical Interview Questions:
1.
2.
3.
4.
5.

HR Interview Questions:
1.
2.
3.

Coding Round Questions:
1.
2.
3.

Hiring Recommendation:
(Short recommendation)

Skill Gap Roadmap:
- what to learn
- what to improve

LinkedIn Bio:
(generate professional bio)

Resume Improvement Suggestions:
- suggestion 1
- suggestion 2
"""

            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            result = response.choices[0].message.content

            score = extract_score(result)

            if score > best_score:
                best_score = score

            all_analysis.append(
                f"# {resume.filename}\n\n{result}"
            )

            lines = result.split("\n")

            for line in lines:

                if "?" in line:

                    clean_line = line.strip()

                    if clean_line not in interview_questions:
                        interview_questions.append(clean_line)

        final_analysis = "\n\n---\n\n".join(all_analysis)

        return {
            "analysis": final_analysis,
            "ats_score": best_score,
            "questions": interview_questions[:10]
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# =========================
# MOCK INTERVIEW
# =========================

@app.post("/mock-interview")
async def mock_interview(
    answer: str = Form(...),
    question: str = Form(...),
    job_description: str = Form(...)
):

    try:

        prompt = f"""
You are an expert technical interviewer.

Job Description:
{job_description}

Interview Question:
{question}

Candidate Answer:
{answer}

Evaluate professionally.

Give:

Feedback:
(short feedback)

Confidence Score:
(X/10)

Behavior Analysis:
(confidence, clarity, communication)

Improvements:
- point 1
- point 2

Better Sample Answer:
(improved answer)
"""

        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result = response.choices[0].message.content

        return {
            "feedback": result
        }

    except Exception as e:

        return {
            "error": str(e)
        }