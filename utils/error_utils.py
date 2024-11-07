import os
import re


def reformat_error(e) -> str:
    err = str(e)
    if "session_id is no longer usable" in err:
        err = "Session expired. Please refresh the page."
    else:
        # Regex pattern to match on "Insufficient privileges:" or "Permission denied:"
        # and replace "User" with the service principal id
        pattern = r"(.*(?:Insufficient privileges:|PERMISSION_DENIED:)\s)(User)(.*)"
        replacement = (
            r"\1Service principal id " + os.getenv("DATABRICKS_CLIENT_ID") + r"\3"
        )
        err = re.sub(pattern, replacement, err)
    return err
