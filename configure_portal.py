import sys
import os
import time
import pexpect
import getpass


history = """
Configure portals to use local input/output.

Version History:
Date		Description

29/nov/2016	Draft

30/nov/2016 V1.0

"""

clear_string = "clear"
log_file = open('logfile_config_port-'+time.strftime("%Y%m%d%H%M%S",time.localtime())+'.log', 'w')
log_flag = True

def writeLog(msg):
	global log_file, log_flag

	if log_flag == True:
		log_file.write(time.strftime("%Y-%m-%d_%H-%M-%S",time.localtime()) + " - " + msg + '\n')


#-----------------------------------------------------------------------------
#	validSysPort function
#	Validate the SYSTEM|PORTAL information retrieved by user
#-----------------------------------------------------------------------------
def validSysPort(sSystem, sPortal):

	# Make a validation on the above information:
	fReturn	= os.popen("echo plan -equip=" + sSystem.strip() + " -portal=" + sPortal.strip() + " | dcs_dportal_utl")
	sAux	= fReturn.readlines()

	if len(sAux) == 0:
		writeLog("SYSTEM: [" + sSystem + "] PORTAL:[" + sPortal + "] Empty content...\nIs ImE environment loaded?\n")
		return False


	sReturn	= sAux[1]

	# Found the SYSTEM|PORTAL on ImE instance
	if sReturn.find("is using") > 0:
		return True
	else:
		writeLog("SYSTEM: [" + sSystem + "] PORTAL:[" + sPortal + "] not found...\n")
		return False


#-----------------------------------------------------------------------------
#	createList
#	retrieve list of portals and some additional info based on cli_menu utility
#		(13) DPSEARCH     (DPS) : Display Data Portal Configuration
#-----------------------------------------------------------------------------
def createList():

	# init variables:
	child	= pexpect.spawn('cli_menu')
	init_dict	= {}

	ret	= child.expect('CLI_MENU>')
	if ret != 0:
		writeLog("Invalid return...")
		writeLog(child.buffer)
		return init_dict, False

	# Select option 13
	child.sendline('13')
	ret	= child.expect('matching specified criteria')
	if ret != 0:
		writeLog("Invalid return...")
		writeLog(child.buffer)
		return init_dict, False

	# The 'before' buffer contains all the portal list and some garbage
	# convert into list format
	buf_list = child.before.split('\r\n')

	counter = 0
	for i in buf_list:
		# the amount of '|' can be used to determine lines indicating system/portal information.
		# everything else is just garbage
		if i.count('|') != 9:
			pass
		else:
			# break the line for each '|' as it indicates different fields
			aux_l = i.split('|')
			aux_count = 0
			aux_dict = {}

			# 0 - system
			# 1 - portal
			# 2 - type (I/O)
			# 3 - s?
			# 4 - fs id?
			# 5 - fn id?
			# 6 - plan
			# 7 - data type
			# 8 - protocol
			# 9 - fdes

			while aux_count < len(aux_l):
				aux = aux_l[aux_count].strip()

				if aux_count == 0:
					aux_dict['SYSTEM'] = aux
				elif aux_count == 1:
					aux_dict['PORTAL'] = aux
				elif aux_count == 2:
					aux_dict['DP_TYPE'] = aux
				elif aux_count == 3:
					pass
				elif aux_count == 4:
					pass
				elif aux_count == 5:
					pass
				elif aux_count == 6:
					aux_dict['BL'] = aux
				elif aux_count == 7:
					aux_dict['DATA_TYPE'] = aux
				elif aux_count == 8:
					aux_dict['PROTOCOL'] = aux
				elif aux_count == 9:
					aux_dict['FDES'] = aux

				init_dict[counter]=aux_dict

				aux_count += 1
			counter += 1

	# finish cli_menu session
	child.close()

#	print (str(init_dict))

	return init_dict, True


