import os


def getConfig(key: str, default=None, required=True):
    value = os.getenv(key)
    if not value:
        print(f"Config variable {key} is not set")
        if required is True:
            raise Exception(f"Config variable {key} is not set")
    return value or default
