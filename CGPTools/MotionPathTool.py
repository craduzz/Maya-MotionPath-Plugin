import maya.cmds as cmds
import MotionPathToolSelection
#note, only supports bezier curves
class Main:

    def __init__(self):
        pass

    def openWindow(self):
        MotionPathToolSelection.runUi()