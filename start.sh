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

export VERSION=2.0.0
export BRANCH=Stable

export SCRIPT_PWD=$(pwd)

# Source variables and basic functions
source variables.sh
source base/telegram.sh

import_modules

if [ $(telegram getUpdates | jq .ok) != "true" ]; then
	echo "Error! Make sure you added the right HTTP API token in variables.sh"
	exit 1
fi

echo "Bot up and running!"
while [ 0 != 1 ]; do
	if [ "$LAST_UPDATE_ID" != "" ]; then
		LAST_UPDATES=$(telegram getUpdates --offset "$LAST_UPDATE_ID")
	else
		LAST_UPDATES=$(telegram getUpdates)
	fi
	UNREAD_UPDATES_NUMBER="$(tg_get_unread_updates_number "$LAST_UPDATES")"
	if [ "$UNREAD_UPDATES_NUMBER" != "0" ]; then
		echo "Found $UNREAD_UPDATES_NUMBER update(s)"
		CURRENT_UPDATES_NUMBER=0
		while [ "$UNREAD_UPDATES_NUMBER" -gt "$CURRENT_UPDATES_NUMBER" ]; do
			execute_module "$(tg_get_specific_update "$LAST_UPDATES" "$CURRENT_UPDATES_NUMBER")" &
			CURRENT_UPDATES_NUMBER=$(( CURRENT_UPDATES_NUMBER + 1 ))
		done
		LAST_UPDATE_ID=$(tg_get_last_update_id "$LAST_UPDATES")
		LAST_UPDATE_ID=$(( LAST_UPDATE_ID + 1 ))
	fi
done
