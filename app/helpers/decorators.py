# standard library imports
import functools

# internal imports
from app.helpers import notifs

def catchall_exceptions(func):
    @functools.wraps(func)
    # catch unhandled exceptions and notify on discord
    def catches_all_exceptions(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            unpacked_kwargs = {**kwargs}
            notifs.send_message_on_discord(
                f'error occured in `{func.__name__}`\nerror trace: {e}'
                f'\nargs: {[*args]}\nkwargs: {unpacked_kwargs}'
            )
            # raise the caught exception for logging
            raise e
    return catches_all_exceptions

def async_catchall_exceptions(func):
    @functools.wraps(func)
    # catch unhandled exceptions and notify on discord
    async def catches_all_exceptions(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            unpacked_kwargs = {**kwargs}
            notifs.send_message_on_discord(
                f'error occured in `{func.__name__}`\nerror trace: {e}'
                f'\nargs: {[*args]}\nkwargs: {unpacked_kwargs}'
            )
            # raise the caught exception for logging
            raise e
    return catches_all_exceptions
