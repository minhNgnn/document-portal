from pathlib import Path
import sys
from exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger


class SingleDocIngestor:
    def __init__(self, pdf_path: Path):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.pdf_path = pdf_path
        except Exception as e:
            self.log.error(f"Error initializing SingleDocIngestor: {e}")
            raise DocumentPortalException(
                f"Failed to initialize SingleDocIngestor: {sys.exc_info()}"
            ) from e

    def ingest_files(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error during file ingestion: {e}")
            raise DocumentPortalException(
                f"Failed to ingest files: {sys.exc_info()}"
            ) from e

    def _create_retriever(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error creating retriever: {e}")
            raise DocumentPortalException(
                f"Failed to create retriever: {sys.exc_info()}"
            ) from e
