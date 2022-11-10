from app.helpers import notifs
import functools

def catchall_exceptions(func):
    @functools.wraps(func)
    # catch unhandled exceptions and notify on discord
    def catches_all_exceptions(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            notifs.send_message_on_discord(
                f'error occured in `{func.__name__}`\nerror trace: {e}'
            )
    return catches_all_exceptions