import requests

path = "/Users/samarthnegi/Desktop/Laksh/AI Recruitment & Resume Screening Intelligence System/IMP_Topics.docx"

with open(path, "rb") as f:
    res = requests.post(
        "http://localhost:8000/upload_resume",
        files={"file": f}
    )

print("STATUS:", res.status_code)
print("RAW RESPONSE:")


print("###########################")
print(res.text)
print("###########################")
