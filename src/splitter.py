from langchain.text_splitter import RecursiveCharacterTextSplitter


def splitter(transcription):
    text_splitter = RecursiveCharacterTextSplitter(separators=[" "], chunk_size=50, chunk_overlap=10)

    docs = text_splitter.split_text(transcription)

    return docs


