import ast
import time
from datetime import timedelta


def seconds_to_hhmmss(seconds: float) -> str:
    """Transform time difference from seconds to `hh:mm:ss.ss` format."""
    return str(timedelta(seconds=seconds))[:-4]


def timer(start_time):
    """Get time difference from start_time to now in hh:mm:ss format."""
    return str(timedelta(seconds=time.time() - start_time))


def print_non_numeric_columns(df, cols):
    """Prints non-numeric columns if exists."""

    df_filtered = df[cols].select_dtypes(exclude=['number', 'bool'])
    if df_filtered.shape[1] != 0:
        print(df_filtered.info())

    return None


def decode_dict(d) -> dict:
    """JSON DECODING FUNCTION TO REMOVE BYTE KEYS."""
    result = {}
    for key, value in d.items():
        if isinstance(key, bytes):
            key = key.decode()
        if isinstance(value, bytes):
            value = value.decode()
        elif isinstance(value, dict):
            value = decode_dict(value)
        result.update({key: value})
    return result


def convert_to_dict(x) -> dict:
    """Converts dict-like value as dict value, otherwise returns the raw
    value."""

    # converts from bytes as str
    if isinstance(x, bytes):
        x = x.decode('utf-8')

    # converts from str as dict
    if isinstance(x, str):
        x = ast.literal_eval(x)

    # return the dict or the raw value
    return x
