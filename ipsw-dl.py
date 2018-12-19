#!/usr/bin/python3
import sys
import os
import shutil
import requests
import json
from urllib.request import urlopen
import zipfile
from clint.textui import progress

# extract IPSW filename from URL
def get_filename(url):
	for i in range(len(url)):
		if url[i] == '/':
			position = i + 1
	return url[position:]

# download file
def dl(url, filename, sizeofile):
	# idk the size of the file
	if sizeofile == 0:
		dl_file = urlopen(url)
		with open(filename,'wb') as output:
			output.write(dl_file.read())

	else :
		dl_file = requests.get(url, stream=True)
		with open(filename,'wb') as output:
			for chunk in progress.bar(dl_file.iter_content(chunk_size=1024), expected_size=(sizeofile/1024) + 1):
				if chunk:
					output.write(chunk)
					output.flush()

# download and parse json file
def parse_json(model, version):
	json_file = model + ".json"
	dl("https://api.ipsw.me/v4/device/" + model, json_file, 0)
	
	if version == None:
		data = json.load(open(json_file))
		with open(json_file):
			ios_version = data["firmwares"][0]["version"]
			buildid = data["firmwares"][0]["buildid"]
			url = data["firmwares"][0]["url"]
			size = data["firmwares"][0]["filesize"]

	
	else :
		data = json.load(open(json_file))
		i = -1
		ios_version = data["firmwares"][i]["version"]
		with open(json_file):
			while ios_version != version :
				i += 1
				ios_version = data["firmwares"][i]["version"]
			buildid = data["firmwares"][i]["buildid"]
			url = data["firmwares"][i]["url"]
			size = data["firmwares"][i]["filesize"]

	ipswfile = get_filename(url)
	print("[+] build ID : %s" % buildid)
	print("[+] IPSW : %s" % ipswfile)
	print("[+] URL : %s" % url)
	print("[+] size : %s" % size)
	os.remove(json_file)
	return url, ipswfile, size

def recursive_rm(folder="ipsw"):

	for files in os.listdir(folder):
		file_path = os.path.join(folder, files)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path): shutil.rmtree(file_path)
		except Exception as error:
			print(error)

def usage(toolname):
	# -u stands for unzip, it will decompress firmware to IPSW folder
	print("usage: %s <model> <version> [-u]" % toolname)

if __name__ == '__main__':
	argv = sys.argv
	argc = len(argv)
	decompress = False
	# if you don't specify a version
	# this tool will download the latest firmware for your device
	if argc == 2:
		device = argv[1]
		version = None
	elif argc == 3:
		device = argv[1]
		if argv[2] == "-u":
			decompress = True
			version = None
		else :
			version = argv[2]
	elif argc == 4:
		device = argv[1]
		version = argv[2]
		if argv[3] == "-u":
			decompress = True
		else :
			usage(argv[0])
			sys.exit(-1)
	else :
		usage(argv[0])
		sys.exit(-1)

	url, ipsw, size_of_ipsw = parse_json(device, version)
	dl(url, ipsw, size_of_ipsw)

	if decompress is True:
		dest = "ipsw"
		if os.path.isdir(dest):
			recursive_rm(dest)
		else :
			os.mkdir(dest)

		with zipfile.ZipFile(ipsw,"r") as z:
			print("\n[i] decompressing %s..." % ipsw)
			z.extractall(dest)
