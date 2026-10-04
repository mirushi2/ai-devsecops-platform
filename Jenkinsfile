pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
        ECR_REGISTRY = '874777259388.dkr.ecr.us-east-1.amazonaws.com'
        IMAGE_REPO = '874777259388.dkr.ecr.us-east-1.amazonaws.com/ai-devsecops-platform'
        KUBECONFIG = '/var/lib/jenkins/.kube/config'
        K8S_NAMESPACE = 'ai-devsecops'
        K8S_DEPLOYMENT = 'ai-devsecops-app'
        K8S_CONTAINER = 'ai-devsecops-app'
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/mirushi2/ai-devsecops-platform.git'
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    python3.13 -m venv .venv

                    .venv/bin/python --version

                    .venv/bin/pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    .venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    .venv/bin/pytest \
                        --cov=app \
                        --cov-report=term-missing \
                        --cov-fail-under=80
                '''
            }
        }

        stage('Dependency Security Scan') {
            steps {
                sh '''
                    .venv/bin/pip install pip-audit

                    .venv/bin/pip-audit -r requirements.txt
                '''
            }
        }

        stage('Trivy FS Scan') {
            steps {
                sh '''
                    trivy fs \
                        --exit-code 1 \
                        --severity HIGH,CRITICAL \
                        .
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {

                sh '''
                    .venv/bin/pip install pysonar
                '''

                withCredentials([
                    string(
                        credentialsId: 'sonar-token',
                        variable: 'SONAR_TOKEN'
                    )
                ]) {
                    sh '''
                        .venv/bin/pysonar \
                            --sonar-host-url=http://localhost:9000 \
                            --sonar-token="$SONAR_TOKEN" \
                            --sonar-project-key=AI-DevSecOps-Platform
                    '''
                }
            }
        }

        stage('ECR Login') {
            steps {
                sh '''
                    aws ecr get-login-password \
                        --region "$AWS_REGION" | \
                    docker login \
                        --username AWS \
                        --password-stdin "$ECR_REGISTRY"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    export DOCKER_BUILDKIT=0

                    docker build \
                        --platform linux/amd64 \
                        -t "$IMAGE_REPO:$BUILD_NUMBER" \
                        -t "$IMAGE_REPO:latest" \
                        .
                '''
            }
        }

        stage('Trivy Image Scan') {
            steps {
                sh '''
                    trivy image \
                        --exit-code 1 \
                        --severity CRITICAL \
                        "$IMAGE_REPO:$BUILD_NUMBER"
                '''
            }
        }

        stage('Push to ECR') {
            steps {
                sh '''
                    docker push "$IMAGE_REPO:$BUILD_NUMBER"

                    docker push "$IMAGE_REPO:latest"
                '''
            }
        }

        stage('Deploy to EKS') {
            steps {
                sh '''
                    echo "Deploying image:"
                    echo "$IMAGE_REPO:$BUILD_NUMBER"

                    echo "Applying Kubernetes namespace..."
                    kubectl apply \
                        -f k8s/namespace.yml

                    echo "Applying Kubernetes deployment..."
                    kubectl apply \
                        -f k8s/deployment.yaml

                    echo "Applying Kubernetes service..."
                    kubectl apply \
                        -f k8s/service.yml

                    echo "Updating deployment image..."

                    kubectl -n "$K8S_NAMESPACE" set image \
                        deployment/"$K8S_DEPLOYMENT" \
                        "$K8S_CONTAINER=$IMAGE_REPO:$BUILD_NUMBER"

                    echo "Current deployment image:"
                    kubectl -n "$K8S_NAMESPACE" get deployment "$K8S_DEPLOYMENT" \
                        -o jsonpath='{.spec.template.spec.containers[0].image}'

                    echo ""

                    echo "Waiting for rollout..."

                    if ! kubectl -n "$K8S_NAMESPACE" rollout status \
                        deployment/"$K8S_DEPLOYMENT" \
                        --timeout=120s
                    then
                        echo "Rollout failed."
                        echo "Rolling back deployment..."

                        kubectl -n "$K8S_NAMESPACE" rollout undo \
                            deployment/"$K8S_DEPLOYMENT"

                        kubectl -n "$K8S_NAMESPACE" rollout status \
                            deployment/"$K8S_DEPLOYMENT" \
                            --timeout=120s || true

                        exit 1
                    fi

                    echo "Rollout completed successfully."
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    echo "Deployment status:"
                    kubectl -n "$K8S_NAMESPACE" get deployment "$K8S_DEPLOYMENT"

                    echo ""
                    echo "Pods:"
                    kubectl -n "$K8S_NAMESPACE" get pods -o wide

                    echo ""
                    echo "Service:"
                    kubectl -n "$K8S_NAMESPACE" get service

                    echo ""
                    echo "Application image:"
                    kubectl -n "$K8S_NAMESPACE" get deployment "$K8S_DEPLOYMENT" \
                        -o jsonpath='{.spec.template.spec.containers[0].image}'

                    echo ""
                '''
            }
        }
    }

    post {

        success {
            echo 'CI/CD pipeline completed successfully.'
            echo 'Application deployed to Amazon EKS.'
        }

        failure {
            echo 'CI/CD pipeline failed.'
            echo 'Check the failed stage and Jenkins console output.'
        }

        always {
            echo "Build Number: ${env.BUILD_NUMBER}"
            echo "Build Result: ${currentBuild.currentResult}"
        }
    }
}