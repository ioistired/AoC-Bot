#!/usr/bin/env python3

import asyncio
import collections
import io
import json
import logging
import operator
import os
import sys
import time
import typing

from yarl import URL

RATE_LIMIT = 15 * 60

logger = logging.getLogger(__name__)

def score_leaderboard(leaderboard: dict) -> typing.Dict[int, typing.List[dict]]:
	scores = collections.defaultdict(list)
	for member in leaderboard['members'].values():
		partial = partial_member(member)
		scores[member['stars']].append(member)

	return sorted_dict(scores, reverse=True)

def owner(leaderboard: dict) -> dict:
	return partial_member(leaderboard['members'][leaderboard['owner_id']])

def partial_member(member: dict) -> dict:
	return {k: member[k] for k in ('id', 'name')}

def sorted_dict(d: dict, *, key=None, reverse=False) -> dict:
	return {k: d[k] for k in sorted(d, key=key, reverse=reverse)}

def format_leaderboard(leaderboard):
	out = io.StringIO()

	scores = score_leaderboard(leaderboard)
	year = leaderboard['event']

	out.write(str(year))
	out.write(' leaderboard\n')

	out.write('Owner: ')
	out.write(owner(leaderboard)['name'])
	out.write('\n')

	for score, members in scores.items():
		sorted_members = sorted(members, key=lambda member: int(member['id']))
		out.write('**')
		out.write(str(score))
		out.write('** ⭐ ')
		out.write(', '.join(map(operator.itemgetter('name'), sorted_members)))
		out.write('\n')

	return out.getvalue()

async def leaderboard(client):
	"""Fetch the latest leaderboard from the web if and only if it has not been fetched recently.
	Otherwise retrieve from disk.
	"""

	now = time.time()
	try:
		last_modified = os.stat('leaderboard.json').st_mtime
	except FileNotFoundError:
		logger.info('Leaderboard file not found, creating.')
		return await refresh_saved_leaderboard(client)

	if now - last_modified > RATE_LIMIT:
		return await refresh_saved_leaderboard(client)

	# we've fetched it recently
	return load_leaderboard()

async def refresh_saved_leaderboard(client):
	"""save the latest leaderboard to disk"""
	leaderboard = await fetch_leaderboard(client)
	save_leaderboard(leaderboard)
	return leaderboard

def save_leaderboard(leaderboard):
	with open('leaderboard.json', 'w') as f:
		json.dump(leaderboard, f, indent=4, ensure_ascii=False)
		f.write('\n')

def load_leaderboard():
	with open('leaderboard.json') as f:
		return json.load(f)

def validate_headers(resp):
	if resp.status == 302:
		url = URL(resp.headers['Location'])
		if url.parts[-2:] == ('leaderboard', 'private'):
			raise RuntimeError('You are not a member of the configured leaderboard.')
		if url.parts[-1] == 'leaderboard':
			raise RuntimeError('An improper session cookie has been configured.')
	elif resp.status != 200:
		resp.raise_for_status()

async def login(client):
	async with client.http.head(client.config['aoc_leaderboard_url'], allow_redirects=False) as resp:
		validate_headers(resp)

async def fetch_leaderboard(client):
	logger.debug('Fetching leaderboard over HTTP')
	async with client.http.get(
		client.config['aoc_leaderboard_url'],
		allow_redirects=False,  # redirects are used as error codes
	) as resp:
		validate_headers(resp)
		return await resp.json()

if __name__ == '__main__':
	main()
