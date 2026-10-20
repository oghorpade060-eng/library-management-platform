# Enterprise Smart Library Management Platform

A Flask-based REST API for managing library books, users, and loans, delivered through a complete DevOps pipeline: **Git/GitHub -> Jenkins CI -> Docker -> Kubernetes (Minikube)**.

This project was built for Unit 3 (DevOps, CI/CD, Containerization & Application Deployment).

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Getting Started (Local)](#getting-started-local)
5. [API Reference](#api-reference)
6. [Running Tests](#running-tests)
7. [CI/CD with Jenkins](#cicd-with-jenkins)
8. [Docker](#docker)
9. [Kubernetes (Minikube)](#kubernetes-minikube)
10. [Git Branching Strategy](#git-branching-strategy)
11. [Author](#author)

---

## Features

- Register and look up library users (Student / Faculty roles)
- Add books and search the catalog by title, author, or ISBN
- Borrow and return books with real-time inventory updates
- Loan quota enforcement: Students can borrow up to 3 books, Faculty up to 5
- Validation rules: no duplicate user/book IDs, no deleting users with active loans, no borrowing out-of-stock books
- Health-check endpoint used by Docker and Kubernetes probes
- Thread-safe in-memory data store with seed data
- Automated unit and integration tests with coverage reporting
- Fully automated pipeline: lint -> test -> build image -> deploy to Kubernetes

---

## Tech Stack

| Area              | Technology                          |
| ----------------- | ----------------------------------- |
| Language          | Python 3.11                         |
| Web Framework     | Flask 3.0                           |
| Testing           | Pytest, pytest-cov                  |
| Linting           | Flake8                              |
| WSGI Server       | Gunicorn                            |
| Version Control   | Git, GitHub                         |
| CI/CD             | Jenkins (Declarative Pipeline)      |
| Containerization  | Docker                              |
| Orchestration     | Kubernetes (Minikube)               |

---

## Project Structure

```
library-management-platform/
├── app/
│   ├── __init__.py              # Flask application factory
│   ├── routes/
│   │   └── api.py               # REST API endpoints
│   ├── services/
│   │   └── library_service.py   # Business logic and rules
│   └── models/
│       ├── book.py              # Book entity
│       └── user.py              # User entity
├── database/
│   └── db.py                    # Thread-safe in-memory data store
├── tests/
│   ├── test_user_service.py     # User operation tests
│   ├── test_book_service.py     # Book catalog tests
│   ├── test_borrow_return.py    # Checkout/return flow tests
│   └── test_api_endpoints.py    # HTTP endpoint tests
├── k8s/
│   ├── deployment.yaml          # Deployment (3 replicas, probes)
│   └── service.yaml             # NodePort service (30080)
├── Jenkinsfile                  # CI/CD pipeline definition
├── Dockerfile                   # Container build recipe
├── .dockerignore
├── .gitignore
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md
```

---

## Getting Started (Local)

### Prerequisites

- Python 3.11+
- pip
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/Sanket-dev98/library-management-platform.git
cd library-management-platform

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

The app starts on `http://localhost:5000`. Set the `PORT` environment variable to use a different port.

Quick check:

```bash
curl http://localhost:5000/api/health
```

### Seed Data

On startup the in-memory database contains:

- Users: `U101` (Alice Johnson, Student), `U102` (Dr. Robert Smith, Faculty)
- Books: `B001` (Cloud Native DevOps Architecture, 5 copies), `B002` (Continuous Delivery Principles, 3 copies)

---

## API Reference

Base path: `/api`

| Method | Endpoint          | Description                              |
| ------ | ----------------- | ---------------------------------------- |
| GET    | `/health`         | Service health check                     |
| POST   | `/users`          | Register a new user                      |
| GET    | `/users/<id>`     | Get a user by ID                         |
| GET    | `/books`          | List books (optional `?q=` search)       |
| POST   | `/books`          | Add a new book                           |
| POST   | `/borrow`         | Borrow a book                            |
| POST   | `/return`         | Return a borrowed book                   |

### Example Requests

Register a user:

```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"user_id": "U200", "name": "Grace Hopper", "email": "grace@navy.mil", "role": "Faculty"}'
```

Add a book:

```bash
curl -X POST http://localhost:5000/api/books \
  -H "Content-Type: application/json" \
  -d '{"book_id": "B003", "title": "The Phoenix Project", "author": "Gene Kim", "isbn": "978-1942788294", "total_copies": 2}'
```

Search books:

```bash
curl "http://localhost:5000/api/books?q=devops"
```

Borrow a book:

```bash
curl -X POST http://localhost:5000/api/borrow \
  -H "Content-Type: application/json" \
  -d '{"user_id": "U101", "book_id": "B001"}'
```

Return a book:

```bash
curl -X POST http://localhost:5000/api/return \
  -H "Content-Type: application/json" \
  -d '{"user_id": "U101", "book_id": "B001"}'
```

Errors are returned as JSON, e.g. `{"error": "User loan quota exceeded (Max: 3)."}` with HTTP status 400 (or 404 for missing users).

---

## Running Tests

```bash
pytest -v --cov=app --cov-report=term-missing --junitxml=reports/test-results.xml tests/
```

The suite covers user management, the book catalog, the borrow/return lifecycle (including quota enforcement), and the HTTP API through Flask's test client. A JUnit XML report is written to `reports/test-results.xml` for Jenkins.

Lint check:

```bash
flake8 app/ database/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

---

## CI/CD with Jenkins

The `Jenkinsfile` defines a declarative multi-stage pipeline:

1. **SCM Checkout** - pulls the code from GitHub
2. **Environment Setup & Dependencies** - creates a virtualenv and installs `requirements.txt`
3. **Code Linting & Syntax Gate** - runs Flake8
4. **Automated Unit & Integration Tests** - runs Pytest with coverage and exports JUnit XML
5. **Build Docker Artifact** - builds and tags `library-management-platform:v1.<BUILD_NUMBER>` and `latest`
6. **Kubernetes Minikube Deployment** - applies the manifests and waits for the rollout

The `post` section archives test reports, cleans the workspace, and reports build success or failure.

**Jenkins setup notes:** Jenkins needs Python 3, Docker, and `kubectl` available to the build user, and the job should be configured as a Pipeline from SCM pointing to this repository.

---

## Docker

Build and run the container locally:

```bash
# Build the image
docker build -t library-management-platform:v1.0.0 .

# Run it with port mapping
docker run -d -p 5000:5000 --name library-container library-management-platform:v1.0.0

# Verify
docker ps
curl http://localhost:5000/api/health

# View logs
docker logs -f library-container

# Clean up
docker stop library-container && docker rm library-container
```

Dockerfile highlights:

- Lightweight `python:3.11-slim` base image
- Dependency layer cached separately from application code
- Runs as a non-root user (`appuser`)
- Built-in `HEALTHCHECK` against `/api/health`

---

## Kubernetes (Minikube)

The `k8s/` folder contains a Deployment (3 replicas, rolling updates, liveness and readiness probes, resource requests/limits) and a NodePort Service exposed on port `30080`.

```bash
# Start the cluster
minikube start --driver=docker

# Build the image inside Minikube's Docker daemon
eval $(minikube docker-env)
docker build -t library-management-platform:v1.0.0 .

# Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Verify
kubectl get pods -l app=library-platform -o wide
kubectl get svc library-service

# Get the application URL
minikube service library-service --url
```

### Testing Self-Healing

Delete a pod and watch Kubernetes recreate it automatically:

```bash
kubectl delete pod $(kubectl get pods -l app=library-platform -o jsonpath='{.items[0].metadata.name}')
kubectl get pods -w
```

---

## Git Branching Strategy

Work was split into topic branches and merged into `main`:

| Branch                              | Purpose                                           |
| ----------------------------------- | ------------------------------------------------- |
| `feature/foundation`                | Base requirements, README, Flask skeleton         |
| `feature/core-app`                  | Business logic, models, REST endpoints, storage   |
| `feature/automated-tests`           | Pytest suites and coverage                        |
| `feature/jenkins-ci`                | Jenkinsfile and CI automation                     |
| `feature/dockerization`             | Dockerfile, `.dockerignore`, container builds     |
| `feature/kubernetes-orchestration`  | Kubernetes manifests and Minikube deployment      |
| `main`                              | Stable production branch                          |

---

## Author

**Onkar**
GitHub: [@Sanket-dev98](https://github.com/Sanket-dev98)

## Maintainer
Onkar Ghorpade

