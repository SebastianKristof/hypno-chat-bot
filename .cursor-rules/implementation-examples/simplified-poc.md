# Simplified POC Implementation

This document outlines a streamlined approach for quickly implementing a hypnotherapy chatbot POC using CrewAI, designed for rapid development while maintaining extensibility.

## Minimal Project Structure

```
hypnobot/
├── README.md                     # Project overview
├── requirements.txt              # Dependencies
├── .env                          # Environment variables
│
├── src/                          # Source code
│   ├── main.py                   # Entry point
│   │
│   ├── agents.py                 # Basic agent definitions
│   ├── tasks.py                  # Simple task definitions
│   ├── tools.py                  # Minimal tool implementations
│   ├── process.py                # Basic process workflow
│   │
│   ├── config/                   # Simple configuration
│   │   ├── settings.py           # Settings from environment
│   │   └── safety_rules.yaml     # Basic safety rules
│   │
│   ├── knowledge/                # Knowledge base
│   │   ├── content/              # Flat structure of .md files
│   │   └── indexer.py            # Simple vector store setup
│   │
│   └── api.py                    # Simple FastAPI app
│
└── scripts/                      # Helper scripts
    └── index_knowledge.py        # Knowledge indexing
```

## Quick Start Implementation

### 1. Define Minimal Agents (agents.py)

```python
"""
Simple agent definitions for hypnotherapy chatbot POC.
"""
from crewai import Agent
from tools import create_knowledge_tool, create_safety_tool
import os

# Get API keys from environment
openai_api_key = os.environ.get("OPENAI_API_KEY")

def create_client_agent():
    """Create the client-facing agent with knowledge tool"""
    knowledge_tool = create_knowledge_tool()
    
    return Agent(
        role="Hypnotherapy Guide",
        goal="Provide accurate, supportive information about hypnotherapy",
        backstory="You are an experienced guide helping people understand hypnotherapy",
        verbose=True,
        llm_config={
            "api_key": openai_api_key,
            "model": "gpt-4",  # Or a more affordable option like "gpt-3.5-turbo"
        },
        tools=[knowledge_tool]
    )

def create_qa_agent():
    """Create the QA agent with safety tool"""
    safety_tool = create_safety_tool()
    
    return Agent(
        role="Hypnotherapy Safety Specialist",
        goal="Ensure responses are safe and ethical",
        backstory="You are a specialist in therapeutic safety guidelines",
        verbose=True,
        llm_config={
            "api_key": openai_api_key,
            "model": "gpt-3.5-turbo",  # More affordable for QA checks
        },
        tools=[safety_tool]
    )
```

### 2. Implement Simple Tasks (tasks.py)

```python
"""
Simple task definitions for hypnotherapy chatbot POC.
"""
from crewai import Task

def create_chat_task(user_query):
    """Create a task for generating responses to user queries"""
    return Task(
        name="generate_response",
        description=f"""
        Generate a supportive, informative response to the user's query about hypnotherapy.
        Focus on being educational while maintaining appropriate boundaries.
        
        User query: {user_query}
        """,
        expected_output="A clear, supportive response that addresses the user's question",
        async_execution=True
    )

def create_review_task(user_query, proposed_response):
    """Create a task for reviewing responses for safety"""
    return Task(
        name="review_response",
        description=f"""
        Review the proposed response for safety concerns, scope violations, and ethical issues.
        
        User query: {user_query}
        Proposed response: {proposed_response}
        """,
        expected_output="A safety analysis with recommended action and modified response if needed",
        async_execution=True
    )
```

### 3. Create Simple Tools (tools.py)

