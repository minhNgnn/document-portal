from __future__ import annotations
import os
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import fitz  # PyMuPDF

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException


class DocumentHandler:
    """
    Handles PDF saving and reading operations
    Automatically logs all actions and supports session-based organization
    """

    def __init__(
        self, data_dir: Optional[str] = None, session_id: Optional[str] = None
    ):
        self.log = CustomLogger().get_logger(__name__)
        self.data_dir = data_dir or os.getenv(
            "DATA_STORAGE_PATH", os.path.join(os.getcwd(), "data", "document_analysis")
        )
        self.session_id = (
            session_id
            or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}"
        )

        # Create base session dir
        self.session_path = os.path.join(self.data_dir, self.session_id)
        os.makedirs(self.session_path, exist_ok=True)

        self.log.info(f"Session initialized: {self.session_id} at {self.session_path}")

    def save_pdf(self, uploaded_file):
        try:
            filename = os.path.basename(uploaded_file.name)

            if not filename.lower().endswith(".pdf"):
                self.log.error("Invalid file type", file_type=filename.split(".")[-1])
                raise ValueError("Invalid file type. Only PDFs are allowed.")

            save_path = os.path.join(self.session_path, filename)
            with open(save_path, "wb") as f:
                if hasattr(uploaded_file, "read"):
                    f.write(uploaded_file.read())
                else:
                    f.write(uploaded_file.get_buffer())
            self.log.info(
                f"PDF saved successfully with file={filename}, save_path={save_path}, session_id={self.session_id}"
            )
            return save_path
        except Exception as e:
            self.log.error(f"Error saving PDF: {e}")
            raise DocumentPortalException(f"Failed to save PDF: {e}") from e

    def read_pdf(self, pdf_path: str):
        try:
            text_chunks = []
            with fitz.open(pdf_path) as doc:
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text_chunks.append(
                        f"\n--- Page {page_num + 1} ---\n{page.get_text()}"
                    )  # type: ignore
            text = "\n".join(text_chunks)
            self.log.info(
                f"PDF read successfully with pdf_path={pdf_path}, session_id={self.session_id}, pages={len(text_chunks)}"
            )
            return text
        except Exception as e:
            self.log.error(f"Error reading PDF: {e}")
            raise DocumentPortalException(f"Failed to read PDF: {e}") from e


if __name__ == "__main__":
    from pathlib import Path

    pdf_path = Path(
        "data/single_document_chat/NIPS-2017-attention-is-all-you-need-Paper.pdf"
    )

    class DummyFile:
        def __init__(self, file_path):
            self.name = Path(file_path).name
            self._file_path = file_path

        def get_buffer(self):
            return open(self._file_path, "rb").read()

    dummy_file = DummyFile(pdf_path)
    handler = DocumentHandler(session_id="test_session")

    try:
        save_path = handler.save_pdf(dummy_file)
        read_text = handler.read_pdf(save_path)
        print(f"PDF saved at: {save_path}")
        print(f"PDF content:\n{read_text}")
    except DocumentPortalException as e:
        print(f"Error: {e}")
