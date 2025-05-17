# syntax=docker/dockerfile:1

#############################################
# Builder stage: build wheels for dependencies
#############################################
FROM python:3.13-alpine AS builder

WORKDIR /app

# Install Alpine build dependencies
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    musl-dev \
    gcc \
    g++ \
    make

# Upgrade pip and install wheel/setuptools
RUN pip install --no-cache-dir --upgrade pip wheel setuptools

# Copy project metadata and source
COPY pyproject.toml ./
COPY src ./src

# Build wheels for project and all dependencies
RUN pip wheel --no-cache-dir . -w wheelhouse

#############################################
# Runtime stage: install dependencies & run app
#############################################
FROM python:3.13-alpine AS runtime

WORKDIR /app

# Install only runtime system libraries
RUN apk add --no-cache libffi

# Copy built wheels from builder and install offline
COPY --from=builder /app/wheelhouse ./wheelhouse
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-index --find-links=wheelhouse llm-wrapper \
    && rm -rf wheelhouse

# Copy application source code
COPY src ./src

# Set Python module root
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "llm_wrapper.server.main:app", "--host", "0.0.0.0", "--port", "8000"]