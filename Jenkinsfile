
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'amimbaig/order-api'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh '''
                    set -e

                    docker run --rm \
                      -v "$WORKSPACE/applications/order-api:/app" \
                      -w /app \
                      python:3.12-slim \
                      sh -c "pip install --no-cache-dir -r requirements.txt && python -m pytest tests/ -v"
                '''
            }
        }

        stage('Build Image') {
            steps {
                sh '''
                    set -e

                    docker build \
                      -t ${IMAGE_NAME}:${BUILD_NUMBER} \
                      -t ${IMAGE_NAME}:latest \
                      applications/order-api
                '''
            }
        }

        stage('Trivy Image Scan') {
            steps {
                sh '''
                    set -e

                    docker save \
                      -o "$WORKSPACE/order-api-image.tar" \
                      ${IMAGE_NAME}:${BUILD_NUMBER}

                    # Generate full HIGH and CRITICAL report
                    docker run --rm \
                      --user "$(id -u):$(id -g)" \
                      -v "$WORKSPACE:/work" \
                      aquasec/trivy:latest \
                      image \
                      --cache-dir /tmp/trivy-cache \
                      --input /work/order-api-image.tar \
                      --severity HIGH,CRITICAL \
                      --format json \
                      --output /work/trivy-report.json

                    # Fail only for CRITICAL vulnerabilities
                    docker run --rm \
                      -v "$WORKSPACE:/work" \
                      aquasec/trivy:latest \
                      image \
                      --cache-dir /tmp/trivy-cache \
                      --input /work/order-api-image.tar \
                      --severity CRITICAL \
                      --exit-code 1 \
                      --format table
                '''

                archiveArtifacts(
                    artifacts: 'trivy-report.json',
                    fingerprint: true
                )
            }

            post {
                always {
                    sh 'rm -f "$WORKSPACE/order-api-image.tar"'
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x

                        echo "$DOCKERHUB_TOKEN" | docker login \
                          --username "$DOCKERHUB_USER" \
                          --password-stdin

                        docker push ${IMAGE_NAME}:${BUILD_NUMBER}
                        docker push ${IMAGE_NAME}:latest

                        docker logout
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Order API CI completed successfully!'
        }

        failure {
            echo 'Order API CI failed. Check the stage logs.'
        }
    }
}
