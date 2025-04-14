# Knowledge Tool Implementation Example

This document provides a sample implementation of the hypnotherapy knowledge retrieval tool using CrewAI's tool framework.

## Knowledge Tool Implementation (tools/knowledge_tool.py)

```python
"""
Knowledge retrieval tool for the hypnotherapy chatbot.
"""
from typing import Dict, Any, List, Optional
import os
import json
from pathlib import Path
from crewai.tools import BaseTool
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.schema import BaseRetriever

class HypnotherapyKnowledgeTool(BaseTool):
    """
    Tool for retrieving information from the hypnotherapy knowledge base.
    """
    
    name: str = "HypnotherapyKnowledgeTool"
    description: str = """
    Retrieves relevant information about hypnotherapy methods, techniques, and best practices.
    Use this tool to find specific information about hypnotherapy to answer user questions accurately.
    
    Input should be a specific question or topic related to hypnotherapy.
    Output will be relevant information from the knowledge base with citations.
    
    Example input: "What is progressive relaxation in hypnotherapy?"
    """
    
    def __init__(
        self,
        knowledge_dir: str = "src/hypnobot/knowledge/content",
        embeddings_model: Optional[Any] = None,
        vector_store_path: str = "data/vector_store",
        top_k: int = 5
    ):
        """
        Initialize the knowledge tool.
        
        Args:
            knowledge_dir: Directory containing knowledge base files
            embeddings_model: Model to use for embeddings (defaults to OpenAI)
            vector_store_path: Path to store/load the vector store
            top_k: Number of top results to return
        """
        super().__init__()
        self.knowledge_dir = knowledge_dir
        self.embeddings_model = embeddings_model or OpenAIEmbeddings()
        self.vector_store_path = vector_store_path
        self.top_k = top_k
        
        # Initialize vector store (load or create)
        self.vector_store = self._initialize_vector_store()
        
    def _initialize_vector_store(self) -> FAISS:
        """
        Initialize the vector store from disk or create a new one.
        
        Returns:
            Initialized FAISS vector store
        """
        # Check if vector store exists
        if os.path.exists(self.vector_store_path) and os.path.isdir(self.vector_store_path):
            try:
                # Load existing vector store
                return FAISS.load_local(
                    self.vector_store_path,
                    self.embeddings_model
                )
            except Exception as e:
                print(f"Error loading vector store: {e}")
                print("Creating new vector store...")
        
        # Create new vector store
        documents = self._load_knowledge_documents()
        if not documents:
            # Create an empty vector store if no documents are found
            empty_document = Document(
                page_content="Hypnotherapy knowledge base",
                metadata={"source": "empty"}
            )
            return FAISS.from_documents(
                [empty_document],
                self.embeddings_model
            )
        
        # Create and save vector store
        vector_store = FAISS.from_documents(
            documents,
            self.embeddings_model
        )
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.vector_store_path), exist_ok=True)
        
        # Save vector store
        vector_store.save_local(self.vector_store_path)
        
        return vector_store
    
    def _load_knowledge_documents(self) -> List[Document]:
        """
        Load knowledge documents from the knowledge directory.
        
        Returns:
            List of Document objects
        """
        documents = []
        
        # Get all files in the knowledge directory and subdirectories
        for root, _, files in os.walk(self.knowledge_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # Process different file types
                    if file.endswith(".md"):
                        documents.extend(self._process_markdown(file_path))
                    elif file.endswith(".txt"):
                        documents.extend(self._process_text(file_path))
                    elif file.endswith(".json"):
                        documents.extend(self._process_json(file_path))
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        
        return text_splitter.split_documents(documents)
    
    def _process_markdown(self, file_path: str) -> List[Document]:
        """Process a markdown file"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract category from path
        category = self._extract_category(file_path)
        
        return [Document(
            page_content=content,
            metadata={
                "source": file_path,
                "category": category,
                "file_type": "markdown"
            }
        )]
    
    def _process_text(self, file_path: str) -> List[Document]:
        """Process a text file"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract category from path
        category = self._extract_category(file_path)
        
        return [Document(
            page_content=content,
            metadata={
                "source": file_path,
                "category": category,
                "file_type": "text"
            }
        )]
    
    def _process_json(self, file_path: str) -> List[Document]:
        """Process a JSON file"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        documents = []
        
        # Handle different JSON formats
        if isinstance(data, list):
            # List of items
            for item in data:
                if isinstance(item, dict) and "content" in item:
                    metadata = {k: v for k, v in item.items() if k != "content"}
                    metadata["source"] = file_path
                    if "category" not in metadata:
                        metadata["category"] = self._extract_category(file_path)
                    metadata["file_type"] = "json"
                    
                    documents.append(Document(
                        page_content=item["content"],
                        metadata=metadata
                    ))
        elif isinstance(data, dict) and "items" in data:
            # Dictionary with "items" key
            for item in data["items"]:
                if isinstance(item, dict) and "content" in item:
                    metadata = {k: v for k, v in item.items() if k != "content"}
                    metadata["source"] = file_path
                    if "category" not in metadata:
                        metadata["category"] = self._extract_category(file_path)
                    metadata["file_type"] = "json"
                    
                    documents.append(Document(
                        page_content=item["content"],
                        metadata=metadata
                    ))
        elif isinstance(data, dict) and "content" in data:
            # Single document
            metadata = {k: v for k, v in data.items() if k != "content"}
            metadata["source"] = file_path
            if "category" not in metadata:
                metadata["category"] = self._extract_category(file_path)
            metadata["file_type"] = "json"
            
            documents.append(Document(
                page_content=data["content"],
                metadata=metadata
            ))
        
        return documents
    
    def _extract_category(self, file_path: str) -> str:
        """
        Extract category from file path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Category name
        """
        path_parts = Path(file_path).parts
        
        # Look for known categories in the path
        categories = ["methods", "faq", "techniques", "safety"]
        for category in categories:
            if category in path_parts:
                return category
        
        # Default to the parent directory name
        if len(path_parts) > 1:
            return path_parts[-2]
        
        return "general"
    
    def _format_results(self, documents: List[Document]) -> str:
        """
        Format retrieved documents into a coherent response.
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted response
        """
        if not documents:
            return "I couldn't find specific information about that in my knowledge base."
        
        # Group by category
        categories = {}
        for doc in documents:
            category = doc.metadata.get("category", "general")
            if category not in categories:
                categories[category] = []
            categories[category].append(doc)
        
        # Format response
        response = []
        
        # Add introduction if multiple categories
        if len(categories) > 1:
            response.append("I found information about this topic in several categories:")
        
        # Add information from each category
        for category, docs in categories.items():
            if len(categories) > 1:
                response.append(f"\n## {category.title()}")
            
            for doc in docs:
                # Extract source information
                source = doc.metadata.get("source", "")
                if source:
                    source = os.path.basename(source)
                
                # Add content with citation
                content = doc.page_content.strip()
                if source:
                    response.append(f"{content}\n(Source: {source})")
                else:
                    response.append(content)
        
        return "\n\n".join(response)
    
    def _run(self, query: str) -> str:
        """
        Run the tool to retrieve knowledge about hypnotherapy.
        
        Args:
            query: The user's question or topic
            
        Returns:
            Relevant information from the knowledge base
        """
        try:
            # Retrieve relevant documents
            documents = self.vector_store.similarity_search(
                query,
                k=self.top_k
            )
            
            # Format results
            return self._format_results(documents)
            
        except Exception as e:
            # Handle errors
            error_message = f"Error retrieving information: {str(e)}"
            print(error_message)
            return "I'm having trouble accessing the hypnotherapy knowledge base at the moment. Please try again later."
    
    async def _arun(self, query: str) -> str:
        """
        Async version of _run.
        
        Args:
            query: The user's question or topic
            
        Returns:
            Relevant information from the knowledge base
        """
        return self._run(query)


# Helper function to create the tool
def create_hypnotherapy_knowledge_tool(
    knowledge_dir: str = None,
    vector_store_path: str = None,
    top_k: int = 5
) -> HypnotherapyKnowledgeTool:
    """
    Create a configured HypnotherapyKnowledgeTool instance.
    
    Args:
        knowledge_dir: Directory containing knowledge base files
        vector_store_path: Path to store/load the vector store
        top_k: Number of top results to return
        
    Returns:
        Configured HypnotherapyKnowledgeTool instance
    """
    # Use default paths if not provided
    if knowledge_dir is None:
        knowledge_dir = os.environ.get(
            "KNOWLEDGE_DIR",
            "src/hypnobot/knowledge/content"
        )
    
    if vector_store_path is None:
        vector_store_path = os.environ.get(
            "VECTOR_STORE_PATH",
            "data/vector_store"
        )
    
    return HypnotherapyKnowledgeTool(
        knowledge_dir=knowledge_dir,
        vector_store_path=vector_store_path,
        top_k=top_k
    )
```

