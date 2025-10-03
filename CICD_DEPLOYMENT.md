# 🚀 CI/CD & Production Deployment Guide

## Overview

Guia completo para pipeline CI/CD e deploy em produção do e-commerce platform.

---

## 🔄 CI/CD Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  CI/CD PIPELINE FLOW                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Developer → Git Push                                   │
│      ↓                                                   │
│  GitHub Actions / GitLab CI                             │
│      ↓                                                   │
│  ┌──────────────┐                                       │
│  │ Stage 1: Build & Test                                │
│  ├──────────────┤                                       │
│  │ • Lint Code (Black, Flake8)                          │
│  │ • Security Scan (Bandit, Safety)                     │
│  │ • Unit Tests (pytest)                                │
│  │ • Code Coverage (>80%)                               │
│  │ • Type Checking (MyPy)                               │
│  └──────┬───────┘                                       │
│         ↓                                                │
│  ┌──────────────┐                                       │
│  │ Stage 2: Docker Build                                │
│  ├──────────────┤                                       │
│  │ • Multi-stage Dockerfile                             │
│  │ • Vulnerability Scan (Trivy)                         │
│  │ • Push to ECR/Docker Hub                             │
│  │ • Tag: git-sha, version                              │
│  └──────┬───────┘                                       │
│         ↓                                                │
│  ┌──────────────┐                                       │
│  │ Stage 3: Integration Tests                           │
│  ├──────────────┤                                       │
│  │ • docker-compose test env                            │
│  │ • API tests (Postman/Newman)                         │
│  │ • Database migrations                                │
│  └──────┬───────┘                                       │
│         ↓                                                │
│  ┌──────────────┐                                       │
│  │ Stage 4: Deploy to Staging                           │
│  ├──────────────┤                                       │
│  │ • Kubernetes: staging namespace                      │
│  │ • Run smoke tests                                    │
│  │ • Performance tests (K6)                             │
│  └──────┬───────┘                                       │
│         ↓                                                │
│  ┌──────────────┐                                       │
│  │ Stage 5: Manual Approval                             │
│  │ (Production only)                                    │
│  └──────┬───────┘                                       │
│         ↓                                                │
│  ┌──────────────┐                                       │
│  │ Stage 6: Deploy to Production                        │
│  ├──────────────┤                                       │
│  │ • Blue/Green Deployment                              │
│  │ • Canary Release (10% → 100%)                        │
│  │ • Health Checks                                      │
│  │ • Rollback on failure                                │
│  └──────┬───────┘                                       │
│         ↓                                                │
│  ┌──────────────┐                                       │
│  │ Stage 7: Post-Deployment                             │
│  ├──────────────┤                                       │
│  │ • Smoke tests                                        │
│  │ • Monitor metrics (5 min)                            │
│  │ • Slack notification                                 │
│  │ • Update changelog                                   │
│  └──────────────┘                                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 GitHub Actions Workflows

### 1. Main CI/CD Workflow

