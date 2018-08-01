import sys
import os
import time


history = """
Create shell scripts for ImE with several different requirements

Version History:
Date		Description

04/oct/2016	Draft

"""

clear_string = "clear"

#-----------------------------------------------------------------------------
#	validSysPort function
#	Validate the SYSTEM|PORTAL information retrieved by user
#-----------------------------------------------------------------------------
def validSysPort(sSystem, sPortal):

	# Make a validation on the above information:
	fReturn	= os.popen("echo plan -equip=" + sSystem.strip() + " -portal=" + sPortal.strip() + " | dcs_dportal_utl")
	sAux	= fReturn.readlines()

	if len(sAux) == 0:
		raw_input("\nSYSTEM: [" + sSystem + "] PORTAL:[" + sPortal + "] Empty content...\nIs ImE environment loaded?\n")
		sys.exit()

	sReturn	= sAux[1]

	# Found the SYSTEM|PORTAL on ImE instance
	if sReturn.find("is using") > 0:
		return True
	else:
		raw_input("\nSYSTEM: [" + sSystem + "] PORTAL:[" + sPortal + "] not found...\n")
		sys.exit()


#-----------------------------------------------------------------------------
#	inputMasterName function
#	Retrieve master file name and it's sequential number
#	Will be used by other functions
#-----------------------------------------------------------------------------
def inputMasterName():
	# init variables:
	sSystem		= ""
	sPortal		= ""
	iInitSeq	= 0
	iEndSeq		= 0
	sResponse	= ""
	bAll		= False
	iCount		= 0
	lMaster		= []

	#=============================================================================
	# Creating the master file ID
	while sSystem == "":
		sSystem 	= raw_input("\nExternal System name: ").strip()
	while sPortal == "":
		sPortal 	= raw_input("\nInput Portal name: ").strip()
	#=============================================================================

	# Validate system portal
	validSysPort(sSystem, sPortal)
	sMasterFile	= sSystem + "_" + sPortal + "_"

	iSeqFlag	= False
	while iSeqFlag == False:
		while True:
			iInitSeq	= raw_input("\nInitial Sequence number: ").strip()
			if iInitSeq.isdigit() == False:
				print ("\n\nNot a valid number!")
			elif int(iInitSeq) < 0 or len(iInitSeq) > 999999:
				print ("\n\nNumber must be between 0-999999!")
			else:
				iInitSeq	= int(iInitSeq)
				break

		while True:
			iEndSeq	= raw_input("\nEnd Sequence number: ")
			if iEndSeq.isdigit() == False:
				print ("\n\nNot a valid number!")
			elif int(iEndSeq) < 0 or len(iEndSeq) > 999999:
				print ("\n\nNumber must be between 0-999999!")
			else:
				iEndSeq		= int(iEndSeq)
				break

		if int(iEndSeq) > int(iInitSeq):
			iSeqFlag	= True
		else:
			print ("\n\nEnd sequence must be greater that initial sequence")

	return str(iInitSeq), str(iEndSeq), sMasterFile


#-----------------------------------------------------------------------------
#	createCPfile function
#	Create file with a list of 'cp' commands to a user defined directory
#	if no directory is specified, use user 'home' directory as default
#-----------------------------------------------------------------------------
def createCPfile(fseq, lseq, master_):

	ffilename = "COPY_" + master_ + fseq + "_" + lseq + ".txt"

	while True:
		cpPath = raw_input("\nSet destination path: ")
		if os.path.isdir(cpPath) == False:
			print "Invalid directory!!!"
		else:
			break

	ffile = open(ffilename, 'w')
	i = int(fseq)

	while i <= int(lseq):
		f_ret = os.popen('echo get ' + master_ + str(i).zfill(6) + '.dat | dcs_filreg_inquire_util')
		l_ret = f_ret.readlines()

		master_path = None
		orig_name = None
		for n in l_ret:
			if n.find("Path") > 0:
				tmp = n.strip()
				master_path = tmp[tmp.find('/'):]
			if n.find("External File Name") > 0:
				tmp = n.strip()
				orig_name = tmp[tmp.find(':')+1:].strip()
		if master_path != None and orig_name != None:
			ffile.write("cp " + master_path + '/' + master_ + str(i).zfill(6) + '.dat ' + cpPath + '/' + orig_name + '\n')
		i += 1
	

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
		1) Create text file which copies processed Master Files in a specific directory with the 
		   original file name based on master file range 

		98)Version History
		99)Exit

		Option: """)

		sSelection.strip()
		sSelection.lstrip('0')

		if sSelection == '1':
			fseq, lseq, master_ = inputMasterName()
			createCPfile(fseq, lseq, master_)			
		elif sSelection == '98':
			raw_input(history)
			os.system(clear_string)
		else:
			print "quitting..."
			time.sleep(.5)
			os.system(clear_string)
			sys.exit()


if __name__ == "__main__":
	main()
