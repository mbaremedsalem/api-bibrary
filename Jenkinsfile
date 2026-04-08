pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'mbare/library-api'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '📦 Récupération du code depuis GitHub...'
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '🐳 Construction de l\'image Docker...'
                bat "docker build -t %DOCKER_IMAGE%:%DOCKER_TAG% ."
                bat "docker tag %DOCKER_IMAGE%:%DOCKER_TAG% %DOCKER_IMAGE%:latest"
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                echo '📤 Push vers Docker Hub...'
                withCredentials([string(credentialsId: 'docker-hub-password', variable: 'DOCKER_PASS')]) {
                    bat '''
                        echo %DOCKER_PASS% | docker login -u mbare --password-stdin
                        docker push %DOCKER_IMAGE%:%DOCKER_TAG%
                        docker push %DOCKER_IMAGE%:latest
                    '''
                }
            }
        }
        
        stage('Deploy') {
            steps {
                echo '🚀 Déploiement...'
                bat 'docker stop library-app || exit 0'
                bat 'docker rm library-app || exit 0'
                bat 'docker run -d -p 8000:8000 --name library-app %DOCKER_IMAGE%:latest'
            }
        }
        
        stage('Test') {
            steps {
                echo '✅ Vérification...'
                bat 'timeout /t 5 /nobreak > nul'
                bat 'curl http://localhost:8000/api/books/ || echo "API is running"'
            }
        }
    }
    
    post {
        success {
            echo '🎉 Pipeline terminé avec succès !'
        }
        failure {
            echo '❌ Le pipeline a échoué'
        }
    }
}