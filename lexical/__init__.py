from . import _version
from ._version import __version__


# 1.0.1.dev0+g196d2c4.d20250701
def convert_version(version: str) -> str:
    version_info = version.split(".")
    for i, v in enumerate(version_info):
        try:
            version_info[i] = int(v)
        except ValueError:
            version_info[i] = v.split("+")[0]
            version_info = version_info[: i + 1]
            break

    dev_tag = None
    try:
        _ = int(version_info[-1])
    except ValueError:
        dev_tag = version_info[-1]

    version_info = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"
    if dev_tag is not None:
        version_info += f"-{dev_tag}"

    return version_info


_version.__version__ = convert_version(__version__)
__all__ = ["__version__"]
