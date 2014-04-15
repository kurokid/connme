from PyQt4 import QtGui

class SystemTrayIcon(QtGui.QSystemTrayIcon):
	
	def __init__(self, icon, parent=None):
		QtGui.QSystemTrayIcon.__init__(self, icon, parent)
		menu = QtGui.QMenu(parent)
		#self.showAction = menu.addAction("Setting")
		#self.setContextMenu(menu)
