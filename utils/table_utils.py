import re
from typing import List


def sanitize_identifier(identifier: str):
    """
    Sanitize and wrap an identifier with backquotes. For example, "a`b" becomes "`a``b`".
    Use this function to sanitize identifiers such as column names in SQL and PySpark.
    """
    return f"`{identifier.replace('`', '``')}`"


def sanitize_identifiers(identifiers: List[str]):
    """
    Sanitize and wrap the identifiers in a list with backquotes.
    """
    return [sanitize_identifier(i) for i in identifiers]


def sanitize_multi_level_name(multi_level_name: str):
    """
    Sanitize a multi-level name (such as an Unity Catalog table name) by sanitizing each segment
    and joining the results. For example, "ca+t.fo`o.ba$r" becomes "`ca+t`.`fo``o`.`ba$r`".
    """
    segments = multi_level_name.split(".")
    return ".".join(sanitize_identifiers(segments))


def is_three_level_name(name) -> bool:
    # regex to match three segments separated by dots
    # each segment should not contain spaces, dots, or control characters
    THREE_LEVEL_NAMESPACE_REGEX = (
        r"^[^\. \/\x00-\x1F\x7F]+(\.[^\. \/\x00-\x1F\x7F]+)(\.[^\. \/\x00-\x1F\x7F]+)$"
    )
    return (
        isinstance(name, str)
        and re.match(THREE_LEVEL_NAMESPACE_REGEX, name) is not None
    )
