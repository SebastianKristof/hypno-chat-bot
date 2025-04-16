FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements-compatible.txt .
RUN pip install --no-cache-dir -r requirements-compatible.txt

# Copy the source code
COPY src/ ./src/
COPY run_cli.py run_api.py ./

# Set environment variable
ENV PYTHONPATH=/app

# Default command to run the CLI version
ENTRYPOINT ["python", "run_cli.py"] 