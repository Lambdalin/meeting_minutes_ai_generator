import os
from typing import Literal

import torch
from dotenv import load_dotenv
from pydantic import BaseModel, computed_field

load_dotenv()


class Settings(BaseModel):
    LLM_MODEL: str = os.getenv("LLM_MODEL", "Qwen/Qwen3-4B-FP8")
    ASR_MODEL: str = os.getenv("ASR_MODEL", "large-v3")
    DTYPE: str = os.getenv("DTYPE", "float16")
    CTX_WINDOW: int = int(os.getenv("CTX_WINDOW", "8096"))
    TORCH_DEVICE: Literal["cuda", "cpu"] | None = None
    ENVIRONMENT: Literal["dev", "prod"] = os.getenv("ENVIRONMENT", "prod")
    CLIENT_URL: str = os.getenv("CLIENT_URL", "http://localhost:8000/v1")

    @computed_field
    @property
    def DEVICE(self) -> Literal["cuda", "cpu"]:
        if self.TORCH_DEVICE:
            return self.TORCH_DEVICE
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"


settings = Settings()
