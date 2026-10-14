
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        DOCKER_IMAGE_NAME = 'library-management-platform'
        IMAGE_TAG = "v1.${BUILD_NUMBER}"
    }

    stages {

        stage('SCM Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Environment Setup & Dependencies') {
            steps {
                sh '''
                    set -e
                    python3 -m venv venv
                    ./venv/bin/python -m pip install --upgrade pip
                    ./venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Code Linting & Syntax Gate') {
            steps {
                sh '''
                    set -e
                    ./venv/bin/flake8 app/ database/ \
                      --count --select=E9,F63,F7,F82 \
                      --show-source --statistics
                '''
            }
        }

        stage('Automated Unit & Integration Tests') {
            steps {
                sh '''
                    set -e
                    mkdir -p reports
                    ./venv/bin/pytest -v --cov=app \
                      --junitxml=reports/test-results.xml tests/
                '''
            }
        }

        stage('Build Docker Artifact') {
            steps {
                sh '''
                    set -e

                    echo "Building Docker image..."
                    docker build \
                      -t ${DOCKER_IMAGE_NAME}:${IMAGE_TAG} .

                    echo "Tagging latest image..."
                    docker tag \
                      ${DOCKER_IMAGE_NAME}:${IMAGE_TAG} \
                      ${DOCKER_IMAGE_NAME}:latest

                    docker images ${DOCKER_IMAGE_NAME}
                '''
            }
        }

        stage('Kubernetes Minikube Deployment') {
            steps {
                sh '''
                    set -e

                    echo "Checking Kubernetes cluster..."
                    kubectl get nodes

                    echo "Loading Docker image into Minikube..."
                    minikube image load \
                      ${DOCKER_IMAGE_NAME}:${IMAGE_TAG}

                    echo "Applying Kubernetes manifests..."
                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    echo "Updating deployment image..."
                    kubectl set image \
                      deployment/library-deployment \
                      library-app=${DOCKER_IMAGE_NAME}:${IMAGE_TAG}

                    echo "Waiting for rollout..."
                    kubectl rollout status \
                      deployment/library-deployment \
                      --timeout=180s

                    echo "Deployment status:"
                    kubectl get deployments
                    kubectl get pods -o wide
                    kubectl get services
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true,
                  testResults: 'reports/test-results.xml'

            cleanWs()
        }

        success {
            echo 'CI/CD Pipeline completed successfully!'
        }

        failure {
            echo 'CI/CD Pipeline failed. Check console output.'
        }
    }
}
