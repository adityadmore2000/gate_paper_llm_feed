# mlcflow_pipeline/stages.py
import pdfplumber
import re
import json

def is_nat_question(text_block):
    """
    Detects if a question is of type NAT (Numerical Answer Type).
    """
    joined_text = " ".join(text_block.lower().split())
    return (
        "answer in integer" in joined_text or
        "answer in decimal" in joined_text or
        "answer in" in joined_text or
        "rounded off to" in joined_text
    )

def extract_pdf_text(pdf_path):
    """
    Extracts text from the provided PDF file and returns the extracted questions as a list of text blocks.
    """
    questions = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                flat = [cell for row in table for cell in row if cell]
                questions.append(flat)
    return questions

import re

def process_question_text(text_blocks):
    """
    Processes the extracted text blocks to format and structure the questions.
    Determines question type and extracts options for MCQ or MSQ.
    """
    questions = []
    for block in text_blocks:
        if not block:
            continue

        qid_match = re.search(r"Q\.?\s?(\d+)", block[0])
        if not qid_match:
            continue
        qid = qid_match.group(1)

        # Combine all text into a single chunk
        text_block = " ".join(block[1:]).strip()

        # If text_block is empty, default to FIGURE options
        if not text_block:
            question = {
                "id": f"Q{qid}",
                "type": "MCQ",  # Default type when nothing is available
                "question": "FIGURE",
                "options": {k: "FIGURE" for k in "ABCD"}
            }
            questions.append(question)
            continue

        # Question text
        option_start = re.search(r"\(?[A-D]\)?[\.\):]", text_block)
        question_text = text_block
        if option_start:
            question_text = text_block[:option_start.start()].strip()

        # Determine type before extracting options
        if "is/are" in question_text.lower():
            qtype = "MSQ"
        elif is_nat_question(text_block):
            qtype = "NAT"
        else:
            qtype = "MCQ"

        question = {
            "id": f"Q{qid}",
            "type": qtype,
            "question": question_text
        }

        # Extract options if MCQ or MSQ
        if qtype in ["MCQ", "MSQ"]:
            option_matches = re.findall(
                r"(?:^|\n|\s)\(?([A-D])\)?[\.\):]\s*(.*?)(?=(?:\n|\s)\(?[A-D]\)?[\.\):]|$)",
                text_block,
                re.DOTALL
            )
            options = {}
            for match in option_matches:
                if len(match) == 2:
                    key, val = match
                    options[key] = val.replace("\n", " ").strip()

            # If no options found, fallback to FIGURE
            if not options:
                options = {k: "FIGURE" for k in "ABCD"}

            question["options"] = options

        questions.append(question)
    return questions

def save_questions_as_json(questions, output_path):
    """
    Saves the list of questions in JSON format to the specified file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    return f"✅ Done. Saved {len(questions)} questions to {output_path}"
