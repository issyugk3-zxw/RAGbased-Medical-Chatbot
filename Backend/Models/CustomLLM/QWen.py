
import os
from typing import Any, List, Optional, Sequence

from llama_index.core.base.llms.types import (
    ChatMessage,
    ChatResponse,
    ChatResponseAsyncGen,
    ChatResponseGen,
    CompletionResponse,
    CompletionResponseAsyncGen,
    CompletionResponseGen,
    LLMMetadata,
    MessageRole,
)
from llama_index.core.bridge.pydantic import Field, PrivateAttr
from llama_index.core.callbacks import CallbackManager
from llama_index.core.llms.callbacks import llm_chat_callback, llm_completion_callback
from llama_index.core.llms.custom import CustomLLM

import dashscope
from dashscope.api_entities.dashscope_response import GenerationResponse




class QWen(CustomLLM):
    model: str = Field(
        default="qwen-turbo", description="The QWen model to use."
    )
    api_key: str = Field(default=None, description="The DashScope API key.")
    temperature: float = Field(
        default=0.7, description="The temperature to use for sampling.", gt=0.0, le=1.0
    )

    _client: Any = PrivateAttr()

    def __init__(
        self,
        model: str = "qwen-turbo",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        callback_manager: Optional[CallbackManager] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(callback_manager=callback_manager, **kwargs)

        self.api_key = "put your api key here"
        dashscope.api_key = self.api_key
        self.model = model
        self.temperature = temperature

    @classmethod
    def class_name(cls) -> str:
        return "QWen_llm"

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=6000,
            num_output=2048,
            is_chat_model=True,
            model_name=self.model,
        )

    @llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        dashscope_messages = []
        for msg in messages:
            dashscope_messages.append({"role": msg.role.value, "content": msg.content})

        response = dashscope.Generation.call(
            model=self.model,
            messages=dashscope_messages,
            temperature=self.temperature,
            result_format="message",  
            **kwargs,
        )

        if response.status_code == 200 and response.output and response.output.choices:
            ai_message = response.output.choices[0].message
            return ChatResponse(
                message=ChatMessage(
                    role=MessageRole(ai_message.role),
                    content=ai_message.content,
                ),
                raw=response,
            )
        else:
            raise RuntimeError(
                f"DashScope API call failed with status: {response.status_code}, message: {response.message}"
            )

    @llm_completion_callback()
    def complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:

        messages = [{"role": MessageRole.USER.value, "content": prompt}]

        response = dashscope.Generation.call(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            result_format="message",
            **kwargs,
        )

        if response.status_code == 200 and response.output and response.output.choices:
            completion_text = response.output.choices[0].message.content
            return CompletionResponse(text=completion_text, raw=response)
        else:
            raise RuntimeError(
                f"DashScope API call failed with status: {response.status_code}, message: {response.message}"
            )

    async def achat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponse:
        return self.chat(messages, **kwargs)

    async def acomplete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        return self.complete(prompt, formatted, **kwargs)
    def stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseGen:
        raise NotImplementedError("stream_chat is not implemented ")

    def stream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseGen:
        raise NotImplementedError("stream_complete is not implemented")


if __name__ == "__main__":

    llm = QWen(model="qwen-turbo")
    completion_response = llm.complete("杭州有什么好玩的？")
    print(f"Completion response: {completion_response.text}")

