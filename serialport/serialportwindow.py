# -*- coding: utf-8 -*-
from serialport import serialportform
from PyQt4 import QtCore,QtGui
import platform
from __builtin__ import int
import serialportcontext
from enaml.widgets.combo_box import ComboBox
import threading
import time

class SerialPortWindow(QtGui.QMainWindow,serialportform.Ui_SerialPortWindow):
    _receive_signal = QtCore.pyqtSignal(str)
    _auto_send_signal = QtCore.pyqtSignal()
    def __init__(self):
        super(SerialPortWindow,self).__init__()
        self.setupUi(self)
        self.initForms()
        
    def initForms(self):
        #init serial ports
        self.setFixedSize(QtCore.QSize(821, 646))
        
        if platform.system() == "Windows":
            ports = QtCore.QStringList()
            for i in range(8):
                ports.append("COM%d" %((i+1)))    
            self.comboBoxPort.addItems(ports)
        else:
            #todo:scan system serial port
            self.__scanSerialPorts__()
        
        #init bauds
        bauds = ["50","75","134","110","150","200","300","600","1200","2400","4800","9600","14400","19200","38400","56000","57600",
                 "115200"];
        self.comboBoxBaud.addItems(bauds)
        self.comboBoxBaud.setCurrentIndex(len(bauds) - 1)
        
        checks = ["None","Odd","Even","Zero","One"]
        self.comboBoxCheckSum.addItems(checks)
        self.comboBoxCheckSum.setCurrentIndex(len(checks) - 1)
        
        bits = ["4 Bits","5 Bits","6 Bits" ,"7 Bits","8 Bits"]
        self.comboBoxBits.addItems(bits)
        self.comboBoxBits.setCurrentIndex(len(bits) - 1)
        
        stopbits = ["1 Bit","1.5 Bits","2 Bits"];
        self.comboBoxStopBits.addItems(stopbits)
        self.comboBoxStopBits.setCurrentIndex(0)
        
        
        
        port = self.comboBoxPort.currentText()
        
        baud = int("%s" % self.comboBoxBaud.currentText(),10)
        self._serial_context_ = serialportcontext.SerialPortContext(port = port,baud = baud)
        
        self.checkBoxCD.setEnabled(False)
        self.checkBoxCTS.setEnabled(False)
        self.checkBoxDSR.setEnabled(False)
        self.checkBoxGND.setEnabled(False)
        self.checkBoxRI.setEnabled(False)
        self.checkBoxDSR.setEnabled(False)
        self.checkBoxRXD.setEnabled(False)
        self.checkBoxTXD.setEnabled(False)
        self.checkBoxDTR.setChecked(True)  
        self.checkBoxRTS.setChecked(True)      
        
        self.lineEditReceivedCounts.setText("0")
        self.lineEditSentCounts.setText("0")
        
        self.pushButtonOpenSerial.clicked.connect(self.__open_serial_port__)
        self._receive_signal.connect(self.__display_recv_data__)
        self.pushButtonClearRecvArea.clicked.connect(self.__clear_recv_area__)
        self.pushButtonSendData.clicked.connect(self.__send_data__)
        self.checkBoxSendHex.clicked.connect(self.__set_send_hex__)
        self.checkBoxDisplayHex.clicked.connect(self.__set_display_hex__)
        self.checkBoxCD.clicked.connect(self.__set_cd__)
        self.checkBoxRTS.clicked.connect(self.__set_rts__)
        self.checkBoxDTR.clicked.connect(self.__set_dtr__)
        self.pushButtonClearAllCounts.clicked.connect(self.__clear_all_counts)
        self.pushButtonClearRecvCounts.clicked.connect(self.__clear_recv_counts)
        self.pushButtonClearSentCounts.clicked.connect(self.__clear_send_counts)
        self.checkBoxSendLooping.clicked.connect(self.__handle_send_looping__)
        self._auto_send_signal.connect(self.__auto_send_update__)
        self.pushButtonOpenRecvFile.clicked.connect(self.__save_recv_file__)
        self.pushButtonOpenSendFile.clicked.connect(self.__open_send_file__)
        
        self._is_auto_sending = False
        self._recv_file_ = None
        self._send_file_ = None
        self._send_file_data = ''
        
    def __open_send_file__(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, caption=QtCore.QString("Open Send File"))
        try:
           
            if filename and self.checkBoxSendFile.isChecked():
                self._send_file_ = open(filename)
                while True:
                    line = self._send_file_.readline()
                    if not line:
                        break
                    else:
                        self._send_file_data += line
                self._send_file_.close()
                self._send_file_ = None
            self.textEditSent.clear()
            if len(self._send_file_data) > 0:
                self.textEditSent.setText(self._send_file_data)
            
        except Exception,e:
            print(e)
            QtGui.QMessageBox.critical(self,u"打开文件",u"无法打开文件,请检查!")
            
    def __save_recv_file__(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, caption=QtCore.QString("Save Received File"))
        try:
            if self._recv_file_ != None:
                self._recv_file_.flush()
                self._recv_file_.close()
            if filename and self.checkBoxSaveAsFile.isChecked():
                self._recv_file_ = open(filename,"a+")
                data = str(self.textEditReceived.toPlainText())
                if len(data) > 0:
                    self._recv_file_.write(data)
                
        except Exception,e:
            QtGui.QMessageBox.critical(self,u"保存文件",u"无法保存文件,请检查!")
             
    def closeEvent(self,event):
        self._is_auto_sending = False
        if self._serial_context_.isRunning():
            self._serial_context_.close()
        if self._recv_file_ != None:
            self._recv_file_.flush()
            self._recv_file_.close()
    
    def __handle_send_looping__(self):
        #if self._is_auto_sending:
            self._is_auto_sending = False
            self.pushButtonSendData.setEnabled(True)
        
        
        
    def __clear_all_counts(self):
        self.lineEditReceivedCounts.setText("0")
        self.lineEditSentCounts.setText("0")
        self._serial_context_.clearAllCounts()
        
    def __clear_send_counts(self):
        self._serial_context_.clearSentCounts()
        self.lineEditSentCounts.setText("0")
    
    def __clear_recv_counts(self):
        self._serial_context_.clearRecvCounts()
        self.lineEditReceivedCounts.setText("0")
      
    def __set_dtr__(self):
        self._serial_context_.setDTR(self.checkBoxDTR.isChecked())
        
    def __set_rts__(self):
        self._serial_context_.setRTS(self.checkBoxRTS.isChecked())
    
    def __set_cd__(self):
        self._serial_context_.setCD(self.checkBoxCD.isChecked())
        
    def __scanSerialPorts__(self):
        ports = []
        for i in range(32):
            ports.append("/dev/ttyS%d" % i)
        for i in range(32):
            ports.append("/dev/ttyUSB%d" % i)
        self.comboBoxPort.addItems(ports)
        
    def __open_serial_port__(self):
        if  self._serial_context_.isRunning():
            self._serial_context_.close()
            self.pushButtonOpenSerial.setText(u'打开')
        else:
            try:
                
                port = self.comboBoxPort.currentIndex()
                baud = int("%s" % self.comboBoxBaud.currentText(),10)
                self._serial_context_ = serialportcontext.SerialPortContext(port = port,baud = baud)
                self._serial_context_.registerReceivedCallback(self.__data_received__)
                self.checkBoxDTR.setChecked(True)
                self._serial_context_.setDTR(True)
                self.checkBoxRTS.setChecked(True)
                self._serial_context_.setRTS(True)
                self._serial_context_.open()
                self.pushButtonOpenSerial.setText(u'关闭')
            except Exception,e:
                QtGui.QMessageBox.critical(self,u"打开端口",u"打开端口失败,请检查!")
        
    def __data_received__(self,data):
        #print('recv:%s' % data)
        self._receive_signal.emit(data)
        if self._recv_file_ != None and self.checkBoxSaveAsFile.isChecked():
            self._recv_file_.write(data)
        
    def __set_display_hex__(self):
        self.textEditReceived.clear()
        
    def __display_recv_data__(self,data):
        if self.checkBoxDisplayHex.isChecked():
            for l in xrange(len(data)):
                hexstr = "%02X " % ord(str(data[l]))
                self.textEditReceived.insertPlainText(hexstr)
        else:
            for l in xrange(len(data)):
                self.textEditReceived.insertPlainText(data[l])
                
        if self.checkBoxNewLine.isChecked():
            self.textEditReceived.insertPlainText("\n")
                    
        self.lineEditReceivedCounts.setText("%d" % self._serial_context_.getRecvCounts())
        
    def __clear_recv_area__(self):
        self.textEditReceived.clear()
        
    def __clear_send_area__(self):
        self.textEditSent.clear()
        
    def __set_send_hex__(self):
        self.textEditSent.clear()
        self.textEditSent.setIsHex(self.checkBoxSendHex.isCheckable())
        
    def __send_data__(self):
        data = str(self.textEditSent.toPlainText())
        if self._serial_context_.isRunning():
            if len(data) > 0:
                self._serial_context_.send(data, self.checkBoxSendHex.isChecked())
                self.lineEditSentCounts.setText("%d" % self._serial_context_.getSendCounts())
                if self.checkBoxEmptyAfterSent.isChecked():
                    self.textEditSent.clear()
            
                if self.checkBoxSendLooping.isChecked():
                    self.pushButtonSendData.setEnabled(False)
                    delay = self.spinBox.value() * 100.0 / 1000.0
                    self._auto_send_thread = threading.Thread(target=self.__auto_send__,args=(delay,))
                    
                    self._is_auto_sending = True
                    self._auto_send_thread.setDaemon(True)
                    self._auto_send_thread.start()
                    
    def __auto_send__(self,delay):
        while self._is_auto_sending:
            if self.checkBoxSendFile.isChecked():
                if len(self._send_file_data) > 0:
                    self._serial_context_.send(self._send_file_data, self.checkBoxSendHex.isChecked())
                    self._auto_send_signal.emit()
                    break
            else:
                data = str(self.textEditSent.toPlainText())
                if self._serial_context_.isRunning():
                    if len(data) > 0:
                        self._serial_context_.send(data, self.checkBoxSendHex.isChecked())
                        self._auto_send_signal.emit()
                        
            time.sleep(delay)
            
    def __auto_send_update__(self):
        self.lineEditSentCounts.setText("%d" % self._serial_context_.getSendCounts())
       
        if self.checkBoxSendFile.isChecked():
            if len(self._send_file_data) > 0:
                self.textEditSent.setText(self._send_file_data)
                
        if self.checkBoxEmptyAfterSent.isChecked():
            self.textEditSent.clear()