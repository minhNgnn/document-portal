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


class SingleDocIngestor:
    def __init__(
        self,
        data_dir: str = "data/single_document_chat",
        faiss_dir: str = "faiss_index",
    ):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)
            self.model_loader = ModelLoader()
            self.log.info(
                f"SingleDocIngestor initialized successfully with data directory: {self.data_dir} and FAISS directory: {self.faiss_dir}"
            )
        except Exception as e:
            self.log.error(f"Error initializing SingleDocIngestor: {e}")
            raise DocumentPortalException(
                f"Failed to initialize SingleDocIngestor: {sys.exc_info()}"
            ) from e

    def ingest_files(self, uploaded_files):
        try:
            documents = []
            for uploaded_file in uploaded_files:
                unique_filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.pdf"
                temp_path = self.data_dir / unique_filename

                with open(temp_path, "wb") as f_out:
                    f_out.write(uploaded_file.read())
                self.log.info(f"File saved to {temp_path}")
                loader = PyPDFLoader(str(temp_path))
                docs = loader.load()
                documents.extend(docs)
            self.log.info(f"Successfully ingested {len(documents)} documents.")
            return self._create_retriever(documents)
        except Exception as e:
            self.log.error(f"Error during file ingestion: {e}")
            raise DocumentPortalException(
                f"Failed to ingest files: {sys.exc_info()}"
            ) from e

    def _create_retriever(self, documents):
        """Create a retriever with chunking from the ingested documents.

        Raises:
            DocumentPortalException: If retriever creation fails.
        """
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=300
            )
            chunks = splitter.split_documents(documents)
            self.log.info(f"Successfully created retriever with {len(chunks)} chunks.")

            embeddings = self.model_loader.load_embeddings()
            vector_store = FAISS.from_documents(documents=chunks, embedding=embeddings)
            self.log.info(
                f"Successfully created FAISS vector store with {len(chunks)} chunks."
            )

            # Save the vector store to disk
            vector_store.save_local(str(self.faiss_dir))
            self.log.info(f"FAISS vector store saved to {self.faiss_dir}")

            retriever = vector_store.as_retriever(
                search_type="similarity", search_kwargs={"k": 5}
            )
            self.log.info("Retriever created successfully")
            return retriever
        except Exception as e:
            self.log.error(f"Error creating retriever: {e}")
            raise DocumentPortalException(
                f"Failed to create retriever: {sys.exc_info()}"
            ) from e
