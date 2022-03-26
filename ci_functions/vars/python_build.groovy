// def call(dockerRepoName, imageName, portNum) {
def call(directoryName, dockerRepoName, imageName) {
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
            stage('Python Lint') { 
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
                    sh "docker build -t ${dockerRepoName}:latest --tag akinofu/${dockerRepoName}:latest ${directoryName}" 
                    sh "docker push akinofu/${dockerRepoName}:latest" 
                    } 
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
            // stage('Deliver') {
            //     when {
            //         expression {params.DEPLOY}
            //     }
            //     steps {
            //         sh "docker stop ${dockerRepoName} || true && docker rm ${dockerRepoName} || true"
            //         sh "docker run -d -p ${portNum}:${portNum} --name ${dockerRepoName} ${dockerRepoName}:latest"
            //     }
            // }

        } 
    }

}
