import sys
import os
from langchain_core.runnables.history import RunnableWithMessageHistory
from exception.custom_exception import DocumentPortalException
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from logger.custom_logger import CustomLogger
from model.models import PromptType, Chat
from prompts.prompt_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader
from langchain_community.vectorstores import FAISS
from langchain_community.chat_message_histories import ChatMessageHistory

class ConversationalRAG:
    def __init__(self, session_id: str, retriever = None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.llm = self._load_llm()
            self.contextualize_prompt = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]

            if retriever is None:
                raise ValueError("Retriever is required")
            self.retriever = retriever
            self._build_lcel_chain()
            self.log.info(f"ConversationalRAG initialized successfully with session_id={session_id}")
            
        except Exception as e:
            self.log.error(f"Error initializing ConversationalRAG: {e}")
            raise DocumentPortalException("Failed to initialize ConversationalRAG")

    def load_retriever_from_faiss(self):
        pass

    def invoke(self):
        pass

    def _load_llm(self):
        pass

    @staticmethod
    def _format_docs(docs):
        pass

    def _build_lcel_chain(self):
        pass