#-----------------------------------------------------------------------------
#	createDirList function
#	given a root directory point, create subdirectories for the local files 
#	based in input and output portal name. Each portal will have one sub-directory
#	eg:
#		<root>/INPUT
#			<root>/input/<SYS>.<PORT>
#		<root>/OUTPUT
#			<root>/output/<SYS>.<PORT>
#-----------------------------------------------------------------------------
def createDirList(dp_dict):

	root_dir = raw_input("insert root path: ")
	if os.path.isdir(root_dir) == False:
		writeLog("Invalid directory!!!")
		return dp_dict, False

	# Start creating the subdirectories:
	# input & output
	input_dir	= root_dir + '/input'
	output_dir	= root_dir + '/output'
	if os.path.isdir(input_dir) == False:
		os.mkdir(input_dir)
	if os.path.isdir(output_dir) == False:
		os.mkdir(output_dir)

	# loop through the dict to create all portals based in system/portal name:
	# and update the passed dict to include the new PATH 
	for i in dp_dict:
		sys		= dp_dict[i]['SYSTEM']
		port	= dp_dict[i]['PORTAL']
		dp_type	= dp_dict[i]['DP_TYPE']

		sts = validSysPort(sys, port)
		if sts == False:
			writeLog("INVALID PORTAL")
			return dp_dict, False

		if dp_type == 'O':
			dp_path = output_dir + '/' + sys + '.' + port
		elif dp_type == 'I':
			dp_path = input_dir + '/' + sys + '.' + port
		# server portal??
		else:
			dp_path = None

		dp_dict[i]['NEW_PATH'] = dp_path
		if os.path.isdir(dp_path) == False:
			os.mkdir(dp_path)

	return dp_dict, True


#-----------------------------------------------------------------------------
#	updPortalList function
#	update portal path configuration to the indicated routing tab
#	
#-----------------------------------------------------------------------------
def updPortalList(dp_dict):

#	while True:
#		user_data = raw_input('Enable portals? (y/n)\n\n***MAKE SURE YOU ARE NOT COLLECTING/GENERATING PRODUCTION DATA FROM NON-PRODUCTION NODE\n\n')
#		if user_data in ['y', 'Y']:
#			enable_flag = True
#			break
#		elif user_data in ['n', 'N']:
#			enable_flag = False
#			break
	while True:
		user_data = raw_input('Which routing? (1-primary route, 2-secondary route, 3-tertiary route)\n')
		if user_data == '1':
			main_rt	= "PRIMARY"
			susp_rt	= ['SECONDARY','TERTIARY']
			break
		elif user_data == '2':
			main_rt	= "SECONDARY"
			susp_rt	= ['PRIMARY','TERTIARY']
			break
		elif user_data == '3':
			main_rt	= "TERTIARY"
			susp_rt	= ['PRIMARY','SECONDARY']
			break

	while True:
		user_data = raw_input('\nServer name: ')
		if len(user_data) > 0:
			serv_nm	= user_data
			break
	while True:
		user_data = raw_input('\nusername: ')
		if len(user_data) > 0:
			user_nm	= user_data
			break
	while True:
		user_data = getpass.getpass('\npassword: ')
		if len(user_data) > 0:
			paswd	= user_data
			break

	# Initialize dcs_dportal_utl program
	child = pexpect.spawn('dcs_dportal_utl')
	ret	= child.expect('DPU>')
	if ret != 0:
		writeLog("Invalid return...")
		writeLog(child.buffer)
		return False

	aux_cnt	= 0
	try:
		for i in dp_dict:
			aux_cnt += 1
			sys.stdout.write("\r%d of %d" % (i,len(dp_dict)))
			sys.stdout.flush()
			writeLog("updating portal %s|%s" % (dp_dict[i]['SYSTEM'], dp_dict[i]['PORTAL']))
			# First need to apply a GET command to the portal:
			get_cmd = 'get routing for %s %s' % (dp_dict[i]['SYSTEM'], dp_dict[i]['PORTAL'])
			child.sendline(get_cmd)
			time.sleep(.1)
#			ret = child.expect_exact(['Primary Get Successful!','DPU>',pexpect.TIMEOUT])
			ret = child.expect_exact(['DPU>',pexpect.TIMEOUT])
			writeLog("command %s" %str(get_cmd))
			writeLog("return %s" %str(ret))
#			writeLog(child.before)
#			writeLog(child.after)
			if ret == 0 and child.before.find('Primary Get Successful!') > 0:
				pass
			else:
				return False
			child.flush()
			# disable alternative routes
			for route_type in susp_rt:
				rt_cmd = 'update routing for %s %s with -route_designation=%s -data_route_status=suspended' % (dp_dict[i]['SYSTEM'], dp_dict[i]['PORTAL'], route_type)
				child.sendline(rt_cmd)
				time.sleep(.1)
#				ret = child.expect_exact(['Update Successful!','DPU>',pexpect.TIMEOUT])
				ret = child.expect_exact(['DPU>',pexpect.TIMEOUT])
				writeLog("command %s" %str(rt_cmd))
				writeLog("return %s" %str(ret))
