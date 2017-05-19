#!groovy
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
                choices: 'basicRtKernelConfig\nfullRtKernelConfig\ndontBuildAgain',
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
                defaultValue: 'raspberrypi-kernel_1.20170405-1',
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
              ],
              [
                $class: 'TextParameterDefinition',
                name: 'deployPathBoot',
                defaultValue: '/media/cheekymusic/boot',
                description: 'Path to Raspi boot dir.'
              ],
              [
                $class: 'TextParameterDefinition',
                name: 'deployPathLib',
                defaultValue: '/media/cheekymusic/f2100b2f-ed84-4647-b5ae-089280112716/lib',
                description: 'Path to Raspi lib dir.'
              ]
            ]
          )
          sh('git clean -xf')
          sh('git reset --hard')
          if (userInput['kernelConfig'] != 'dontBuildAgain') {
            sh('rm -rf tools linux modules rtkernel')

          } else {
            echo 'Not cleaning previously built kernel.'
          }
        }
      }
    }
    stage('Clone') {
      steps {
        script {
          if (userInput['kernelConfig'] != 'dontBuildAgain') {
            parallel 'tools':{
              sh("git clone --single-branch $userInput.toolsRepo")
            }, 'kernel':{
              sh("git clone --single-branch $userInput.kernelRepo -b $userInput.kernelRepoTag")
            }
          }
          else {
            echo 'Using previously pulled repos.'
          }
        }
      }
    }
    stage('Patch Kernel') {
      steps {
        script {

          if (userInput['kernelConfig'] != 'dontBuildAgain') {
            // Move pre-made configs into kernel folder
            sh("mv .$userInput.kernelConfig linux/.config")
            // Patch Kernel code with realtime code
            dir('linux/') {
              sh("wget $userInput.patchUrl/$userInput.patchFile")
              sh("zcat $userInput.patchFile | patch -p1")
            }
          } else {
            echo 'No need to patch, reusing kernel'
          }
        }
      }
    }
    stage('Build Kernel') {
      steps {
        script {
          if (userInput['kernelConfig'] != 'dontBuildAgain') {
            sh('ls -la')
            sh('mkdir modules')
            sh('mkdir -p rtkernel/boot')
            // LETS BUILD A KERNEL!!!
            dir('linux/') {
              sh '''
                source ../jenkins.source
                env
                make zImage modules dtbs -j4
                make modules_install -j4
                ./scripts/mkknlimg ./arch/arm/boot/zImage $INSTALL_MOD_PATH/boot/$KERNEL.img
              '''
            }
          } else {
            echo 'No need to build kernel :)'
          }
        }
      }
    }
    stage('Deploy Kernel') {
      steps {
        script {
          sh('ls -la')
          sh("sudo rm -r $userInput.deployPathBoot/overlays/ || true")
          // sh("sudo rm -r $userInput.deployPathLib/firmware/") // do i need this part?
          // LETS DEPLOY A KERNEL!!!

          parallel 'boot':{
            dir('rtkernel/boot/') {
              sh("sudo cp -rd * $userInput.deployPathBoot/")
              sh("sudo touch $userInput.deployPathBoot/ssh") // enables ssh for raspi
            }
          }, 'lib':{
            dir('rtkernel/lib/') {
              sh("sudo cp -dr * $userInput.deployPathLib/")
            }
          }
        }
      }
    }
    stage('Configure Pi Boot') {
      steps {
        script {
          sh('ls -la')
          sh("sudo sed -i '1s/$/ dwc_otg.speed=1 sdhci_bcm2708.enable_llm=0 smsc95xx.turbo_mode=N/' $userInput.deployPathBoot/cmdline.txt")
        }
      }
    }
  }
}