#!/usr/bin/groovy

podTemplate(
  label: 'jenkins-pipeline', 
  inheritFrom: 'default',
  containers: [
    containerTemplate(name: 'ng', image: 'alexsuch/angular-cli:1.6.1', command: 'cat', ttyEnabled: true)
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
  } // end node
} // end podTemplate