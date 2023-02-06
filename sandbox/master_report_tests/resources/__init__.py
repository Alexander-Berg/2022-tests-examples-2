from sandbox.sdk2 import Resource, parameters


class YabsMasterReportRequests(Resource):
    """Resource with master report requests
    """
    __default_attribute__ = parameters.String

    releasable = True
    auto_backup = True
    any_arch = True
    releasers = ["YANDEX_MONETIZE_BANNER"]


class YabsMasterReportBackupDescription(Resource):
    """Resource with master report backup description
    """
    __default_attribute__ = parameters.String

    releasable = True
    auto_backup = True
    any_arch = True
    releasers = ["YANDEX_MONETIZE_BANNER"]


class YabsMasterReportSpec(Resource):
    """Resource with master report testing spec
    """
    __default_attribute__ = parameters.String

    releasable = True
    auto_backup = True
    any_arch = True
    releasers = ["YANDEX_MONETIZE_BANNER"]


class YabsMasterReportShootResults(Resource):
    """Resource with master report B2B shoot results
    """

    auto_backup = True
    any_arch = True


class YabsMasterReportCompareResults(Resource):
    """Resource with master report B2B comparison results
    """

    auto_backup = True
    any_arch = True
