{
	# obtained from https://my.telegram.org
	'api_id': ...,
	'api_hash': ...,
	# obtained from the BotFather
	'api_token': ...,
	# pick anything?
	'session_name': 'anon',

	# @mention of this bot's admin
	'owner': ...,

	# the ID of a private leaderboard
	# get this from https://adventofcode.com/2019/leaderboard/private, and [View] any leaderboard you're a member of.
	# The leaderboard ID is the last part of the URL.
	'aoc_leaderboard_id': ...,
	# your session cookie obtained after signing in to AoC
	'aoc_session_cookie': ...,
	# Only members of this chat ID will be able to access score commands.
	# If set to None, or not set, anyone will be able to access the configured private leaderboard.
	'aoc_chat_id': None,
	# Whether to send a message to the above chat ID whenever a new puzzle is expected to release.
	'aoc_notify': False,
}
