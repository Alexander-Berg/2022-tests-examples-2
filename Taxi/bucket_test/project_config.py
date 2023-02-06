from nile.api.v1 import clusters

from projects.common.nile import environment as penv


def prepare_environment(obj, parallel_operations_limit=None, use_cxx=False):
    return penv.configure_environment(
        obj,
        requirements=tuple(),
        extra_requirements=tuple(),
        parallel_operations_limit=parallel_operations_limit,
        add_cxx_bindings=use_cxx,
    )


def get_project_cluster(
        parallel_operations_limit=None,
        use_cxx=False,
        proxy=penv.DEFAULT_CLUSTER,
        use_yql=False,
):
    if use_yql:
        cluster = clusters.yql.YQLProduction(proxy=proxy)
    else:
        cluster = clusters.yt.YT(proxy=proxy)
    return prepare_environment(
        cluster,
        parallel_operations_limit=parallel_operations_limit,
        use_cxx=use_cxx,
    )
