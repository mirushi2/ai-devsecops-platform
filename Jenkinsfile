// pipeline {
//     agent any

//     environment {
//         AWS_REGION = 'us-east-1'
//         ECR_REGISTRY = '874777259388.dkr.ecr.us-east-1.amazonaws.com'
//         IMAGE_REPO = '874777259388.dkr.ecr.us-east-1.amazonaws.com/ai-devsecops-platform'
//         KUBECONFIG = '/var/lib/jenkins/.kube/config'
//         K8S_NAMESPACE = 'ai-devsecops'
//         K8S_DEPLOYMENT = 'ai-devsecops-app'
//         K8S_CONTAINER = 'ai-devsecops-app'
//     }

//     stages {

//         stage('Checkout') {
//             steps {
//                 git branch: 'main',
//                     url: 'https://github.com/mirushi2/ai-devsecops-platform.git'
//             }
//         }

//         stage('Setup Python') {
//             steps {
//                 sh '''
//                     python3.13 -m venv .venv

//                     .venv/bin/python --version

//                     .venv/bin/pip install --upgrade pip
//                 '''
//             }
//         }

//         stage('Install Dependencies') {
//             steps {
//                 sh '''
//                     .venv/bin/pip install -r requirements.txt
//                 '''
//             }
//         }

//         stage('Run Tests') {
//             steps {
//                 sh '''
//                     .venv/bin/pytest \
//                         --cov=app \
//                         --cov-report=term-missing \
//                         --cov-fail-under=80
//                 '''
//             }
//         }

//         stage('Dependency Security Scan') {
//             steps {
//                 sh '''
//                     .venv/bin/pip install pip-audit

//                     .venv/bin/pip-audit -r requirements.txt
//                 '''
//             }
//         }

//         stage('Trivy FS Scan') {
//             steps {
//                 sh '''
//                     trivy fs \
//                         --exit-code 1 \
//                         --severity HIGH,CRITICAL \
//                         .
//                 '''
//             }
//         }

//         stage('SonarQube Analysis') {
//             steps {

//                 sh '''
//                     .venv/bin/pip install pysonar
//                 '''

//                 withCredentials([
//                     string(
//                         credentialsId: 'sonar-token',
//                         variable: 'SONAR_TOKEN'
//                     )
//                 ]) {
//                     sh '''
//                         .venv/bin/pysonar \
//                             --sonar-host-url=http://localhost:9000 \
//                             --sonar-token="$SONAR_TOKEN" \
//                             --sonar-project-key=AI-DevSecOps-Platform
//                     '''
//                 }
//             }
//         }

//         stage('ECR Login') {
//             steps {
//                 sh '''
//                     aws ecr get-login-password \
//                         --region "$AWS_REGION" | \
//                     docker login \
//                         --username AWS \
//                         --password-stdin "$ECR_REGISTRY"
//                 '''
//             }
//         }

//         stage('Build Docker Image') {
//             steps {
//                 sh '''
//                     export DOCKER_BUILDKIT=0

//                     docker build \
//                         --platform linux/amd64 \
//                         -t "$IMAGE_REPO:$BUILD_NUMBER" \
//                         -t "$IMAGE_REPO:latest" \
//                         .
//                 '''
//             }
//         }

//         stage('Trivy Image Scan') {
//             steps {
//                 sh '''
//                     trivy image \
//                         --exit-code 1 \
//                         --severity CRITICAL \
//                         "$IMAGE_REPO:$BUILD_NUMBER"
//                 '''
//             }
//         }

//         stage('Push to ECR') {
//             steps {
//                 sh '''
//                     docker push "$IMAGE_REPO:$BUILD_NUMBER"

//                     docker push "$IMAGE_REPO:latest"
//                 '''
//             }
//         }

//         stage('Deploy to EKS') {
//             steps {
//                 sh '''
//                     echo "Deploying image:"
//                     echo "$IMAGE_REPO:$BUILD_NUMBER"

//                     echo "Applying Kubernetes namespace..."
//                     kubectl apply \
//                         -f k8s/namespace.yml

//                     echo "Applying Kubernetes deployment..."
//                     kubectl apply \
//                         -f k8s/deployment.yaml

//                     echo "Applying Kubernetes service..."
//                     kubectl apply \
//                         -f k8s/service.yml

//                     echo "Updating deployment image..."

//                     kubectl -n "$K8S_NAMESPACE" set image \
//                         deployment/"$K8S_DEPLOYMENT" \
//                         "$K8S_CONTAINER=$IMAGE_REPO:$BUILD_NUMBER"

//                     echo "Current deployment image:"
//                     kubectl -n "$K8S_NAMESPACE" get deployment "$K8S_DEPLOYMENT" \
//                         -o jsonpath='{.spec.template.spec.containers[0].image}'

//                     echo ""

//                     echo "Waiting for rollout..."

//                     if ! kubectl -n "$K8S_NAMESPACE" rollout status \
//                         deployment/"$K8S_DEPLOYMENT" \
//                         --timeout=120s
//                     then
//                         echo "Rollout failed."
//                         echo "Rolling back deployment..."

//                         kubectl -n "$K8S_NAMESPACE" rollout undo \
//                             deployment/"$K8S_DEPLOYMENT"

//                         kubectl -n "$K8S_NAMESPACE" rollout status \
//                             deployment/"$K8S_DEPLOYMENT" \
//                             --timeout=120s || true

//                         exit 1
//                     fi

//                     echo "Rollout completed successfully."
//                 '''
//             }
//         }

//         stage('Verify Deployment') {
//             steps {
//                 sh '''
//                     echo "Deployment status:"
//                     kubectl -n "$K8S_NAMESPACE" get deployment "$K8S_DEPLOYMENT"

