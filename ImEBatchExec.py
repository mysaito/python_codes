import sys
import os
#import time

history = """
Create shell scripts for ImE with several different requirements

Version History:
Date		Description

13/oct/2008	Script creation
20/oct/2008	Include option to remove master file also
21/oct/2008	Include menu options 81 and 82
27/oct/2008	Include menu options 4, 5 and 6
17/dec/2008	Change option 6 to be BL specific

"""

clear_string = "clear"


#-----------------------------------------------------------------------------
#	removeDerived function
#	Create a file used to remove all descendent files which contain
#	an specific interval of sequence number for specific SYSTEM|PORTAL
#-----------------------------------------------------------------------------
def removeDerived(lFiles):
	sFileName	= ""
	sMasterFlag	= ""
	iCount	= 0

	while sFileName == "":
		sFileName	= raw_input("\nType the desired file name: ")

	while sMasterFlag.upper() not in ('Y', 'N', 'YES', 'NO'):
		sMasterFlag	= raw_input("\nShould master file be removed?\nType (Y/N): ")

	sFileName	= sFileName + ".sh"
	fHandle	= open("./" + sFileName, 'w')

	fHandle.write("dcs_filreg_inquire_util << -EOF\n")

	while iCount < len(lFiles):
		if sMasterFlag.upper() in ('Y', 'YES'):
			fHandle.write("remove " + lFiles[iCount] + " -OVERRIDE -MASTER_ALSO\n")
		else:
			fHandle.write("remove " + lFiles[iCount] + " -OVERRIDE\n")
		iCount	+= 1

	fHandle.write("EOF\n")

	fHandle.close()


#-----------------------------------------------------------------------------
#	reprocMaster function
#	Create a file used to reprocess all master files which contain
#	an specific interval of sequence number for specific SYSTEM|PORTAL
#-----------------------------------------------------------------------------
def reprocMaster(lFiles):
	sFileName	= ""
	sPlanName	= ""
	iCount	= 0

	while sFileName == "":
		sFileName	= raw_input("\nType the desired file name: ")
	while sPlanName == "":
		sPlanName	= raw_input("\nType the associated plan name: ")

	sFileName	= sFileName + ".sh"
	fHandle	= open("./" + sFileName, 'w')

	fHandle.write("dcs_filreg_inquire_util << -EOF\n")

	while iCount < len(lFiles):
		fHandle.write("LAUNCH " + lFiles[iCount] + " -plan="  + sPlanName + "\n")
		iCount	+= 1

	fHandle.write("EOF\n")

	fHandle.close()


#-----------------------------------------------------------------------------
#	clearDRD function
#	Retrieve master file name and it's sequential number
#	Will be used by other functions
#-----------------------------------------------------------------------------
def clearDRD():
	sFileName	= ""
	sDrdArea	= ""
	iCount		= 0
	lDrdList	= []

	while sFileName == "":
		sFileName	= raw_input("\nType the desired file name: ")
	while sDrdArea == "":
		sDrdArea	= raw_input("\nType DRD area name separeted by (,): ")

	sFileName	= sFileName + ".sh"
	lDrdList	= sDrdArea.split(',')

	fHandle	= open("./" + sFileName, 'w')

	fHandle.write("drd_utl << -EOF\n")

	while iCount < len(lDrdList):
		fHandle.write("echo delete_pf_by_area -area_name=" + lDrdList[iCount].strip() + " | drd_utl\n")
		fHandle.write("echo delete_isam_by_area -area_name=" + lDrdList[iCount].strip() + " | drd_utl\n")
		fHandle.write("echo reset " + lDrdList[iCount].strip() + " | drd_utl\n")
		iCount	+= 1

	fHandle.write("EOF\n")

	fHandle.close()


#-----------------------------------------------------------------------------
#	removeAllDerived function
#	Create a file used to remove all descendent files on system
#-----------------------------------------------------------------------------
def removeAllDerived():
	sFileName	= ""
	sMasterFlag	= ""

	while sFileName == "":
		sFileName	= raw_input("\nType the desired file name: ")

	while sMasterFlag.upper() not in ('Y', 'N', 'YES', 'NO'):
		sMasterFlag	= raw_input("\nShould master file be removed?\nType (Y/N): ")

	sFileName	= sFileName + ".sh"

	fReturn	= os.popen("echo req_get -h=first -all -brief |dcs_plan_utl | grep '.dat'")
	lReturn	= fReturn.readlines()
	fReturn.close()

	# List will contain all Master file's name
	lMaster	= []
	iCount	= 0

	while iCount < len(lReturn):
		sMaster	= lReturn[iCount].split('|')[1]
		if lMaster.count(sMaster) == 0:
			lMaster.append(sMaster)
		iCount += 1

	fHandle	= open("./" + sFileName, 'w')

	fHandle.write("dcs_filreg_inquire_util << -EOF\n")

	iCount	= 0
	while iCount < len(lMaster):
		if sMasterFlag.upper() in ('Y', 'YES'):
			fHandle.write("remove " + lMaster[iCount] + " -OVERRIDE -MASTER_ALSO\n")
		else:
			fHandle.write("remove " + lMaster[iCount] + " -OVERRIDE\n")
		iCount	+= 1

	fHandle.write("EOF\n")

	fHandle.close()


