pipeline {
  agent any

  environment {
    IMAGE = "zipgo-svc:4"
    CONTAINER_NAME = "zipgo-svc-4"
    PORT = "12184"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Pre-check Docker') {
      steps {
        script {
          // run docker version and fail clearly if not available
          def rc = sh(script: "docker info > /dev/null 2>&1 || echo NO_DOCKER", returnStdout: true).trim()
          if (rc == "NO_DOCKER") {
            error("Docker is not available on this agent. Ensure Docker daemon is installed and user running Jenkins has permission to use Docker.")
          }
          // also print docker version for visibility
          sh "docker --version"
          sh "docker info --format '{{ json .ServerVersion }}' || true"
        }
      }
    }

    stage('Build image') {
      steps {
        sh """
          docker build -t ${IMAGE} .
        """
      }
    }

    stage('Stop previous container (if any)') {
      steps {
        script {
          sh """
            if docker ps -a --format '{{.Names}}' | grep -q '^${CONTAINER_NAME}$' ; then
              echo 'Stopping and removing existing container ${CONTAINER_NAME}'
              docker rm -f ${CONTAINER_NAME} || true
            else
              echo 'No existing container ${CONTAINER_NAME} found.'
            fi
          """
        }
      }
    }

    stage('Run container') {
      steps {
        sh """
          docker run -d --name ${CONTAINER_NAME} -p ${PORT}:12184 --restart unless-stopped ${IMAGE}
        """
      }
    }

    stage('Smoke test') {
      steps {
        // Wait a moment for server to come up, then curl
        sh """
          echo 'Waiting for service to start...'
          for i in 1 2 3 4 5; do
            sleep 1
            if curl -s --max-time 2 http://127.0.0.1:${PORT}/ | grep -q 'ZipGo'; then
              echo 'Smoke test passed'
              exit 0
            fi
            echo 'Attempt ' $i ' - not up yet'
          done
          echo 'Service failed to respond on port ${PORT}'
          docker logs ${CONTAINER_NAME} || true
          exit 1
        """
      }
    }
  }

  post {
    failure {
      echo "Pipeline failed — gather container state and logs:"
      sh "docker ps -a || true"
      sh "docker images | grep zipgo-svc || true"
      sh "docker logs ${CONTAINER_NAME} || true"
    }
    success {
      echo "Pipeline completed successfully and container ${CONTAINER_NAME} is running on port ${PORT}"
      sh "docker ps --filter name=${CONTAINER_NAME} --format 'table {{.ID}}\\t{{.Names}}\\t{{.Ports}}'"
    }
  }
}
