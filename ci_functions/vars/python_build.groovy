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
            stage ("Cleanup") {
                steps {
                    sh "docker rmi akinofu/${dockerRepoName}:latest"
                }
            }
            // stage('Zip Artifacts') { 
            //     steps { 
            //         sh 'zip app.zip *.py' 
            //     }
            //     post {
            //         always {
            //             archiveArtifacts artifacts: 'app.zip', onlyIfSuccessful: true
            //             //test
            //         }
            //     }
            // }
            stage('Deploy') {
                when {
                    expression {params.DEPLOY}
                }
                steps {
                    sshagent(credentials: ['akino-vm-key']) {
                        sh "ssh -o StrictHostKeyChecking=no azureuser@acit3855-household-account-app.eastus.cloudapp.azure.com 'cd ~/acit3855-lab/deployment && docker-compose stop ${dockerRepoName}'"
                        sh "ssh -o StrictHostKeyChecking=no azureuser@acit3855-household-account-app.eastus.cloudapp.azure.com 'docker rmi ${dockerRepoName}'"
                        sh "ssh -o StrictHostKeyChecking=no azureuser@acit3855-household-account-app.eastus.cloudapp.azure.com 'cd ~/acit3855-lab/deployment && docker-compose up -d'"
                    }
                }
            }

        } 
    }

}
