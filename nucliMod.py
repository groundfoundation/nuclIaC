#!/usr/bin/env python3
# NuclIaC - nucliMod business end of the NuclIac
# Scripting tool for managing IaC 

import subprocess
import nucliConfig as nconfig
import json
import tfvars
import re
import os
import sys
import datetime as dt


class init(object):

    def setActionOptions(self):
        self.actionOption = {
            'plan': {'destription': "Run Terraform plan in selected environment",
                    'command': ["terraform", "plan"]},
            'apply': {'destription': "Run Terraform init, plan, and apply in selected environment",
                    'command': ["terraform", "apply"]},
            'destroy': {'destription': "Run Terraform destroy in selected environment",
                    'command': ["terraform", "destroy"]},
            'kill': {'destription': "Run a backup, unlicense, and destroy in selected environment",
                    'command': ["terraform", "kill"]},
            'unlicense': {'destription': "Run a unlicense script on selected environment VM",
                    'command': ["runSshCommand", "/opt/tableau/data/unlicense.sh"]},
            'log': {'destription': "Follow build log on selected environment VM. Ctrl+C to break",
                    'command': ["runSshCommand", "tail -f /var/log/cloud-init-output.log"]},
            'backup': {'destription': "Run Backup on selected environment VM application",
                    'command': ["tsm", "backup"]},
            'restore': {'destription': "Run Restore on selected environment VM application",
                    'command': ["tsm", "restore"]},
            'localbackup': {'destription': "Run Application Backup and copy file locally",
                    'command': ["localbackup"]},
            'download': {'destription': "Download file from selected application VM to local filesystem",
                    'command': ["movetabbackup", "download"]},
            'upload': {'destription': "Upload file from local filesystem to the selected application VM",
                    'command': ["movetabbackup", "upload"]},
            'publish': {'destription': "Run Terraform Apply and follow the build log. Ctrl+C to break",
                    'command': ["publish"]}
        }

    def runArgs(self):
        if self.action.lower() == 'plan': return self.terraform('plan')
        elif self.action.lower() == 'apply': return self.terraform('apply')
        elif self.action.lower() == 'destroy': return self.terraform('destroy')
        elif self.action.lower() == 'kill': return self.kill()
        elif self.action.lower() == 'unlicense': return self.runSshCommand("/opt/tableau/data/unlicense.sh")
        elif self.action.lower() == 'log': return self.runSshCommand("tail -f /var/log/cloud-init-output.log")
        elif self.action.lower() == 'backup': return self.tsm('backup')
        elif self.action.lower() == 'restore': return self.tsm('restore')
        elif self.action.lower() == 'localbackup': return self.localBackup()
        elif self.action.lower() == 'download': return self.moveTabBackup('download')
        elif self.action.lower() == 'upload': return self.moveTabBackup('upload')
        elif self.action.lower() == 'publish': return self.publish()
        else: goDie(f"Could not run Action: {self.action}")


    def __init__(self, serviceName, envSelect, depSelect, args, promptMe=True):
        #load DataBag 
        with open(nconfig.deployments()[serviceName]['databagLoc']) as f: self.dBag = json.load(f)
        try: 
            with open(nconfig.deployments()[serviceName]['databagLoc']) as f: self.dBag = json.load(f)
        except:
            if action == "buildfs":
                pass
            else:
                quit('Could not load DataBag!')

        self.promptMe = promptMe
        self.prodConfirmation = False
        self.serviceName = serviceName
        self.environment = envSelect
        self.deployment = depSelect
        self.printLabel = "{}:{}:{}".format(serviceName, envSelect, depSelect)
        self.tabBuild = "None"
        if depSelect == 'local':
            self.varList = getVarList(serviceName, envSelect, 'global')
        else:
            self.varList = getVarList(serviceName, envSelect, depSelect)
        #self.defaultVarList = getVarList(serviceName, envSelect, 'default')
        #self.defaultVars = getDefaultVarList(serviceName, envSelect, depSelect)
        self.currentEnv = getVar(self.varList)
        #self.nameStart = "{}-{}-{}-{}".format(
        #            getVar(self.varList, 'prefix'), envSelect,
        #            nconfig.deployments()[serviceName]['productLabel'], self.deployment
        #            )
        #self.nameEnd = "{}-{}".format(
        #            getVar(self.varList, 'location_label'), getVar(self.varList, 'zone_label')
        #            )
        #self.agPrefix = "{}-{}-{}".format(
        #            getVar(self.varList, 'prefix'), envSelect,
        #            nconfig.deployments()[serviceName]['productLabel']
        #            )
        #self.namePrefix = "{}-{}".format( self.nameStart, self.nameEnd )
        #self.svrPrefix = "{}-svr-{}".format( self.nameStart, self.nameEnd )
        #self.apiPrefix = "{}-api-{}".format( self.nameStart, self.nameEnd )
        #self.pubPrefix = "{}-pub-{}".format( self.nameStart, self.nameEnd )
        #self.configDic = nconfig.cloudModConfig()[serviceName]
        #self.gjenkins = "{}/{}".format(nconfig.cloudModConfig()[serviceName]['jenkinsroot'],
        #            nconfig.cloudModConfig()[serviceName]['globaljenkins'])
        #self.mjenkins = "{}/{}".format(nconfig.cloudModConfig()[serviceName]['jenkinsroot'],
        #        nconfig.cloudModConfig()[serviceName]['mainjenkins'])
        self.components = nconfig.deployments()[serviceName]['components']
        self.root = nconfig.deployments()[serviceName]['localProjectDirectory']
        try:
            self.mainRepo = nconfig.deployments()[serviceName]['mainRepo']
            self.globalRepo = nconfig.deployments()[serviceName]['globalRepo']
        except:
            self.mainRepo = 'None'
            self.globalRepo = 'None'
        self.buildLoc = '{}/build/{}'.format(self.root, self.environment, )
        self.mainLoc = '{}/{}/main'.format(self.root, self.environment)
        self.globalLoc = '{}/{}/global'.format(self.root, self.environment)
        self.certLoc = '{}/certs'.format(self.root)
        self.backupLoc = '{}/backup'.format(self.root)
        self.mergeLoc = '{}/merge'.format(self.root)
        self.gYml='{}/OptumFile.'.format(self.mainLoc)
        self.groupFilter = nconfig.deployments()[serviceName]['productLabel']
        #self.jenkins = self.mjenkins
        self.tabCurrentVersion = True
        self.globalKeyvault = 'None'
        #if re.search('global', depSelect):
        #    self.jenkins = self.gjenkins
        #    self.globalNamePrefix = self.namePrefix
        #else:
        #    self.globalEnv = environment(serviceName, envSelect, 'global', action)
        #    self.globalNamePrefix = self.globalEnv.globalNamePrefix

        self.setActionOptions()
        self.args = args
        try: action=args[0]
        except: 
            print(f"Available Actions: {self.actionOption.keys()}")
            goDie(f"Could not find action in {args}")
        self.action = action

    def moveTabBackup(self, direction, fileName=None):
        backupDir = f"{self.root}/backup"
        domain = getVar(self.varList, 'domain_zone')
        cname = getVar(self.varList, 'dns_cname')
        if not fileName:
            try:
                fileName = self.args[1]
            except:
                goDie("You must add a backup file as an argument")
        if direction == 'download':
            print(f"Downloading {fileName}")
            runCmdLive(['scp', f"ubuntu@{cname}.{domain}:/opt/tableau/data/backup/{fileName}", f"{backupDir}/{fileName}"])
        elif direction == 'upload':
            runCmdLive(['scp', f"{backupDir}/{fileName}", f"ubuntu@{cname}.{domain}:/opt/tableau/data/backup/{fileName}"])
            runCmdLive(['ssh', f"ubuntu@{cname}.{domain}", f"chmod 755 /opt/tableau/data/backup/{fileName}"])
        
    def runSshCommand(self, cmd, live=True):
        domain = getVar(self.varList, 'domain_zone')
        cname = getVar(self.varList, 'dns_cname')
        if live:
            runCmdLive(['ssh', f"ubuntu@{cname}.{domain}", cmd])
        else:
            return runCmd(['ssh', f"ubuntu@{cname}.{domain}", cmd])

    def publish(self):
        self.terraform('apply')
        self.runSshCommand("tail /var/log/cloud-init-output.log", live=False)

    def kill(self):
        print("Backing Up Locally")
        self.localBackup()
        input("Did it Backup?")
        print("Unlicensing")
        self.runSshCommand("/opt/tableau/data/unlicense.sh")
        input("Did it unlicense?")
        self.terraform('destroy')

    def waitForInitLogItem(self, item):
        self.envPrint("Waiting for init-log item: \"{}\"".format(item))
        moveon = 0
        while moveon == 0:
            resp = self.checkInitLog(item)
            if checkForString(resp, item)['success'] == True:
                moveon = 1
            else:
                time.sleep(5)
        print("Found!")

    def terraform(self, tfAction):
        loc = f"{self.buildLoc}/{self.deployment}"
        os.chdir(loc)
        print(f"in {loc}")
        tf = nconfig.deployments()[self.serviceName]['terraformPath']
        print(tf)
        if tfAction.lower() == "apply":
            runCmdLive([tf, "init"])
            runCmdLive([tf, "plan"])
            input("How does it look?")
            runCmdLive([tf, "apply", "-auto-approve"])
        elif tfAction.lower() == "destroy":
            runCmdLive([tf, "plan", "-destroy"])
            input("This is going to Destory everything above!!")
            runCmdLive([tf, "apply", "-destroy", "-auto-approve"])
        else:
            runCmdLive([tf, tfAction])

    def tsm(self, cmd):
        print(f"Running TSM {cmd}") 
        tsmCmd = "/opt/tableau/tableau_server/packages/customer-bin.*/tsm"
        if cmd == 'backup':
            d = dt.datetime.now()
            dStamp = "{}-{}-{}-{}-{}".format(d.year, d.month, d.day, d.hour, d.minute)
            bkFile = f"{self.serviceName}Tableau-{self.environment}-aws-{dStamp}.tsbak"
            bcommand = '{} maintenance backup -f {}'.format(tsmCmd, bkFile)
            self.runSshCommand(bcommand)
            return bkFile
        if cmd == 'restore':
            try:
                fileName = self.args[1]
            except:
                goDie("You must add a restore filename as an argument")
            bcommand = '{} maintenance restore -f {}'.format(tsmCmd, fileName)
            self.runSshCommand(bcommand)
            scommand = '{} start'.format(tsmCmd, fileName)
            self.runSshCommand(scommand)
            return fileName

    def localBackup(self):
        bkFile = self.tsm('backup')
        print("Backup Complete. Downloading File")
        self.moveTabBackup('download', bkFile)

    def envPrint(self, str):
        print(bcolors.WARNING + "{}>\t\t{}".format(self.printLabel, str) + bcolors.ENDC)

def goDie(msg):
  if msg != 'skip':
    print("Error:\n{}\n".format(msg))
  quit()

def runCmd(cmdList, printOut = True):
    process = subprocess.Popen(cmdList,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        if printOut: print('RunCmd StdErr: {}'.format(stderr.decode('utf-8')))
    return stdout.decode('utf-8'), stderr.decode('utf-8')

def runCmdLive(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for c in iter(lambda: process.stdout.read(1), b""):
        sys.stdout.buffer.write(c)

def getVarList(serviceName, environment, deployment):
    varFileName = getVarFileName(serviceName, environment, deployment)
    tfv = tfvars.LoadSecrets(varFileName)
    return tfv

def getVarFileName(serviceName, environment, deployment):
    root = nconfig.deployments()[serviceName]['localProjectDirectory']
    fname = f"{root}build/{environment}/{deployment}/terraform.tfvars"
    print(fname)
    return fname

def getVar(y, key='none'):
    if key == 'none':
        return y
    else:
        return y[key]
