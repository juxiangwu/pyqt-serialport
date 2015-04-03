# -*- coding: utf-8 -*-
import serialport.serialportwindow
from PyQt4 import QtCore,QtGui
import sys

def main():
    app = QtGui.QApplication(sys.argv)
    win = serialport.serialportwindow.SerialPortWindow()
    win.show()
    sys.exit(app.exec_())
    
    
if __name__ == '__main__':
    main()