from distutils.core import setup
import sys
import py2exe

sys.argv.append('py2exe')
setup(
	# options = {'py2exe':{'bundle_files':1, 'compressed':True}},
    windows =[{'script':'logConv.py'}],
    # zipfile = None,
    )
