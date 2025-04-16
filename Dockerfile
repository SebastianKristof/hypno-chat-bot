FROM python:3.10-slim

WORKDIR /app

# Copy source code and static files
COPY src/ ./src/
COPY run_cli.py run_api.py ./

# Ensure static directory exists
RUN mkdir -p src/hypnobot/static

# Use either approach:
# Approach 1: With actual embedchain (more functionality, more dependencies)
# Approach 2: With memory_patch.py (mock implementation, fewer dependencies)
ARG APPROACH=2

# Install dependencies with minimal constraints
RUN pip install --no-cache-dir --upgrade pip && \
    # Install core dependencies first
    pip install --no-cache-dir \
        'pydantic>=1.10.0,<3.0.0' \
        'langchain>=0.0.325' \
        'langchain-openai>=0.0.1' \
        'langchain-community>=0.0.10' \
        'tiktoken>=0.5.1' && \
    # Install API dependencies
    pip install --no-cache-dir \
        'fastapi>=0.100.0' \
        'uvicorn>=0.20.0' \
        'python-dotenv>=0.20.0' \
        'PyYAML>=6.0.0' && \
    # Conditionally install embedchain or skip it (using our mock)
    if [ "$APPROACH" = "1" ]; then \
        pip install --no-cache-dir 'embedchain>=0.0.68' && \
        pip install --no-cache-dir 'crewai>=0.28.0,<0.29.0'; \
    else \
        pip install --no-cache-dir 'crewai>=0.28.0,<0.29.0' --no-deps; \
    fi

# Set environment variable
ENV PYTHONPATH=/app

# Default to API server
CMD ["uvicorn", "src.hypnobot.api:app", "--host", "0.0.0.0", "--port", "8000"] 