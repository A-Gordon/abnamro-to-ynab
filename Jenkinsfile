#!/usr/bin/groovy

podTemplate(
  label: 'jenkins-pipeline', 
  inheritFrom: 'default',
  containers: [
    containerTemplate(name: 'ng', image: 'alexsuch/angular-cli:1.6.1', command: 'cat', ttyEnabled: true),
    containerTemplate(name: 'python', image: 'python:2.7', command: 'cat', ttyEnabled: true)
  ]
) {
  node ('jenkins-pipeline') {
    stage ('Get Latest') {
      checkout scm
    }

    stage ('Build') {
      container ('ng') {
        sh "npm install"
      }
    }

    stage ('python version') {
      container ('python') {
          checkout scm
          sh "python --version"
          sh "ls -al"
      }
    }
    
    stage ('Test parallelism') {
      parallel {
        stage ('Test sleep command - 30seconds') {
          container ('python') {
            sh "sleep 30"
          }
        }
        stage ('Test sleep command - 60seconds') {
          container ('python') {
            sh "sleep 60"
          }
        }
      }
    }


  } // end node
} // end podTemplate