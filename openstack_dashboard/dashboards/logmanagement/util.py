import horizon
import os


config_file = os.path.dirname(os.path.realpath(__file__)) + '/logmanagement.conf'
config = {}

def getConfig(key):	
	with open(config_file) as f:
			data = f.read()
			lines = data.split('\n')
			for line in lines:
				config_line = line.split('=')
				if (config_line[0] and config_line[1]):
					config[config_line[0]] = config_line[1]

	if not config[key]:
		return None

	return config[key]

def setConfig(key, value):
	with open(config_file) as f:
		data = f.read()
		lines = data.split('\n')
		for line in lines:
			config_line = line.split('=')
			if (config_line[0] and config_line[1]):
				config[config_line[0]] = config_line[1]

	config[key] = value

	config_str = ''
	for i in config:
		config_str += i + '=' + config[i] + os.linesep

	f = open(config_file,'w+')
	f.write(config_str)
	f.close() 