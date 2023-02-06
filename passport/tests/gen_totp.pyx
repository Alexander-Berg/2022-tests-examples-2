# coding: utf-8

from util.generic.string cimport TString
from libc.time cimport time_t

cdef extern from "passport/infra/daemons/blackbox/src/totp/hotp.h" namespace "NPassport::NBb::NRfc4226":
    cdef cppclass THotpFactory:
        cppclass EHotpType "THotpFactory::EHotpType":
            pass

    cdef THotpFactory.EHotpType cDigits "NPassport::NBb::NRfc4226::THotpFactory::EHotpType::Digits"
    cdef THotpFactory.EHotpType cLetters "NPassport::NBb::NRfc4226::THotpFactory::EHotpType::Letters"

cdef extern from "passport/infra/daemons/blackbox/src/totp/totp.h" namespace "NPassport::NBb::NRfc6238":
    cdef cppclass TTotpFactory:
        @staticmethod
        TString GenTotp(int length, THotpFactory.EHotpType type, TString secret, time_t keyTime)
        @staticmethod
        TString GenRfcTotp(TString secret, time_t keyTime)


class HotpType:
    Digits = <int>cDigits
    Letters = <int>cLetters


def gen_totp(length, type, secret, keyTime):
    cdef THotpFactory.EHotpType t = cDigits
    if (type == <int>cLetters):
        t = cLetters

    if isinstance(secret, str):
        s = secret.encode('ascii')
    else:
        s = secret

    return TTotpFactory.GenTotp(length, t, s, keyTime).decode('ascii')


def gen_rfc_totp(secret, keyTime):
    return TTotpFactory.GenRfcTotp(secret.encode('ascii'), keyTime).decode('ascii')
