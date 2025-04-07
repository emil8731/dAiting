# Dating App AI Assistant - Installation and Deployment Guide

This guide provides detailed instructions for installing, configuring, and deploying the Dating App AI Assistant in various environments.

## Table of Contents

1. [Local Installation](#local-installation)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Configuration Options](#configuration-options)
5. [Security Considerations](#security-considerations)
6. [Maintenance and Updates](#maintenance-and-updates)

## Local Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)
- OpenAI API key

### Step-by-Step Installation

1. **Clone or download the repository**

   ```bash
   git clone https://github.com/yourusername/dating-app-ai-assistant.git
   cd dating-app-ai-assistant
   ```

   Alternatively, download and extract the source code from the releases page.

2. **Create and activate a virtual environment**

   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate on Linux/macOS
   source venv/bin/activate

   # Activate on Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment variables file**

   Create a `.env` file in the root directory with the following content:

   ```
   OPENAI_API_KEY=your_api_key_here
   DATABASE_PATH=/path/to/database.db  # Optional, defaults to dating_app.db in the current directory
   ```

5. **Initialize the application**

   ```bash
   python setup.py
   ```

   This will create the database, initialize the required tables, and generate default configuration files.

6. **Verify installation**

   ```bash
   python run_tests.py
   ```

   All tests should pass, confirming that the installation is working correctly.

### Running the Application

You can use the application in several ways:

1. **As a Python module**

   ```python
   from src.app import DatingAppAIAssistant

   app = DatingAppAIAssistant()
   # Use the app as described in the user documentation
   ```

2. **Using the command-line interface**

   ```bash
   python cli.py --help
   ```

3. **Using the web interface (if implemented)**

   ```bash
   python web_app.py
   ```

   Then open your browser and navigate to `http://localhost:5000`.

## Docker Deployment

### Prerequisites

- Docker
- Docker Compose (optional, for multi-container deployment)

### Building and Running with Docker

1. **Build the Docker image**

   ```bash
   docker build -t dating-app-ai-assistant .
   ```

2. **Run the container**

   ```bash
   docker run -d \
     --name dating-assistant \
     -e OPENAI_API_KEY=your_api_key_here \
     -v /path/to/data:/app/data \
     -p 5000:5000 \
     dating-app-ai-assistant
   ```

   This will:
   - Run the container in detached mode
   - Set the OpenAI API key
   - Mount a volume for persistent data storage
   - Expose port 5000 for the web interface (if implemented)

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3'

services:
  dating-assistant:
    build: .
    container_name: dating-assistant
    environment:
      - OPENAI_API_KEY=your_api_key_here
    volumes:
      - ./data:/app/data
    ports:
      - "5000:5000"
    restart: unless-stopped
```

Then run:

```bash
docker-compose up -d
```

## Cloud Deployment

The Dating App AI Assistant can be deployed to various cloud platforms. Here are instructions for some popular options:

### Heroku Deployment

1. **Create a Heroku account and install the Heroku CLI**

2. **Login to Heroku**

   ```bash
   heroku login
   ```

3. **Create a new Heroku app**

   ```bash
   heroku create dating-app-ai-assistant
   ```

4. **Add a Procfile**

   Create a file named `Procfile` in the root directory with the following content:

   ```
   web: gunicorn web_app:app
   ```

5. **Set environment variables**

   ```bash
   heroku config:set OPENAI_API_KEY=your_api_key_here
   ```

6. **Deploy the application**

   ```bash
   git push heroku main
   ```

### AWS Elastic Beanstalk Deployment

1. **Install the AWS CLI and EB CLI**

2. **Initialize EB application**

   ```bash
   eb init -p python-3.8 dating-app-ai-assistant
   ```

3. **Create an environment**

   ```bash
   eb create dating-assistant-env
   ```

4. **Set environment variables**

   ```bash
   eb setenv OPENAI_API_KEY=your_api_key_here
   ```

5. **Deploy the application**

   ```bash
   eb deploy
   ```

### Google Cloud Run Deployment

1. **Install the Google Cloud SDK**

2. **Build and push the Docker image**

   ```bash
   gcloud builds submit --tag gcr.io/your-project-id/dating-app-ai-assistant
   ```

3. **Deploy to Cloud Run**

   ```bash
   gcloud run deploy dating-assistant \
     --image gcr.io/your-project-id/dating-app-ai-assistant \
     --platform managed \
     --set-env-vars OPENAI_API_KEY=your_api_key_here
   ```

## Configuration Options

The Dating App AI Assistant can be configured through several files:

### Main Configuration

The main configuration is stored in `config.json` in the root directory:

```json
{
  "database_path": "dating_app.db",
  "log_level": "INFO",
  "log_file": "dating_app.log",
  "template_path": "src/data/message_templates.json",
  "openai": {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 150
  }
}
```

### Notification Configuration

Notification settings are stored in `notification_config.json`:

```json
{
  "enabled": true,
  "notification_types": {
    "new_message": true,
    "new_match": true,
    "conversation_inactive": true,
    "suggested_response": true
  },
  "channels": {
    "console": true,
    "email": false,
    "push": false
  },
  "email_settings": {
    "smtp_server": "",
    "smtp_port": 587,
    "username": "",
    "password": "",
    "from_address": ""
  },
  "quiet_hours": {
    "enabled": false,
    "start_hour": 22,
    "end_hour": 8
  }
}
```

### Message Templates

Message templates are stored in `src/data/message_templates.json`. You can customize these templates to match your preferred style and tone.

## Security Considerations

### Authentication Token Storage

Authentication tokens for dating platforms are stored in the local database. While they are encrypted, you should take precautions to secure your database file:

- Set appropriate file permissions (chmod 600 on Unix-like systems)
- Use full-disk encryption if possible
- Don't share your database file with others

### API Key Protection

Your OpenAI API key should be kept secure:

- Store it in environment variables, not in code
- Don't commit it to version control
- Rotate it periodically

### Network Security

When deploying to a public server:

- Use HTTPS for all communications
- Implement proper authentication for the web interface
- Consider using a VPN or SSH tunnel for remote access
- Set up a firewall to restrict access

## Maintenance and Updates

### Backup Procedures

Regularly back up your database file to prevent data loss:

```bash
# Create a backup
cp dating_app.db dating_app.db.backup

# Restore from backup if needed
cp dating_app.db.backup dating_app.db
```

For automated backups, consider setting up a cron job (Linux/macOS) or scheduled task (Windows).

### Updating the Application

To update to a new version:

1. **Backup your data**

   ```bash
   cp dating_app.db dating_app.db.backup
   ```

2. **Pull the latest changes**

   ```bash
   git pull origin main
   ```

3. **Update dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations (if any)**

   ```bash
   python migrate.py
   ```

5. **Verify the update**

   ```bash
   python run_tests.py
   ```

### Monitoring and Logging

The application logs to `dating_app.log` by default. Monitor this file for errors and warnings.

For production deployments, consider integrating with a monitoring service like:
- Datadog
- New Relic
- Prometheus + Grafana

### Troubleshooting Common Issues

1. **Authentication failures**
   - Check that your tokens are valid and not expired
   - Verify your internet connection
   - Check if the dating platform's API has changed

2. **Database errors**
   - Verify file permissions
   - Check disk space
   - Try restoring from a backup

3. **OpenAI API errors**
   - Verify your API key is valid
   - Check your API usage limits
   - Ensure you have billing set up correctly
