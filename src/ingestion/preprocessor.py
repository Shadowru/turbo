from typing import Iterable
import re
import nltk
from nltk.tokenize import sent_tokenize

nltk.download("punkt", quiet=True)

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\u00a0", " ").strip()
    return text

def chunk_text(text: str, max_tokens: int = 400, overlap: int = 50) -> Iterable[str]:
    sentences = sent_tokenize(text, language="russian")
    chunks, current_chunk = [], []
    token_count = 0

    for sentence in sentences:
        sentence_tokens = len(sentence.split())
        if token_count + sentence_tokens > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = current_chunk[-overlap:] if overlap < len(current_chunk) else current_chunk
            token_count = sum(len(s.split()) for s in current_chunk)

        current_chunk.append(sentence)
        token_count += sentence_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks