"""twrpdtgen CI project."""

from datetime import date
from homebot.core.config import get_config
from homebot.modules.ci.parser import CIParser
from homebot.modules.ci.project import ProjectBase
from git.exc import GitCommandError
from github import Github, GithubException
from pathlib import Path
import requests
from telegram import Update
from telegram.ext import CallbackContext
from tempfile import TemporaryDirectory
from twrpdtgen.device_tree import DeviceTree
from twrpdtgen.info_extractors.buildprop import PARTITIONS

BUILD_DESCRIPTION = ["ro.build.description"] + [f"ro.{partition}.build.description" for partition in PARTITIONS]

class Project(ProjectBase):
	name = "twrpdtgen"

	def __init__(self, update: Update, context: CallbackContext, args: list[str]):
		"""Init twrpdtgen project class."""
		super().__init__(update, context, args)
		parser = CIParser(prog="/ci twrpdtgen")
		parser.set_output(self.update.message.reply_text)
		parser.add_argument('url', help='URL of the image')
		self.parsed_args = parser.parse_args(args)

	def build(self):
		status_message = self.update.message.reply_text("Downloading file...")

		# Download file
		tempdir = TemporaryDirectory()
		path = Path(tempdir.name)
		url = self.parsed_args.url
		file = path / "recovery.img"
		open(file, 'wb').write(requests.get(url, allow_redirects=True).content)

		# Generate device tree
		status_message.edit_text("Generating device tree...")
		try:
			devicetree = DeviceTree(path / "working", recovery_image=file)
		except Exception as e:
			status_message.edit_text("Device tree generation failed\n"
									f"Error: {e}")
			return

		try:
			build_description = devicetree.build_prop_reader.get_prop(BUILD_DESCRIPTION, "build description")
			branch = build_description.replace(" ", "-")
		except AssertionError:
			status_message.edit_text("Failed to get build description prop, using date as a branch")
			today = date.today()
			build_description = None
			branch = f"{today.year}-{today.month}-{today.day}"

		# Upload to GitHub
		status_message.edit_text("Pushing to GitHub...")
		gh_username = get_config("ci.github_username")
		gh_token = get_config("ci.github_token")
		gh_org_name = get_config("ci.twrpdtgen.github_org")
		repo_name = f"android_device_{devicetree.manufacturer}_{devicetree.codename}"
		git_repo_url = f"https://{gh_username}:{gh_token}@github.com/{gh_org_name}/{repo_name}"

		# Get organization
		try:
			gh = Github(gh_token)
			gh_org = gh.get_organization(gh_org_name)
		except GithubException as error:
			status_message.edit_text(f"Failed to get organization\n"
									 f"Error: {error}")
			return

		# Create repo if needed
		status_message.edit_text("Creating repo if needed...")
		try:
			devicetree_repo = gh_org.create_repo(name=repo_name, private=False, auto_init=False)
		except GithubException as error:
			if error.status != 422:
				status_message.edit_text("Repo creation failed\n"
										 f"Error: {error.status} {error}")
				return
			devicetree_repo = gh_org.get_repo(name=repo_name)

		status_message.edit_text("Pushing...")
		try:
			devicetree.git_repo.git.push(git_repo_url, f"HEAD:refs/heads/{branch}")
			devicetree_repo.edit(default_branch=branch)
		except GitCommandError:
			status_message.edit_text("Error: Push to remote failed!")
			return

		status_message.edit_text("Done")

		channel_id = get_config("ci.twrpdtgen.channel_id")
		self.context.bot.send_message(channel_id,
									  "TWRP device tree generated\n"
									  f"Codename: {devicetree.codename}\n"
									  f"Manufacturer: {devicetree.manufacturer}\n"
									  f"Build description: {build_description}\n"
									  f"Device tree: {devicetree_repo.html_url}/tree/{branch}",
									  disable_web_page_preview=True)
