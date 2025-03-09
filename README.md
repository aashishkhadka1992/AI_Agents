# AI-Powered Personal Assistant

An intelligent personal assistant that provides clothing recommendations based on weather conditions.

## Features

- Location-aware weather information
- Smart clothing recommendations
- Context-aware responses
- Efficient caching system
- Comprehensive error handling

## Prerequisites

- Python 3.9+
- Docker (for containerized deployment)
- Docker Compose (for easy container management)

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd AI_Agents
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment file and configure:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. Run the application:
```bash
python src/main.py
```

### Docker Deployment

1. Clone the repository:
```bash
git clone <repository-url>
cd AI_Agents
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

To run in detached mode:
```bash
docker-compose up -d
```

To stop the container:
```bash
docker-compose down
```

## Development

### Running Tests

Local:
```bash
python -m pytest src/tests/
```

Docker:
```bash
docker-compose exec ai-assistant python -m pytest src/tests/
```

### Code Style

Follow PEP 8 guidelines for Python code style.

## Architecture

The application follows a modular architecture:

- `src/agents/` - AI agent implementations
- `src/tools/` - Utility tools and APIs
- `src/utils/` - Helper functions
- `src/llm/` - LLM integration
- `src/tests/` - Test suite

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here] 