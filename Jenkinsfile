pipeline {

    agent any

    environment {

        // ==================================================
        // Application
        // ==================================================

        APP_DIR      = '/home/totoro/Pythonproject/business-analyzer'
        SERVICE_NAME = 'business-analyzer'


        // ==================================================
        // Python
        // ==================================================

        VENV_DIR   = '/home/totoro/Pythonproject/business-analyzer/venv'
        PYTHON_BIN = '/usr/bin/python3'


        // ==================================================
        // Application User
        // ==================================================

        APP_USER  = 'totoro'
        APP_GROUP = 'totoro'


        // ==================================================
        // Streamlit
        // ==================================================

        STREAMLIT_URL = 'http://127.0.0.1:8501'
    }


    stages {


        // ==================================================
        // 1. Checkout
        // ==================================================

        stage('Checkout') {

            steps {

                checkout scm

                echo '===================================='
                echo 'GitHub 소스 체크아웃 완료'
                echo '===================================='
            }
        }


        // ==================================================
        // 2. Deploy Source
        // ==================================================

        stage('Deploy Source') {

            steps {

                sh '''
                    set -e

                    echo "===================================="
                    echo "소스 배포 시작"
                    echo "===================================="


                    # ----------------------------------------
                    # Application Directory
                    # ----------------------------------------

                    sudo mkdir -p "${APP_DIR}"


                    # ----------------------------------------
                    # Source Deploy
                    # ----------------------------------------

                    sudo rsync -av \
                        --delete \
                        --exclude='.git' \
                        --exclude='.env' \
                        --exclude='venv' \
                        --exclude='__pycache__' \
                        --exclude='*.pyc' \
                        ./ \
                        "${APP_DIR}/"


                    echo "소스 복사 완료"


                    # ----------------------------------------
                    # Ownership
                    # ----------------------------------------

                    sudo chown -R \
                        "${APP_USER}:${APP_GROUP}" \
                        "${APP_DIR}"


                    echo "파일 소유권 변경 완료"
                    echo "소스 배포 완료"
                '''
            }
        }


        // ==================================================
        // 3. Python Setup
        // ==================================================

        stage('Python Setup') {

            steps {

                sh '''
                    set -e

                    echo "===================================="
                    echo "Python 환경 설정"
                    echo "===================================="


                    # ----------------------------------------
                    # System Python
                    # ----------------------------------------

                    sudo -u "${APP_USER}" \
                        "${PYTHON_BIN}" \
                        --version


                    # ----------------------------------------
                    # Virtual Environment
                    # ----------------------------------------

                    if [ ! -d "${VENV_DIR}" ]; then

                        echo "venv 생성"

                        sudo -u "${APP_USER}" \
                            "${PYTHON_BIN}" \
                            -m venv \
                            "${VENV_DIR}"

                    else

                        echo "기존 venv 사용"

                    fi


                    # ----------------------------------------
                    # Virtual Environment Python Check
                    # ----------------------------------------

                    sudo -u "${APP_USER}" \
                        "${VENV_DIR}/bin/python" \
                        --version


                    # ----------------------------------------
                    # pip Upgrade
                    #
                    # IMPORTANT:
                    # pip 실행파일 직접 호출하지 않음
                    # python -m pip 사용
                    # ----------------------------------------

                    echo "pip 업그레이드"

                    sudo -u "${APP_USER}" \
                        "${VENV_DIR}/bin/python" \
                        -m pip \
                        install \
                        --upgrade pip


                    # ----------------------------------------
                    # requirements.txt
                    # ----------------------------------------

                    if [ -f "${APP_DIR}/requirements.txt" ]; then

                        echo "requirements.txt 설치"

                        sudo -u "${APP_USER}" \
                            "${VENV_DIR}/bin/python" \
                            -m pip \
                            install \
                            -r "${APP_DIR}/requirements.txt"

                    else

                        echo "WARNING: requirements.txt 없음"

                    fi


                    echo "Python 환경 설정 완료"
                '''
            }
        }


        // ==================================================
        // 4. Test
        // ==================================================

        stage('Test') {

            steps {

                sh '''
                    set -e

                    echo "===================================="
                    echo "Python 문법 검사"
                    echo "===================================="


                    cd "${APP_DIR}"


                    # ----------------------------------------
                    # Python Compile Test
                    # ----------------------------------------

                    sudo -u "${APP_USER}" \
                        "${VENV_DIR}/bin/python" \
                        -m compileall \
                        -q \
                        app.py \
                        src


                    echo "Python 문법 검사 성공"
                '''
            }
        }


        // ==================================================
        // 5. Restart Application
        // ==================================================

        stage('Restart Application') {

            steps {

                sh '''
                    set -e

                    echo "===================================="
                    echo "Application Restart"
                    echo "===================================="


                    # ----------------------------------------
                    # Restart
                    # ----------------------------------------

                    sudo systemctl restart \
                        "${SERVICE_NAME}"


                    echo "서비스 재시작 완료"


                    # ----------------------------------------
                    # Wait
                    # ----------------------------------------

                    sleep 5


                    # ----------------------------------------
                    # Systemd Status
                    # ----------------------------------------

                    sudo systemctl is-active \
                        --quiet \
                        "${SERVICE_NAME}"


                    echo "서비스 상태: ACTIVE"
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

                    echo "===================================="
                    echo "Health Check"
                    echo "===================================="


                    # ----------------------------------------
                    # Streamlit HTTP Check
                    # ----------------------------------------

                    curl \
                        --fail \
                        --silent \
                        --show-error \
                        --max-time 10 \
                        "${STREAMLIT_URL}" \
                        > /dev/null


                    echo "Streamlit 정상 동작"
                    echo "URL: ${STREAMLIT_URL}"


                    # ----------------------------------------
                    # Systemd Check
                    # ----------------------------------------

                    sudo systemctl is-active \
                        --quiet \
                        "${SERVICE_NAME}"


                    echo "Systemd 서비스 정상 동작"
                '''
            }
        }
    }


    // ==================================================
    // Post
    // ==================================================

    post {


        // ==================================================
        // SUCCESS
        // ==================================================

        success {

            echo '''
====================================
       DEPLOY SUCCESS
====================================
Application : business-analyzer
Service     : business-analyzer
Port        : 8501
Status      : 정상
====================================
'''
        }


        // ==================================================
        // FAILURE
        // ==================================================

        failure {

            echo '''
====================================
       DEPLOY FAILED
====================================
Application : business-analyzer
Service     : business-analyzer
====================================
'''


            sh '''
                echo "===== SYSTEMD STATUS ====="

                sudo systemctl status \
                    "${SERVICE_NAME}" \
                    --no-pager \
                    || true


                echo "===== JOURNAL ====="

                sudo journalctl \
                    -u "${SERVICE_NAME}" \
                    -n 100 \
                    --no-pager \
                    || true
            '''
        }


        // ==================================================
        // ALWAYS
        // ==================================================

        always {

            echo 'Jenkins Pipeline 종료'
        }
    }
}
