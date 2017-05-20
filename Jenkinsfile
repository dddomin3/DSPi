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
                choices: 'basicRtKernelConfig\nfullRtKernelConfig\ndontBuildAgain\ndontBuildOrDeployAgain',
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
                name: 'deployPathLibPrefix',
                defaultValue: '/media/cheekymusic/f2100b2f-ed84-4647-b5ae-089280112716',
                description: 'Path to Raspi lib dir.'
              ]
            ]
          )
          userInput['deployPathLib'] = "$userInput.deployPathLibPrefix/lib"          
          sh('git clean -xf')
          sh('git reset --hard')
          if ((userInput['kernelConfig'] == 'dontBuildAgain')||(userInput['kernelConfig'] == 'dontBuildOrDeployAgain')) {
            echo 'Not cleaning previously built kernel.'
          } else {
            sh('rm -rf tools linux modules rtkernel')
          }
        }
      }
    }
    stage('Clone') {
      steps {
        script {
          if ((userInput['kernelConfig'] == 'dontBuildAgain')||(userInput['kernelConfig'] == 'dontBuildOrDeployAgain')) {
            echo 'Using previously pulled repos.'
          }
          else {
            parallel 'tools':{
              sh("git clone --single-branch $userInput.toolsRepo")
            }, 'kernel':{
              sh("git clone --single-branch $userInput.kernelRepo -b $userInput.kernelRepoTag")
            }
          }
        }
      }
    }
    stage('Patch Kernel') {
      steps {
        script {

          if ((userInput['kernelConfig'] == 'dontBuildAgain')||(userInput['kernelConfig'] == 'dontBuildOrDeployAgain')) {
            echo 'No need to patch, reusing kernel'
          } else {
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
    stage('Build Kernel') {
      steps {
        script {
          if ((userInput['kernelConfig'] == 'dontBuildAgain')||(userInput['kernelConfig'] == 'dontBuildOrDeployAgain')) {
            echo 'No need to build kernel :)'
          } else {
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
          }
        }
      }
    }
    stage('Deploy Kernel') {
      steps {
        script {
          sh('ls -la')

          if (userInput['kernelConfig'] == 'dontBuildOrDeployAgain') {
            echo('Not deploying previously deployed kernel :)')
          } else {
            echo("LETS DEPLOY A KERNEL!!!")
            sh("sudo rm -r $userInput.deployPathBoot/overlays/ || true")
            // sh("sudo rm -r $userInput.deployPathLib/firmware/") // do i need this part?
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
    }
    stage('Configure Pi Boot') {
      steps {
        script {
          sh('ls -la')
          if (sh("sudo grep -c '<allow own=\"org.freedesktop.ReserveDevice1.Audio1\"/>' $userInput.deployPathLibPrefix/etc/dbus-1/system.conf") == 0) {
            sh '''
sudo sed -i 's/<\\/busconfig>/  <policy user="pi">\\
    <allow own="org.freedesktop.ReserveDevice1.Audio1"\\/>\\
  <\\/policy>\\
<\\/busconfig>/' system.conf
            '''
          } else { echo "Already configured system.conf!" }
          if (sh("sudo grep -c \"dwc_otg.speed=1 sdhci_bcm2708.enable_llm=0 smsc95xx.turbo_mode=N\" $userInput.deployPathBoot/cmdline.txt") == 0) {
            sh("sudo sed -i '1s/\$/ dwc_otg.speed=1 sdhci_bcm2708.enable_llm=0 smsc95xx.turbo_mode=N/' $userInput.deployPathBoot/cmdline.txt")
          } else { echo "Already configured cmdline.txt!"} 
        }
      }
    }
  }
}