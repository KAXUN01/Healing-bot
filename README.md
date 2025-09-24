# Healing-bot

An AI-powered incident response and self-healing system that monitors, detects, and responds to system incidents automatically.

## Features

- **Incident Detection**: Uses machine learning to detect DDoS attacks and other system anomalies
- **Self-Healing**: Automated response capabilities for common issues
- **Monitoring Dashboard**: Real-time system metrics visualization
- **AI-Powered Analysis**: Leverages Google's Gemini AI for incident analysis
- **Prometheus Integration**: Exports metrics in Prometheus format
- **Slack Integration**: Optional notifications via Slack webhooks

## Components

1. **Incident Bot** (`/incident-bot`)
   - FastAPI application that handles incident detection and response
   - AI-powered analysis using Google Gemini
   - AWS S3 integration for log storage

2. **ML Model** (`/model`)
   - DDoS detection model built with TensorFlow
   - Real-time prediction capabilities
   - Feature extraction from system metrics

3. **Monitoring** (`/monitoring`)
   - Flask-based monitoring dashboard
   - Prometheus metrics export
   - System resource monitoring
   - Alert manager configuration

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your configuration
3. Install dependencies:
   ```bash
   # For development
   pip install -r requirements-dev.txt
   
   # For each component
   cd incident-bot && pip install -r requirements.txt
   cd ../model && pip install -r requirements.txt
   cd ../monitoring/server && pip install -r requirements.txt
   ```

4. Run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

## Development

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Code formatting:
   ```bash
   black .
   isort .
   ```

4. Type checking:
   ```bash
   mypy .
   ```

## Configuration

See `.env.example` for all available configuration options.

## License

See LICENSE file for details.