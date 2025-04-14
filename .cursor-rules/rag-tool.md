## Put all your methodology materials in:
src/hypnobot/docs/
├── intro_to_your_method.md
├── faq.md
├── client_prep_guide.txt
├── advanced_techniques.pdf


## methodology rag tool

from crewai_tools import tool
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.llms import OpenAI

@tool("HypnotherapyMethodologyTool")
def hypnotherapy_methodology_tool(query: str) -> str:
    """Answers questions using your own hypnotherapy methodology docs."""
    loader = DirectoryLoader('src/hypnobot/docs', glob='**/*.md', show_progress=True)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever()

    relevant_docs = retriever.get_relevant_documents(query)
    llm = OpenAI(temperature=0)
    chain = load_qa_with_sources_chain(llm, chain_type="stuff")

    result = chain.run(input_documents=relevant_docs, question=query)
    return result

## Add the Tool to the Agent
In your crew.py or agents.yaml:

from src.hypnobot.tools.methodology_rag_tool import hypnotherapy_methodology_tool

support_assistant = Agent(
  role='Friendly Hypnotherapy Assistant',
  goal='Answer client questions using practice-specific methodology',
  backstory='...',
  tools=[hypnotherapy_methodology_tool]
)

## How to Do It
We’ll use a CrewAI-compatible RAG tool — likely one of:
- crew.ai_tools.RagTool if you want quick setup with text/markdown