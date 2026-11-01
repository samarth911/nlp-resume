from fastapi import FastAPI, UploadFile
import shutil
from parser import parse_resume
from ai_matcher import match_with_jd

app = FastAPI()
# decorator

@app.post("/upload_resume")
async def upload(file: UploadFile):

    path = f"temp_{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = parse_resume(path)

    return {"message": "resume uploaded", "resume": text}

print(parse_resume("/Users/samarthnegi/Desktop/Laksh/AI Recruitment & Resume Screening Intelligence System/IMP_Topics.docx"))

@app.post("/match")
async def match(data: dict):

    resume_text = data.get("resume","")
    jd = data.get("jd","")

    if not resume_text or not jd:
        return {"error":"empty input"}

    result = match_with_jd(resume_text, jd)

    return result


@app.post("/bulk_match")
async def bulk_match(data: dict):

    resumes = data.get("resumes", [])  # list of resume texts
    jd = data.get("jd", "")            # single job description text (backward compatibility)
    jds = data.get("jds", [])          # list of {name, text} for multiple JDs

    if not resumes:
        return {"error": "No resumes provided"}
    
    # Support both single JD (backward compatibility) and multiple JDs
    if jds:
        # Multiple JDs mode
        if not jds or len(jds) == 0:
            return {"error": "No job descriptions provided"}
        
        results = []
        
        # Process each JD
        for jd_item in jds:
            jd_name = jd_item.get("name", "Unknown JD")
            jd_text = jd_item.get("text", "")
            
            if not jd_text or not jd_text.strip():
                continue
            
            ranking = []
            
            # Process each resume against this JD
            for resume_text in resumes:
                if not resume_text or not resume_text.strip():
                    continue
                    
                result = match_with_jd(resume_text, jd_text)
                
                ranking.append({
                    "name": result.get("name", "Not Found"),
                    "email": result.get("email", "Not Found"),
                    "phone": result.get("phone", "Not Found"),
                    "score": result.get("ATS_Score", 0.0),
                    "matching_skills": result.get("matching_skills", [])
                })
            
            # Sort by score (highest first)
            ranking = sorted(ranking, key=lambda x: x["score"], reverse=True)
            
            results.append({
                "jd_name": jd_name,
                "ranking": ranking
            })
        
        return {
            "results": results
        }
    
    elif jd and jd.strip():
        # Single JD mode (backward compatibility)
        ranking = []
        
        # Process each resume
        for resume_text in resumes:
            if not resume_text or not resume_text.strip():
                continue
                
            result = match_with_jd(resume_text, jd)
            
            ranking.append({
                "name": result.get("name", "Not Found"),
                "email": result.get("email", "Not Found"),
                "phone": result.get("phone", "Not Found"),
                "score": result.get("ATS_Score", 0.0),
                "matching_skills": result.get("matching_skills", [])
            })
        
        # Sort by score (highest first)
        ranking = sorted(ranking, key=lambda x: x["score"], reverse=True)
        
        return {
            "ranking": ranking
        }
    else:
        return {"error": "Job description is required"}

