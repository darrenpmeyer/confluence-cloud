"""
confluence-cloud
"""
import os
import logging

mlog = logging.getLogger(__name__)
_DETAILED_DEBUG = False


CONFIG_PATHS = [
    '.',
    os.path.join(os.getenv('HOME'), '.config/confluence-cloud')
]


def config_file_path(filename, search_path=None, max_mode=0o644):
    """
    finds the first file named ``filename`` in the ``search_path``
    and returns its absolute path

    :param filename: name of file to search for
    :param search_path: list of paths to search for the file
    :param max_mode: the maximum allowable mode (permissions) for the file
    :return: str - absolute path of found file
    :raises: FileNotFoundException if no file is found
    :raises: PermissionError if file exceeds ``max_mode``
    """
    if search_path is None:
        search_path = CONFIG_PATHS
    fq_path = None  # the fully-qualified path to return
    errors = []  # errors with files that _are_ found

    for path in [os.path.dirname(filename), search_path]:
        file_path = os.path.abspath(os.path.join(path, filename))
        if os.path.isfile(file_path):
            stat = os.stat(file_path)
            mode_mask = 0o777 - max_mode

            if stat.st_mode & mode_mask:
                errors.append(f"'{file_path}' is not sufficiently restricted" +
                              f" (had mode {oct(stat.st_mode)}, max is {oct(max_mode)})")
                continue  # permission issue, so skip

            fq_path = file_path
            break  # we found a good file, no need to check more

    if fq_path is not None:
        return fq_path  # happy path -- all after here are error conditions

    if len(errors) == 1:
        # the one file had a problem
        raise PermissionError(errors[0])  # so report it
    elif len(errors) > 1:
        raise PermissionError(f"Found {len(errors)} files, all of which had permissions issues\n\t" +
                              "\n\t".join(errors))
    else:
        raise FileNotFoundError("Did not find any files in search path")
    # end of procedure


def api_token_from_file(filename, search_path=None):
    with open(config_file_path(filename, search_path, max_mode=0o600)) as cfg_file:
        (userid, api_token) = cfg_file.readline().strip().split(':', 2)

    return userid, api_token