## Sample Knowledge Base Structure (knowledge/content)

```
src/hypnobot/knowledge/content/
├── methods/
│   ├── induction.md
│   ├── deepening.md
│   └── regression.md
├── techniques/
│   ├── progressive_relaxation.md
│   ├── visualization.md
│   └── anchoring.md
├── faq/
│   ├── what_is_hypnotherapy.md
│   ├── session_expectations.md
│   └── misconceptions.md
└── safety/
    ├── boundaries.md
    ├── contraindications.md
    └── ethical_guidelines.md
```

## Sample Content Files

### methods/induction.md
```markdown
# Hypnotic Induction Methods

Hypnotic induction is the initial phase of hypnotherapy where the client is guided into a hypnotic state. This receptive state allows for more effective suggestion work during the main therapeutic phase.

## Common Induction Techniques

### Progressive Relaxation Induction
This involves guiding the client to progressively relax different muscle groups throughout their body, creating a state of deep physical relaxation that facilitates the hypnotic state.

### Eye Fixation Induction
The client is asked to fix their gaze on a specific point (sometimes a spot on the ceiling or wall, or the therapist's finger). As they continue to stare, suggestions of relaxation and eye fatigue are given until the eyes close naturally.

### Confusion Induction
This more advanced technique involves deliberately overloading the conscious mind with complex or contradictory information, creating a brief moment of confusion that can facilitate a rapid transition into hypnosis.

## Selection Criteria

The choice of induction method should be tailored to:
- The client's personality and preferences
- Their previous experience with hypnosis
- The therapeutic goals of the session
- Any physical limitations they may have

An effective induction creates a comfortable transition into the hypnotic state while building rapport and trust between the therapist and client.
```

