#!/bin/bash
#
# Copyright (C) 2020 SebaUbuntu's HomeBot
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

module_speedtest() {
	local MESSAGE_ID=$(tg_send_message --chat_id "$(tg_get_chat_id "$@")" --text "Running speedtest..." --reply_to_message_id "$(tg_get_message_id "$@")" | jq .result.message_id)
	tg_edit_message_text --chat_id "$(tg_get_chat_id "$@")" --message_id "$MESSAGE_ID" --text "\`$(speedtest-cli | grep "Mbit/s")\`" --parse_mode "Markdown"
}
