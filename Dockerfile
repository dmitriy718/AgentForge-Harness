FROM python:3.12-slim

# Install system dependencies required for build and execution
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up the working directory
WORKDIR /app

# Create a non-root user for security
RUN useradd -m -s /bin/bash aih_user
RUN chown -R aih_user:aih_user /app

# Copy the pyproject.toml and the rest of the application
COPY . /app

# Install the application and its dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Switch to the non-root user
USER aih_user

# Expose an environment variable to define the default config
ENV AI_HARNESS_HOME=/app
ENV AIH_COLOR=always

# Default command
ENTRYPOINT ["aih"]
CMD ["--help"]
