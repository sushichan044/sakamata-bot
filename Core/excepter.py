import traceback
from functools import wraps


def excepter(func):
    @wraps(func)
    async def wrapped(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except Exception as e:
            orig_error = getattr(e, "original", e)
            err_msg = "".join(
                traceback.TracebackException.from_exception(orig_error).format()
            )
            app_info = await self.bot.application_info()
            await app_info.owner.send(f"```Python Bot Error\n{err_msg}\n```")

    return wrapped
