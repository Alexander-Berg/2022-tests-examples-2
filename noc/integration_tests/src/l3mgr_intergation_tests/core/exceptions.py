class L3mgrClientException(Exception):
    pass


class CouldNotAddServiceError(L3mgrClientException):
    pass


class CouldNotDeleteServiceError(L3mgrClientException):
    pass


class CouldNotAddIPError(L3mgrClientException):
    pass


class CouldNotGetIPError(L3mgrClientException):
    pass


class CouldNotCreateConfigError(L3mgrClientException):
    pass


class CouldNotDeployConfigError(L3mgrClientException):
    pass


class CouldNotGetBalancerID(L3mgrClientException):
    pass


class CouldNotAddBalancerToABCError(L3mgrClientException):
    pass


class UnexpectedConfigState(L3mgrClientException):
    pass


class TestNotCompleteInExpectedTime(L3mgrClientException):
    pass


class CouldNotDeleteConfigError(L3mgrClientException):
    pass


class CouldNotGetConfigError(L3mgrClientException):
    pass


class CouldNotAddVSError(L3mgrClientException):
    pass
