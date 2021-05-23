"""HomeBot CI module."""

from homebot.core.config import get_config
from homebot.core.error_handler import format_exception
from homebot.core.logging import LOGE, LOGI
from homebot.core.modules_manager import ModuleBase
from homebot.lib.libadmin import user_is_admin
from homebot.modules.ci.parser import CIParser
from homebot.modules.ci.queue_manager import queue_manager
from homebot.modules.ci.workflow import Workflow
from importlib import import_module
from telegram.ext import CallbackContext
from telegram.update import Update

class Module(ModuleBase):
	name = "ci"
	description = "A module that let you trigger actions with a single Telegram message"
	version = "1.0.0"

	def ci(update: Update, context: CallbackContext):
		if not user_is_admin(update.message.from_user.id):
			update.message.reply_text("Error: You are not authorized to use CI function of this bot.\n"
									  "Ask to who host this bot to add you to the authorized people list")
			return

		if get_config("ci.channel_id") is None:
			update.message.reply_text("Error: CI channel or user ID not defined")
			LOGE("CI channel or user ID not defined")
			return

		parser = CIParser(prog="/ci")
		parser.set_output(update.message.reply_text)
		parser.add_argument('project', help='CI project',
							nargs='?', default=None,)
		parser.add_argument('-s', '--status',
							action='store_true', help='show queue status')

		args, project_args = parser.parse_known_args(context.args)

		if args.status:
			update.message.reply_text(queue_manager.get_formatted_queue_list())
			return

		if args.project is None:
			parser.error("Please specify a project")

		try:
			project_class = import_module(f"homebot.modules.ci.projects.{args.project}", package="Project").Project
		except (ModuleNotFoundError, AttributeError):
			update.message.reply_text("Error: Project script not found")
			return
		except Exception as e:
			text = "Error: Error while importing project:"
			text += format_exception(e)
			update.message.reply_text(text)
			LOGE(text)
			return

		try:
			project = project_class(update, context, project_args)
		except Exception as e:
			text = "Error: Project class initialization failed:\n"
			text += format_exception(e)
			update.message.reply_text(text)
			LOGE(text)
			return

		workflow = Workflow(project)
		queue_manager.put(workflow)
		update.message.reply_text("Workflow added to the queue")
		LOGI("Workflow added to the queue")

	commands = {
		ci: ['ci']
	}
