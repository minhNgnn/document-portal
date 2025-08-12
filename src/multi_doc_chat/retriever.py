import sys
import os
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger
from model.models import PromptType
from prompts.prompt_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader
from langchain_community.vectorstores import FAISS


class ConversationalRAG:
    def __init__(self, session_id: str, retriever=None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.llm = self._load_llm()
            self.contextualize_prompt = PROMPT_REGISTRY[
                PromptType.CONTEXTUALIZE_QUESTION.value
            ]
            self.qa_prompt = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]

            if retriever is None:
                raise ValueError("Retriever is required")
            self.retriever = retriever
            self._build_lcel_chain()
            self.log.info(
                f"ConversationalRAG initialized successfully with session_id={session_id}"
            )

        except Exception as e:
            self.log.error(f"Error initializing ConversationalRAG: {e}")
            raise DocumentPortalException("Failed to initialize ConversationalRAG")

    def load_retriever_from_faiss(self, index_path: str):
        """
        Load a FAISS vectorstore from disk and convert to retriever.
        """
        try:
            embeddings = ModelLoader().load_embeddings()
            if not os.path.exists(index_path):
                raise FileNotFoundError(f"FAISS index not found at {index_path}")

            vectorstore = FAISS.load_local(
                index_path, embeddings, allow_dangerous_deserialization=True
            )
            self.retriever = vectorstore.as_retriever(
                search_type="similarity", search_kwargs={"k": 5}
            )
            self.log.info(f"FAISS retriever loaded successfully in {self.session_id}")
            self._build_lcel_chain()
            return self.retriever
        except Exception as e:
            self.log.error(f"Error loading FAISS retriever: {e}")
            raise DocumentPortalException("Failed to load FAISS retriever", sys) from e

    def invoke(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error invoking ConversationalRAG: {e}")
            raise DocumentPortalException(
                "Failed to invoke ConversationalRAG", sys
            ) from e

    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            if not llm:
                self.log.error("LLM not loaded")
                raise ValueError("LLM not loaded")
            self.log.info(f"LLM loaded successfully: {llm} in {self.session_id}")
            return llm
        except Exception as e:
            self.log.error(f"Error loading LLM: {e}")
            raise DocumentPortalException("Failed to load LLM", sys) from e

    @staticmethod
    def _format_docs(docs):
        return "\n\n".join(d.page_content for d in docs)

    def _build_lcel_chain(self):
        try:
            question_rewriter = (
                {
                    "input": itemgetter("input"),
                    "chat_history": itemgetter("chat_history"),
                }
                | self.contextualize_prompt
                | self.llm
                | StrOutputParser()
            )
            retrieve_docs = question_rewriter | self.retriever | self._format_docs
            self.lcel_chain = (
                {
                    "context": retrieve_docs,
                    "input": itemgetter("input"),
                    "chat_history": itemgetter("chat_history"),
                }
                | self.qa_prompt
                | self.llm
                | StrOutputParser()
            )
            self.log.info(f"LCEL chain built successfully in {self.session_id}")
        except Exception as e:
            self.log.error(f"Error building LCEL chain: {e}")
            raise DocumentPortalException("Failed to build LCEL chain", sys) from e