```yaml
# .github/workflows/ci-cd.yml

name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  release:
    types: [created]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ============================================
  # JOB 1: Code Quality & Security
  # ============================================
  code-quality:
    name: Code Quality & Security Checks
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11']

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt

      - name: Code Formatting Check
        run: |
          black --check --diff services/
          isort --check-only services/

      - name: Linting
        run: |
          flake8 services/ --max-line-length=100 --exclude=migrations
          pylint services/ --disable=C0111,R0903

      - name: Type Checking
        run: |
          mypy services/ --ignore-missing-imports

      - name: Security Scan
        run: |
          bandit -r services/ -f json -o bandit-report.json
          safety check --json

      - name: Upload Security Reports
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json

  # ============================================
  # JOB 2: Unit Tests
  # ============================================
  unit-tests:
    name: Unit Tests
    runs-on: ubuntu-latest
    needs: code-quality

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      mongodb:
        image: mongo:7
        env:
          MONGO_INITDB_ROOT_USERNAME: test_user
          MONGO_INITDB_ROOT_PASSWORD: test_password
        ports:
          - 27017:27017

      redis:
        image: redis:alpine
        ports:
          - 6379:6379

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run Unit Tests
        env:
          POSTGRES_HOST: localhost
          POSTGRES_PORT: 5432
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: test_password
          MONGO_HOST: localhost
          MONGO_PORT: 27017
          REDIS_HOST: localhost
        run: |
          pytest services/ \
            --cov=services \
            --cov-report=xml \
            --cov-report=html \
            --cov-fail-under=80 \
            --junitxml=junit.xml

      - name: Upload Coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: ./coverage.xml
          fail_ci_if_error: true

      - name: Upload Test Results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: |
            junit.xml
            htmlcov/

  # ============================================
  # JOB 3: Build Docker Images
  # ============================================
  build-images:
    name: Build Docker Images
    runs-on: ubuntu-latest
    needs: unit-tests
    strategy:
      matrix:
        service:
          - auth-service
          - user-service
          - product-service
          - order-service
          - payment-service
          - notification-service

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}
          tags: |
            type=sha,format=short
            type=semver,pattern={{version}}
            type=ref,event=branch

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./services/${{ matrix.service }}
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}:buildcache,mode=max

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}:sha-${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

  # ============================================
  # JOB 4: Integration Tests
  # ============================================
  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: build-images

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Create .env file
        run: |
          cp .env.example .env

      - name: Start services
        run: |
          docker-compose -f docker-compose.test.yml up -d
          sleep 30  # Wait for services to be ready

      - name: Run integration tests
        run: |
          docker-compose -f docker-compose.test.yml run --rm \
            integration-tests pytest tests/integration/ -v

      - name: Run API tests with Newman
        run: |
          npm install -g newman
          newman run tests/postman/collection.json \
            -e tests/postman/env.json \
            --reporters cli,json \
            --reporter-json-export newman-report.json

      - name: Cleanup
        if: always()
        run: docker-compose -f docker-compose.test.yml down -v

  # ============================================
  # JOB 5: Deploy to Staging
  # ============================================
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: integration-tests
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging.ecommerce.com

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Configure kubectl
        run: |
          aws eks update-kubeconfig --name ecommerce-staging --region us-east-1

      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/staging/ -n staging
          kubectl set image deployment/auth-service \
            auth-service=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/auth-service:sha-${{ github.sha }} \
            -n staging
          kubectl rollout status deployment/auth-service -n staging

      - name: Run smoke tests
        run: |
          sleep 60
          curl -f https://staging.ecommerce.com/health || exit 1

  # ============================================
  # JOB 6: Deploy to Production
  # ============================================
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: integration-tests
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://ecommerce.com

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID_PROD }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY_PROD }}
          aws-region: us-east-1

      - name: Configure kubectl
        run: |
          aws eks update-kubeconfig --name ecommerce-prod --region us-east-1

      - name: Blue/Green Deployment
        run: |
          ./scripts/blue-green-deploy.sh \
            --service auth-service \
            --image ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/auth-service:sha-${{ github.sha }} \
            --namespace production

      - name: Post-deployment checks
        run: |
          sleep 120
          ./scripts/post-deploy-checks.sh

      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Deployment to production completed successfully!'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}

  # ============================================
  # JOB 7: Performance Tests
  # ============================================
  performance-tests:
    name: Performance Tests
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/develop'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run K6 load tests
        uses: grafana/k6-action@v0.3.1
        with:
          filename: tests/performance/load-test.js
          flags: --out json=results.json

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: k6-results
          path: results.json
```

---

## 🐳 Optimized Dockerfile (Multi-stage Build)

```dockerfile
# services/auth-service/Dockerfile

# ============================================
# Stage 1: Base
# ============================================
FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# Stage 2: Dependencies
# ============================================
FROM base AS dependencies

COPY requirements.txt .

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 3: Development
# ============================================
FROM base AS development

COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dev dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

EXPOSE 5000

CMD ["python", "run.py"]

# ============================================
# Stage 4: Testing
# ============================================
FROM development AS testing

RUN pytest tests/ --cov=app --cov-report=term-missing

# ============================================
# Stage 5: Production
# ============================================
FROM base AS production

# Copy only necessary files
COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--worker-class", "gthread", \
     "--threads", "2", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "run:app"]
```

---

## ☸️ Kubernetes Manifests

### 1. Deployment

```yaml
# k8s/production/auth-service/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: production
  labels:
    app: auth-service
    version: v1
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "5000"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: auth-service
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000

      # Init container for migrations
      initContainers:
        - name: db-migrations
          image: ghcr.io/yourorg/auth-service:latest
          command: ["flask", "db", "upgrade"]
          envFrom:
            - secretRef:
                name: auth-service-secrets
            - configMapRef:
                name: auth-service-config

      containers:
        - name: auth-service
          image: ghcr.io/yourorg/auth-service:latest
          imagePullPolicy: Always
          ports:
            - name: http
              containerPort: 5000
              protocol: TCP
          envFrom:
            - secretRef:
                name: auth-service-secrets
            - configMapRef:
                name: auth-service-config
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            successThreshold: 1
            failureThreshold: 3
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 15"]

      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - auth-service
                topologyKey: kubernetes.io/hostname
```

### 2. Service

```yaml
# k8s/production/auth-service/service.yaml

apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: production
  labels:
    app: auth-service
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: http
      protocol: TCP
      name: http
  selector:
    app: auth-service
```

### 3. HorizontalPodAutoscaler

