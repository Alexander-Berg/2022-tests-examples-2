from sandbox.projects.common.noapacheupper.search_component import Noapacheupper
from sandbox.projects.common.search import config as sconf
from sandbox import sdk2
import os


def get_noapacheupper(differ_noapacheupper, build_values, **kwargs):
    """
        based on projects.common.noapacheupper.search_component.get_noapacheupper
        but try give resources as sdk2.Resource
        More simple version without neh_cache_mode
    """

    config_file = str(sdk2.ResourceData(build_values["config"]).path)

    pure_dir = None
    rearrange_id = differ_noapacheupper.Parameters.noapache_rearrange_data
    rearrange_dir = str(sdk2.ResourceData(rearrange_id).path) if rearrange_id else None
    rearrange_dynamic_id = differ_noapacheupper.Parameters.noapache_rearrange_dynamic_data
    rearrange_dynamic_dir = str(sdk2.ResourceData(rearrange_dynamic_id).path) if rearrange_dynamic_id else None

    data_id = build_values["data"]
    if data_id:
        data_path = str(sdk2.ResourceData(data_id).path)
        pure_dir = os.path.join(data_path, "pure")
        if not rearrange_dir:
            rearrange_dir = os.path.join(data_path, "rearrange")
        if not rearrange_dynamic_dir:
            rearrange_dynamic_dir = os.path.join(data_path, "rearrange.dynamic")

    neh_cache = None

    kwargs.update(
        is_int=False,
        work_dir=str(differ_noapacheupper.path),
        binary=str(sdk2.ResourceData(build_values["binary"]).path),
        config_class=sconf.NoapacheupperConfig,
        config_file=config_file,
        pure_dir=pure_dir,
        rearrange_dir=rearrange_dir,
        rearrange_dynamic_dir=rearrange_dynamic_dir,
        start_timeout=differ_noapacheupper.Parameters.start_timeout,
        neh_cache=neh_cache,
        use_verify_stderr=kwargs.get('use_verify_stderr', True),
        apphost_mode=differ_noapacheupper.Parameters.apphost_mode,
        server_input_deadline=differ_noapacheupper.Parameters.server_input_deadline,
    )

    noapacheupper = Noapacheupper(**kwargs)
    noapacheupper.shutdown_timeout = differ_noapacheupper.Parameters.shutdown_timeout
    return noapacheupper
