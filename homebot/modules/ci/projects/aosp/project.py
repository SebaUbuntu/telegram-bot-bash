from datetime import datetime
from pathlib import Path
from homebot import bot_path
from homebot.core.config import get_config
from homebot.core.error_handler import format_exception
from homebot.core.logging import LOGE
from homebot.lib.libupload import Uploader
from homebot.modules.ci.artifacts import STATUS_NOT_UPLOADED, STATUS_UPLOADED, STATUS_UPLOADING, Artifacts
from homebot.modules.ci.parser import CIParser
from homebot.modules.ci.project import ProjectBase
from homebot.modules.ci.projects.aosp.post import PostManager
from homebot.modules.ci.projects.aosp.returncode import ERROR_CODES, NEEDS_LOGS_UPLOAD, SUCCESS
import re
import subprocess
from telegram.ext import CallbackContext
from telegram.update import Update

class AOSPProject(ProjectBase):
	"""
	This class represent an AOSP project.
	"""
	# This value will also be used for folder name
	name: str
	# Version of the project
	version: str
	# Android version to display on Telegram post
	android_version: str
	# Name of the parent folder used when uploading
	category: str
	# These next 2 values are needed for lunch (e.g. "lineage"_whyred-"userdebug")
	lunch_prefix: str
	lunch_suffix: str
	# Target to build (e.g. to build a ROM's OTA package, use "bacon" or "otapackage", for a recovery project, use "recoveryimage")
	build_target: str
	# Filename of the output. You can also use wildcards if the name isn't fixed
	artifacts: str

	def __init__(self, update: Update, context: CallbackContext, args: list[str]):
		"""Initialize AOSP project class."""
		super().__init__(update, context, args)
		parser = CIParser(prog="/ci")
		parser.set_output(self.update.message.reply_text)
		parser.add_argument('device', help='device codename')
		parser.add_argument('-ic', '--installclean', help='make installclean before building', action='store_true')
		parser.add_argument('-c', '--clean', help='make clean before building', action='store_true')
		parser.set_defaults(clean=False, installclean=False)
		self.parsed_args = parser.parse_args(args)

	def build(self):
		project_dir = Path(f"{get_config('ci.main_dir', '')}/{self.name}-{self.version}")
		device_out_dir = project_dir / "out" / "target" / "product" / self.parsed_args.device

		artifacts = Artifacts(device_out_dir, self.artifacts)
		post_manager = PostManager(self, self.parsed_args.device, artifacts)

		if self.parsed_args.clean is True:
			clean_type = "clean"
		elif self.parsed_args.installclean is True:
			clean_type = "installclean"
		else:
			clean_type = "none"

		post_manager.update("Building")

		command = [bot_path / "modules" / "ci" / "projects" / "aosp" / "tools" / "building.sh",
				"--sources", project_dir,
				"--lunch_prefix", self.lunch_prefix,
				"--lunch_suffix", self.lunch_suffix,
				"--build_target", self.build_target,
				"--clean", clean_type,
				"--device", self.parsed_args.device]

		last_edit = datetime.now()
		process = subprocess.Popen(command, encoding="UTF-8",
								stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		while True:
			output = process.stdout.readline()
			if output == '' and process.poll() is not None:
				break
			if not output:
				continue

			now = datetime.now()
			if (now - last_edit).seconds < 150:
				continue

			result = re.search(r"\[ +([0-9]+% [0-9]+/[0-9]+)\]", output.strip())
			if result is None:
				continue
			result_split = str(result.group(1)).split()
			if len(result_split) != 2:
				continue

			percentage, targets = re.split(" +", result.group(1))
			post_manager.update(f"Building: {percentage} ({targets})")

			last_edit = now

		returncode = process.poll()

		# Process return code
		build_result = ERROR_CODES.get(returncode, "Build failed: Unknown error")

		post_manager.update(build_result)

		needs_logs_upload = NEEDS_LOGS_UPLOAD.get(returncode, False)
		if needs_logs_upload != False:
			log_file = open(project_dir / needs_logs_upload, "rb")
			self.context.bot.send_document(get_config("ci.channel_id"), log_file)
			log_file.close()

		if returncode != SUCCESS or get_config("ci.upload_artifacts", False) is not True:
			return

		# Upload artifacts
		try:
			uploader = Uploader()
		except Exception as e:
			post_manager.update(f"{build_result}\n"
								f"Upload failed: {type(e)}: {e}")
			return

		artifacts.update()

		post_manager.update(build_result)

		for artifact in artifacts.artifacts:
			artifact.status = STATUS_UPLOADING
			post_manager.update(build_result)

			try:
				uploader.upload(artifact.path, Path(self.category) / self.parsed_args.device / self.name / self.android_version)
			except Exception as e:
				artifact.status = f"{STATUS_NOT_UPLOADED}: {type(e)}: {e}"
				LOGE(f"Error while uploading artifact {artifact.name}:\n"
					 f"{format_exception(e)}")
			else:
				artifact.status = STATUS_UPLOADED

			post_manager.update(build_result)
