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
        success { echo 'Pipeline completado correctamente.' }
        failure { echo 'El pipeline fallo: revisar el log de la etapa en rojo.' }
    }
}