#				writeLog(child.before)
#				writeLog(child.after)
				if ret == 0 and child.before.find('Update Successful!') > 0:
					pass
				else:
					return False
				child.flush()
			# update portal according to the protocol
			# LOCAL:
			if dp_dict[i]['PROTOCOL'] == "LOCAL":
				res_cls	= "DIR_CLASS"
				upd_cmd	= 'update routing for %s %s with -route_designation=%s -data_route_status=active -data_rtg_mode=DIRECTORY -res_clas=%s -data_tgt_path=%s' % (dp_dict[i]['SYSTEM'], dp_dict[i]['PORTAL'], main_rt, res_cls, dp_dict[i]['NEW_PATH'])
			elif dp_dict[i]['PROTOCOL'] in ["FAI_FTAM", "CFTP", "CFTPI", "FDI", "FAI", "FTP", ]:
				res_cls	= "FTP_CLASS"
				upd_cmd	= "update routing for %s %s with -route_designation=%s -data_route_status=active -data_rtg_mode=CLI -res_clas=%s -data_tgt_name=%s -data_tgt_login=%s -data_tgt_security=%s -data_tgt_path=%s" % (dp_dict[i]['SYSTEM'], dp_dict[i]['PORTAL'], main_rt, res_cls, serv_nm, user_nm, paswd, dp_dict[i]['NEW_PATH'])
			else:
				writeLog("uneligible PROTOCOL: %s, %s|%s" % (dp_dict[i]['PROTOCOL'], dp_dict[i]['SYSTEM'], dp_dict[i]['PORTAL']))

			if dp_dict[i]['PROTOCOL'] in ["FAI_FTAM", "FDI","FAI",]:
				writeLog("check portal manually for testing - PROTOCOL:%s, %s|%s" % (dp_dict[i]['PROTOCOL'], dp_dict[i]['SYSTEM'], dp_dict[i]['PORTAL']))

			child.sendline(upd_cmd)
			time.sleep(.1)
#			ret = child.expect(['Update Successful!','DPU>',pexpect.TIMEOUT])
			ret = child.expect(['DPU>',pexpect.TIMEOUT])
			writeLog("command %s" %str(upd_cmd))
			writeLog("return %s" %str(ret))
#			writeLog(child.before)
#			writeLog(child.after)
			if ret == 0 and child.before.find('Update Successful!') > 0:
				pass
			else:
				return False

		child.close()
	except Exception, e:
		writeLog("exception raised: %s" % str(e))


#-----------------------------------------------------------------------------
#	Main function - selection of user action
#-----------------------------------------------------------------------------
def main():

	os.system(clear_string)

	sSelection	= ""
	lFiles		= []

	while sSelection != '99':
		os.system(clear_string)
		sSelection	= raw_input ("""
		select an action:

		ImE Proccess
		1) get portal list from local environment

		98)Version History
		99)Exit

		Option: """)

		sSelection.strip()
		sSelection.lstrip('0')

		if sSelection == '1':
			dp_dict, sts = createList()
			break
#		elif sSelection == '2':
#			f = raw_input("insert file name: ")
#			os.system(clear_string)
		elif sSelection == '98':
			raw_input(history)
			os.system(clear_string)
		else:
			print "quitting..."
			time.sleep(.5)
			os.system(clear_string)
			sys.exit()

	os.system(clear_string)
	if sts == False:
		print "quitting..."
		time.sleep(.5)
		sys.exit()
	# test 
#	test_dict = {0: {'FDES': 'STREMUX', 'DP_TYPE': 'O', 'DATA_TYPE': 'TDP_INTAL_FLAT', 'BL': 'n/a', 'SYSTEM': 'TTIWS', 'PORTAL': 'INTAL2', 'PROTOCOL': 'FTP'}, 1: {'FDES': 'STREMUX', 'DP_TYPE': 'O', 'DATA_TYPE': 'TDP_INTAL_FLAT', 'BL': 'n/a', 'SYSTEM': 'TTIWS', 'PORTAL': 'INTAL3', 'PROTOCOL': 'FTP'}, 2: {'FDES': 'AXE463', 'DP_TYPE': 'I', 'DATA_TYPE': 'TDP_AXE463', 'BL': 'TTWA', 'SYSTEM': 'TTWA', 'PORTAL': 'TWA', 'PROTOCOL': 'MTPRBP'}, 3: {'FDES': 'AXE463', 'DP_TYPE': 'I', 'DATA_TYPE': 'TDP_AXE463', 'BL': 'TTWA', 'SYSTEM': 'TTWA_2', 'PORTAL': 'TWA', 'PROTOCOL': 'FAI'}}

	# Create folders, getting a new dict object with additional parameter (NEW PATH)
#	dp_dict_upd, sts = createDirList(test_dict)
	dp_dict_upd, sts = createDirList(dp_dict)
	if sts == False:
		print "quitting..."
		time.sleep(.5)
		sys.exit()

	# Change portal configuration:
	sts = updPortalList(dp_dict_upd)
	

if __name__ == "__main__":
	main()
