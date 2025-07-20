from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import io

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    total_sum = 0
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                # Find header row to locate column indices
                headers = [col.strip().lower() for col in table[0]]
                try:
                    prod_idx = headers.index("product")
                    total_idx = headers.index("total")
                except ValueError:
                    continue  # skip tables without correct headers
                for row in table[1:]:
                    if row[prod_idx].strip().lower() == "gizmo":
                        value = row[total_idx].replace(',', '').strip()
                        try:
                            total_sum += int(value)
                        except ValueError:
                            continue
    return {"sum": total_sum}
