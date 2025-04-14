import os
import glob
from typing import List, Optional

from crewai.tools import BaseTool
from langchain.text_splitter import MarkdownTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document

from hypnobot.utils.logging import get_logger

logger = get_logger(__name__)

class HypnotherapyKnowledgeTool(BaseTool):
    """Tool for retrieving information about hypnotherapy from the knowledge base."""
    
    name: str = "HypnotherapyKnowledgeTool"
    description: str = """
    Retrieves information about hypnotherapy methods, techniques, and practices.
    Use this tool to find accurate information about hypnotherapy to answer user questions.
    Input should be a specific query about hypnotherapy.
    Output will be relevant information from the knowledge base.
    """
    
    def __init__(self):
        """Initialize the knowledge tool."""
        super().__init__()
        self.knowledge_dir = os.path.join(
            os.path.dirname(__file__), "..", "knowledge", "content"
        )
        self.vector_store = None
    
    def _initialize_vector_store(self) -> None:
        """Initialize the vector store with content from the knowledge directory."""
        try:
            # Check if OpenAI API key is set
            if not os.environ.get("OPENAI_API_KEY"):
                logger.warning("OPENAI_API_KEY not found in environment variables")
                return
            
            # Load documents
            documents = self._load_documents()
            if not documents:
                logger.warning("No documents found in knowledge directory")
                return
            
            # Split documents into chunks
            text_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200)
            doc_chunks = text_splitter.split_documents(documents)
            
            # Create vector store
            self.vector_store = FAISS.from_documents(
                doc_chunks, OpenAIEmbeddings()
            )
            
            logger.info(f"Vector store initialized with {len(doc_chunks)} chunks")
        
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            self.vector_store = None
    
    def _load_documents(self) -> List[Document]:
        """Load documents from the knowledge directory."""
        documents = []
        
        # Find all markdown files in the knowledge directory
        md_files = glob.glob(os.path.join(self.knowledge_dir, "**/*.md"), recursive=True)
        
        for file_path in md_files:
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                
                # Get relative path for metadata
                rel_path = os.path.relpath(file_path, self.knowledge_dir)
                
                # Create document
                documents.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": rel_path,
                            "title": os.path.basename(file_path).replace(".md", ""),
                            "category": os.path.dirname(rel_path),
                        }
                    )
                )
            
            except Exception as e:
                logger.error(f"Error loading document {file_path}: {e}")
        
        return documents
    
    def _run(self, query: str) -> str:
        """Run the tool on the given input.
        
        Args:
            query: The user's query about hypnotherapy.
            
        Returns:
            Relevant information from the knowledge base.
        """
        try:
            # Initialize vector store if not already initialized
            if self.vector_store is None:
                self._initialize_vector_store()
            
            # If still None, fall back to basic information
            if self.vector_store is None:
                return self._fallback_response(query)
            
            # Search for relevant documents
            docs = self.vector_store.similarity_search(query, k=3)
            
            # Format the results
            result = "Here's information about hypnotherapy:\n\n"
            
            for i, doc in enumerate(docs):
                source = doc.metadata.get("source", "Unknown")
                title = doc.metadata.get("title", "Untitled").replace("_", " ").title()
                
                result += f"--- {title} ---\n\n"
                result += doc.page_content + "\n\n"
            
            return result
        
        except Exception as e:
            logger.error(f"Error retrieving knowledge: {e}")
            return self._fallback_response(query)
    
    def _fallback_response(self, query: str) -> str:
        """Provide a fallback response when vector store is unavailable.
        
        Args:
            query: The user's query.
            
        Returns:
            A basic response about hypnotherapy.
        """
        return """
        Hypnotherapy is a form of complementary therapy that uses hypnosis, an enhanced state 
        of awareness and focused attention, to help create positive changes in thoughts, 
        feelings, and behaviors.
        
        During hypnotherapy, you remain in control and aware throughout the process. It's 
        typically used for issues like anxiety, stress management, habit change, and various 
        psychological and behavioral concerns.
        
        For more specific information, please ask a qualified hypnotherapist.
        """ 