from langchain.text_splitter import RecursiveCharacterTextSplitter


def split(transcription: str) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, chunk_overlap=20
    )

    docs = text_splitter.split_text(transcription)

    return docs
