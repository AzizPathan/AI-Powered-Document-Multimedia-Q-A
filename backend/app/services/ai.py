from collections.abc import AsyncGenerator

from openai import AsyncOpenAI, OpenAIError

from app.config import get_settings
from app.services.retrieval import RetrievedChunk
from app.services.text import summarize_text


def fallback_answer(question: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "I could not find relevant extracted content for that question."
    context = " ".join(chunk.text for chunk in chunks[:2])
    return f"Based on the uploaded content: {summarize_text(context, max_sentences=3)}"


async def answer_question(question: str, chunks: list[RetrievedChunk]) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        return fallback_answer(question, chunks)

    context = "\n\n".join(f"Source {index + 1}: {chunk.text}" for index, chunk in enumerate(chunks))
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Answer only from the supplied uploaded-file context. Mention when the context is insufficient.",
                },
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
            ],
            temperature=0.2,
        )
    except OpenAIError:
        return fallback_answer(question, chunks)

    return response.choices[0].message.content or fallback_answer(question, chunks)


async def stream_answer(question: str, chunks: list[RetrievedChunk]) -> AsyncGenerator[str, None]:
    answer = await answer_question(question, chunks)
    for word in answer.split():
        yield f"{word} "
