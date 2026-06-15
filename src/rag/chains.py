from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


SUMMARY_TEMPLATE = PromptTemplate(
    input_variables=["transcript"],
    template="""You are an expert AI assistant that creates concise, insightful summaries of YouTube videos.

[Instructions]
1. Read the transcript below and extract the core message, key points, and valuable insights.
2. Write a single, well-structured paragraph that captures the essence of the video.
3. Ignore timestamps and focus solely on the spoken content.
4. Be informative but engaging — make the reader understand why this video matters.
5. If the video covers multiple topics, mention the most important ones in order of significance.

[Transcript]
{transcript}

[Summary]""",
)


QA_TEMPLATE = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are an expert answering questions about a YouTube video based on its transcript.

[Instructions]
1. Answer the question using ONLY the context provided below.
2. If the context doesn't contain enough information to answer fully, say so honestly.
3. Be precise, concise, and avoid speculation.
4. Structure your answer clearly with supporting details from the transcript.
5. Do NOT include timestamps in your answer.

[Context from Transcript]
{context}

[Question]
{question}

[Answer]""",
)


def create_summary_chain(llm):
    return LLMChain(llm=llm, prompt=SUMMARY_TEMPLATE, verbose=False)


def create_qa_chain(llm):
    return LLMChain(llm=llm, prompt=QA_TEMPLATE, verbose=False)


def summarize(chain: LLMChain, transcript: str) -> str:
    return chain.run({"transcript": transcript})


def answer_question(chain: LLMChain, context: str, question: str) -> str:
    return chain.run({"context": context, "question": question})
