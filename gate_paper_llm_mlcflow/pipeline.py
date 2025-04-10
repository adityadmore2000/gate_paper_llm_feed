# mlcflow_pipeline/pipeline.py
import os
from gate_paper_llm_mlcflow.stages import extract_pdf_text, process_question_text, save_questions_as_json

def process_pdf_to_json(pdf_path, output_path=os.path.join(os.path.dirname(__file__), "output", "gate_questions.json")):
    """
    Main pipeline function that orchestrates the stages: 
    extracting text from the PDF, processing it, and saving it to a JSON file.
    """
    # Extract text blocks from the PDF
    text_blocks = extract_pdf_text(pdf_path)
    
    # Process the extracted text to format the questions
    questions = process_question_text(text_blocks)
    
    # Save the processed questions to a JSON file
    result_message = save_questions_as_json(questions, output_path)
    
    return result_message
