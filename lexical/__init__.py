# from typing import Tuple
# from . import _version
# from ._version import __version__
#
#
# # 1.0.1.dev0+g196d2c4.d20250701
# def convert_version(version: str) -> Tuple:
#     version_info = version.split(".")
#     for i, v in enumerate(version_info):
#         try:
#             version_info[i] = int(v)
#         except ValueError:
#             version_info[i] = v.split("+")[0]
#             version_info = version_info[: i + 1]
#             break
#
#     return tuple(version_info)
#
#
# _version.VERSION_INFO = convert_version(__version__)
# __all__ = ["__version__"]
