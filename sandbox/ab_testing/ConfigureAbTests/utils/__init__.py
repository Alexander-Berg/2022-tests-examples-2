import six  # noqa
import typing  # noqa
import logging
import os
import yaml
import json

from sandbox.projects.common.vcs import arc
from sandbox.projects.release_machine.core import const as rm_const


class ExperimentConfigLoadingError(Exception):
    pass


STR = six.string_types
STR_OR_INT = typing.Union[six.string_types + six.integer_types]

ARC_INFO_NAMES_KEY = "names"
ARC_INFO_NAMES_PATH_KEY = "path"


def get_config_path_from_arc_commit_info(commit_id, commit_info):  # type: (STR_OR_INT, STR) -> STR
    """
    Given a commit id and it's info returns experiment config path

    :raises ExperimentConfigLoadingError:
        Raised if unexpected commit info obtained (e.g., too much paths detected or no paths at all)
    """

    if len(commit_info) == 0:
        raise ExperimentConfigLoadingError(
            "Unable to get arc info for commit {}. `arc show` response was: {}".format(
                commit_id,
                commit_info,
            ),
        )

    commit_info = commit_info[0]

    if ARC_INFO_NAMES_KEY not in commit_info:
        raise ExperimentConfigLoadingError(
            "`arc show` result cannot be parsed (no {} key found): {}".format(ARC_INFO_NAMES_KEY, commit_info)
        )

    commit_info_names = commit_info[ARC_INFO_NAMES_KEY]

    if len(commit_info_names) > 1:
        raise ExperimentConfigLoadingError(
            "More than 1 path detected for commit {} - unable to decide which one to use. Full response: {}".format(
                commit_id,
                commit_info_names,
            ),
        )

    path = commit_info_names[0].get(ARC_INFO_NAMES_PATH_KEY, "")

    if not path:
        raise ExperimentConfigLoadingError("Path cannot be detected for commit {}".format(commit_id))

    return path


def load_experiment_config_from_fs(arcadia_root, config_path):  # type: (STR, STR) -> dict
    """
    Load experiment yaml config

    :param arcadia_root: Arcadia local root path
    :param config_path: config file path relative to Arcadia root
    :return: experiment config (dict)
    """

    from library.python import fs

    full_path = os.path.join(arcadia_root, config_path)
    logging.info("Full path to load: %s", full_path)
    return yaml.safe_load(fs.read_file_unicode(full_path))


def get_experiment_config(
    commit_id,
    arc_secret_name=rm_const.COMMON_TOKEN_NAME,
    arc_secret_owner=rm_const.COMMON_TOKEN_OWNER,
    arc_oauth_token=None,
):  # type: (STR_OR_INT, STR, STR, STR) -> dict
    """
    Load experiment config committed at :param commit_id:

    :param commit_id: either arc commit hash, or svn revision (both str and int accepted)
    :param arc_secret_name: arc secret name (SB Vault)
    :param arc_secret_owner: arc secret owner (SB Vault)
    :param arc_oauth_token: arc OAuth token

    :raises arc.ArcCommandFailed:
        Raised if arc command fails

    :raises ExperimentConfigLoadingError:
        Raised if unexpected commit info obtained (e.g., too much paths detected or no paths at all)

    """

    logging.info("Going to load experiment config")

    if isinstance(commit_id, six.integer_types) or commit_id.isdigit():
        commit_id = "r{}".format(commit_id)

    logging.info("commit: %s", commit_id)

    arc_client = arc.Arc(
        secret_name=arc_secret_name,
        secret_owner=arc_secret_owner,
        arc_oauth_token=arc_oauth_token,
    )

    with arc_client.mount_path(None, None, fetch_all=False, extra_params=["--vfs-version", "2"]) as mp:

        commit_info = arc_client.show(mp, commit=commit_id, as_dict=True, name_status=True)

        logging.info("`arc show` response: %s", commit_info)

        config_file_path = get_config_path_from_arc_commit_info(commit_id, commit_info)

        logging.info("Config file path detected: %s", config_file_path)

        arc_client.checkout(mp, commit_id)

        logging.info("Checked Arcadia out at %s", commit_id)

        config = load_experiment_config_from_fs(mp, config_file_path)

        logging.info("Config loaded: %s", json.dumps(config, indent=2))

    return config
