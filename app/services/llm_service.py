# models/llm_service.py

from langchain_openai import ChatOpenAI
from langchain_classic.prompts import ChatPromptTemplate
from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from config import Config


class LLMService:
    def __init__(self, vector_store):
        # 1) LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",         # use any valid model you have access to
            temperature=0.7,
            api_key=Config.OPENAI_API_KEY
        )

        # 2) Per-session chat histories (RunnableWithMessageHistory expects a ChatMessageHistory, not ConversationBufferMemory)
        self._histories = {}  # session_id -> ChatMessageHistory

        # 3) Retriever from your Chroma store
        retriever = vector_store.vector_store.as_retriever(search_kwargs={"k": 4})

        # 4) Prompt to rewrite the user question using history
        contextualize_q_prompt = ChatPromptTemplate.from_template(
            """Rewrite the user's latest question to be self-contained, using the chat history if needed.
If rewriting isn't necessary, return the original question.

Chat history:
{chat_history}

Latest user question:
{input}"""
        )
        history_aware = create_history_aware_retriever(
            llm=self.llm,
            retriever=retriever,
            prompt=contextualize_q_prompt
        )

        # 5) QA prompt that uses retrieved context
        qa_prompt = ChatPromptTemplate.from_template(
            """Use the following context to answer the question. If you don't know, say you don't know.

Context:
{context}

Question:
{input}"""
        )

        # 6) Build chains: doc combiner + retrieval chain
        qa_chain = create_stuff_documents_chain(llm=self.llm, prompt=qa_prompt)
        rag_chain = create_retrieval_chain(history_aware, qa_chain)

        # 7) Wrap with message history so chat turns are remembered
        def _get_session_history(session_id: str):
            if session_id not in self._histories:
                self._histories[session_id] = ChatMessageHistory()
            return self._histories[session_id]

        self.chain = RunnableWithMessageHistory(
            rag_chain,
            _get_session_history,
            input_messages_key="input",       # matches prompts' {input}
            history_messages_key="chat_history",
            output_messages_key="answer"
        )

    def get_response(self, query: str, session_id: str = "default") -> str:
        try:
            result = self.chain.invoke(
                {"input": query},
                config={"configurable": {"session_id": session_id}}
            )
            # result includes: 'answer' and 'context' (retrieved docs)
            return result.get("answer", "")
        except Exception as e:
            print(f"Error getting LLM response: {e}")
            return "I encountered an error processing your request."