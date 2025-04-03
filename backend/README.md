# Linux ACL Manager Backend

A FastAPI-based backend for managing Linux ACLs on research storage systems.

## Features

- File system ACL management
- LDAP authentication support
- File operations with ACL preservation
- RESTful API endpoints
- Comprehensive logging
- Docker support

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
# For production
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Create required directories:
```bash
mkdir -p data logs
```

## Development

1. Run the development server:
```bash
uvicorn app.main:app --reload
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
black .
isort .
```

4. Type checking:
```bash
mypy .
```

## Docker

Build and run with Docker:
```bash
docker build -t linux-acl-manager .
docker run -p 8000:8000 linux-acl-manager
```

## API Documentation

Once the server is running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/        # API endpoints
│   ├── core/       # Core functionality
│   ├── model/      # Data models
│   ├── service/    # Business logic
│   └── util/       # Utilities
├── test/           # Tests
├── deployment/     # Deployment configs
└── requirements/   # Dependencies
``` 