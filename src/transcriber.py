import whisper
model = whisper.load_model('large-v3-turbo')

def transcriber(audio):
    result = model.transcribe(audio)
    return result['text']
