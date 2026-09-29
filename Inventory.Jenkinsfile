
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'amimbaig/inventory-api'
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
                      -v "$WORKSPACE/applications/inventory-api:/app" \
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
                      applications/inventory-api
                '''
            }
        }

        stage('Trivy Image Scan') {
            steps {
                sh '''
                    set -e

                    docker save \
                      -o "$WORKSPACE/inventory-api-image.tar" \
                      ${IMAGE_NAME}:${BUILD_NUMBER}

                    # Generate full HIGH and CRITICAL report
                    docker run --rm \
                      --user "$(id -u):$(id -g)" \
                      -v "$WORKSPACE:/work" \
                      aquasec/trivy:latest \
                      image \
                      --cache-dir /tmp/trivy-cache \
                      --input /work/inventory-api-image.tar \
                      --severity HIGH,CRITICAL \
                      --format json \
                      --output /work/trivy-report.json

                    # Fail only for CRITICAL vulnerabilities
                    docker run --rm \
                      -v "$WORKSPACE:/work" \
                      aquasec/trivy:latest \
                      image \
                      --cache-dir /tmp/trivy-cache \
                      --input /work/inventory-api-image.tar \
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
                    sh 'rm -f "$WORKSPACE/inventory-api-image.tar"'
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
            echo 'Inventory API CI completed successfully!'
        }

        failure {
            echo 'Inventory API CI failed. Check the stage logs.'
        }
    }
}
