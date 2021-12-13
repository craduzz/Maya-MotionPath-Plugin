import os
import sys
import maya.cmds as cmds
import maya.OpenMayaUI as apiUI

import MotionPathToolSelection

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
UI_NAME    = "settingsWindow"

def loadUiWidget(uiFilename, parent=None):
    loader = QUiLoader()
    uiFile = QFile(uiFilename)
    uiFile.open(QFile.ReadOnly)
    ui = loader.load(uiFile,parent)
    uiFile.close()
    return ui

class motionPathToolsConfig(QMainWindow):
    def __init__(self):
        super(motionPathToolsConfig, self).__init__()

        self.__objName = ''
        self.__curveName = ''

        self.meshList = []
        self.aniCurves = []

        MayaMain = wrapInstance(long(apiUI.MQtUtil.mainWindow()),QWidget)

        #set up window inside of maya
        self.MainWindowUI = loadUiWidget(SCRIPT_LOC+UI_NAME+".ui",MayaMain)
        self.MainWindowUI.setAttribute(Qt.WA_DeleteOnClose,True)

        #connectButtons
        #self.MainWindowUI.select_object_btn.clicked.connect(lambda: self.getObjectName("obj"))
        self.MainWindowUI.back_btn.clicked.connect(lambda: self.backBtn())
        self.MainWindowUI.finish_btn.clicked.connect(lambda: self.createMotionPathBtn())


        self.MainWindowUI.follow_box.clicked.connect(lambda: self.unlock_follow_suboptions(self.MainWindowUI.follow_box.isChecked()))

        self.MainWindowUI.flow_path_box.clicked.connect(lambda: self.unlock_flow_path(self.MainWindowUI.flow_path_box.isChecked()))


        #show ui
        self.MainWindowUI.show()

    def backBtn(self):
        self.MainWindowUI.close()
        MotionPathToolSelection.runUi()

    def createMotionPathBtn(self):

        self.meshList.append(self.__objName)

        dupesAmount = self.MainWindowUI.dupe_amount.value()

        anim_duration = self.MainWindowUI.frame_duration.value()
        delay_amount = self.MainWindowUI.frame_delay.value()
        delay = 0

        use_follow = self.MainWindowUI.follow_box.isChecked()
        use_bank = self.MainWindowUI.bank_box.isChecked() * self.MainWindowUI.bank_box.isEnabled()

        use_flow_path = self.MainWindowUI.flow_path_box.isChecked() * self.MainWindowUI.flow_path_box.isEnabled()
        flow_path_subdiv = self.get_flow_path_subdiv()

        f_axis_value = self.check_front_axis()
        u_axis_value = self.check_up_axis()

        tangent_type = self.get_tangent_type()

        scale_x = self.MainWindowUI.size_change_x.value()
        scale_y = self.MainWindowUI.size_change_y.value()
        scale_z = self.MainWindowUI.size_change_z.value()
        x = y = z = 0


        print "follow: " + str(use_follow) + ". bank: "+str(use_bank)+". flowPath: "+str(use_flow_path)


        for i in range(dupesAmount):
            t = cmds.duplicate(self.__objName, n=self.__objName+"_copy_%02d" % (i))
            self.meshList.append(t[0])


        for obj in self.meshList:
            cmds.scale(x+1, y+1, z+1, obj,)
            x += scale_x
            y += scale_y
            z += scale_z



        for meshToPath in self.meshList:
            curve_name = meshToPath+"_aniCurve"
            self.aniCurves.append(curve_name)
            cmds.pathAnimation(meshToPath,
                               c   = self.__curveName,
                               stu = delay,
                               etu = anim_duration+delay,
                               f   = use_follow,
                               b   = use_bank,
                               fa  = f_axis_value,
                               ua  = u_axis_value,
                               n   = curve_name
                               )
            delay += delay_amount

        delay = 0

        for curve in self.aniCurves:
            cmds.keyTangent(curve,
                            itt = tangent_type,
                            ott= tangent_type
                            )

        if use_flow_path:
            for path in self.meshList:
                cmds.select(path,r=True)
                cmds.flow(dv = (flow_path_subdiv[0], flow_path_subdiv[1], flow_path_subdiv[2]))


        self.MainWindowUI.close()

    def setMeshName(self,name):
        self.__objName = name

    def setCurveName(self,name):
        self.__curveName = name

    def unlock_follow_suboptions(self,enabled):
        if enabled:
            self.MainWindowUI.x_front_axis.setEnabled(True)
            self.MainWindowUI.y_front_axis.setEnabled(True)
            self.MainWindowUI.z_front_axis.setEnabled(True)
            self.MainWindowUI.x_up_axis.setEnabled(True)
            self.MainWindowUI.y_up_axis.setEnabled(True)
            self.MainWindowUI.z_up_axis.setEnabled(True)
            self.MainWindowUI.bank_box.setEnabled(True)
            self.MainWindowUI.flow_path_box.setEnabled(True)
        else:
            self.MainWindowUI.x_front_axis.setEnabled(False)
            self.MainWindowUI.y_front_axis.setEnabled(False)
            self.MainWindowUI.z_front_axis.setEnabled(False)
            self.MainWindowUI.x_up_axis.setEnabled(False)
            self.MainWindowUI.y_up_axis.setEnabled(False)
            self.MainWindowUI.z_up_axis.setEnabled(False)
            self.MainWindowUI.bank_box.setEnabled(False)
            self.MainWindowUI.flow_path_box.setEnabled(False)

    def unlock_flow_path(self,enabled):
        if enabled:
            self.MainWindowUI.flow_subdiv_x.setEnabled(True)
            self.MainWindowUI.flow_subdiv_y.setEnabled(True)
            self.MainWindowUI.flow_subdiv_z.setEnabled(True)
        else:
            self.MainWindowUI.flow_subdiv_x.setEnabled(False)
            self.MainWindowUI.flow_subdiv_y.setEnabled(False)
            self.MainWindowUI.flow_subdiv_z.setEnabled(False)

    def check_front_axis(self):
        tmp = ''
        if self.MainWindowUI.x_front_axis.isChecked():
            tmp = 'x'
        elif self.MainWindowUI.y_front_axis.isChecked():
            tmp = 'y'
        elif self.MainWindowUI.z_front_axis.isChecked():
            tmp = 'z'

        return tmp

    def check_up_axis(self):
        tmp = ''
        if self.MainWindowUI.x_up_axis.isChecked():
            tmp = 'x'
        elif self.MainWindowUI.y_up_axis.isChecked():
            tmp = 'y'
        elif self.MainWindowUI.z_up_axis.isChecked():
            tmp = 'z'

        return tmp

    def get_tangent_type(self):
        return str(self.MainWindowUI.tangent_type.currentText())

    def get_flow_path_subdiv(self):
        x = self.MainWindowUI.flow_subdiv_x.value()
        y = self.MainWindowUI.flow_subdiv_y.value()
        z = self.MainWindowUI.flow_subdiv_z.value()
        return [x,y,z]

def runUi(mesh,curve):

    if not cmds.window(UI_NAME,exists=True):
        ui = motionPathToolsConfig()
    else:
        sys.stderr.write("Tool is already open!\n")

    ui.setMeshName(mesh)
    ui.setCurveName(curve)
