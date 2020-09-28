"""
utils - common methods for manipulating data structures and the like
"""
import unicodedata


def normalize_str(text):
    """
    prepares unicode strings for equality comparisons

    :param text:
    :return:
    """
    return unicodedata.normalize("NFKD", text)


def str_nocase_equal(str1, str2):
    """
    Performs a reliable Unicode string case-insensitive comparison between two strings

    :param str1:
    :param str2:
    :return:
    """
    return normalize_str(str1.casefold()) == normalize_str(str2.casefold())


def thin_dict(template, preserve=None, strip_value=None):
    """
    Produce a dictionary from a template dict by removing all keys where the value
    is None (or whatever is specified in ``strip_value``)

    :param strip_value: the value that isn't permitted, default is "None"
    :param preserve: a list of keys that should not be removed ever
    :param template: the dict to thin
    :return:
    """
    if preserve is None:
        preserve = []

    thinned = template.copy()
    delete_keys = []
    for k in thinned.keys():
        if k not in preserve and thinned[k] == strip_value:
            delete_keys.append(k)

    for k in delete_keys:
        del(thinned[k])

    return thinned
