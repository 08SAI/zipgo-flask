pipeline {
  agent any
  environment {
    IMAGE_TAG = "zipgo-svc:4"
    CONTAINER_NAME = "zipgo-svc-4"
    HOST_PORT = "12184"
    CONTAINER_PORT = "12184"
  }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Pre-check Docker') {
      steps {
        script {
          def rc = sh(returnStatus: true, script: 'docker --version >/dev/null 2>&1 || echo MISSING')
          if (rc != 0) { error("Docker is not available on this agent (docker --version failed).") }
          def infoStatus = sh(returnStatus: true, script: 'docker info >/dev/null 2>&1 || echo DAEMON_DOWN')
          if (infoStatus != 0) { error("Docker daemon not responding (docker info failed).") }
        }
      }
    }
    stage('Build Docker Image') { steps { sh "docker build -t ${IMAGE_TAG} ." } }
    stage('Stop previous container (if any)') { steps { sh "docker rm -f ${CONTAINER_NAME} >/dev/null 2>&1 || true" } }
    stage('Run container') { steps { sh "docker run -d --name ${CONTAINER_NAME} -p ${HOST_PORT}:${CONTAINER_PORT} ${IMAGE_TAG}" } }
    stage('Smoke test') {
      steps {
        sh '''
          sleep 2
          curl -sS --max-time 5 http://localhost:${HOST_PORT}/ || (echo "SMOKE_FAIL" && exit 2)
        '''
      }
    }
  }
  post { success { echo "SUCCESS: ${IMAGE_TAG} running on port ${HOST_PORT}" } failure { echo "FAILED - see above" } }
}
