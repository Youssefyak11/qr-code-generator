# syntax=docker/dockerfile:1
FROM python:3.12-slim-bullseye

# Install minimal system packages (needed by Pillow for image handling)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo libpng16-16 \
 && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
ARG APP_USER=myuser
RUN useradd -m -s /usr/sbin/nologin ${APP_USER}

# Set working directory
WORKDIR /app

# Copy requirements first and install dependencies
COPY --chown=${APP_USER}:${APP_USER} requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create app directories with correct ownership
RUN mkdir -p /app/logs /app/qr_codes \
 && chown -R ${APP_USER}:${APP_USER} /app

# Copy app source
COPY --chown=${APP_USER}:${APP_USER} . .

# Switch to non-root user
USER ${APP_USER}

# Default environment variables
ENV OUTPUT_DIR=/app/qr_codes

# Start the app
ENTRYPOINT ["python", "main.py"]
CMD ["--url", "http://github.com/kaw393939", "--out", "/app/qr_codes"]
