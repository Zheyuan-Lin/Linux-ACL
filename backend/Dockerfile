FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libldap2-dev \
    libsasl2-dev \
    ldap-utils \
    acl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create non-root user
RUN adduser --disabled-password --gecos "" aclmanager
RUN chown -R aclmanager:aclmanager /app

# Run as non-root user
USER aclmanager

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]