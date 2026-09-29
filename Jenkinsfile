pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Source code checked out successfully.'
            }
        }

        stage('Install Dependencies') {
            steps {
                dir('applications/order-api') {
                    sh '''
                        python3 -m venv .venv
                        .venv/bin/pip install --upgrade pip
                        .venv/bin/pip install -r requirements.txt
                        .venv/bin/pip install pytest
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                dir('applications/order-api') {
                    sh '.venv/bin/python -m pytest tests/ -v'
                }
            }
        }
    }

    post {
        success {
            echo 'Order API CI pipeline completed successfully!'
        }
        failure {
            echo 'Order API CI pipeline failed. Check the console output.'
        }
        always {
            cleanWs()
        }
    }
}
