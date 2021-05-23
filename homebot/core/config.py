from homebot import config

def get_config(name, default=None):
	if not name in config:
		return default

	if config[name] == "":
		return default

	return config[name]
