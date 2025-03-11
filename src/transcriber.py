
# from langchain.text_splitter import RecursiveCharacterTextSplitter

# text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=1000, chunk_overlap=100)
# docs = text_splitter.splitt_text()
import whisper
model = whisper.load_model('large-v3-turbo')

def transcriber(audio):
    result = model.transcribe(audio)
    return result['text']
