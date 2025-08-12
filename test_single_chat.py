import sys
from pathlib import Path


def test_conversation_rag(pdf_path: str, question: str):
    try:
        pass
    except Exception as e:
        print(f"Error during test: {e}")
        raise


if __name__ == "__main__":
    pdf_path = "path/to/your/pdf"
    question = "What is the main topic of the document?"

    if not Path(pdf_path).exists():
        print(f"PDF file does not exist: {pdf_path}")
        sys.exit(1)

    test_conversation_rag(pdf_path, question)
