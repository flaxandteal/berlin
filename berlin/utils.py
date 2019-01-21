import appdirs

APPNAME = 'berlin'
APPAUTHOR = 'flaxandteal'

config_dir = appdirs.user_config_dir(APPNAME, APPAUTHOR)
cache_dir = appdirs.user_cache_dir(APPNAME, APPAUTHOR)
