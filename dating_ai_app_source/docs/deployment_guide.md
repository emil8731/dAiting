# Deployment Guide for Dating App AI Assistant

This guide provides instructions for deploying the Dating App AI Assistant web application permanently to various cloud platforms or locally using Docker.

## Prerequisites

Before deploying, ensure you have:

1. An OpenAI API key for the AI message generation functionality
2. Git installed on your system
3. Docker and Docker Compose installed (for local deployment)
4. Appropriate CLI tools installed for your chosen cloud platform

## Deployment Options

The Dating App AI Assistant can be deployed in several ways:

### 1. Local Deployment with Docker

This is the simplest option for testing or personal use:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your_openai_api_key

# Run the deployment script and select option 4
./deploy.sh
```

This will:
- Create a `.env` file with necessary environment variables
- Build and start Docker containers for the web app, nginx, and SSL certificate management
- Make the application available at http://localhost

### 2. Digital Ocean App Platform

For a managed cloud deployment with minimal configuration:

```bash
# Install doctl if not already installed
# https://docs.digitalocean.com/reference/doctl/how-to/install/

# Authenticate with Digital Ocean
doctl auth init

# Set your OpenAI API key
export OPENAI_API_KEY=your_openai_api_key

# Run the deployment script and select option 1
./deploy.sh
```

### 3. Heroku Deployment

For a simple PaaS deployment:

```bash
# Install Heroku CLI if not already installed
# https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Set your OpenAI API key
export OPENAI_API_KEY=your_openai_api_key

# Run the deployment script and select option 2
./deploy.sh
```

### 4. AWS Elastic Beanstalk

For deployment on AWS infrastructure:

```bash
# Install AWS CLI and EB CLI if not already installed
# https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
# pip install awsebcli

# Configure AWS credentials
aws configure

# Set your OpenAI API key
export OPENAI_API_KEY=your_openai_api_key

# Run the deployment script and select option 3
./deploy.sh
```

## Manual Deployment

If you prefer to deploy manually or to a different platform:

1. Build the Docker image:
   ```bash
   docker build -t dating-app-ai-assistant .
   ```

2. Run the container:
   ```bash
   docker run -p 8080:8080 \
     -e FLASK_APP=web_app.py \
     -e FLASK_ENV=production \
     -e FLASK_SECRET_KEY=your_secret_key \
     -e OPENAI_API_KEY=your_openai_api_key \
     dating-app-ai-assistant
   ```

3. Set up a reverse proxy (like nginx) to handle SSL termination and serve the application.

## Environment Variables

The following environment variables are required:

- `FLASK_APP`: Set to `web_app.py`
- `FLASK_ENV`: Set to `production` for deployment
- `FLASK_SECRET_KEY`: A secure random string for session encryption
- `OPENAI_API_KEY`: Your OpenAI API key for AI message generation

## SSL Configuration

For production deployments, SSL is essential. The Docker Compose configuration includes Certbot for automatic SSL certificate management. To use your own certificates:

1. Place your SSL certificates in `./nginx/certbot/conf/`
2. Update the nginx configuration in `./nginx/nginx.conf` to reference your certificates

## Database Configuration

By default, the application uses SQLite for simplicity. For production deployments, consider:

1. Uncommenting the database service in `docker-compose.yml`
2. Updating the application to use PostgreSQL instead of SQLite
3. Setting appropriate database credentials as environment variables

## Monitoring and Maintenance

After deployment:

1. Set up monitoring for your application
2. Implement regular backups of the data directory
3. Set up a process for updating the application when new versions are available

## Troubleshooting

If you encounter issues during deployment:

1. Check the application logs: `docker-compose logs web`
2. Verify all environment variables are set correctly
3. Ensure ports are not blocked by firewalls
4. Verify your OpenAI API key is valid and has sufficient quota

For additional help, refer to the documentation for your chosen deployment platform.
