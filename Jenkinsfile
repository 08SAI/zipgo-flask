pipeline {
  agent any

  environment {
    IMAGE_TAG = "zipgo-svc:4"
    CONTAINER_NAME = "zipgo-svc-4"
    HOST_PORT = "12184"
    CONTAINER_PORT = "12184"
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
          if (isUnix()) {
            // Unix/WSL: check docker CLI and daemon
            if (sh(returnStatus: true, script: 'command -v docker >/dev/null 2>&1') != 0) {
              error("Docker CLI not found on this agent (is docker installed / on PATH?).")
            }
            if (sh(returnStatus: true, script: 'docker info >/dev/null 2>&1') != 0) {
              error("Docker daemon not responding on this agent (docker info failed).")
            }
          } else {
            // Windows agent: try docker directly; if that fails, try bash (Git-for-Windows) as fallback
            def direct = bat(returnStatus: true, script: 'docker --version >nul 2>&1')
            if (direct == 0) {
              def infoStatus = bat(returnStatus: true, script: 'docker info >nul 2>&1')
              if (infoStatus != 0) {
                error("Docker daemon not responding on Windows agent (docker info failed).")
              }
            } else {
              // try Git-for-Windows bash which may provide docker in some setups or WSL integration
              def bashTry = bat(returnStatus: true, script: 'bash -lc "command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1"')
              if (bashTry != 0) {
                error("Docker not available on this Windows agent. Tried 'docker' and 'bash -lc docker'.")
              }
            }
          }
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          if (isUnix()) {
            sh "docker build -t ${IMAGE_TAG} ."
          } else {
            bat "docker build -t %IMAGE_TAG% ."
          }
        }
      }
    }

    stage('Stop previous container (if any)') {
      steps {
        script {
          if (isUnix()) {
            sh "docker rm -f ${CONTAINER_NAME} >/dev/null 2>&1 || true"
          } else {
            bat 'docker rm -f %CONTAINER_NAME% >nul 2>&1 || exit 0'
          }
        }
      }
    }

    stage('Run container') {
      steps {
        script {
          if (isUnix()) {
            sh "docker run -d --name ${CONTAINER_NAME} -p ${HOST_PORT}:${CONTAINER_PORT} ${IMAGE_TAG}"
          } else {
            bat 'docker run -d --name %CONTAINER_NAME% -p %HOST_PORT%:%CONTAINER_PORT% %IMAGE_TAG%'
          }
        }
      }
    }

    stage('Smoke test') {
      steps {
        script {
          if (isUnix()) {
            sh '''
              sleep 2
              curl -sS --max-time 5 http://localhost:${HOST_PORT}/ || (echo "SMOKE_FAIL" && exit 2)
            '''
          } else {
            bat '''
              timeout /t 2 /nobreak >nul
              curl -sS --max-time 5 http://localhost:%HOST_PORT% || (echo SMOKE_FAIL & exit /b 2)
            '''
          }
        }
      }
    }
  }

  post {
    success {
      script {
        echo "SUCCESS: ${env.IMAGE_TAG} running on port ${env.HOST_PORT}"
      }
    }
    failure {
      script {
        echo "FAILED - check prior logs for errors"
      }
    }
    always {
      script {
        // optional: print container listing for debugging evidence
        if (isUnix()) {
          sh 'docker ps --filter name=${CONTAINER_NAME} --format "table {{.ID}}\\t{{.Names}}\\t{{.Ports}}" || true'
        } else {
          bat 'docker ps --filter name=%CONTAINER_NAME% --format "table {{.ID}}\\t{{.Names}}\\t{{.Ports}}" || exit 0'
        }
      }
    }
  }
}
