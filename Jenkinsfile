pipeline {

    agent any

    environment {

        APP_DIR = '/home/totoro/Pythonproject/business-analyzer'
        SERVICE_NAME = 'business-analyzer'

        VENV_DIR = '/home/totoro/Pythonproject/business-analyzer/venv'
    }


    stages {

        // ==================================================
        // 1. Checkout
        // ==================================================

        stage('Checkout') {

            steps {

                checkout scm

                echo 'GitHub 소스 체크아웃 완료'
            }
        }


        // ==================================================
        // 2. Python 환경
        // ==================================================

        stage('Python Setup') {

            steps {

                sh '''
                    set -e

                    python3 --version

                    if [ ! -d "${VENV_DIR}" ]; then
                        python3 -m venv "${VENV_DIR}"
                    fi

                    "${VENV_DIR}/bin/pip" install --upgrade pip

                    "${VENV_DIR}/bin/pip" install \
                        -r requirements.txt
                '''
            }
        }


        // ==================================================
        // 3. 테스트
        // ==================================================

        stage('Test') {

            steps {

                sh '''
                    set -e

                    "${VENV_DIR}/bin/python" \
                        -m compileall \
                        -q \
                        app.py \
                        src
                '''
            }
        }


        // ==================================================
        // 4. Deploy
        // ==================================================

        stage('Deploy') {

            steps {

                sh '''
                    set -e

                    echo "===== Deploy ====="

                    rsync -av \
                        --delete \
                        --exclude='.git' \
                        --exclude='.env' \
                        --exclude='venv' \
                        ./ \
                        "${APP_DIR}/"

                    echo "소스 배포 완료"
                '''
            }
        }


        // ==================================================
        // 5. Restart
        // ==================================================

        stage('Restart Application') {

            steps {

                sh '''
                    set -e

                    sudo systemctl restart \
                        "${SERVICE_NAME}"

                    sleep 5

                    sudo systemctl status \
                        "${SERVICE_NAME}" \
                        --no-pager
                '''
            }
        }


        // ==================================================
        // 6. Health Check
        // ==================================================

        stage('Health Check') {

            steps {

                sh '''
                    set -e

                    curl \
                        --fail \
                        --silent \
                        --show-error \
                        http://127.0.0.1:8501 \
                        > /dev/null

                    echo "Streamlit 정상 동작"
                '''
            }
        }
    }


    post {

        success {

            echo '===================================='
            echo '배포 성공'
            echo '===================================='
        }

        failure {

            echo '===================================='
            echo '배포 실패'
            echo '===================================='

            sh '''
                sudo journalctl \
                    -u business-analyzer \
                    -n 50 \
                    --no-pager || true
            '''
        }
    }
}