#-----------------------------------------------------------------------------
#	reprocAllDerived function
#	Create a file used to reprocess all master files on system
#-----------------------------------------------------------------------------
def reprocAllDerived():
	sFileName	= ""

	while sFileName == "":
		sFileName	= raw_input("\nType the desired file name: ")

	sFileName	= sFileName + ".sh"

	fReturn	= os.popen("echo iget -first -all -brief |dcs_filreg_utl | grep '.dat'")
	lReturn	= fReturn.readlines()
	fReturn.close()

	# List lMaster will contain all Master file's name
	lMaster	= []
	iCount	= 0

	while iCount < len(lReturn):
		sMaster	= lReturn[iCount].split('-')[0].strip()
		fBl	= os.popen("echo get file_info " + sMaster + " -PLAN_ID |dcs_filreg_utl")
		lBl	= fBl.readlines()
		sBl	= lBl[2].split('=')[1].strip()
		sMaster	= sMaster + ";" + sBl
		print (sMaster)
		if lMaster.count(sMaster) == 0:
			lMaster.append(sMaster)
		iCount += 1

	fHandle	= open("./" + sFileName, 'w')

	fHandle.write("dcs_filreg_inquire_util << -EOF\n")

	iCount	= 0

	while iCount < len(lMaster):
		fHandle.write("LAUNCH " + lMaster[iCount].split(';')[0] + " -plan=" + lMaster[iCount].split(';')[1] + "\n")
		iCount	+= 1

	fHandle.write("EOF\n")

	fHandle.close()


#-----------------------------------------------------------------------------
#	removeAssem() function
#	Create a file used to remove all Assembled derived files for specific BL
#-----------------------------------------------------------------------------
def removeAssem():
	sFileName	= ""
	sMasterFlag	= ""
	sBusinessLogic	= ""

	while sFileName == "":
		sFileName	= raw_input("\nType the desired file name: ")

	while sMasterFlag.upper() not in ('Y', 'N', 'YES', 'NO'):
		sMasterFlag	= raw_input("\nShould master file be removed?\nType (Y/N): ")

	while sBusinessLogic == "":
		sBusinessLogic	= raw_input("\nType associated BL (type ALL for all assembled in instance): ")

	sFileName	= sFileName + ".sh"

	# List all master files
	fReturn	= os.popen("echo req_get -h=first -all -brief |dcs_plan_utl | grep '|' | grep " + sBusinessLogic)
	lReturn	= fReturn.readlines()
	fReturn.close()

	# List will contain all Master file's name
	lMaster	= []
	iCount	= 0

	while iCount < len(lReturn):

		sMaster	= lReturn[iCount].split('|')[1]
		if lMaster.count(sMaster) == 0:
			lMaster.append(sMaster)
		iCount += 1

	# Ok. 'lMaster' will contain all master file's ID at this point.
	# Now let's separate the assembly master files:
	iCount	= 0
	lAssem	= []
	while iCount < len(lMaster):
		fReturn	= os.popen("echo get_ftype " + lMaster[iCount] + " | dcs_filreg_utl")
		lReturn	= fReturn.readlines()
		if lReturn[3].find("ASSEMBLED") >= 0:
			lAssem.append(lMaster[iCount])
		iCount += 1
		fReturn.close()

	# At this point, 'lAssem' will have all assembly master file's name
	raw_input( str(lAssem))

	fHandle	= open("./" + sFileName, 'w')

	fHandle.write("dcs_filreg_inquire_util << -EOF\n")

	iCount	= 0
	while iCount < len(lAssem):
		if sMasterFlag.upper() in ('Y', 'YES'):
			fHandle.write("remove " + lAssem[iCount] + " -OVERRIDE -MASTER_ALSO\n")
		else:
			fHandle.write("remove " + lAssem[iCount] + " -OVERRIDE\n")
		iCount	+= 1

	fHandle.write("EOF\n")

	fHandle.close()



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
#	renameFiles function
#	Rename all '.old' files in a path indicated by user:
#-----------------------------------------------------------------------------
def renameFiles():
	sPath	= ""
	lList	= []
	iCount	= 0
	while sPath == "":
		sPath 	= raw_input("\nIndicate the path where the files are situated: ").strip()

	os.chdir(sPath)

	lList	= os.listdir(sPath)

	while iCount < len(lList):
		if lList[iCount][-4:] == ".old":
			os.rename(lList[iCount], lList[iCount][:-4])
		iCount += 1


