FROM python:3.12-slim AS builder

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  build-essential \
  git \ 
  libpq-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt into the local user
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip \
  && pip install --user --no-cache-dir -r requirements.txt


FROM python:3.12-slim AS base

ENV PYTHONOPTIMIZE=1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Add the path to the installed Python binaries to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Set the working directory in the container to /app
WORKDIR /app

# We install only the system libraries needed for work (without compilers)
RUN apt-get update && apt-get install -y --no-install-recommends \
  libpq5 \
  curl \
  postgresql-client \
  git \
  ca-certificates \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Create a user and group
RUN addgroup --gid 1000 appgroup && adduser --uid 1000 --gid 1000 --disabled-password appuser

# create downloads directory and Establish the rights to the directory
RUN mkdir -p /app/static/downloads /app/sessions /app/migrations/versions && \
  chown -R appuser:appgroup /app

# Copy the installed libraries from the builder to the new user’s folder
COPY --from=builder --chown=appuser:appgroup /root/.local /home/appuser/.local

# Copy the launch script
COPY --chown=appuser:appgroup entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Switching to an unheard of user
USER appuser

# EXPOSE ports
EXPOSE 8080

# Run the application
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "main.py"]


FROM base AS media

# Switch to root to install the package
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
  ffmpeg \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Returning to safe mode
USER appuser


FROM base AS manager

# copy manager source code
COPY --chown=appuser:appgroup manager/ .

# EXPOSE ports
EXPOSE 5000

# Run the application
ENTRYPOINT ["/app/entrypoint.sh"]