### faq/what_is_hypnotherapy.md
```markdown
# What is Hypnotherapy?

Hypnotherapy is a therapeutic approach that uses guided hypnosis to help clients achieve a state of focused attention and heightened suggestibility. In this relaxed state, clients are more open to positive suggestions and exploring thoughts or feelings that might be less accessible during their normal waking state.

## Key Aspects of Hypnotherapy

- **Collaborative Process**: Hypnotherapy is always a collaboration between the therapist and client. The client remains in control throughout the process.

- **Natural State**: The hypnotic state is actually a natural state that most people experience daily when deeply absorbed in a book, movie, or creative activity.

- **Conscious Awareness**: Contrary to common misconceptions, people under hypnosis are not asleep or unconscious. They are actually in a state of heightened awareness and focused attention.

- **Complementary Approach**: Hypnotherapy often works best as a complementary approach alongside other therapeutic methods or medical treatments.

## What Happens During Hypnotherapy?

A typical hypnotherapy session involves:

1. **Pre-talk**: Discussion about goals, expectations, and addressing any concerns
2. **Induction**: Guiding the client into a relaxed, receptive state
3. **Deepening**: Enhancing the hypnotic state
4. **Therapeutic Work**: Applying techniques specific to the client's goals
5. **Post-hypnotic Suggestions**: Providing suggestions for continued benefit
6. **Emergence**: Guiding the client back to full alertness

Hypnotherapy can help with a wide range of issues including stress management, anxiety reduction, habit control, pain management, and personal development.
```

