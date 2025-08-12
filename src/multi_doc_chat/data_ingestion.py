from pathlib import Path
from exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger
from utils.model_loader import ModelLoader
from datetime import datetime
import uuid
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_community.document_loaders.markdown import (
    UnstructuredMarkdownLoader as MarkdownLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


class DocumentIngestor:
    SUPPORTED_FILE_TYPES = ["pdf", "docx", "txt", "md"]

    def __init__(
        self,
        temp_dir: str = "data/multi_doc_chat",
        faiss_dir: str = "faiss_index",
        session_id: str | None = None,
    ):
        try:
            self.log = CustomLogger().get_logger(__name__)

            # Base dirs
            self.temp_dir = Path(temp_dir)
            self.faiss_dir = Path(faiss_dir)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)

            # Sessionized paths
            self.session_id = (
                session_id
                or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            )
            self.session_temp_dir = self.temp_dir / self.session_id
            self.session_faiss_dir = self.faiss_dir / self.session_id
            self.session_temp_dir.mkdir(parents=True, exist_ok=True)
            self.session_faiss_dir.mkdir(parents=True, exist_ok=True)

            self.model_loader = ModelLoader()
            self.log.info(
                f"Initialized DocumentIngestor with session ID: {self.session_id}"
            )
        except Exception as e:
            self.log.error(f"Error initializing DocumentIngestor: {e}")
            raise DocumentPortalException("Failed to initialize DocumentIngestor")

    def ingest_files(self, uploaded_files):
        try:
            self.log.info("Ingesting files...")
            documents = []

            for uploaded_file in uploaded_files:
                ext = Path(uploaded_file.name).suffix.lower()
                if ext not in self.SUPPORTED_FILE_TYPES:
                    self.log.warning(f"Unsupported file type: {ext}")
                    continue
                unique_filename = f"{uuid.uuid4().hex[:8]}{ext}"
                temp_path = self.session_temp_dir / unique_filename

                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
                self.log.info(
                    f"Saved uploaded file to: {temp_path} in {self.session_id}"
                )

                if ext == ".pdf":
                    self.log.info(f"Processing PDF file: {temp_path}")
                    loader = PyPDFLoader(str(temp_path))
                elif ext == ".docx":
                    self.log.info(f"Processing DOCX file: {temp_path}")
                    loader = Docx2txtLoader(str(temp_path))
                elif ext == ".txt":
                    self.log.info(f"Processing TXT file: {temp_path}")
                    loader = TextLoader(str(temp_path))
                elif ext == ".md":
                    self.log.info(f"Processing MD file: {temp_path}")
                    loader = MarkdownLoader(str(temp_path))
                else:
                    self.log.warning(f"Unsupported file type: {ext}")
                    continue

                docs = loader.load()
                documents.extend(docs)

                if not documents:
                    self.log.error(f"No documents found for file: {temp_path}")
                    raise DocumentPortalException("No documents found")

            self.log.info(f" All documents ingestion completed in {self.session_id}.")
            return self._create_retriever(documents)

        except Exception as e:
            self.log.error(f"Error ingesting files: {e}")
            raise DocumentPortalException("Failed to ingest files")

    def _create_retriever(self, documents):
        try:
            self.log.info("Creating retriever...")
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=300
            )
            chunks = splitter.split_documents(documents)
            self.log.info(f"Created {len(chunks)} chunks in {self.session_id}.")

            embeddings = self.model_loader.load_embeddings()
            vectorstore = FAISS.from_documents(chunks, embeddings)
            vectorstore.save_local(str(self.session_faiss_dir))
            self.log.info(
                f"Created FAISS vector store at {self.session_faiss_dir} in {self.session_id}."
            )

            retriever = vectorstore.as_retriever(
                search_type="similarity", search_kwargs={"k": 5}
            )
            self.log.info(f"Created retriever in {self.session_id}.")
            return retriever
        except Exception as e:
            self.log.error(f"Error creating retriever: {e}")
            raise DocumentPortalException("Failed to create retriever")
