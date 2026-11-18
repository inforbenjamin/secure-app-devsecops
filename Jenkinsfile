// Pipeline DevSecOps - SecureDev
// Etapas: Build -> Test -> Analyze (SonarQube) -> Dependencias -> Deploy -> Security Test (ZAP)
pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 60, unit: 'MINUTES')
    }

    environment {
        IMAGE   = 'secure-app'
        APP_URL = 'http://app:5000/hello?name=test'   // URL interna (red docker "devsecops")
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                // Construye la imagen final de la aplicacion
                sh 'docker build --target final -t $IMAGE:$BUILD_NUMBER -t $IMAGE:latest .'
            }
        }

        stage('Test') {
            steps {
                // La etapa "test" del Dockerfile ejecuta pytest; si falla, falla el pipeline
                sh 'docker build --target test -t $IMAGE-test:$BUILD_NUMBER .'
            }
        }

        stage('Analyze - SonarQube (SAST)') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    script {
                        def scannerHome = tool 'SonarScanner'
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Security Test - Dependencias') {
            steps {
                // 1) pip-audit: rapido, consulta vulnerabilidades conocidas de requirements.txt
                sh '''
                    pip-audit -r requirements.txt > pip-audit-report.txt 2>&1 || true
                    cat pip-audit-report.txt
                '''
                // 2) OWASP Dependency-Check (plugin de Jenkins)
                //    Para acelerar la descarga de la base NVD, crea una API key gratis y
                //    agrega:  --nvdApiKey TU_KEY   dentro de additionalArguments
                dependencyCheck additionalArguments: '--scan . --format HTML --format XML --prettyPrint',
                                odcInstallation: 'dependency-check'
                dependencyCheckPublisher pattern: 'dependency-check-report.xml'
            }
        }

        stage('Deploy (entorno de prueba)') {
            steps {
                sh '''
                    docker rm -f app || true
                    docker run -d --name app --network devsecops -p 5001:5000 $IMAGE:latest
                    sleep 8
                    docker ps --filter name=app
                '''
            }
        }

        stage('Security Test - OWASP ZAP (DAST)') {
            steps {
                sh '''
                    docker rm -f zap || true
                    docker run --name zap --network devsecops ghcr.io/zaproxy/zaproxy:stable \
                        sh -c "mkdir -p /zap/wrk && zap-full-scan.py -t $APP_URL -m 2 -r zap-report.html -I" || true
                    docker cp zap:/zap/wrk/zap-report.html ./zap-report.html || true
                    docker rm -f zap || true
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'zap-report.html, pip-audit-report.txt, dependency-check-report.*', allowEmptyArchive: true
        }
        success { echo 'Pipeline completado correctamente.' }
        failure { echo 'El pipeline fallo: revisar el log de la etapa en rojo.' }
    }
}
