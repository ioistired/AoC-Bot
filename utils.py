import inspect
from functools import wraps

def ensure_corofunc(f):
	if inspect.iscoroutinefunction(f):
		return f
	@wraps(f)
	async def wrapped(*args, **kwargs):
		return f(*args, **kwargs)
	return wrapped
