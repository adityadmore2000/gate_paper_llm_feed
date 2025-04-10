import pdfplumber
import re
import os
import json

def update_answers_from_pdf(answer_pdf_path, questions):
    """
    Parses the answer key table from the given PDF and adds an 'answer' field to the questions.
    """
    answer_map = {}

    with pdfplumber.open(answer_pdf_path) as pdf:
        page = pdf.pages[0]  # Only first page as instructed
        tables = []
        for page in pdf.pages:
            tables.extend(page.extract_tables())

        for table in tables:
            for row in table:
                # Skip empty or short rows
                if not row or len(row) < 2:
                    continue

                try:
                    qno_raw = row[0].strip()
                    key_raw = row[-2].strip()  # <-- Second column from right

                    if not qno_raw.isdigit():
                        continue

                    qid = f"Q{int(qno_raw)}"
                    answer_map[qid] = key_raw
                except Exception as e:
                    print(f"Skipping row due to error: {row} -> {e}")

    # Inject answers into questions
    matched = 0
    for q in questions:
        qid = q.get("id")
        if qid in answer_map:
            q["answer"] = answer_map[qid]
            matched += 1

    print(f"✅ Injected answers for {matched}/{len(questions)} questions.")
    return questions

# Paths
base_dir = os.path.dirname(__file__)
input_path = os.path.join(base_dir, "..","output", "gate_questions.json")
output_path = os.path.join(base_dir, "..","output", "gate_questions_updated.json")

# Load questions JSON
with open(input_path, "r", encoding="utf-8") as f:
    questions = json.load(f)

# Update with answers
updated_questions = update_answers_from_pdf(r"C:\Users\adity\Downloads\CS1_Keys.pdf", questions)

# Save updated JSON
with open(output_path, "w", encoding="utf-8") as fp:
    json.dump(updated_questions, fp, indent=4, ensure_ascii=False)

print(f"✅ Done. Saved {len(updated_questions)} questions to {output_path}")
