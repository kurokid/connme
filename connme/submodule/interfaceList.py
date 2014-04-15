class Interface():
	'Class untuk memeriksa network interface yang ada'
	def __init__(self):
		self.interfaces = list()
		with open('/proc/net/dev') as f:
                    for interface in f:
                        if ':' in interface:
                            item = interface.split(':')[0].strip()
                            self.interfaces.append(item)
	def __str__(self):
		return(str(self.interfaces))

	def getInterface(self):
		return(self.interfaces)
