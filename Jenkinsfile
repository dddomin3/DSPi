pipeline {
  agent any
  stages {
    stage('Clean and Prepare') {
      steps {
        script {
          // Get User Input
          userInput = input(id: 'userInput', message: 'Lets build a kernel', parameters: [
              [
                $class: 'TextParameterDefinition',
                defaultValue: '/home/cheekymusic/tools',
                name: 'toolsRepo',
                description: 'Repopath for kernel tools'
              ],
              [
                $class: 'TextParameterDefinition',
                defaultValue: '/home/cheekymusic/linux',
                name: 'kernelRepo',
                description: 'Repopath for kernel'
              ],
              [
                $class: 'TextParameterDefinition',
                defaultValue: 'raspberrypi-kernel_1.20170303-1',
                name: 'kernelRepoTag',
                description: 'git tag for kernel repo'
              ],
              [
                $class: 'TextParameterDefinition',
                defaultValue: '/home/cheekymusic/Documents/DSPi',
                name: 'dspiRepo',
                description: 'Repopath for DSPi'
              ],
              [
                $class: 'TextParameterDefinition',
                defaultValue: 'https://www.kernel.org/pub/linux/kernel/projects/rt/4.4/older',
                name: 'patchUrl',
                description: 'URL to realtime kernel patch'
              ],
              [
                $class: 'TextParameterDefinition',
                defaultValue: 'patch-4.4.50-rt63.patch.gz',
                name: 'patchFile',
                description: 'kernel patch file name. Should be *.patch.gz'
              ]
          ])
          sh("git clean -xf")
          sh("git reset --hard")
          sh("rm -rf tools")
          sh("rm -rf linux")
        }
      }
    }
    stage('Clone') {
      steps {
        script {
          sh("git clone --single-branch " + userInput['toolsRepo'])
          sh("git clone --single-branch " + userInput['kernelRepo'] + " -b " + userInput['kernelRepoTag'])
          dir('linux/') {
            sh("wget "+ userInput['patchUrl'] + "/" + userInput['patchFile'])
          }
        }
      }
    }
    stage('Patch Kernel') {
      steps {
        script {
          echo ("kernelRepo: $userInput['kernelRepo']")
          echo ("toolsRepo: $userInput['toolsRepo']")
          echo ("dspiRepo: $userInput['dspiRepo']")
          echo ("patchUrl: $userInput['patchUrl']")
          echo ("patchFile: $userInput['patchFile']")
          sh("ls -la")
          sh("pwd")
          sh("zcat $userInput['patchFile'] | patch -p1")
          // Patch Kernel code with realtime code
          // zcat userInput['patchFile'] | patch -p1
        }
      }
    }
  }
}