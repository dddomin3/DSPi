pipeline {
  agent any
  stages {
    stage('Clean and Prepare') {
      steps {
        script {
          // Get User Input
          userInput = input(
            id: 'userInput',
            message: 'Lets build a kernel',
            parameters: [
              [
                $class: 'ChoiceParameterDefinition',
                choices: 'basicRtKernelConfig\nfullRtKernelConfig',
                description: 'Pick between pre-made kernel config files.',
                name: 'kernelConfig'
              ],
              [
                $class: 'TextParameterDefinition',
                name: 'toolsRepo',
                defaultValue: '/home/cheekymusic/tools',
                description: 'Repopath for kernel tools'
              ],
              [
                $class: 'TextParameterDefinition',
                name: 'kernelRepo',
                defaultValue: '/home/cheekymusic/linux',
                description: 'Repopath for kernel'
              ],
              [
                $class: 'TextParameterDefinition',
                name: 'kernelRepoTag',
                defaultValue: 'raspberrypi-kernel_1.20170303-1',
                description: 'git tag for kernel repo'
              ],
              [
                $class: 'TextParameterDefinition',
                name: 'dspiRepo',
                defaultValue: '/home/cheekymusic/Documents/DSPi',
                description: 'Repopath for DSPi'
              ],
              [
                $class: 'TextParameterDefinition',
                name: 'patchUrl',
                defaultValue: 'https://www.kernel.org/pub/linux/kernel/projects/rt/4.4/older',
                description: 'URL to realtime kernel patch'
              ],
              [
                $class: 'TextParameterDefinition',
                name: 'patchFile',
                defaultValue: 'patch-4.4.50-rt63.patch.gz',
                description: 'kernel patch file name. Should be *.patch.gz'
              ]
            ]
          )
          sh('git clean -xf')
          sh('git reset --hard')
          sh('rm -rf tools')
          sh('rm -rf linux')
        }
      }
    }
    stage('Clone') {
      steps {
        script {
          sh("git clone --single-branch $userInput.toolsRepo")
          sh("git clone --single-branch $userInput.kernelRepo -b $userInput.kernelRepoTag")
        }
      }
    }
    stage('Patch Kernel') {
      steps {
        script {
          echo ("kernelRepo: $userInput.kernelRepo")
          echo ("toolsRepo: $userInput.toolsRepo")
          echo ("dspiRepo: $userInput.dspiRepo")
          echo ("patchUrl: $userInput.patchUrl")
          echo ("patchFile: $userInput.patchFile")
          echo ("kernelConfig: .$userInput.kernelConfig")
          sh('ls -la')
          // Move pre-made configs into kernel folder
          sh("mv .$userInput.kernelConfig linux/.config")
          // Patch Kernel code with realtime code
          dir('linux/') {
            sh("wget $userInput.patchUrl/$userInput.patchFile")
            sh("zcat $userInput.patchFile | patch -p1")
          }
        }
      }
    }
  }
}