```yaml
# k8s/production/auth-service/hpa.yaml

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: auth-service-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: auth-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
        - type: Pods
          value: 2
          periodSeconds: 60
      selectPolicy: Max
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
```

### 4. Ingress (with SSL)

```yaml
# k8s/production/ingress.yaml

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ecommerce-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - api.ecommerce.com
      secretName: ecommerce-tls
  rules:
    - host: api.ecommerce.com
      http:
        paths:
          - path: /api/auth
            pathType: Prefix
            backend:
              service:
                name: auth-service
                port:
                  number: 80
          - path: /api/products
            pathType: Prefix
            backend:
              service:
                name: product-service
                port:
                  number: 80
          - path: /api/orders
            pathType: Prefix
            backend:
              service:
                name: order-service
                port:
                  number: 80
```

---

## 📊 Monitoring & Observability

### 1. Prometheus ServiceMonitor

```yaml
# k8s/production/monitoring/servicemonitor.yaml

apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: auth-service
  namespace: production
spec:
  selector:
    matchLabels:
      app: auth-service
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

### 2. Grafana Dashboard

```json
{
  "dashboard": {
    "title": "E-commerce Services",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [{
          "expr": "rate(http_requests_total[5m])"
        }]
      },
      {
        "title": "Error Rate",
        "targets": [{
          "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
        }]
      },
      {
        "title": "Response Time (p95)",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
        }]
      }
    ]
  }
}
```

---

## 🔄 Blue/Green Deployment Script

```bash
#!/bin/bash
# scripts/blue-green-deploy.sh

set -e

SERVICE=$1
IMAGE=$2
NAMESPACE=$3

echo "Starting blue/green deployment for $SERVICE"

# Deploy green environment
kubectl apply -f k8s/$NAMESPACE/$SERVICE-green.yaml

# Wait for green to be ready
kubectl wait --for=condition=available --timeout=300s \
  deployment/$SERVICE-green -n $NAMESPACE

# Run health checks
echo "Running health checks on green environment..."
GREEN_POD=$(kubectl get pods -n $NAMESPACE -l app=$SERVICE-green -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n $NAMESPACE $GREEN_POD -- curl -f http://localhost:5000/health

# Switch traffic to green
kubectl patch service $SERVICE -n $NAMESPACE -p '{"spec":{"selector":{"version":"green"}}}'

# Wait and monitor
sleep 60

# Check metrics
ERROR_RATE=$(kubectl exec -n $NAMESPACE prometheus-0 -- \
  promtool query instant 'rate(http_requests_total{status=~"5..",service="'$SERVICE'"}[5m])' | \
  grep -oP '\d+\.\d+')

if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
  echo "Error rate too high, rolling back!"
  kubectl patch service $SERVICE -n $NAMESPACE -p '{"spec":{"selector":{"version":"blue"}}}'
  exit 1
fi

# Delete blue deployment
kubectl delete deployment $SERVICE-blue -n $NAMESPACE

echo "Deployment successful!"
```

---

## 🌍 Infrastructure as Code (Terraform)

```hcl
# terraform/main.tf

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
  }

  backend "s3" {
    bucket         = "ecommerce-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock"
  }
}

# VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "ecommerce-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false

  tags = {
    Environment = "production"
    Project     = "ecommerce"
  }
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"

  cluster_name    = "ecommerce-prod"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access = true

  eks_managed_node_groups = {
    general = {
      min_size     = 3
      max_size     = 10
      desired_size = 5

      instance_types = ["t3.large"]
      capacity_type  = "ON_DEMAND"

      labels = {
        workload = "general"
      }

      tags = {
        Environment = "production"
      }
    }
  }
}

# RDS PostgreSQL
module "rds" {
  source = "terraform-aws-modules/rds/aws"

  identifier = "ecommerce-postgres"

  engine               = "postgres"
  engine_version       = "15.4"
  family               = "postgres15"
  major_engine_version = "15"
  instance_class       = "db.t3.large"

  allocated_storage     = 100
  max_allocated_storage = 500

  db_name  = "ecommerce"
  username = "dbadmin"
  port     = 5432

  multi_az               = true
  subnet_ids             = module.vpc.private_subnets
  vpc_security_group_ids = [module.security_group_rds.security_group_id]

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = {
    Environment = "production"
  }
}
```

---

**Deployment Checklist**:

- [ ] All tests passing
- [ ] Security scans clean
- [ ] Database migrations ready
- [ ] Environment variables configured
- [ ] Monitoring dashboards set up
- [ ] Backup strategy in place
- [ ] Disaster recovery plan documented
- [ ] Runbook for incidents
- [ ] On-call rotation scheduled
- [ ] Stakeholders notified

---

**Version: 1.0**
**Last Updated: 2025-01-01**
