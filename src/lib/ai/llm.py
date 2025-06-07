import logging
from typing import Type

import vllm
from openai import OpenAI
from pydantic import BaseModel
from vllm.sampling_params import GuidedDecodingParams

from settings import settings

log = logging.getLogger("app")

generation_params = {
    "max_tokens": 8096,
    "temperature": 0,
    "top_p": 0.95,
    "frequency_penalty": 0.5,
    "presence_penalty": 1.2,
}


class OpenAIClient:
    def __init__(self) -> None:
        self.model = OpenAI(
            api_key="API",
            base_url=settings.CLIENT_URL,
        )

    def generate(
        self,
        prompt: str,
        schema: Type[BaseModel],
    ) -> str:
        response = self.model.chat.completions.create(
            messages=[{"role": "assistant", "content": prompt}],
            model=settings.LLM_MODEL,
            extra_body={"guided_json": schema.model_json_schema()},
            **generation_params,
        )
        return response.choices[0].message.content or ""


class vLLMClient:
    def __init__(self) -> None:
        log.info("Initializing vLLM")
        self.model = vllm.LLM(
            model=settings.LLM_MODEL,
            dtype=settings.DTYPE,
            task="generate",
            max_model_len=settings.CTX_WINDOW,
            max_num_seqs=2,
            enable_chunked_prefill=True,
            gpu_memory_utilization=0.5,
            reasoning_parser="deepseek_r1",
            guided_decoding_backend="xgrammar",
        )

    def generate(
        self,
        prompt: str,
        schema: Type[BaseModel],
    ) -> str:
        response = self.model.generate(
            prompt,
            sampling_params=vllm.SamplingParams(
                **generation_params,
                guided_decoding=GuidedDecodingParams(json=schema.model_json_schema()),
            ),
        )
        return response[0].outputs[0].text
