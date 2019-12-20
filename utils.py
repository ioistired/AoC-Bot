import asyncio
import logging
import inspect
from functools import wraps

def ensure_corofunc(f):
	if inspect.iscoroutinefunction(f):
		return f
	@wraps(f)
	async def wrapped(*args, **kwargs):
		return f(*args, **kwargs)
	return wrapped

async def task_wrapper(f, *, _logger=logging.getLogger('task-wrapper')):
	delay = 1
	while True:
		try:
			await f()
		except Exception as exc:
			_logger.error(
				'Ignoring exception in %s(). Will retry in %d seconds.',
				f,
				delay,
				exc_info=exc
			)
			await asyncio.sleep(delay)
			delay <<= 1
