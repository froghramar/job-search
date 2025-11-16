# Deployment Guide

This guide covers deploying your LinkedIn Job Agent to production using various methods.

## 🎯 Deployment Options

### 1. LangGraph Cloud (Recommended for Production)

LangGraph Cloud provides managed infrastructure for LangGraph applications.

#### Prerequisites
- LangSmith account
- GitHub repository with your code

#### Steps

```bash
# 1. Push your code to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/linkedin-job-agent.git
git push -u origin main

# 2. Deploy via LangSmith UI
# - Go to https://smith.langchain.com
# - Navigate to "Deployments"
# - Click "New Deployment"
# - Connect your GitHub repository
# - Select branch and langgraph.json
# - Configure environment variables
# - Deploy
```

#### Configuration

In LangSmith deployment settings:
- **Name**: linkedin-job-agent
- **Branch**: main
- **Config File**: langgraph.json
- **Environment Variables**: Add all from .env

### 2. Docker Deployment

Build and run as Docker container for any cloud platform.

#### Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY linkedin_agent/ ./linkedin_agent/
COPY langgraph.json .
COPY .env .

# Expose port
EXPOSE 8000

# Run the application
CMD ["langgraph", "up", "--port", "8000"]
```

#### Build and Run

```bash
# Build image
langgraph build -t linkedin-job-agent:latest

# Or manually with Docker
docker build -t linkedin-job-agent:latest .

# Run container
docker run -p 8000:8000 \
  --env-file .env \
  linkedin-job-agent:latest

# Test
curl http://localhost:8000/health
```

#### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  linkedin-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY}
      - LANGCHAIN_TRACING_V2=true
    volumes:
      - ./linkedin_agent:/app/linkedin_agent
    restart: unless-stopped
  
  # Optional: Add MongoDB for persistence
  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=password

volumes:
  mongodb_data:
```

Run with:
```bash
docker-compose up -d
```

### 3. AWS Deployment

#### Option A: AWS ECS (Elastic Container Service)

```bash
# 1. Configure AWS CLI
aws configure

# 2. Create ECR repository
aws ecr create-repository --repository-name linkedin-job-agent

# 3. Build and push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker tag linkedin-job-agent:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/linkedin-job-agent:latest

docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/linkedin-job-agent:latest

# 4. Create ECS task definition (see task-definition.json below)
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 5. Create ECS service
aws ecs create-service \
  --cluster linkedin-agent-cluster \
  --service-name linkedin-agent-service \
  --task-definition linkedin-job-agent \
  --desired-count 1 \
  --launch-type FARGATE
```

#### task-definition.json

```json
{
  "family": "linkedin-job-agent",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "linkedin-agent",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/linkedin-job-agent:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "your-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/linkedin-agent",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Option B: AWS Lambda (Serverless)

For lightweight, event-driven deployments:

```python
# lambda_handler.py
from linkedin_agent import graph
import json

def lambda_handler(event, context):
    """
    AWS Lambda handler for LinkedIn agent.
    """
    body = json.loads(event['body'])
    
    result = graph.invoke({
        "messages": body.get("messages", []),
        "user_profile": body.get("user_profile", {}),
        # ... other state fields
    })
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

Deploy with AWS SAM or Serverless Framework.

### 4. Google Cloud Platform

#### Cloud Run Deployment

```bash
# 1. Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# 2. Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/linkedin-job-agent

# 3. Deploy to Cloud Run
gcloud run deploy linkedin-job-agent \
  --image gcr.io/PROJECT-ID/linkedin-job-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY
```

### 5. Azure Deployment

#### Azure Container Instances

```bash
# 1. Login to Azure
az login

# 2. Create resource group
az group create --name linkedin-agent-rg --location eastus

# 3. Create container registry
az acr create --resource-group linkedin-agent-rg \
  --name linkedinagentacr --sku Basic

# 4. Build and push
az acr build --registry linkedinagentacr \
  --image linkedin-job-agent:latest .

# 5. Deploy to Container Instances
az container create \
  --resource-group linkedin-agent-rg \
  --name linkedin-agent \
  --image linkedinagentacr.azurecr.io/linkedin-job-agent:latest \
  --dns-name-label linkedin-agent \
  --ports 8000 \
  --environment-variables \
    OPENAI_API_KEY=$OPENAI_API_KEY
```

### 6. Kubernetes Deployment

#### deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: linkedin-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: linkedin-agent
  template:
    metadata:
      labels:
        app: linkedin-agent
    spec:
      containers:
      - name: linkedin-agent
        image: linkedin-job-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: linkedin-agent-service
spec:
  selector:
    app: linkedin-agent
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

## 🔧 Production Configuration

### Environment Variables

