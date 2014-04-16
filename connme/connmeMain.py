# -*- coding: utf-8 -*-

import sys, time, subprocess, os
from PyQt4 import QtCore, QtGui, QtNetwork
from submodule import mainWindow, mainTray, interfaceList, worker

KONFIGURASI = '/etc/connme.conf'

class connme(QtCore.QObject):

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.config = self.getConfig()
        self.ui = myDialog(self)
        self.ui.STATUS = 1
        self.updateData()
        self.mainProc = QtCore.QProcess()
        self.secondProc = QtCore.QProcess()
        self.workerPool = []
        self.interface = interfaceList.Interface()

        self.ui.comboBox.addItems(self.interface.getInterface())
        self.ui.comboBox_2.addItems(self.interface.getInterface())
        self.ui.lineEdit_2.setText(self.config["ssid"])
        ITEM = self.ui.comboBox.findText(self.config["share"])
        self.ui.comboBox.setCurrentIndex(ITEM)
        ITEM = self.ui.comboBox.findText(self.config["source"])
        self.ui.comboBox_2.setCurrentIndex(ITEM)
        self.ui.comboBox_3.setCurrentIndex(int(self.config["security"]))
        self.ui.lineEdit.setText(self.config["password"])
        self.ui.vinterface_cbox.setChecked(self.config["vinterface"] == 'True')

        self.ui.trayIcon.activated.connect(self.showGui)
        self.secondProc.finished.connect(self.finishProc)
        self.mainProc.started.connect(self.mainStarted)
        self.mainProc.finished.connect(self.mainFinished)
        self.ui.tableWidget.cellDoubleClicked.connect(self.blockNetwork)
        self.ui.pushButton.clicked.connect(self.buttonClicked)
        self.connect(self.mainProc, QtCore.SIGNAL("readyReadStandardOutput()"),self.logOutput)

    def addClient(self, mac):
        hostname = self.translateClient(mac)
        self.ui.tableWidget.insertRow(self.ui.tableWidget.rowCount())
        row = self.ui.tableWidget.rowCount()
        item = QtGui.QTableWidgetItem(hostname)
        item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.ui.tableWidget.setItem(row-1,0,item)
        item = QtGui.QTableWidgetItem("On")
        item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.ui.tableWidget.setItem(row-1,1,item)
        self.jmlClient += 1
        self.ui.lineEdit_3.setText("%s Client" % self.jmlClient)

    def blockNetwork(self, row, column):
        item = QtGui.QTableWidgetItem()
        for i in self.client.values():
            if i[3] == self.ui.tableWidget.item(row,0).text():
                clientMAC = i[1]

        if self.ui.tableWidget.item(row,1).text() == "On":
            subprocess.Popen("iptables -I FORWARD -p ALL -m mac --mac-source %s -j DROP" % clientMAC, stdout=subprocess.PIPE, shell=True)
            self.xClient.append(clientMAC)
            item.setText("Off")
            item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidget.setItem(row,1,item)
        else:
            subprocess.Popen("iptables -D FORWARD -p ALL -m mac --mac-source %s -j DROP" % clientMAC, stdout=subprocess.PIPE, shell=True)
            self.xClient.pop(self.xClient.index(clientMAC))
            item.setText("On")
            item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidget.setItem(row,1,item)

    def buttonClicked(self,event):
        if self.ui.STATUS == 1:
            self.setConfig()
            self.jmlClient = 0
            self.xClient = []
            ARGS = [self.ui.comboBox.currentText(), self.ui.comboBox_2.currentText(), self.ui.lineEdit_2.text()]
            if self.ui.comboBox_3.currentIndex() != 0:
                if self.ui.comboBox_3.currentIndex() != 3:
                    ARGS.append('-w %s' % self.ui.comboBox_3.currentIndex())
                ARGS.append(self.ui.lineEdit.text())
            if self.ui.vinterface_cbox.isChecked():
                ARGS.append('--no-virt')
            self.mainProc.start('tether', ARGS)
        else:
            self.ui.pushButton.setEnabled(False)
            self.secondProc.terminate()
            subprocess.Popen("killall hostapd", stdout=subprocess.PIPE, shell=True)

    def delClient(self, mac):
        items = self.ui.tableWidget.findItems(self.translateClient(mac),QtCore.Qt.MatchExactly)
        self.ui.tableWidget.removeRow(self.ui.tableWidget.indexFromItem(items[0]).row())
        self.jmlClient -= 1
        self.ui.lineEdit_3.setText("%s Client" % self.jmlClient)

    def finishProc(self, exitCode):
        if exitCode != 0:
            time.sleep(5)
            self.secondProc.start('hostapd_cli -a %s' % self.address)

    def getConfig(self):
        config = {}
        with open(KONFIGURASI, 'r') as configFile:
            for baris in configFile.readlines():
                if baris.strip() == "":
                    pass
                else:
                    baris = baris.strip()
                    config[baris.split('=')[0]] = baris.split('=')[1]
        return(config)

    def logOutput(self):
        output = self.mainProc.readAllStandardOutput()
        cursor = self.ui.txt_log.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(str(output))
        if output.contains('Using interface'):
            self.wpaRunning()
        self.ui.txt_log.ensureCursorVisible()

    def mainStarted(self):
        self.ui.lineEdit_3.setText("Configuring...")
        self.ui.changeState(False)

    def mainFinished(self, exitCode):
        self.wpaStopped()

    def processClient(self, client):
        clientData = client.split()
        if clientData[1] == 'AP-STA-CONNECTED':
            self.workerPool.append(worker.Worker(self.addClient, clientData[2]))
            self.workerPool[len(self.workerPool)-1].start()
        if clientData[1] == 'AP-STA-DISCONNECTED':
            self.workerPool.append(worker.Worker(self.delClient, clientData[2]))
            self.workerPool[len(self.workerPool)-1].start()

    def setConfig(self):
        replacer = { 'ssid='+self.config["ssid"] : "ssid="+self.ui.lineEdit_2.text(), 
        'password='+self.config["password"] : "password="+self.ui.lineEdit.text(), 
        'security='+self.config["security"] : "security="+str(self.ui.comboBox_3.currentIndex()), 
        'share='+self.config["share"] : "share="+self.ui.comboBox.currentText(),
        'source='+self.config["source"] : "source="+self.ui.comboBox_2.currentText(),
        'vinterface='+self.config["vinterface"] : "vinterface="+str(self.ui.vinterface_cbox.isChecked()),
         }
        self.editFile(KONFIGURASI, replacer)

    def editFile(self,path, replacer):
        infile =  open(path).read()
        outfile =  open(path, 'w')
        replacerList = replacer
        for i in replacerList:
            infile = infile.replace(i, replacerList[i])
        outfile.write(infile)
        outfile.close()

    def showGui(self):
        self.ui.show()

    def translateClient(self,clientAddress):
        error = 0
        while error != 15:
            try:
                if self.client[clientAddress][3] == '*':
                    return(self.client[clientAddress][2])
                else:
                    return(self.client[clientAddress][3])
                break
            except KeyError:
                self.updateData()
                time.sleep(2)
                error = error + 1
        return(clientAddress)

    def updateData(self):
        self.client = {}
        try:
            with open("/var/lib/misc/dnsmasq.leases","r") as file:
                for line in file.readlines():
                    line = line.strip().split()
                    self.client[line[1]] = line
        except IOError:
            pass
        return

    def wpaRunning(self):
        self.ui.lineEdit_3.setText("%s Client" % self.jmlClient)
        self.ui.pushButton.setEnabled(True)
        self.ui.pushButton.setText('Stop Hotspot')
        self.ui.STATUS = 0
        self.ui.trayIcon.show()
        self.secondProc.start('hostapd_cli -a %s' % self.address)

    def wpaStopped(self):
        self.ui.lineEdit_3.setText("Stopped")
        self.ui.changeState(True)
        self.ui.pushButton.setEnabled(True)
        self.ui.pushButton.setText('Start Hotspot')
        self.ui.STATUS = 1
        self.ui.trayIcon.hide()

class myDialog(QtGui.QMainWindow, mainWindow.Ui_MainWindow):

    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self)
        self._parent = parent
        self.setupUi(self)
        self.trayIcon = mainTray.SystemTrayIcon(QtGui.QIcon(':/connme/img/icon.png'),self)

    def closeEvent(self, event):
        if self.STATUS == 1:
            event.accept()
        else:
            event.ignore()
            if QtGui.QSystemTrayIcon.isSystemTrayAvailable():
                self.trayIcon.show()
                self.hide()
            else:
                self.setWindowState(QtCore.Qt.WindowMinimized)
			
    def changeState(self,status):
        self.lineEdit_2.setEnabled(status)
        self.lineEdit.setEnabled(status)
        self.comboBox_2.setEnabled(status)
        self.comboBox.setEnabled(status)
        self.comboBox_3.setEnabled(status)
        self.vinterface_cbox.setEnabled(status)
        self.ui.pushButton.setEnabled(status)