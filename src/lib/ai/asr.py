import time
from pathlib import Path

import numpy as np
import vllm
import whisper
from librosa import load, resample
from transformers import WhisperTokenizerFast

from settings import settings

params = {
    "temperature": 0,
    "top_p": 1.0,
    "max_tokens": 2048,
}


class Whisper:
    def __init__(self) -> None:
        self.model = whisper.load_model(
            name=settings.ASR_MODEL,
            device=settings.DEVICE,
        )

    def transcribe(self, audio_path: str) -> str:
        result = self.model.transcribe(audio_path)
        return result["text"]


class vLLMWhisper:
    def __init__(self) -> None:
        self.model = vllm.LLM(
            model=settings.ASR_MODEL,
            limit_mm_per_prompt={"audio": 1},
            gpu_memory_utilization=0.8,
            dtype="float16",
            max_num_seqs=400,
            max_num_batched_tokens=2048,
            task="transcription",
        )
        self.tokenizer = WhisperTokenizerFast.from_pretrained(
            settings.ASR_MODEL, language="es"
        )

    def transcribe(
        self, audio_path: Path, language: str = "es", debug: bool = False
    ) -> str:
        # Figure out Language Code
        lang_code = self.tokenizer.convert_tokens_to_ids(f"<|{language}|>")
        if lang_code == 50257:
            raise ValueError(f"Language code for {language} not found")

        samples = {}
        # Load the audio file
        audio, sample_rate = load(audio_path, sr=16000)
        if sample_rate != 16000:
            # Use librosa to resample the audio
            audio = resample(
                audio.numpy().astype(np.float32),
                orig_sr=sample_rate,
                target_sr=16000,
            )
        print(
            f"File: {audio_path}, Sample rate: {sample_rate}, Audio shape: {audio.shape}, Duration: {audio.shape[0] / sample_rate:.2f} seconds"
        )
        chunks = self._chunk(audio, 16000)
        samples[audio_path.stem] = [(chunk, 16000) for chunk in chunks]

        # Inference Loop
        outputs = []
        for file, chunks in samples.items():
            prompts = [
                {
                    "encoder_prompt": {
                        "prompt": "",
                        "multi_modal_data": {
                            "audio": chunk,
                        },
                    },
                    "decoder_prompt": f"<|startoftranscript|><|{lang_code}|><|transcribe|><|notimestamps|>",
                }
                for chunk in chunks
            ]
            print(f"File: {file}, Chunks: {len(chunks)}")

            start = time.time()

            # Inferense based on max_num_seqs
            for i in range(len(prompts)):
                output = self.model.generate(
                    prompts[i],
                    sampling_params=vllm.SamplingParams(
                        temperature=0,
                        top_p=1.0,
                        max_tokens=8192,
                    ),
                )
                outputs.extend(output)

            if debug:
                # Print the outputs.
                generated = ""
                for output in outputs:
                    prompt = output.prompt
                    encoder_prompt = output.encoder_prompt
                    generated_text = output.outputs[0].text
                    generated += generated_text
                    print(
                        f"Encoder prompt: {encoder_prompt!r}, "
                        f"Decoder prompt: {prompt!r}, "
                        f"Generated text: {generated_text!r}"
                    )

                duration = time.time() - start

                print("Duration:", duration)
                print("RPS:", len(prompt) / duration)
                print("Generated text:", generated)

    def _chunk(self, audio: np.ndarray, sample_rate: int) -> list[np.ndarray]:
        """Split audio to 30 seconds duration chunks"""
        max_duration_samples = sample_rate * 30.0
        padding = max_duration_samples - np.remainder(
            len(audio), max_duration_samples
        )
        audio = np.pad(
            audio, (0, padding.astype(int)), "constant", constant_values=0.0
        )
        return np.split(audio, len(audio) // max_duration_samples)