#-----------------------------------------------------------------------------
#	splitFile function
#	Split a file by row number
#-----------------------------------------------------------------------------
def splitFile():
	sTargetFile	= ""
	sRowCount	= ""

	bFileFlag	= True

	lFileRows	= []
	iFileSeq	= 0	# file sequence as extension
	iRowCount	= 0	# count the number of rows for each sub-file
	iCount		= 0	# count the number of rows of the master file

	while sTargetFile == "":
		sTargetFile 	= raw_input("\nType the target original file name: ").strip()

	# File Validation
	bFileFlag	= os.access(sTargetFile, os.F_OK)
	if (bFileFlag == False):
		raw_input("\nNot possible to access file.\nCheck file existence and its permission\n")
		sys.exit()

	fHandle		= open(sTargetFile, 'r')
	lFileRows	= fHandle.readlines()
	fHandle.close()

	while sRowCount == "" and sRowCount.isdigit() == False:
		sRowCount 	= raw_input("\nIndicate the number of rows that each sub-file must have: ").strip()

	while iCount < len(lFileRows):
		iRowCount	= 0
		fSubHandle	= open(sTargetFile + "." + str(iFileSeq).zfill(3), "w")
		while iRowCount < int(sRowCount):
			fSubHandle.write(lFileRows[iCount])
			iRowCount	+= 1
			iCount		+= 1
			if (iCount == len(lFileRows)):
				break
		fSubHandle.close()
		iFileSeq	+= 1


