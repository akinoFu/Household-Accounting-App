def call(directoryName, dockerRepoName) {
    pipeline { 
        agent any
        parameters {
          booleanParam(defaultValue: false, description: 'Deploy the App', name: 'DEPLOY')
        }

        stages { 
            stage('Build') { 
                steps {
                    sh "pip install -r ${directoryName}/requirements.txt"
                } 
            }
            stage('Lint') { 
                steps { 
                    sh "pylint-fail-under --fail_under 5.0 ${directoryName}/*.py"
                } 
            }
            stage('Package') { 
                when { 
                    expression { env.GIT_BRANCH == 'main' } 
                } 
                steps { 
                    withCredentials([string(credentialsId: 'akino_dockerhub', variable: 'TOKEN')]) { 
                        sh "docker login -u 'akinofu' -p '$TOKEN' docker.io" 
                        sh "docker build --tag akinofu/${dockerRepoName}:latest ${directoryName}" 
                        sh "docker push akinofu/${dockerRepoName}:latest" 
                    } 
                } 
            }
            // stage ("CheckDIGEST") {
            //     steps {
            //         sh "docker image inspect -f '{{ .RepoDigests }}' akinofu/${dockerRepoName}:latest"
            //         // sh "docker rmi akinofu/${dockerRepoName}:latest"
            //     }
            // }
            stage('Deploy') {
                when {
                    expression {params.DEPLOY}
                }
                environment {
                    DOCKER_PASS = credentials('akino_dockerhub')
                    SSH_CMD = "ssh -o StrictHostKeyChecking=no azureuser@acit3855-household-account-app.eastus.cloudapp.azure.com"
                }
                steps {
                    sshagent(credentials: ['akino-vm-key']) 
                        sh "${SSH_CMD} 'cd ~/acit3855-lab/deployment && \
                                        docker-compose stop ${dockerRepoName} && \
                                        docker-compose rm -f ${dockerRepoName}'"
                        sh "${SSH_CMD} 'docker rmi -f akinofu/${dockerRepoName}'"
                        sh "${SSH_CMD} 'docker login -u akinofu -p $DOCKER_PASS docker.io && \
                                        cd ~/acit3855-lab/deployment && \
                                        docker-compose up -d'"
                    }
                }
            }

        } 
    }

}
