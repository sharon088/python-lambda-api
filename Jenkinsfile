pipeline {
    agent any
    environment {
        AWS_REGION = 'eu-central-1'
        DOCKER_IMAGE = 'sharon088/python-lambda-api'
        DOCKER_CREDENTIALS_ID = 'DOCKER_HUB'
    }
    stages {
        stage('Install Dependencies') {
            steps {
                script {
                    sh '''
                        apt update -y
                        apt install -y python3-pip pylint jq zip python3-venv docker.io
                        usermod -aG docker jenkins
                    '''
                }
            }
        }

        stage('Identify Changed Lambda Files') {
            steps {
                script {
                    env.CHANGED_LAMBDA_FILES = sh(
                        script: 'git diff --name-only HEAD~1 HEAD | grep "^lambda-functions/" | grep ".py$"',
                        returnStdout: true
                    ).trim()
                    if (!env.CHANGED_LAMBDA_FILES) {
                        echo "No Lambda files changed."
                        currentBuild.result = 'SUCCESS'
                        return
                    }
                    echo "Changed Lambda files: ${env.CHANGED_LAMBDA_FILES}"
                }
            }
        }
        
        stage('Run Pylint on Lambda Functions') {
            when {
                expression { env.CHANGED_LAMBDA_FILES }
            }
            steps {
                script {
                    sh "pylint --fail-under=5 ${env.CHANGED_LAMBDA_FILES}"
                }
            }
        }

        stage('Install AWS CLI') {
            steps {
                    script {
                        def awsCliInstalled = sh(script: 'which aws || true', returnStdout: true).trim()
                        if (!awsCliInstalled) {
                            echo "AWS CLI not found. Installing..."
                            sh '''
                                curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                                unzip -o awscliv2.zip
                                ./aws/install
                            '''
                        } else {
                            echo "AWS CLI is already installed. Updating..."
                            sh '''
                                curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                                unzip -o awscliv2.zip
                                ./aws/install --update
                            '''
                        }
                    }
            }
        }

        stage('Test Lambda Functions') {
            when {
                expression { env.CHANGED_LAMBDA_FILES }
            }
            steps {
                script {
                    def lambdas = [
                        'backup': 'lambda-functions/backup/test_event.json',
                        'create_user': 'lambda-functions/create_user/test_event.json',
                        'csv_to_excel': 'lambda-functions/csv_to_excel/test_event.json',
                        'get_info': 'lambda-functions/get_info/test_event.json',
                        'new_project': 'lambda-functions/new_project/test_event.json',
                        'send_whatsapp': 'lambda-functions/send_whatsapp/test_event.json'
                    ]
                    def changedLambdas = lambdas.findAll { lambdaName, _ ->
                        env.CHANGED_LAMBDA_FILES.contains("lambda-functions/${lambdaName}.py")
                    }
                    def parallelTests = [:]
                    changedLambdas.each { lambdaName, eventFile ->
                        parallelTests["Test ${lambdaName}"] = {
                            withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY', credentialsId: 'aws-credentials']]) {
                                sh """
                                    aws lambda invoke \
                                    --cli-binary-format raw-in-base64-out \
                                    --function-name ${lambdaName} \
                                    --payload file://${eventFile} \
                                    output-${lambdaName}.txt
                                """
                                def output = readFile("output-${lambdaName}.txt")
                                echo "Lambda function ${lambdaName} output: ${output}"
                                assert output.contains('"statusCode": 200'), "Test failed for ${lambdaName}"
                            }
                        }
                    }
                    parallel parallelTests
                }
            }
        }

        stage('Deploy Lambda Functions') {
            when {
                    expression { env.CHANGED_LAMBDA_FILES }
            }
            steps {
                script {
                    def lambdaFiles = env.CHANGED_LAMBDA_FILES.split('\n')
                    lambdaFiles.each { file ->
                        def functionName = file.replace('lambda-functions/', '').replace('.py', '').split('/')[0]
                        echo "Deploying ${functionName} to AWS Lambda"
                        sh "mkdir -p /tmp/${functionName}"
                        sh "cp ${file} /tmp/${functionName}/"
                        if (fileExists("lambda-functions/${functionName}/requirements.txt")) {
                            echo "Installing dependencies for ${functionName} from requirements.txt"
                            sh """
                                python3 -m venv /tmp/${functionName}/venv
                                . /tmp/${functionName}/venv/bin/activate
                                pip install -r lambda-functions/${functionName}/requirements.txt
                            """
                            sh "cp -r /tmp/${functionName}/venv/lib/python3.*/site-packages/* /tmp/${functionName}/"
                        }
                        sh "find /tmp/${functionName} -name '*.json' -exec rm -f {} \\;"
                        sh "cd /tmp/${functionName} && zip -r /tmp/${functionName}.zip ."
                        
                        def s3Bucket = "tasty-kfc-bucket"
                def s3Key = "lambda-deployment/${functionName}.zip"
                echo "Uploading ${functionName} to S3"
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY', credentialsId: 'aws-credentials']]) {
                            sh "aws s3 cp /tmp/${functionName}.zip s3://${s3Bucket}/${s3Key}"
                        }
                        
                        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY', credentialsId: 'aws-credentials']]) {
                            sh """
                                aws lambda update-function-code \
                                --function-name ${functionName} \
                                --s3-bucket ${s3Bucket} \
                    --s3-key ${s3Key} \
                                --region ${AWS_REGION}
                            """
                        }
                    }
                }
            }
        }
        
        stage('Run Pylint on Website') {
            steps {
                script {
                    sh 'pylint --fail-under=5 website/app.py'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${env.DOCKER_IMAGE}", "-f ./website/Dockerfile ./website")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', env.DOCKER_CREDENTIALS_ID) {
                        def image = docker.image("${env.DOCKER_IMAGE}")
                        image.push('latest')
                        image.push("${env.BUILD_NUMBER}")
                    }
                }
            }
        }
    }
}
