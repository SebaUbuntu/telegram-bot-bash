from homebot.core.config import get_config
from homebot.modules.ci.artifacts import Artifacts
from telegram.error import TimedOut, RetryAfter
from time import sleep

chat_id = get_config("ci.channel_id")

class PostManager:
	def __init__(self, project, device: str, artifacts: Artifacts):
		"""Initialize PostManager class."""
		self.project = project
		self.device = device
		self.artifacts = artifacts
		self.base_message_text = self.get_base_message_text()
		self.message = self.project.context.bot.send_message(chat_id, self.base_message_text)

	def get_base_message_text(self):
		text =  f"🛠 CI | {self.project.name} {self.project.version} ({self.project.android_version})\n"
		text += f"Device: {self.device}\n"
		text += f"Lunch flavor: {self.project.lunch_prefix}_{self.device}-{self.project.lunch_suffix}\n"
		text += "\n"
		return text

	def update(self, status: str):
		text = self.base_message_text
		text += f"Status: {status}\n"
		text += "\n"
		if self.artifacts.artifacts:
			text += self.artifacts.get_readable_artifacts_list()
		self.edit_text(text)

	def edit_text(self, text):
		# FIXME:
		# telegram.vendor.ptb_urllib3.urllib3.exceptions.ReadTimeoutError:
		# HTTPSConnectionPool(host='api.telegram.org', port=443):
		# Read timed out. (read timeout=5.0)
		try:
			return self.message.edit_text(text)
		except RetryAfter as err:
			# Just in case
			sleep(err.retry_after + 5)
			return self.edit_text(text)
		except TimedOut:
			pass
