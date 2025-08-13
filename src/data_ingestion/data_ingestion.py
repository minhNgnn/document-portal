from __future__ import annotations
import os
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import fitz  # PyMuPDF
import shutil

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


class FaissManager:
    def __init__(self):
        try:
            self.log = CustomLogger().get_logger(__name__)
        except Exception as e:
            self.log.error(f"Error initializing FaissManager: {e}")
            raise DocumentPortalException(
                f"Failed to initialize FaissManager: {e}"
            ) from e

    def _exists(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error checking existence: {e}")
            raise DocumentPortalException(f"Failed to check existence: {e}") from e

    def _fingerprint(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error generating fingerprint: {e}")
            raise DocumentPortalException(f"Failed to generate fingerprint: {e}") from e

    def _save_meta(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error saving metadata: {e}")
            raise DocumentPortalException(f"Failed to save metadata: {e}") from e

    def load_or_create(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error loading or creating: {e}")
            raise DocumentPortalException(f"Failed to load or create: {e}") from e


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


class ChatIngestor:
    def __init__(self):
        pass

    def _resolve_dir(self):
        pass

    def _split(self):
        pass

    def build_retriever(self):
        pass


class DocumentComparator:
    """
    Save, read & combine PDFs for comparison with session-based versioning.
    """

    def __init__(
        self, base_dir: str = "data/document_compare", session_id: Optional[str] = None
    ):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.session_id = (
            session_id
            or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}"
        )
        self.session_path = self.base_dir / self.session_id
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.log.info(
            f"DocumentComparator initialized session_path={self.session_path}"
        )

    def save_uploaded_files(self, reference_file, actual_file) -> tuple[Path, Path]:
        try:
            ref_path = self.session_path / reference_file.name
            act_path = self.session_path / actual_file.name
            for fobj, out in ((reference_file, ref_path), (actual_file, act_path)):
                if not fobj.name.lower().endswith(".pdf"):
                    raise ValueError("Only PDF files are allowed.")
                with open(out, "wb") as f:
                    if hasattr(fobj, "read"):
                        f.write(fobj.read())
                    else:
                        f.write(fobj.getbuffer())
            self.log.info(
                f"Files saved reference={ref_path}, actual={act_path}, session={self.session_id}"
            )
            return ref_path, act_path
        except Exception as e:
            self.log.error(
                f"Error saving PDF files error={str(e)}, session={self.session_id}"
            )
            raise DocumentPortalException(f"Error saving files {str(e)}") from e

    def read_pdf(self, pdf_path: Path) -> str:
        """Read text from a PDF file.

        Args:
            pdf_path (Path): The path to the PDF file.

        Raises:
            ValueError: If the PDF is encrypted or cannot be read.
            DocumentPortalException: If an error occurs while reading the PDF.

        Returns:
            str: The extracted text from the PDF.
        """
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError(f"PDF is encrypted: {pdf_path.name}")
                parts = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text()  # type: ignore
                    if text.strip():
                        parts.append(f"\n --- Page {page_num + 1} --- \n{text}")
            self.log.info(f"PDF read successfully file={pdf_path}, pages={len(parts)}")
            return "\n".join(parts)
        except Exception as e:
            self.log.error(f"Error reading PDF file={pdf_path}, error={str(e)}")
            raise DocumentPortalException(f"Error reading PDF {str(e)}  ", e) from e

    def combine_documents(self) -> str:
        """Combine two PDF documents into a single document.

        Raises:
            DocumentPortalException: If an error occurs while reading or combining documents.

        Returns:
            str: The combined text of all documents.
        """
        try:
            doc_parts = []
            for file in sorted(self.session_path.iterdir()):
                if file.is_file() and file.suffix.lower() == ".pdf":
                    content = self.read_pdf(file)
                    doc_parts.append(f"Document: {file.name}\n{content}")
            combined_text = "\n\n".join(doc_parts)
            self.log.info(
                f"Documents combined count={len(doc_parts)}, session={self.session_id}"
            )
            return combined_text
        except Exception as e:
            self.log.error(
                f"Error combining documents error={str(e)}, session={self.session_id}"
            )
            raise DocumentPortalException(
                f"Error combining documents {str(e)}", e
            ) from e

    def clean_old_sessions(self, keep_latest: int = 3):
        try:
            sessions = sorted(
                [f for f in self.base_dir.iterdir() if f.is_dir()], reverse=True
            )
            for folder in sessions[keep_latest:]:
                shutil.rmtree(folder, ignore_errors=True)
                self.log.info(f"Old session folder deleted path={str(folder)}")
        except Exception as e:
            self.log.error(f"Error cleaning old sessions error={str(e)}")
            raise DocumentPortalException(
                f"Error cleaning old sessions {str(e)}", e
            ) from e


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
