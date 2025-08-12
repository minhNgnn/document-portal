# Testing code for document comparison using LLMs

import io
from pathlib import Path
from src.data_ingestion.data_ingestion import DocumentComparator
from src.document_compare.document_comparator import DocumentComparatorLLM


# ---- Setup: Load local PDF files as if they were "uploaded" ---- #
def load_fake_uploaded_file(file_path: Path):
    return io.BytesIO(file_path.read_bytes())  # simulate .getbuffer()


# ---- Step 1: Save and combine PDFs ---- #
def test_compare_documents():
    ref_path = Path(
        "/Users/pc/Developer/document-portal/data/document_compare/Long_Report_V1.pdf"
    )
    act_path = Path(
        "/Users/pc/Developer/document-portal/data/document_compare/Long_Report_V2.pdf"
    )

    # Wrap them like Streamlit UploadedFile-style
    class FakeUpload:
        def __init__(self, file_path: Path):
            self.name = file_path.name
            self._buffer = file_path.read_bytes()

        def getbuffer(self):
            return self._buffer

    # Instantiate
    comparator = DocumentComparator()
    ref_upload = FakeUpload(ref_path)
    act_upload = FakeUpload(act_path)

    # Save files and combine
    ref_file, act_file = comparator.save_uploaded_files(ref_upload, act_upload)
    combined_text = comparator.combine_documents()
    comparator.clean_old_sessions(keep_latest=3)

    print("\n Combined Text Preview (First 1000 chars):\n")
    print(combined_text[:1000])

    # ---- Step 2: Run LLM comparison ---- #
    llm_comparator = DocumentComparatorLLM()
    df = llm_comparator.compare_documents(combined_text)

    print("\n Comparison DataFrame:\n")
    print(df)


if __name__ == "__main__":
    test_compare_documents()
