# -*- coding: utf-8 -*-


class TestUserServiceException(Exception):
    code = 'tus.error'

    def __init__(self, error_description):
        self.error_description = error_description


class TvmToolError(TestUserServiceException):
    code = 'tvmtool.error'


class InvalidRequestError(TestUserServiceException):
    code = 'request.invalid'


class HeadersMissedError(TestUserServiceException):
    code = 'headers.missed'


class AuthorizationHeaderError(TestUserServiceException):
    code = 'authorization_header.invalid'


class TestUserServiceInternalException(TestUserServiceException):
    code = 'backend.permanent'


class ResponseParsingError(TestUserServiceException):
    code = 'backend.failed'


class TemporarilyUnavailableError(TestUserServiceException):
    code = 'backend.temporary'


class PassportRegistrationError(TestUserServiceException):
    code = 'passport.registration_failed'


class PassportBindPhoneFailed(TestUserServiceException):
    code = 'passport.bind_phone_failed'


class AccountNotFoundError(TestUserServiceException):
    code = 'account.not_found'


class RemoveAccountFailedError(TestUserServiceException):
    code = 'account.remove_failed'


class SaveAccountFailedError(TestUserServiceException):
    code = 'account.save_failed'


class UnlockAccountFailedError(TestUserServiceException):
    code = 'account.unlock_failed'


class TusConsumerNotMatchedError(TestUserServiceException):
    code = 'tus_consumer.not_matched'


class TusConsumerAccessDenied(TestUserServiceException):
    code = 'tus_consumer.access_denied'


class TusConsumerAlreadyExist(TestUserServiceException):
    code = 'tus_consumer.already_exist'


class TusConsumerNotExist(TestUserServiceException):
    code = 'tus_consumer.not_exist'


class CreateTusConsumerError(TestUserServiceException):
    code = 'create_tus_consumer.error'


class KolmogorCounterOverflow(TestUserServiceException):
    code = 'kolmogor.counter_overflow'


class BlackboxOAuthTokenIsNotValid(TestUserServiceException):
    code = 'blackbox.token_not_valid'


class BlackboxAccountPasswordNotMatchLogin(TestUserServiceException):
    code = 'blackbox.password_not_match_login'


class BlackboxAccountUidNotMatchLogin(TestUserServiceException):
    code = 'blackbox.uid_not_match_login'


class PassportEnvNotAllowed(TestUserServiceException):
    code = 'passport_env.not_allowed'
