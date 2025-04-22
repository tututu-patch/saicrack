import os, io, shutil, time, re, struct

def replaceN():
	# open sai2.exe and find N
	fsai2 = io.FileIO("sai2.exe", 'r+')
	content = fsai2.read()
	pos = content.find(b"\x83\xB0\xBC\x5C\xD1\x61\xAE\x1E\x3A\x64\x68\x7C\x41\x6D\xB3\x22\x48\x87\xBB\x18\xD7\x2B\xCA\xB0\x89\xCF\xC2\xC6\x5C\x2E\xBB\xCF\x45\x22\x3A\x86\x9C\x86\xA7\xCB\xA9\x05\x84\x0D\xC0\xFA\x0D\x5C\x03\xE7\xBA\x00\x96\x32\x96\xEC\x50\xA5\xBD\xAD\xEF\xFF\xA2\x94\xEC\x1F\xF9\x0E\x39\xA2\x3D\x21\x16\xD7\x61\x85\xDD\x96\x65\xCB\x77\xB4\xFE\x1C\x28\x63\x2F\x75\x74\x2C\x1D\xDB\xC0\x83\xBD\x05\xD8\x9A\x15\xD1\xAF\x1B\xAA\xAE\xB0\xBE\x4C\x17\xC1\xFD\x28\x40\x8C\xD6\xB6\xB7\x8A\x86\xA7\x66\x57\x6A\xFF\xEA\xA7\xDF\x2E\xBF")
	# no known N is found
	if pos == -1:
		print("does not support this version of sai")
		fsai2.close()
		return False

	# write back new N
	fsai2.seek(pos)
	fsai2.write(b"\x09\x0A\xE8\x4E\x68\x96\x88\x02\x86\x2F\x9E\x29\x45\xE5\xF5\x0D\x8B\x14\x20\x5C\xA1\xD7\xC8\x11\x4E\xE1\x71\xBC\xDA\x92\x61\x15\xE1\x90\x81\x2F\x12\xB2\xDF\xBE\x78\x60\x92\xAC\x7F\x9A\x05\x0F\xA9\x76\x98\x2F\x91\x47\xE9\xFC\xEE\xD4\x44\xF1\x60\x8D\xE2\x13\x4C\x60\xF4\xE6\x37\x68\xF4\xC7\xA0\xD6\x02\xEA\x9D\x92\xEE\x39\x64\x6F\xA6\x29\x85\x9D\x64\x6C\x66\xBA\xA4\xDC\x59\x25\xBD\x35\xAF\x38\x4F\x98\x82\xAD\xD2\xAD\x2D\x9A\xA4\xEE\xE8\x5D\x88\x49\x44\x7C\x1A\xCC\xDC\x9F\xB3\xDD\xC3\x69\x34\x3C\xEC\x82\x8F\x9B")
	fsai2.close()


	return True

def create_license():
	sysid = ""
	while True:
		sysid = input("System ID:")
		
		# len
		if len(sysid) != 8:
			print("System ID length must be 8 char, therwise unsupported.")
			continue
		
		# validate char
		lstInvalidChar = re.findall(r"[^0-9a-fA-F]", sysid)
		if len(lstInvalidChar):
			print(("invalid char found: %s" % str(lstInvalidChar)[1:-1]))
			continue

		break

	# get number M
	M = "000000010000000000000001000000000000000000000000%s00000001" % sysid
	try:
		nM = int(M, 16)
	except:
		return False
	# get number D
	nD = 0x30C1B95A4BC06DC9FB29FA981CCCCC5826E7FBEF2F251E41E4F25C79CB3D415A0130E88D12CFFAB07196D39C52229D553FA71C032CBE7900E9CB1C03317B34D70667F886E488A2E4C2DFC3BBC225E4709C2A5CDAF4611CF6399AB07F2B86C854940966B607B16BA1F68A18B5FD94141760AA4AFEDD3965E57475FCE84F5F1D35
	# get number N
	nN = 0x9B8F82EC3C3469C3DDB39FDCCC1A7C4449885DE8EEA49A2DADD2AD82984F38AF35BD2559DCA4BA666C649D8529A66F6439EE929DEA02D6A0C7F46837E6F4604C13E28D60F144D4EEFCE947912F9876A90F059A7FAC926078BEDFB2122F8190E1156192DABC71E14E11C8D7A15C20148B0DF5E545299E2F86028896684EE80A09

	# calc
	ans = 1
	while nD != 0:
		if nD & 1 == 1:
			ans = (ans * nM) % nN
		nD >>= 1
		nM = (nM * nM) % nN

	# prepare license data
	slc = []
	while ans:
		slc.append(ans & 0xff)
		ans >>= 8
	
	if len(slc) > 128:
		print("internal error.")
		return False
	if len(slc) < 128:
		slc.extend( [0] * (128-len(slc)) )

	# write license
	try:
		fslc = io.FileIO("license.slc", "w")
		strSlc = struct.pack("<128B", *slc)
		fslc.write(strSlc)
		fslc.close()
	except Exception as e:
		print(("write license.slc failed: maybe no write permission.", e))
		return False

	return True


def docrack():
	# check if file is exist
	if not os.path.isfile("sai2.exe"):
		print("sai2.exe doesn't exists.")
		return False

	# remove previous backup
	for saifile in os.listdir("."):
		# if not a file
		if not os.path.isfile(saifile):
			continue
		
		match = re.match(r"sai2.exe.[0-9]{10}.bak", saifile)
		# do not match
		if match is None:
			continue
		
		# match whole
		if match.group(0) == saifile:
			try:
				os.remove(saifile)
			except:
				pass

	# do backup
	t = time.time()
	bakfile = "sai2.exe.%s.bak" % int(t)
	try:
		shutil.copy("sai2.exe", bakfile)
	except:
		print("backup failed: maybe no write permission.")
		return False

	# check if backup is success
	if not os.path.isfile(bakfile):
		print("backup failed: maybe no write permission.")
		return False

	# create license
	if create_license() is False:
		# try to restore, do nothing if failed
		try:
			os.remove("sai2.exe")
			os.rename(bakfile, "sai2.exe")
		except:
			print("restore backup failed.")
			return False

		print("restore backup success.")
		return False

	# close sai
	while input("close sai if it is opened, type OK to continue:") != "OK":
		pass

	# replaceN
	if replaceN() is False:
		# try to restore, do nothing if failed
		try:
			os.remove("sai2.exe")
			os.rename(bakfile, "sai2.exe")
		except:
			print("restore backup failed.")
			return False

		print("restore backup success.")
		return False

	return True


if __name__ == '__main__':
	ret = False
	try:
		try:
			# info
			print("sai cracker ver 1.0.0\n")
			# do crack
			ret = docrack()
		except Exception as e:
			print(e)
			import traceback
			traceback.print_exc()
			ret = False
	finally:
		if ret is True:
			print("crack success!")
		else:
			print("crack failed!")
	input("Press ENTER key to continue...")

 
