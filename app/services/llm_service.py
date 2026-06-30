from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings
from app.core.prompts import (
    ASK_SYSTEM_PROMPT,
    COMPARE_SYSTEM_PROMPT,
    build_ask_user_prompt,
    build_compare_user_prompt,
)

MISSING_INFORMATION_MESSAGE = (
    "I could not find this information in the uploaded documents."
)


class LLMService:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
        )

    def _invoke(self, system_prompt: str, user_prompt: str) -> str:
        response = self.llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
        return response.content

    def generate_answer(
        self,
        question: str,
        context: str,
    ) -> str:
        if not context.strip():
            return MISSING_INFORMATION_MESSAGE

        return self._invoke(
            ASK_SYSTEM_PROMPT,
            build_ask_user_prompt(question, context),
        )

    def generate_comparison(
        self,
        question: str,
        document_sections: list[str],
    ) -> str:
        if not document_sections:
            return "Not enough documents found for comparison."

        return self._invoke(
            COMPARE_SYSTEM_PROMPT,
            build_compare_user_prompt(question, document_sections),
        )

    def generate_text(
        self,
        prompt: str,
    ) -> str:
        return self._invoke(ASK_SYSTEM_PROMPT, prompt)
