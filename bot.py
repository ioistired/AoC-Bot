#!/usr/bin/env python3

# Copyright © 2018–2019 Io Mintz <io@mintz.cc>
#
# AoC Bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AoC Bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with AoC Bot.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import datetime as dt
import logging
from functools import wraps

import aiohttp
from telethon import TelegramClient, errors, events, tl

import aoc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bot')

def seconds_until_next_puzzle():
	now = dt.datetime.utcnow()
	est_now = now - dt.timedelta(hours=5)
	tomorrow = est_now + dt.timedelta(days=1)
	next_midnight_est = dt.datetime.combine(tomorrow, dt.time(5, 0))
	if next_midnight_est.month != 12:
		return None
	return (next_midnight_est - now).total_seconds()

async def notify_loop(client):
	chat_id = client.config.get('aoc_notify_chat_id')
	if not chat_id:
		return

	while True:
		seconds = seconds_until_next_puzzle()
		if seconds is None:
			return
		print('sleeping', seconds, 'seconds')
		await asyncio.sleep(seconds)
		await client.send_message(chat_id, "Oh shirt, a new puzzle! Let's get this gingerbread!")

def is_command(event):
	# this is insanely complicated kill me now
	message = event.message
	username = getattr(event.client.user, 'username', None)
	if not username:
		logger.warning('I have no username!')
		return False
	dm = isinstance(message.to_id, tl.types.PeerUser)
	for entity, text in message.get_entities_text(tl.types.MessageEntityBotCommand):
		if entity.offset != 0:
			continue
		if dm or text.endswith('@' + username):
			return True
	return False

def command_required(f):
	@wraps(f)
	async def handler(event):
		if not is_command(event):
			return
		await f(event)
		raise events.StopPropagation
	return handler

# so that we can register them all in the correct order later (globals() is not guaranteed to be ordered)
event_handlers = []
def register_event(*args, **kwargs):
	def deco(f):
		event_handlers.append(events.register(*args, **kwargs)(f))
		return f
	return deco

@register_event(events.NewMessage(pattern=r'^/ping'))
@command_required
async def ping_command(event):
	await event.respond('Pong')

@register_event(events.NewMessage(pattern=r'^/license'))
@command_required
async def license_command(event):
	with open('short-license.txt') as f:
		await event.respond(f.read())

@register_event(events.NewMessage(pattern=r'^/scores'))
@command_required
async def scores_command(event):
	leaderboard = await aoc.leaderboard(event.client)
	await event.respond(aoc.format_leaderboard(leaderboard))

def get_client():
	with open('config.py') as f:
		config = eval(f.read(), {})

	client = TelegramClient(config['session_name'], config['api_id'], config['api_hash'])
	client.config = config

	for handler in event_handlers:
		client.add_event_handler(handler)

	client.http = aiohttp.ClientSession(
		headers={
			'Cookie': 'session=' + client.config['aoc_session_cookie'],
		},
		cookie_jar = aiohttp.DummyCookieJar(),  # suppress normal cookie handling
	)

	return client

async def main():
	client = get_client()

	await client.start(bot_token=client.config['api_token'])
	client.user = await client.get_me()
	async with client.http:
		await aoc.login(client)
		t = asyncio.create_task(notify_loop(client))
		try:
			await client._run_until_disconnected()
		finally:
			await client.disconnect()
			t.cancel()

if __name__ == '__main__':
	asyncio.run(main())
