import sys
import os
from langchain_core.runnables.history import RunnableWithMessageHistory
from exception.custom_exception import DocumentPortalException
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from logger.custom_logger import CustomLogger
from model.models import PromptType
from prompts.prompt_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader
from langchain.vectorstores import FAISS


class ConversationRAG:
    def __init__(self, session_id: str, retriever):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.retriever = retriever
            self.llm = self._load_llm()
            self.contextualize_prompt = PROMPT_REGISTRY[
                PromptType.CONTEXTUALIZE_QUESTION
            ]
            self.qa_prompt = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]

            self.history_aware_retriever = create_history_aware_retriever(
                self.llm, self.retriever, self.contextualize_prompt
            )
            self.log.info(
                f"History-aware retriever created successfully with {session_id}"
            )

            self.qa_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)
            self.rag_chain = create_retrieval_chain(
                self.history_aware_retriever, self.qa_chain
            )
            self.log.info(f"ConversationRAG initialized successfully with {session_id}")

            self.chain = RunnableWithMessageHistory(
                self.rag_chain,
                self._get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer",
            )
            self.log.info(
                f"RunnableWithMessageHistory created successfully with {session_id}"
            )

        except Exception as e:
            CustomLogger().get_logger(__name__).error(
                f"Error initializing ConversationRAG: {e}"
            )
            raise DocumentPortalException(
                f"Failed to initialize ConversationRAG: {sys.exc_info()}"
            ) from e

    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            self.log.info(f"LLM loaded successfully: {llm}")
            return llm
        except Exception as e:
            self.log.error(f"Error loading LLM: {e}")
            raise DocumentPortalException(
                f"Failed to load LLM: {sys.exc_info()}"
            ) from e

    def _get_session_history(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error getting session history: {e}")
            raise DocumentPortalException(
                f"Failed to get session history: {sys.exc_info()}"
            ) from e

    def load_retriever_from_faiss(self, index_path: str):
        try:
            embedding_model = ModelLoader().load_embedding_model()
            if not os.path.isdir(index_path):
                self.log.error(f"FAISS index path does not exist: {index_path}")
                raise FileExistsError(f"FAISS index path does not exist: {index_path}")
            vector_store = FAISS.load_local(index_path, embedding_model)
            self.log.info(f"FAISS vector store loaded successfully from: {index_path}")
            return vector_store.as_retriever(
                search_type="similarity", search_kwargs={"k": 5}
            )

        except Exception as e:
            self.log.error(f"Error loading retriever from FAISS: {e}")
            raise DocumentPortalException(
                f"Failed to load retriever from FAISS: {sys.exc_info()}"
            ) from e

    def invoke(self, user_input: str):
        try:
            response = self.chain.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": self.session_id}},
            )
            answer = response.get("answer", "No answer.")
            if not answer:
                self.log.warning(f"No answer found for user input: {self.session_id}")

            self.log.info(
                f"Conversation RAG invoked successfully for session: {self.session_id}"
            )
            return answer
        except Exception as e:
            self.log.error(f"Error invoking conversation RAG: {e}")
            raise DocumentPortalException(
                f"Failed to invoke conversation RAG: {sys.exc_info()}"
            ) from e
