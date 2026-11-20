pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        IMAGE = 'secure-app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build - Construccion') {
            steps {
                sh 'docker build --target final -t $IMAGE:$BUILD_NUMBER -t $IMAGE:latest .'
            }
        }

        stage('Test - Pruebas') {
            steps {
                sh 'docker build --target test -t $IMAGE-test:$BUILD_NUMBER .'
            }
        }

        stage('Analyze - SonarQube') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    script {
                        def scannerHome = tool 'SonarScanner'
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Dependencias - pip-audit') {
            steps {
                sh '''
                    pip-audit -r requirements.txt > pip-audit-report.txt 2>&1 || true
                    cat pip-audit-report.txt
                '''
            }
        }

        stage('Deploy - Despliegue') {
            steps {
                sh '''
                    docker rm -f app || true
                    docker run -d --name app --network devsecops -p 5001:5000 $IMAGE:latest
                    sleep 5
                    docker ps --filter name=app
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'pip-audit-report.txt', allowEmptyArchive: true
        }
        success { echo 'Pipeline completado correctamente.' }
        failure { echo 'El pipeline fallo: revisar el log de la etapa en rojo.' }
    }
}