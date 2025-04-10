# main.py
import argparse

from gate_paper_llm_mlcflow.pipeline import process_pdf_to_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract GATE questions using table-first strategy")
    parser.add_argument("--pdf_path", help="Path to the GATE PDF")
    parser.add_argument("--output", default="output/gate_questions.json", help="Output JSON file path")
    
    args = parser.parse_args()

    # Run the pipeline with the provided PDF and output path
    print(process_pdf_to_json(pdf_path=args.pdf_path, output_path=args.output))
