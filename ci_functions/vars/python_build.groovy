// def call(dockerRepoName, imageName, portNum) {
def call(directoryName) {
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
                    sh 'pylint-fail-under --fail_under 5.0 *.py' 
                } 
            } 
            // stage('Test and Coverage') { 
            //     steps { 
            //         script {
            //             def files = findFiles(glob: 'test*.py')
            //             for (file in files) {
            //                 sh "coverage run --omit */site-packages/*,*/dist-packages/* ${file.path}"
            //             }
            //         }
            //         sh 'coverage report' 
            //     }
            //     post { 
            //         always {
            //             script {
            //                 def test_reports_exist = fileExists 'test-reports'
            //                 if (test_reports_exist) {                        
            //                     junit 'test-reports/*.xml'
            //                 }
            //                 def api_test_reports_exist = fileExists 'api-test-reports'
            //                 if (api_test_reports_exist) {                        
            //                     junit 'api-test-reports/*.xml'
            //                 }
            //                 def carlot_test_reports_exist = fileExists 'carlot-test-reports'
            //                 if (carlot_test_reports_exist) {                        
            //                     junit 'carlot-test-reports/*.xml'
            //                 }
            //             }
            //         } 
            //     } 
            // }
            // stage('Package') { 
            //     when { 
            //         expression { env.GIT_BRANCH == 'origin/main' } 
            //     } 
            //     steps { 
            //         withCredentials([string(credentialsId: 'DockerHub', variable: 'TOKEN')]) { 
            //         sh "docker login -u 'cherylk19' -p '$TOKEN' docker.io" 
            //         sh "docker build -t ${dockerRepoName}:latest --tag cherylk19/${dockerRepoName}:${imageName} ." 
            //         sh "docker push cherylk19/${dockerRepoName}:${imageName}" 
            //         } 
            //     } 
            // }
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
