"""Remote upload utils library."""

from ftplib import FTP, error_perm
from homebot.core.config import get_config
from homebot.core.logging import LOGI
import os.path
import paramiko
from pathlib import Path
import shutil

ALLOWED_METHODS = ["localcopy", "ftp", "sftp"]

def ftp_chdir(ftp: FTP, remote_directory: Path):
	if remote_directory == '/':
		ftp.cwd('/')
		return
	if remote_directory == '':
		return
	try:
		ftp.cwd(str(remote_directory))
	except error_perm:
		dirname, basename = os.path.split(str(remote_directory).rstrip('/'))
		ftp_chdir(ftp, dirname)
		ftp.mkd(basename)
		ftp.cwd(basename)
		return True

def sftp_chdir(sftp: paramiko.SFTPClient, remote_directory: Path):
	if remote_directory == '/':
		sftp.chdir('/')
		return
	if remote_directory == '':
		return
	try:
		sftp.chdir(str(remote_directory))
	except IOError:
		dirname, basename = os.path.split(str(remote_directory).rstrip('/'))
		sftp_chdir(sftp, dirname)
		sftp.mkdir(basename)
		sftp.chdir(basename)
		return True

class Uploader:
	def __init__(self):
		"""Initialize the uploader variables."""
		self.method = get_config("libupload.method")
		self.destination_path_base = Path(get_config("libupload.base_dir"))
		self.host = get_config("libupload.host")
		self.port = get_config("libupload.port")
		self.server = self.host if self.port is None else f"{self.host}:{self.port}"
		self.username = get_config("libupload.username")
		self.password = get_config("libupload.password")

		if self.method not in ALLOWED_METHODS:
			raise NotImplementedError("Upload method not valid")

	def upload(self, file: Path, destination: Path):
		"""Upload an artifact using settings from config.env."""
		if not file.is_file():
			raise FileNotFoundError("File doesn't exists")

		if self.destination_path_base is None:
			destination_path = destination
		else:
			destination_path = self.destination_path_base / destination

		LOGI(f"Started uploading of {file.name}")

		if self.method == "localcopy":
			os.makedirs(destination_path, exist_ok=True)
			shutil.copy(file, destination_path)
		elif self.method == "ftp":
			ftp = FTP(self.server)
			ftp.login(self.username, self.password)
			ftp_chdir(ftp, destination_path)
			with open(file, 'rb') as f:
				ftp.storbinary('STOR %s' % file.name, f)
				f.close()
			ftp.close()
		elif self.method == "sftp":
			transport = paramiko.Transport(self.server)
			transport.connect(username=self.username, password=self.password)
			sftp = paramiko.SFTPClient.from_transport(transport)
			sftp_chdir(sftp, destination_path)
			sftp.put(file, file.name)
			sftp.close()
			transport.close()

		LOGI(f"Finished uploading of {file.name}")
		return True
