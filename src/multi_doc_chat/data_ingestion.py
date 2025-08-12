from pathlib import Path
import sys
from exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger
from utils.model_loader import ModelLoader
from datetime import datetime
import uuid
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

class DocumentIngestor:
    SUPPORTED_FILE_TYPES = ['pdf', 'docx', 'txt', 'md']
    def __init__(self, temp_dir: str = "data/multi_doc_chat", faiss_dir:str = "faiss_index", session_id:str|None = None):
        try:
            self.log = CustomLogger().get_logger(__name__)

            # Base dirs
            self.temp_dir = Path(temp_dir)
            self.faiss_dir = Path(faiss_dir)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)

            # Sessionized paths
            self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            self.session_temp_dir = self.temp_dir / self.session_id
            self.session_faiss_dir = self.faiss_dir / self.session_id
            self.session_temp_dir.mkdir(parents=True, exist_ok=True)
            self.session_faiss_dir.mkdir(parents=True, exist_ok=True)

            self.model_loader = ModelLoader()
            self.log.info(f"Initialized DocumentIngestor with session ID: {self.session_id}")
        except Exception as e:
            self.log.error(f"Error initializing DocumentIngestor: {e}")
            raise DocumentPortalException("Failed to initialize DocumentIngestor")

    def ingest_files(self):
        try:
            self.log.info("Ingesting files...")
            # Implement file ingestion logic here
        except Exception as e:
            self.log.error(f"Error ingesting files: {e}")
            raise DocumentPortalException("Failed to ingest files")

    def _create_retriever(self):
        try:
            self.log.info("Creating retriever...")
            # Implement retriever creation logic here
        except Exception as e:
            self.log.error(f"Error creating retriever: {e}")
            raise DocumentPortalException("Failed to create retriever")