Set these in your production environment:

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional but recommended
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_...
LANGCHAIN_PROJECT=linkedin-agent-prod

# Application
LOG_LEVEL=INFO
DEBUG=false
MAX_APPLICATIONS_PER_DAY=50

# Database (if using persistence)
MONGODB_URI=mongodb://...
POSTGRES_URL=postgresql://...
```

### Scaling Configuration

#### Horizontal Scaling

```python
# langgraph.json - add scaling config
{
  "dependencies": ["."],
  "graphs": {
    "linkedin_job_agent": "./linkedin_agent/agent.py:graph"
  },
  "env": ".env",
  "scaling": {
    "min_instances": 2,
    "max_instances": 10,
    "target_cpu_utilization": 70
  }
}
```

#### Load Balancing

Use NGINX or cloud load balancers:

```nginx
# nginx.conf
upstream linkedin_agent {
    least_conn;
    server agent1:8000;
    server agent2:8000;
    server agent3:8000;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://linkedin_agent;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring

### LangSmith Integration

Already configured with environment variables. View at:
- https://smith.langchain.com

### CloudWatch/Stackdriver Logs

Add structured logging:

```python
import structlog
import logging

logger = structlog.get_logger()

# In your agent
logger.info("job_search_initiated", 
           user_id=user_id,
           search_params=params)
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram

job_searches = Counter('job_searches_total', 'Total job searches')
application_duration = Histogram('application_duration_seconds', 
                                'Application processing time')

@application_duration.time()
def apply_to_job(job_id):
    job_searches.inc()
    # ... application logic
```

## 🔐 Security Best Practices

### 1. Secrets Management

Use cloud secret managers:

```python
# AWS Secrets Manager
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

OPENAI_API_KEY = get_secret('linkedin-agent/openai-key')
```

### 2. API Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/search")
@limiter.limit("10/minute")
def search_jobs(request: Request):
    # ... search logic
    pass
```

### 3. Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Security(security)):
    token = credentials.credentials
    # Verify JWT token
    if not verify_jwt(token):
        raise HTTPException(status_code=401)
```

## 📈 Performance Optimization

### 1. Caching

```python
from functools import lru_cache
import redis

redis_client = redis.Redis(host='localhost', port=6379)

@lru_cache(maxsize=100)
def get_job_details(job_id: str):
    # Check cache first
    cached = redis_client.get(f"job:{job_id}")
    if cached:
        return json.loads(cached)
    
    # Fetch and cache
    result = fetch_from_linkedin(job_id)
    redis_client.setex(f"job:{job_id}", 3600, json.dumps(result))
    return result
```

### 2. Async Operations

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def search_multiple_locations(locations):
    tasks = [search_location(loc) for loc in locations]
    results = await asyncio.gather(*tasks)
    return results
```

## 🧪 Testing in Production

### Health Checks

```python
# Add to your application
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/ready")
def readiness_check():
    # Check dependencies
    checks = {
        "database": check_db_connection(),
        "llm": check_llm_api(),
        "linkedin": check_linkedin_access()
    }
    
    if all(checks.values()):
        return {"status": "ready", "checks": checks}
    return JSONResponse(
        status_code=503,
        content={"status": "not_ready", "checks": checks}
    )
```

### Smoke Tests

```bash
# smoke-test.sh
#!/bin/bash

BASE_URL="https://your-deployment.com"

# Test health endpoint
curl -f $BASE_URL/health || exit 1

# Test agent endpoint
curl -f -X POST $BASE_URL/invoke \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "test"}]}' \
  || exit 1

echo "Smoke tests passed!"
```

## 📋 Deployment Checklist

- [ ] Environment variables configured
- [ ] Secrets properly stored
- [ ] Database connections tested
- [ ] API rate limits configured
- [ ] Monitoring and logging enabled
- [ ] Health checks implemented
- [ ] SSL/TLS certificates configured
- [ ] Backup strategy in place
- [ ] Scaling policies defined
- [ ] CI/CD pipeline setup
- [ ] Documentation updated
- [ ] Team access configured
- [ ] Alerts configured
- [ ] Load testing completed
- [ ] Security scan passed

## 🆘 Troubleshooting

### Common Issues

**Issue**: Container fails to start
```bash
# Check logs
docker logs linkedin-agent
kubectl logs deployment/linkedin-agent
```

**Issue**: High memory usage
```bash
# Add memory limits
docker run -m 1g linkedin-agent
```

**Issue**: Slow response times
- Enable caching
- Add more replicas
- Optimize LLM calls
- Use async operations

## 📚 Additional Resources

- [LangGraph Deployment Docs](https://docs.langchain.com/langgraph-platform)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [AWS ECS Guide](https://docs.aws.amazon.com/ecs/)