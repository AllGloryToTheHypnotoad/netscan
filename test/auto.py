#!/usr/bin/env python

import commands
import sys
import argparse

def pip():
	# update and setuptools first
	print 'pip update pip and setuptools'
	ans = commands.getoutput('pip install -U pip setuptools')
	if ans: print ans
	
	# find outdated packages
	p = commands.getoutput('pip list --outdated').split('\n')
	pkgs = []
	for i in p:
		if i.find('===') > 0: continue
		
		pkg = i.split()[0]
		if pkg == 'Warning:': continue
		elif pkg == 'Could': continue
		elif pkg == 'Some': continue
		elif pkg == 'You': continue
		pkgs.append(pkg)
	
	if not pkgs:
		print 'Nothing needing to be updated'
		exit()
		
	# update packages
	p = ' '.join(pkgs)
	print 'Updating:',p
	ans = commands.getoutput('pip install -U %s'%(p))
	if ans: print ans

def brew():
	print '-[brew]----------'
	print 'brew update'
	ans = commands.getoutput('brew update')
	if ans: print ans
	print 'brew upgrade packages'
	ans = commands.getoutput('brew upgrade')
	if ans: print ans
	
	print 'brew prune old sym links'
	ans = commands.getoutput('brew prune')
	if ans: print ans
	print 'brew cleanup old packages'
	ans = commands.getoutput('brew cleanup')
	if ans: print ans

def kernel():
	ans=commands.getoutput('uname -a')
	arm = ans.find('arm')
	
	# this is not an ARM linux computer ... can't do this
	if arm == -1: return
	
	commands.getoutput('apt-get upgrade rpi-update')
	commands.getoutput('rpi-update')	

def aptget():
	ans=commands.getoutput('apt-get update')
	if ans: print ans
	ans=commands.getoutput('apt-get upgrade')
	if ans: print ans

def getArgs():
	parser = argparse.ArgumentParser('A simple automation tool to update your system.')
	parser.add_argument('-p', '--no_pip', help='do not update pip', action='store_true')
	parser.add_argument('-t', '--no_tools', help='do not update system tools', action='store_true')
	args = vars(parser.parse_args())
	
	return args

def main():
	args = getArgs()
	
	if args['no_pip']: pass
	else: pip()
	
	if args['no_tools']: pass
	else:
		system = sys.platform
		if system == 'darwin': brew()
		elif system == 'linux' or system == 'linux2': 
			aptget()
			kernel()
		
	
if __name__ == "__main__":
  main()