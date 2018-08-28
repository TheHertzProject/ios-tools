#!/usr/bin/python
import sys
import os
sys.path.insert(0, ".")
import decrypt_img
import scrapkeys

# boring part of the code.
# TODO : find a better way
def get_image_type_name(image):
	if image == "ogol" or image == "logo":
		img_type = "applelogo"
	elif image == "0ghc" or image == "chg0":
		img_type = "batterycharging0"
	elif image == "1ghc" or image ==  "chg1":
		img_type = "batterycharging1"
	elif image == "Ftab" or image == "batF":
		img_type = "batteryfull"
	elif image == "0tab" or image == "bat0":
		img_type = "batterylow0"
	elif image == "1tab" or image == "bat1":
		img_type = "batterylow1"
	elif image == "ertd" or image == "dtre":
		img_type = "devicetree"
	elif image == "Cylg" or image == "glyC":
		img_type = "glyphcharging"
	elif image == "Pylg" or image == "glyP":
		img_type = "glyphplugin"
	elif image == "tobi" or image == "ibot":
		img_type = "iboot"
	elif image == "blli" or image == "illb":
		img_type = "llb"
	elif image == "ssbi" or image == "ibss":
		img_type = "ibss"
	elif image == "cebi" or image == "ibec":
		img_type = "ibec"
	elif image == "lnrk" or image == "krnl" :
		img_type = "kernelcache"
	else :
		print("image type not supported : %s" % image)
		img_type = None
	return img_type

def usage(tool):
	print("usage : %s -f <img3 file> -i [iOS version] -d [device]" % tool)
	print("options : ")
	print("-f [IMG3 file]")
	print("-i |iOS version]")
	print("-b [build version]")
	print("-d [device]")

if __name__ == '__main__':
	argv = sys.argv
	argc = len(argv)
	set_ios_version = False
	ios_version = None
	device = None
	build = None
	codename = None

	if argc != 7:
		usage(argv[0])
		sys.exit(1)

	for i in range(0, argc):
		if argv[i] == "-f" :
			file = argv[i + 1]
		elif argv[i] == "-i":
			ios_version = argv[i + 1]
			set_ios_version = True
		elif argv[i] == "-b":
			build = argv[i + 1]
		elif argv[i] == "-d":
			device = argv[i + 1]
		elif argv[i] == "-c":
			codename = argv[i + 1]
		elif argv[i] == "-h":
			usage(argv[0])

	if set_ios_version is True:
		build = scrapkeys.version_or_build(device, ios_version, build)
	else:
		ios_version = scrapkeys.version_or_build(device, ios_version, build)

	if codename is None:
		codename = scrapkeys.get_codename(device, ios_version, build)

	url = "https://www.theiphonewiki.com/wiki/" + codename + "_" + build + "_" + "(" + device + ")"

	magic, image_type = decrypt_img.get_image_type(file)
	image_name = get_image_type_name(image_type)

	print("[x] image : %s" % image_name)
	print("[+] grabbing keys from %s" % url)
	image_keys = scrapkeys.parse_iphonewiki(url, image_name)
	iv = image_keys[:32]
	key = image_keys[-64:]
	print("[+] iv : %s" % iv)
	print("[+] key : %s" % key)
	decrypt_img.decrypt_img(file, file + ".dec", magic, key, iv, openssl='openssl')
	print("[x] done")
