"""
Memory patch module to avoid embedchain dependency.
This provides mock implementations of the required classes.
"""

class MockApp:
    """Mock of embedchain App class."""
    
    def __init__(self, *args, **kwargs):
        self.data = {}
    
    def add(self, text, metadata=None):
        """Mock add method."""
        return True
    
    def query(self, query_text, **kwargs):
        """Mock query method."""
        return "No memory found (embedchain disabled)"

class MockRAGStorage:
    """Mock of RAGStorage class."""
    
    def __init__(self, *args, **kwargs):
        self.app = MockApp()
    
    def save_entity(self, entity_text, metadata=None):
        """Mock save_entity method."""
        return self.app.add(entity_text, metadata)
    
    def get_relevant_entities(self, query_text, **kwargs):
        """Mock get_relevant_entities method."""
        return []

class MockBaseLlm:
    """Mock base LLM class."""
    
    def __init__(self, *args, **kwargs):
        pass
        
    def get_llm(self):
        """Return None as mock LLM."""
        return None

    @classmethod
    def create(cls, *args, **kwargs):
        """Create mock LLM."""
        return cls()

class InvalidDimensionException(Exception):
    """Mock of InvalidDimensionException class."""
    pass

def patch_memory():
    """
    Patch the crewai memory module to avoid the embedchain dependency.
    Call this before importing HypnoBot.
    """
    import sys
    
    # Create mock packages and modules
    class MockChroma:
        InvalidDimensionException = InvalidDimensionException
    
    class MockVectorDB:
        chroma = MockChroma
    
    class MockLLM:
        base = type('base', (), {'BaseLlm': MockBaseLlm})
    
    class MockEmbedder:
        pass
    
    class MockEmbedchain:
        App = MockApp
        llm = MockLLM
        embedder = MockEmbedder
        vectordb = MockVectorDB
        # Add any other top-level modules needed
        
    # Add mock embedchain and its submodules to sys.modules
    sys.modules['embedchain'] = MockEmbedchain
    sys.modules['embedchain.llm'] = MockEmbedchain.llm
    sys.modules['embedchain.llm.base'] = MockEmbedchain.llm.base
    sys.modules['embedchain.embedder'] = MockEmbedchain.embedder
    sys.modules['embedchain.vectordb'] = MockEmbedchain.vectordb
    sys.modules['embedchain.vectordb.chroma'] = MockEmbedchain.vectordb.chroma
    
    # If crewai is already imported, patch the RAGStorage class
    if 'crewai.memory.storage.rag_storage' in sys.modules:
        import crewai.memory.storage.rag_storage as rag_storage
        rag_storage.RAGStorage = MockRAGStorage
        # Also patch the ImportError
        if hasattr(rag_storage, 'InvalidDimensionException'):
            rag_storage.InvalidDimensionException = InvalidDimensionException
    
    # Print successful patch
    print("📦 Embedchain dependency successfully mocked")
    
    return True 