//                     echo ""
//                     echo "Pods:"
//                     kubectl -n "$K8S_NAMESPACE" get pods -o wide

//                     echo ""
//                     echo "Service:"
//                     kubectl -n "$K8S_NAMESPACE" get service

//                     echo ""
//                     echo "Application image:"
//                     kubectl -n "$K8S_NAMESPACE" get deployment "$K8S_DEPLOYMENT" \
//                         -o jsonpath='{.spec.template.spec.containers[0].image}'

//                     echo ""
//                 '''
//             }
//         }
//     }

//     post {

//         success {
//             echo 'CI/CD pipeline completed successfully.'
//             echo 'Application deployed to Amazon EKS.'
//         }

//         failure {
//             echo 'CI/CD pipeline failed.'
//             echo 'Check the failed stage and Jenkins console output.'
//         }

//         always {
//             echo "Build Number: ${env.BUILD_NUMBER}"
//             echo "Build Result: ${currentBuild.currentResult}"
//         }
//     }
// }

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

        AI_DIR = '/opt/devsecops-ai/app'
        AI_PYTHON = '/opt/devsecops-ai/venv/bin/python'
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
                sh '.venv/bin/pip install -r requirements.txt'
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
                sh '.venv/bin/pip install pysonar'

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

                    kubectl apply -f k8s/namespace.yml
                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yml

                    kubectl -n "$K8S_NAMESPACE" set image \
                        deployment/"$K8S_DEPLOYMENT" \
                        "$K8S_CONTAINER=$IMAGE_REPO:$BUILD_NUMBER"

                    if ! kubectl -n "$K8S_NAMESPACE" rollout status \
                        deployment/"$K8S_DEPLOYMENT" \
                        --timeout=120s
                    then
                        echo "Rollout failed. Rolling back deployment."

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
                    kubectl -n "$K8S_NAMESPACE" get deployment "$K8S_DEPLOYMENT"
                    kubectl -n "$K8S_NAMESPACE" get pods -o wide
                    kubectl -n "$K8S_NAMESPACE" get service
                '''
            }
        }
    }

    post {

        success {
            echo 'CI/CD pipeline completed successfully.'
            echo 'AI analysis skipped because the build succeeded.'
        }

        failure {
            echo 'CI/CD pipeline failed. Starting AI diagnosis.'

            withCredentials([
                string(credentialsId: 'databricks-token', variable: 'DATABRICKS_TOKEN'),
                string(credentialsId: 'databricks-host', variable: 'DATABRICKS_HOST')
            ]) {
                script {
                    try {
                        sh '''
                            mkdir -p ai/reports

                            set +e

                            echo "Collecting Kubernetes diagnostics..."

                            kubectl -n "$K8S_NAMESPACE" get deployment "$K8S_DEPLOYMENT" \
                                > ai/reports/deployment.txt 2>&1

                            kubectl -n "$K8S_NAMESPACE" get pods -o wide \
                                > ai/reports/pods.txt 2>&1

                            kubectl -n "$K8S_NAMESPACE" get events \
                                --sort-by=.lastTimestamp \
                                > ai/reports/events.txt 2>&1

                            echo "Collecting Jenkins console log..."
                            echo "See Jenkins build console output for full pipeline logs." \
                                > ai/reports/jenkins.log

                            cat > ai/reports/ai_input.json <<'JSON'
{
    "build_number": "BUILD_NUMBER_PLACEHOLDER",
    "build_status": "FAILED",
    "jenkins_logs": "Jenkins pipeline failed. Inspect the failed stage and console output.",
    "trivy_output": "See archived pipeline logs for Trivy scan results.",
    "pip_audit_output": "See archived pipeline logs for pip-audit results.",
    "sonar_output": "See archived pipeline logs for SonarQube results.",
    "deployment_status": "See deployment diagnostics.",
    "pod_status": "See pod diagnostics.",
    "kubernetes_events": "See Kubernetes event diagnostics."
}
JSON

                            sed -i "s/BUILD_NUMBER_PLACEHOLDER/$BUILD_NUMBER/" \
                                ai/reports/ai_input.json

                            cp ai/reports/ai_input.json \
                                /opt/devsecops-ai/ai_input.json

                            chown jenkins:jenkins /opt/devsecops-ai/ai_input.json

                            echo "Running three-agent AI analysis..."

                            cd "$AI_DIR"

                            DATABRICKS_HOST="$DATABRICKS_HOST" \
                            DATABRICKS_TOKEN="$DATABRICKS_TOKEN" \
                            DATABRICKS_ENDPOINT="databricks-llama-4-maverick" \
                            AI_INPUT_FILE="/opt/devsecops-ai/ai_input.json" \
                            AI_REPORT_FILE="$WORKSPACE/ai/reports/ai_report.txt" \
                            PYTHONPATH="$AI_DIR" \
                            "$AI_PYTHON" -m ai.run_ai \
                                > "$WORKSPACE/ai/reports/ai_execution.log" 2>&1

                            AI_EXIT_CODE=$?

                            cat "$WORKSPACE/ai/reports/ai_execution.log"

                            if [ "$AI_EXIT_CODE" -ne 0 ]; then
                                echo "AI diagnosis failed with exit code $AI_EXIT_CODE."
                            fi

                            exit 0
                        '''
                    } catch (Exception error) {
                        echo "AI diagnosis encountered an error: ${error.getMessage()}"
                    }
                }
            }
        }

        always {
            archiveArtifacts(
                artifacts: 'ai/reports/**',
                allowEmptyArchive: true
            )

            echo "Build Number: ${env.BUILD_NUMBER}"
            echo "Build Result: ${currentBuild.currentResult}"
        }
    }
}