## Using the Knowledge Tool with CrewAI Agents

The knowledge tool can be integrated with CrewAI agents to provide access to the hypnotherapy knowledge base:

```python
from crewai import Agent
from hypnobot.tools.knowledge_tool import create_hypnotherapy_knowledge_tool

# Create the knowledge tool
knowledge_tool = create_hypnotherapy_knowledge_tool()

# Create a client-facing agent with the knowledge tool
client_agent = Agent(
    role="Hypnotherapy Guide",
    goal="Provide accurate, supportive information about hypnotherapy",
    backstory="You are an experienced guide helping people understand hypnotherapy and its benefits.",
    verbose=True,
    tools=[knowledge_tool]
)
```

## Tool Usage in Agent Conversations

When interacting with users, the client-facing agent can use the knowledge tool to retrieve accurate information:

```
USER: What exactly happens during a hypnotherapy session?

AGENT THOUGHT: I need information about hypnotherapy sessions to provide an accurate response. I'll use the knowledge tool to retrieve relevant information.

TOOL CALL: HypnotherapyKnowledgeTool
TOOL INPUT: "what happens during a hypnotherapy session structure steps"
TOOL OUTPUT: 
# What Happens During Hypnotherapy?

A typical hypnotherapy session involves:

1. **Pre-talk**: Discussion about goals, expectations, and addressing any concerns
2. **Induction**: Guiding the client into a relaxed, receptive state
3. **Deepening**: Enhancing the hypnotic state
4. **Therapeutic Work**: Applying techniques specific to the client's goals
5. **Post-hypnotic Suggestions**: Providing suggestions for continued benefit
6. **Emergence**: Guiding the client back to full alertness

Hypnotherapy can help with a wide range of issues including stress management, anxiety reduction, habit control, pain management, and personal development.
(Source: what_is_hypnotherapy.md)

AGENT RESPONSE: A typical hypnotherapy session follows a structured approach designed to maximize effectiveness and ensure your comfort throughout the experience.

Your session will begin with a pre-talk, where you'll discuss your goals and expectations with the hypnotherapist. This helps establish rapport and addresses any questions or concerns you might have.

Next comes the induction phase, where the therapist guides you into a relaxed, receptive state. This is followed by deepening techniques that enhance the hypnotic state, allowing you to become more receptive to positive suggestions.

The main portion of the session involves the therapeutic work specifically tailored to your goals, whether that's stress reduction, habit change, or personal development.

Near the end, the therapist will provide post-hypnotic suggestions designed to extend the benefits beyond the session, followed by a gentle emergence process that brings you back to full alertness, typically feeling refreshed and relaxed.

Would you like to know more about any specific part of the hypnotherapy process?
```

## Benefits of This Approach

1. **Accurate Information**: The knowledge tool ensures that agents provide information that's consistent with the practice's approach to hypnotherapy.

2. **Scalable Knowledge**: The knowledge base can be expanded over time without requiring changes to agent prompts.

3. **Retrievable Sources**: The tool provides source information, allowing for verification and updates as needed.

4. **Organized Content**: Information is categorized for more relevant retrieval and presentation.

5. **Separation of Concerns**: Content management is separated from agent implementation, making the system easier to maintain.

This implementation provides a robust foundation for knowledge retrieval in the hypnotherapy chatbot, ensuring that responses are accurate, helpful, and aligned with the practice's approach to hypnotherapy. 