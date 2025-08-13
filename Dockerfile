# Stage 1: Build stage to install dependencies
FROM python:3.12-slim as builder

# Install poetry
RUN pip install poetry

# Set the working directory
WORKDIR /app

# Copy the dependency files
COPY poetry.lock pyproject.toml ./

# Install dependencies
# --no-root: Don't install the project itself
# --no-dev: Don't install dev dependencies
# --only main: Only install dependencies from the `main` group
RUN poetry install --no-root --no-dev --only main

# Stage 2: Final stage
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv ./.venv

# Activate the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Copy the application code
COPY src/ ./src/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.template_llm_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