```python
"""
Simplified tools for hypnotherapy chatbot POC.
"""
from crewai.tools import BaseTool
import os
import yaml
import json
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# Define simple knowledge tool
class SimpleKnowledgeTool(BaseTool):
    """Simplified knowledge retrieval tool"""
    
    name = "SimpleKnowledgeTool"
    description = "Search for information about hypnotherapy"
    
    def __init__(self, vector_store_path="data/vector_store"):
        super().__init__()
        self.vector_store_path = vector_store_path
        self.embeddings = OpenAIEmbeddings()
        
        # Load or create vector store
        if os.path.exists(vector_store_path) and os.path.isdir(vector_store_path):
            self.vector_store = FAISS.load_local(vector_store_path, self.embeddings)
        else:
            # Empty vector store as fallback
            self.vector_store = FAISS.from_documents(
                [Document(page_content="Hypnotherapy knowledge base", metadata={"source": "empty"})],
                self.embeddings
            )
    
    def _run(self, query):
        """Run the tool on the given query"""
        try:
            # Get relevant documents
            docs = self.vector_store.similarity_search(query, k=3)
            
            # Format results
            results = []
            for doc in docs:
                source = doc.metadata.get("source", "unknown")
                category = doc.metadata.get("category", "general")
                results.append(f"[{category}] {doc.page_content}\nSource: {source}")
            
            return "\n\n".join(results)
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"

    async def _arun(self, query):
        """Async version of _run"""
        return self._run(query)

# Define simple safety tool
class SimpleSafetyTool(BaseTool):
    """Simplified safety evaluation tool"""
    
    name = "SimpleSafetyTool"
    description = "Evaluate content for safety concerns"
    
    def __init__(self, rules_path="src/config/safety_rules.yaml"):
        super().__init__()
        self.rules_path = rules_path
        self.rules = self._load_rules()
    
    def _load_rules(self):
        """Load safety rules from YAML"""
        if os.path.exists(self.rules_path):
            try:
                with open(self.rules_path, 'r') as file:
                    return yaml.safe_load(file)
            except Exception:
                pass
        
        # Default rules if file not found
        return {
            "rules": [
                {
                    "rule_id": "crisis_detection",
                    "keywords": ["suicide", "kill myself", "want to die"],
                    "severity": "critical",
                    "response": "I notice you've mentioned something concerning. This chatbot isn't equipped to provide crisis support. Please contact a mental health professional or call a crisis helpline like 988 (US)."
                },
                {
                    "rule_id": "medical_advice",
                    "keywords": ["cure", "treat", "diagnose", "prescription"],
                    "severity": "medium",
                    "response": "I need to clarify that hypnotherapy is a complementary approach, not a standalone treatment or cure. It works best alongside traditional treatments under professional guidance."
                }
            ]
        }
    
    def _run(self, content):
        """Run the tool on the given content"""
        try:
            # Check content against rules
            for rule in self.rules.get("rules", []):
                keywords = rule.get("keywords", [])
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        return {
                            "safe": False,
                            "rule_id": rule.get("rule_id"),
                            "severity": rule.get("severity"),
                            "suggested_response": rule.get("response")
                        }
            
            # Default safe response
            return {
                "safe": True
            }
        except Exception as e:
            return {
                "safe": False,
                "error": str(e),
                "severity": "low"
            }

    async def _arun(self, content):
        """Async version of _run"""
        return self._run(content)

def create_knowledge_tool():
    """Create a simple knowledge tool instance"""
    return SimpleKnowledgeTool()

def create_safety_tool():
    """Create a simple safety tool instance"""
    return SimpleSafetyTool()
```

### 4. Create Simple Process (process.py)

```python
"""
Simple process workflow for hypnotherapy chatbot POC.
"""
from crewai import Process
from agents import create_client_agent, create_qa_agent
from tasks import create_chat_task, create_review_task

async def process_query(user_query):
    """Process a user query through the agent workflow"""
    # Create agents
    client_agent = create_client_agent()
    qa_agent = create_qa_agent()
    
    # Create tasks
    chat_task = create_chat_task(user_query)
    
    # First, have the client agent generate a response
    response = await client_agent.execute_task(chat_task)
    
    # Then, have the QA agent review it
    review_task = create_review_task(user_query, response)
    review_result = await qa_agent.execute_task(review_task)
    
    # Simple process - no need for complex Process setup yet
    # This allows faster iteration while testing the core functionality
    
    # Determine final response based on safety evaluation
    if isinstance(review_result, dict) and not review_result.get("safe", True):
        final_response = review_result.get("suggested_response", response)
    else:
        final_response = response
    
    return {
        "user_query": user_query,
        "original_response": response,
        "safety_result": review_result,
        "final_response": final_response
    }
```

