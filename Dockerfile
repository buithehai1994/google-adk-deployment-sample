# Use a slim Python base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install git, which is required by some ADK/MCP components for session management.
RUN apt-get update && apt-get install -y git --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN adduser --disabled-password --gecos "" myuser

# Copy requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install all dependencies from your requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Copy your project files (important so main.py and database folder exist)
COPY . .

# Create the database directory and give ownership to the non-root user
RUN mkdir -p /app/database && chown -R myuser:myuser /app/database

# Switch to the non-root user
USER myuser

# Set the PATH environment variable for the non-root user's packages
ENV PATH="/home/myuser/.local/bin:${PATH}"

# Set environment variables for Google Cloud runtime.
ENV GOOGLE_GENAI_USE_VERTEXAI=0

# Expose the port the app will run on
EXPOSE 8080

# Run the application by executing main.py
CMD ["python", "main.py"]
