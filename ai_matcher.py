import re #exact patterns of characters
import spacy  #who reads the resume to find specific facts and clean up the noise.
from sentence_transformers import SentenceTransformer, util #The Encoder ,The Calculator

nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer('all-MiniLM-L6-v2')


SKILL_DB = [
    "python","java","c++","machine learning","deep learning",
    "sql","mysql","mongodb","react","node","aws","docker",
    "communication","leadership","teamwork","problem solving",
    "html","css","javascript","flask","django"
]


def clean(text):
    return " ".join(text.lower().split())


def extract_skills(text):
    text = clean(text)

    found = []
    for skill in SKILL_DB:
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            found.append(skill)

    return list(set(found))


def semantic_score(resume, jd):

    emb1 = model.encode(resume)
    emb2 = model.encode(jd)

    score = util.cos_sim(emb1, emb2)

    return float(score[0][0]) * 100


def match_with_jd(resume_text, jd_text):

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    common = list(set(resume_skills) & set(jd_skills))
    missing = list(set(jd_skills) - set(resume_skills))

    sem_score = semantic_score(resume_text, jd_text)

    skill_score = (len(common) / max(1, len(jd_skills))) * 100

    final = round((0.6 * sem_score) + (0.4 * skill_score), 2)

    return {
    "name": extract_name(resume_text),
    "email": extract_email(resume_text),
    "phone": extract_phone(resume_text),

    "ATS_Score": final,
    "semantic_score": round(sem_score,2),
    "skill_match_score": round(skill_score,2),

    "skills_found": resume_skills,
    "matching_skills": common,
    "missing_skills": missing
    }



def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else "Not Found"


def extract_phone(text):

    pattern = r"(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}"

    match = re.search(pattern, text)

    return match.group(0) if match else "Not Found"


def extract_name(text):

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    email = extract_email(text)

    # 1. If line contains email, previous line is usually name
    for i, line in enumerate(lines):
        if email in line and i > 0:
            return lines[i-1]

    # 2. spaCy NER fallback
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON" and len(ent.text.split()) <= 3:
            return ent.text

    # 3. heuristic first line
    return lines[0][:30]