### 5. Simple API Setup (api.py)

```python
"""
Simple FastAPI app for the hypnotherapy chatbot POC.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from process import process_query
import uvicorn

app = FastAPI(title="Hypnotherapy Chatbot POC")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Process a chat message and return a response"""
    try:
        # Process the user query
        result = await process_query(request.message)
        
        # Return the final response
        return ChatResponse(response=result["final_response"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

def start_api():
    """Start the API server"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_api()
```

### 6. Main Entry Point (main.py)

```python
"""
Main entry point for the hypnotherapy chatbot POC.
"""
import os
from dotenv import load_dotenv
from api import start_api

def main():
    """Main function to start the application"""
    # Load environment variables
    load_dotenv()
    
    # Validate essential environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set it in the .env file")
        return
    
    # Start the API server
    print("Starting Hypnotherapy Chatbot POC API...")
    start_api()

if __name__ == "__main__":
    main()
```

### 7. Knowledge Indexing Script (scripts/index_knowledge.py)

```python
"""
Script to index knowledge content for the hypnotherapy chatbot POC.
"""
import os
import glob
from pathlib import Path
from dotenv import load_dotenv
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

def index_knowledge():
    """Index the knowledge content"""
    # Load environment variables
    load_dotenv()
    
    # Validate API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        return
    
    # Settings
    knowledge_dir = "src/knowledge/content"
    vector_store_path = "data/vector_store"
    
    # Create directories if they don't exist
    os.makedirs(knowledge_dir, exist_ok=True)
    os.makedirs(vector_store_path, exist_ok=True)
    
    # Load documents
    documents = []
    
    # Find all markdown files
    markdown_files = glob.glob(f"{knowledge_dir}/**/*.md", recursive=True)
    
    print(f"Found {len(markdown_files)} markdown files")
    
    # Process each file
    for file_path in markdown_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Extract category from path
            path_parts = Path(file_path).parts
            category = "general"
            
            # Check if file is in a subdirectory
            if len(path_parts) > 1:
                category = path_parts[-2]
            
            # Create document
            documents.append(Document(
                page_content=content,
                metadata={
                    "source": file_path,
                    "category": category
                }
            ))
            
            print(f"Processed: {file_path}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Check if any documents were found
    if not documents:
        print("No documents found to index")
        return
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    
    chunks = text_splitter.split_documents(documents)
    
    print(f"Created {len(chunks)} document chunks")
    
    # Create vector store
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # Save vector store
    vector_store.save_local(vector_store_path)
    
    print(f"Vector store saved to {vector_store_path}")

if __name__ == "__main__":
    index_knowledge()
```

## Getting Started

1. **Set up environment**:
   ```bash
   # Clone repository
   git clone <repository-url>
   cd hypnobot
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Create .env file**:
   ```
   OPENAI_API_KEY=your_openai_key_here
   ```

3. **Add knowledge content**:
   Create a few markdown files in `src/knowledge/content/` with basic hypnotherapy information.

4. **Index knowledge content**:
   ```bash
   python scripts/index_knowledge.py
   ```

5. **Start the API**:
   ```bash
   python src/main.py
   ```

6. **Test the API**:
   ```bash
   curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"message":"What is hypnotherapy?"}'
   ```

## Extending the POC

This minimal implementation is designed for easy extension:

1. **Add more agents**: Create specialized agents for different aspects of hypnotherapy in `agents.py`.

2. **Enhance tools**: Expand the knowledge and safety tools with more sophisticated features.

3. **Improve workflow**: Upgrade to CrewAI's Process class for more complex interactions in `process.py`.

4. **Expand knowledge**: Add more content to the knowledge base and improve the indexing process.

5. **Enhance API**: Add authentication, rate limiting, and conversation history to the API.

This POC structure provides a solid foundation that can grow into a production system while allowing for quick initial development and testing. 