#-----------------------------------------------------------------------------
#	selectRows function
#	Create a new file containing the rows selected by user
#-----------------------------------------------------------------------------
def selectRows():
	sTargetFile	= ""
	sUserSelection	= ""

	bFileFlag	= True
	bCharFlag	= True
	bContent	= True

	lSelectedRows	= []
	lFileRows	= []
	iRowCount	= 0	# count the number of rows for each sub-file
	iCount		= 0	# count the number of rows of the master file

	while sTargetFile == "":
		sTargetFile 	= raw_input("\nType the target original file name: ").strip()

	# File Validation
	bFileFlag	= os.access(sTargetFile, os.F_OK)
	if (bFileFlag == False):
		raw_input("\nNot possible to access file.\nCheck file existence and its permission\n")
		sys.exit()

	fHandle		= open(sTargetFile, 'r')
	lFileRows	= fHandle.readlines()
	fHandle.close()

	# Selection Validation on user options
	while sUserSelection == "" or bCharFlag == False:
		bCharFlag	= True
		sUserSelection	= raw_input("\nType the rows to include in the new file.\nUse '-' to get a range of rows and ',' to get separate itens: ").strip()
		while iCount < len(sUserSelection):
			if sUserSelection[iCount].isdigit() == False and sUserSelection[iCount] not in (',', '-', ' '):
				bCharFlag = False
			iCount	+= 1

	lSelectedRows	= sUserSelection.split(',')

	# Selection Validation on passed content
	iCount	= 0
	while iCount < len(lSelectedRows):
		if lSelectedRows[iCount].strip().find('-') >= 0:
			# Check if the first parameter is lower than second parameter
			if int(lSelectedRows[iCount][:lSelectedRows[iCount].find('-')]) >= int(lSelectedRows[iCount][lSelectedRows[iCount].find('-') + 1:]):
				bContent	= False
			# Check if the parameters are lower than file's highest row
			if int(lSelectedRows[iCount][:lSelectedRows[iCount].find('-')]) >= len(lFileRows):
				bContent	= False
			if int(lSelectedRows[iCount][lSelectedRows[iCount].find('-') + 1:]) >= len(lFileRows):
				bContent	= False
		else:
			# Check if the parameter is lower than file's highest row
			if int(lSelectedRows[iCount]) >= len(lFileRows):
				bContent	= False

		if bContent == False:
			raw_input("\nInvalid parameter: " + str(lSelectedRows[iCount]) + "\n")
			sys.exit()
		iCount	+= 1

	fNewHandle	= open(sTargetFile + ".new", 'w')
	iCount	= 0
	while iCount < len(lSelectedRows):
		if lSelectedRows[iCount].strip().find('-') >= 0:
			iRange	= int(lSelectedRows[iCount][:lSelectedRows[iCount].find('-')])
			while iRange < int(lSelectedRows[iCount][lSelectedRows[iCount].find('-') + 1:]):
				fNewHandle.write(lFileRows[iRange - 1])
				iRange	+= 1
		else:
			fNewHandle.write(lFileRows[int(lSelectedRows[iCount]) - 1])
		iCount	+= 1

	fNewHandle.close()


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

	validSysPort(sSystem, sPortal)
	sMasterFile	= sSystem + "_" + sPortal + "_"

	while sResponse.upper() not in ('Y', 'YES', 'N', "NO"):
		sResponse 	= raw_input("\nShould all master files be included?\n(Type Y or N): ").strip()

	if sResponse.upper() in ('Y', 'YES'):
		bAll	= True
	else:
		iSeqFlag	= False
		while iSeqFlag == False:
			while iInitSeq == 0:
				iInitSeq	= raw_input("\nInitial Sequence number: ")
				if iInitSeq.isdigit() == False:
					iInitSeq	= 0
					print ("\n\nNot a valid number!")
				elif int(iInitSeq) < 0 or len(iInitSeq) > 999999:
					iInitSeq	= 0
					print ("\n\nNumber must be between 0-999999!")
				else:
					iInitSeq	= int(iInitSeq)

			while iEndSeq == 0:
				iEndSeq	= raw_input("\nEnd Sequence number: ")
				if iEndSeq.isdigit() == False:
					iEndSeq		= 0
					print ("\n\nNot a valid number!")
				elif int(iEndSeq) < 0 or len(iEndSeq) > 999999:
					iEndSeq		= 0
					print ("\n\nNumber must be between 0-999999!")
				else:
					iEndSeq		= int(iEndSeq)

			if int(iEndSeq) > int(iInitSeq):
				iSeqFlag	= True
			else:
				print ("\n\nEnd sequence must be greater that initial sequence")

	# Creating a list of all valid master_id sequence numbers:
	# First, get the existent master files:
	fReturn	= os.popen("echo iget -key_id=0 -first -all -br | dcs_filreg_utl | grep " + sMasterFile + " | grep dat")
	lReturn	= fReturn.readlines()
	while iCount < len(lReturn):
		lReturn[iCount]	= lReturn[iCount].split(' ')[0]
		iCount += 1

	iCount		= 0
	# If the user had specified specific sequence number interval:
	if bAll == False:
		iSeqCount	= iEndSeq - iInitSeq
		while iCount <= iSeqCount:
			sUserMaster	= sMasterFile + str(iInitSeq + iCount).zfill(6) + ".dat"
			if sUserMaster in lReturn:
				lMaster.append(sUserMaster)
			iCount += 1
	else:
		while iCount < len(lReturn):
			lMaster.append(lReturn[iCount])
			iCount += 1

	if len(lMaster) == 0:
		raw_input("There are no files processed for this SYSTEM|PORTAL - [" + sSystem + "|" + sPortal + "]\n\nPress any key to exit\n")
		sys.exit()

	return lMaster


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
		1) Create a .sh file to remove derived files for specific SYSTEM|PORTAL
		2) Create a .sh file to reprocess master files for specific SYSTEM|PORTAL
		3) Create a .sh file to clean DRD area(s)
		4) Create a .sh file to remove ALL derived files in instance
		5) Create a .sh file to reprocess ALL derived files in instance
		6) Create a .sh file to remove assembled files associated for specific BL (May remove master also)

		File Manipulation
		80)Rename all .old files of specific path
		81)Split file by row count
		82)Split file by rows selected by user

		98)Version History
		99)Exit:

		Option: """)

		sSelection.strip()
		sSelection.lstrip('0')

		if sSelection == '1':
			lFiles	= inputMasterName()
			removeDerived(lFiles)
		elif sSelection == '2':
			lFiles	= inputMasterName()
			reprocMaster(lFiles)
		elif sSelection == '3':
			clearDRD()
		elif sSelection == '4':
			removeAllDerived()
		elif sSelection == '5':
			reprocAllDerived()
		elif sSelection == '6':
			removeAssem()
		elif sSelection == '80':
			renameFiles()
		elif sSelection == '81':
			splitFile()
		elif sSelection == '82':
			selectRows()
		elif sSelection == '98':
			raw_input(history)
		elif sSelection == '99':
			sys.exit()


if __name__ == "__main__":
	main()
