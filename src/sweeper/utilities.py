import logging
from fnmatch import fnmatch

log = logging.getLogger("sweeper")


def apply_exclusions(list, exclusions):
    """
    Apply exclusions to a list of items. Matches are checked using the fnmatch module.

    Args:
        list (list): The list of items to apply exclusions to.
        exclusions (list): The list of exclusion fnmatch-compatible patterns.

    Returns:
        list: The updated list after applying exclusions.
    """
    for exclusion in exclusions:
        new_list = []
        for item in list:
            if fnmatch(item, exclusion):
                log.info(f"Excluding {item} based on exclusion {exclusion}")
            else:
                new_list.append(item)
        list = new_list

    return list
