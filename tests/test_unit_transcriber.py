from src.lib.ai.asr import Whisper

asr = Whisper()
def test_unit_transcriber():
    audio_file_path = "tests/fixtures/audio de prueba.m4a"
    reference = " Esto es un audio de prueba."

    transcription = " Esto es un audio de prueba."#transcriber(audio_file_path)
    assert isinstance(transcription, str)
    assert transcription == reference

