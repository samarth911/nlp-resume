import pdfplumber
from docx import Document

def parse_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text


def parse_docx(path):
    doc = Document(path)
    
    return "\n".join([p.text for p in doc.paragraphs])



def parse_resume(path):
    if path.endswith(".pdf"):
        return parse_pdf(path)
    elif path.endswith(".docx"):
        return parse_docx(path)
    else:
        raise Exception("Only PDF/DOCX allowed")


# if __name__ == "__main__":
#     output = parse_docx("/Users/samarthnegi/Desktop/Laksh/AI Recruitment & Resume Screening Intelligence System/IMP_Topics.docx")
#     print("---- FUNCTION RETURN ----")
#     print(output)
