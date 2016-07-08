node {
   stage 'Build'

   def workspace = pwd() 

   sh '''
   	echo $PWD
   	echo $BRANCH_NAME
   	cd $PWD@script/api;
      mvn versions:set -DnewVersion=$BRANCH_NAME
	   mvn clean package
	'''

   stage 'Test'
   sh '''
   '''

   stage 'Deploy' 
   build job: 'deploy-component', parameters: [[$class: 'StringParameterValue', name: 'branch', value: env.BRANCH_NAME],[$class: 'StringParameterValue', name: 'component', value: "package-repository"],[$class: 'StringParameterValue', name: 'release_path', value: "platform/releases"],[$class: 'StringParameterValue', name: 'release', value: "${workspace}@script/api/target/package-repository-${env.BRANCH_NAME}.tar.gz"]]


}