import pdfplumber
import json
import re
from fractions import Fraction


def normalize_fraction(text):
    parts = text.split("\n")
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        return f"{parts[0]}/{parts[1]}"
    return text.strip()


def is_nat_question(text_block):
    # Flatten multi-line lowercased text for robust detection
    joined_text = " ".join(text_block.lower().split())
    return (
        "answer in integer" in joined_text or
        "answer in decimal" in joined_text or
        "answer in" in joined_text or
        "rounded off to" in joined_text
    )


def extract_questions_from_pdf(pdf_path):
    questions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                flat = [cell for row in table for cell in row if cell]
                q_indices = [i for i, x in enumerate(flat) if re.match(r"Q\.?\s?\d+", x)]
                for idx, q_idx in enumerate(q_indices):
                    start = q_idx
                    end = q_indices[idx + 1] if idx + 1 < len(q_indices) else len(flat)
                    block = flat[start:end]

                    qid_match = re.search(r"Q\.?\s?(\d+)", block[0])
                    if not qid_match:
                        continue
                    qid = qid_match.group(1)

                    # Combine all text into a single chunk
                    text_block = " ".join(block[1:]).strip()

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
                                val = normalize_fraction(val.replace("\n", " ").strip())
                                options[key] = val
                        if options:
                            question["options"] = options

                    questions.append(question)

    return questions


def save_results(results, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"✅ Done. Saved {len(results)} questions to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract GATE questions using table-first strategy")
    parser.add_argument("pdf_path", help="Path to the GATE PDF")
    parser.add_argument("--output", default="gate_questions.json", help="Output JSON file path")

    args = parser.parse_args()

    results = extract_questions_from_pdf(args.pdf_path)
    save_results(results, args.output)
