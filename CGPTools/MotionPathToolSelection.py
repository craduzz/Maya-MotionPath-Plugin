import os
import sys
import maya.cmds as cmds
import maya.OpenMayaUI as apiUI

import MotionPathToolConfig



#import Pyside Modules
try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2.QtUiTools import *
    from shiboken2 import wrapInstance
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide.QtWidgets import *
    from PySide.QtUiTools import *
    from shiboken2 import wrapInstance

#Get Variables
SCRIPT_LOC = os.path.split(__file__)[0] + "/"
UI_NAME    = "selectionWindow"


def loadUiWidget(uiFilename, parent=None):
    loader = QUiLoader()
    uiFile = QFile(uiFilename)
    uiFile.open(QFile.ReadOnly)
    ui = loader.load(uiFile,parent)
    uiFile.close()
    return ui

class motionPathToolsSelection(QMainWindow):
    def __init__(self):
        super(motionPathToolsSelection, self).__init__()

        self.__objFlag = False
        self.__curveFlag = False
        self.__objName = ''
        self.__curveName = ''

        #
        MayaMain = wrapInstance(long(apiUI.MQtUtil.mainWindow()),QWidget)

        #set up window inside of maya
        self.MainWindowUI = loadUiWidget(SCRIPT_LOC+UI_NAME+".ui",MayaMain)
        self.MainWindowUI.setAttribute(Qt.WA_DeleteOnClose,True)

        #connectButtons
        self.MainWindowUI.select_object_btn.clicked.connect(lambda: self.getObjectName("obj"))
        self.MainWindowUI.select_curve_btn.clicked.connect(lambda: self.getObjectName("curve"))
        self.MainWindowUI.accept_btn.clicked.connect(lambda: self.getNextWindow())
        self.MainWindowUI.Cancel_01_btn.clicked.connect(lambda: self.closeWindow())




        #show ui
        self.MainWindowUI.show()

    def getObjectName(self,btn_type):

        selectedObject = cmds.ls(sl=True)
        #print btn_type

        if not selectedObject:
            sys.stderr.write("Nothing is selected.")
            self.setWarningMsg("Nothing is selected.")
            return
        elif len(selectedObject) > 1:
            sys.stderr.write("More that 1 object was selected please select only 1.")
            self.setWarningMsg("More that 1 object was selected please select only 1.")
            return



        if btn_type == 'obj':

            if self.checkSelectionType(selectedObject,'mesh'):
                self.MainWindowUI.object_label.setText(selectedObject[0])
                self.__objFlag = True
                self.__objName = selectedObject[0]
                self.setWarningMsg('')

            else:
                sys.stderr.write("You can only select mesh here!")
                self.setWarningMsg("You can only select mesh here!")

        elif btn_type == 'curve':
            if self.checkSelectionType(selectedObject, 'bezierCurve'):
                self.MainWindowUI.curve_label.setText(selectedObject[0])
                self.__curveFlag = True
                self.__curveName = selectedObject[0]
                self.setWarningMsg('')

            else:
                sys.stderr.write("You can only select curves here!")
                self.setWarningMsg("You can only select curves here!")

        self.unlockBtn()

    def unlockBtn(self):

        if self.__objFlag and self.__curveFlag:
            self.MainWindowUI.accept_btn.setEnabled(True)

    def getNextWindow(self):

        self.MainWindowUI.close()
        MotionPathToolConfig.runUi(self.__objName,self.__curveName)

    def closeWindow(self):
        self.MainWindowUI.close()

    def checkSelectionType(self, object,type):

        object.sort(key=len, reverse=True)
        children = cmds.listRelatives(object, children=True, fullPath=True) or []

        if len(children) == 1:
            child = children[0]
            objtype = cmds.objectType(child)
        else:
            objtype = cmds.objectType(object)

        #print objtype

        if objtype == type:
            return True
        else:
            return False

    def setWarningMsg(self,text):
        self.MainWindowUI.warning_label.setText(text)



def runUi():

    if not cmds.window(UI_NAME,exists=True):
        ui = motionPathToolsSelection()
    else:
        sys.stderr.write("Tool is already open!\n")
