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
                    mkdir -p ai/reports

                    set +e
                    python3.13 -m venv .venv \
                        > ai/reports/setup.log 2>&1
                    RESULT=$?

                    .venv/bin/python --version \
                        >> ai/reports/setup.log 2>&1
                    .venv/bin/pip install --upgrade pip \
                        >> ai/reports/setup.log 2>&1

                    cat ai/reports/setup.log
                    exit "$RESULT"
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    set +e

                    .venv/bin/pip install -r requirements.txt \
                        > ai/reports/dependencies.log 2>&1

                    RESULT=$?
                    cat ai/reports/dependencies.log
                    exit "$RESULT"
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    set +e

                    .venv/bin/pytest \
                        --cov=app \
                        --cov-report=term-missing \
                        --cov-fail-under=80 \
                        > ai/reports/pytest.log 2>&1

                    RESULT=$?
                    cat ai/reports/pytest.log
                    exit "$RESULT"
                '''
            }
        }

        stage('Dependency Security Scan') {
            steps {
                sh '''
                    set +e

                    .venv/bin/pip install pip-audit \
                        > ai/reports/pip_audit.log 2>&1

                    INSTALL_RESULT=$?

                    if [ "$INSTALL_RESULT" -eq 0 ]; then
                        .venv/bin/pip-audit -r requirements.txt \
                            >> ai/reports/pip_audit.log 2>&1
                        RESULT=$?
                    else
                        RESULT=$INSTALL_RESULT
                    fi

                    cat ai/reports/pip_audit.log
                    exit "$RESULT"
                '''
            }
        }

        stage('Trivy FS Scan') {
            steps {
                sh '''
                    set +e

                    trivy fs \
                        --exit-code 1 \
                        --severity HIGH,CRITICAL \
                        . > ai/reports/trivy_fs.log 2>&1

                    RESULT=$?
                    cat ai/reports/trivy_fs.log
                    exit "$RESULT"
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                sh '''
                    set +e

                    .venv/bin/pip install pysonar \
                        > ai/reports/sonar.log 2>&1

                    RESULT=$?
                    cat ai/reports/sonar.log
                    exit "$RESULT"
                '''

                withCredentials([
                    string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')
                ]) {
                    sh '''
                        set +e

                        .venv/bin/pysonar \
                            --sonar-host-url=http://localhost:9000 \
                            --sonar-token="$SONAR_TOKEN" \
                            --sonar-project-key=AI-DevSecOps-Platform \
                            >> ai/reports/sonar.log 2>&1

                        RESULT=$?
                        cat ai/reports/sonar.log
                        exit "$RESULT"
                    '''
                }
            }
        }

        stage('ECR Login') {
            steps {
                sh '''
                    set +e

                    aws ecr get-login-password \
                        --region "$AWS_REGION" | \
                    docker login \
                        --username AWS \
                        --password-stdin "$ECR_REGISTRY" \
                        > ai/reports/ecr_login.log 2>&1

                    RESULT=$?
                    cat ai/reports/ecr_login.log
                    exit "$RESULT"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set +e
                    export DOCKER_BUILDKIT=0

                    docker build \
                        --platform linux/amd64 \
                        -t "$IMAGE_REPO:$BUILD_NUMBER" \
                        -t "$IMAGE_REPO:latest" \
                        . > ai/reports/docker_build.log 2>&1

                    RESULT=$?
                    cat ai/reports/docker_build.log
                    exit "$RESULT"
                '''
            }
        }

        stage('Trivy Image Scan') {
            steps {
                sh '''
                    set +e

                    trivy image \
                        --exit-code 1 \
                        --severity CRITICAL \
                        "$IMAGE_REPO:$BUILD_NUMBER" \
                        > ai/reports/trivy_image.log 2>&1

                    RESULT=$?
                    cat ai/reports/trivy_image.log
                    exit "$RESULT"
                '''
            }
        }

        stage('Push to ECR') {
            steps {
                sh '''
                    set +e

                    docker push "$IMAGE_REPO:$BUILD_NUMBER" \
                        > ai/reports/ecr_push.log 2>&1
                    RESULT=$?

                    if [ "$RESULT" -eq 0 ]; then
                        docker push "$IMAGE_REPO:latest" \
                            >> ai/reports/ecr_push.log 2>&1
                        RESULT=$?
                    fi

                    cat ai/reports/ecr_push.log
                    exit "$RESULT"
                '''
            }
        }

        stage('Deploy to EKS') {
            steps {
                sh '''
                    set +e

                    {
                        echo "Deploying image: $IMAGE_REPO:$BUILD_NUMBER"

                        kubectl apply -f k8s/namespace.yml
                        RESULT=$?

                        if [ "$RESULT" -eq 0 ]; then
                            kubectl apply -f k8s/deployment.yaml
                            RESULT=$?
                        fi

                        if [ "$RESULT" -eq 0 ]; then
                            kubectl apply -f k8s/service.yml
                            RESULT=$?
                        fi

                        if [ "$RESULT" -eq 0 ]; then
                            kubectl -n "$K8S_NAMESPACE" set image \
                                deployment/"$K8S_DEPLOYMENT" \
                                "$K8S_CONTAINER=$IMAGE_REPO:$BUILD_NUMBER"
                            RESULT=$?
                        fi

                        if [ "$RESULT" -eq 0 ]; then
                            echo "Waiting for rollout..."

                            kubectl -n "$K8S_NAMESPACE" rollout status \
                                deployment/"$K8S_DEPLOYMENT" \
                                --timeout=120s
                            RESULT=$?
                        fi

                        if [ "$RESULT" -ne 0 ]; then
                            echo "Deployment or rollout failed."
                            echo "Attempting rollback..."

                            kubectl -n "$K8S_NAMESPACE" rollout undo \
                                deployment/"$K8S_DEPLOYMENT"

                            kubectl -n "$K8S_NAMESPACE" rollout status \
                                deployment/"$K8S_DEPLOYMENT" \
                                --timeout=120s || true

                            exit 1
                        fi

                        echo "Rollout completed successfully."
                    } > ai/reports/deployment.log 2>&1

                    RESULT=$?
                    cat ai/reports/deployment.log
                    exit "$RESULT"
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    set +e

                    {
                        echo "Deployment status:"
                        kubectl -n "$K8S_NAMESPACE" get deployment "$K8S_DEPLOYMENT"

                        echo "Pods:"
                        kubectl -n "$K8S_NAMESPACE" get pods -o wide

                        echo "Service:"
                        kubectl -n "$K8S_NAMESPACE" get service

                        echo "Application image:"
                        kubectl -n "$K8S_NAMESPACE" get deployment "$K8S_DEPLOYMENT" \
                            -o jsonpath='{.spec.template.spec.containers[0].image}'
                        echo ""
                    } > ai/reports/kubernetes_verify.log 2>&1

                    RESULT=$?
                    cat ai/reports/kubernetes_verify.log
                    exit "$RESULT"
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

            script {
                try {
                    withCredentials([
                        string(credentialsId: 'databricks-token', variable: 'DATABRICKS_TOKEN'),
                        string(credentialsId: 'databricks-host', variable: 'DATABRICKS_HOST')
                    ]) {
                        sh '''
                            set +e

                            mkdir -p "$WORKSPACE/ai/reports"

                            echo "Collecting Kubernetes diagnostics..."

                            kubectl -n "$K8S_NAMESPACE" get deployment "$K8S_DEPLOYMENT" \
                                > "$WORKSPACE/ai/reports/deployment_status.txt" 2>&1

                            kubectl -n "$K8S_NAMESPACE" get pods -o wide \
                                > "$WORKSPACE/ai/reports/pods.txt" 2>&1

                            kubectl -n "$K8S_NAMESPACE" get events \
                                --sort-by=.lastTimestamp \
                                > "$WORKSPACE/ai/reports/events.txt" 2>&1

                            echo "Updating AI application files..."

                            mkdir -p "$AI_DIR/ai"

                            cp -a "$WORKSPACE/ai/." "$AI_DIR/ai/"

                            echo "Preparing actual pipeline diagnostics..."

                            "$AI_PYTHON" - <<'PY'
import json
import os
from pathlib import Path

reports = Path(os.environ["WORKSPACE"]) / "ai" / "reports"

def read_report(filename):
    path = reports / filename
    if path.is_file():
        return path.read_text(encoding="utf-8", errors="replace")
    return f"{filename}: Not available. The stage may not have executed."

def combine(*filenames):
    return "\\n\\n".join(
        f"===== {filename} =====\\n{read_report(filename)}"
        for filename in filenames
    )

data = {
    "build_number": os.environ["BUILD_NUMBER"],
    "build_status": "FAILED",
    "jenkins_logs": combine(
        "setup.log",
        "dependencies.log",
        "pytest.log",
        "deployment.log",
        "kubernetes_verify.log"
    ),
    "trivy_output": combine(
        "trivy_fs.log",
        "trivy_image.log"
    ),
    "pip_audit_output": read_report("pip_audit.log"),
    "sonar_output": read_report("sonar.log"),
    "deployment_status": combine(
        "deployment.log",
        "deployment_status.txt"
    ),
    "pod_status": read_report("pods.txt"),
    "kubernetes_events": read_report("events.txt")
}

output = reports / "ai_input.json"
output.write_text(json.dumps(data, indent=2), encoding="utf-8")
print(f"AI input created: {output}")
PY

                            echo "Running three-agent AI analysis..."

                            cd "$AI_DIR"

                            export PYTHONPATH="$AI_DIR"
                            export DATABRICKS_HOST
                            export DATABRICKS_TOKEN
                            export DATABRICKS_ENDPOINT="databricks-llama-4-maverick"
                            export AI_INPUT_FILE="$WORKSPACE/ai/reports/ai_input.json"
                            export AI_REPORT_FILE="$WORKSPACE/ai/reports/ai_report.txt"

                            "$AI_PYTHON" -m ai.run_ai \
                                > "$WORKSPACE/ai/reports/ai_execution.log" 2>&1

                            AI_EXIT_CODE=$?

                            cat "$WORKSPACE/ai/reports/ai_execution.log"

                            if [ "$AI_EXIT_CODE" -ne 0 ]; then
                                echo "AI analysis failed with exit code $AI_EXIT_CODE."
                            else
                                echo "AI analysis completed."
                            fi

                            exit 0
                        '''
                    }
                } catch (Exception error) {
                    echo "AI diagnosis encountered an error: ${error.getMessage()}"
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
