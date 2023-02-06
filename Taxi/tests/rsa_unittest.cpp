#include <gtest/gtest.h>

#include <utils/rsa.hpp>
#include <utils/rsa_keys.hpp>

const std::string public_key =
    "-----BEGIN PUBLIC KEY-----\n"
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyYnGx5g5rIKcXT06Gy0J\n"
    "rPJsTWNkDRCmKubAfiRzdyaq2xfdyTLyOcIrsq7xV7LfntN0i+zMe8IbUNs0DN0D\n"
    "ZixDL1+NF1CBgU1Y1ZskV4oi6D9+lUqEnSn7WqiCheXCgh0tJPjDkB82VXCLxJxw\n"
    "SepTtcNc/8RORtvJSLaRIg+ivZp64/pbSWQdXlv61hQ/kNO1DmZmptRH/+gT4nL2\n"
    "BvV7edI4OmwmeD1GG9z8HCJ+rQfzmL8D05iPIRuoMw1wSumFMiRaGjt/3dmm5c49\n"
    "X7KhifdnSEjf5Z9bpCCybAu2u7CJ+DaOWTTJJRnAQ784pETClVbMbK3OidDCcTTQ\n"
    "RQIDAQAB\n"
    "-----END PUBLIC KEY-----";

const std::string signature =
    "GuuamvnZbv2xTHvG5qcOinIQz7F/qrBlhkiA246uhAicvFwz531ueajyLGOIWIbu\n"
    "brbnAPfp+uSoCjIHd0wdWY08CHwG212HDhNS4v1v/IGHold8b9wJJKITv3UCNpg6\n"
    "3au9stiM05OT2KiiL8h/fEvVLdfkTC6NLEOgZdVDzlmtd9xejUP3aAb1Rgt1aYbw\n"
    "8o+hO5X8cvnrXwx2TUzSLAs61SvPTIH4md3yUI+n34cJvwsuFLALKYYWoWiWTLuI\n"
    "JOJ74O5OA1hxzym/KCXok/0F2r2S1SAatJzorhU3Zg0kFc9atMgXl204TonteofK\n"
    "xo3PVKzlEUvjLdo+DCAp3Q==";

TEST(RSA, verify_signature) {
  using namespace utils::rsa;
  PublicKey rsa_public_key = public_key;
  LogExtra extra;
  EXPECT_TRUE(VerifyMessage("hello\n", signature, rsa_public_key, extra));
  EXPECT_FALSE(VerifyMessage("bye", signature, rsa_public_key, extra));
  EXPECT_FALSE(VerifyMessage("hello\n", "lalala", rsa_public_key, extra));
  EXPECT_THROW(VerifyMessage("hello\n", signature, PublicKey{}, extra),
               std::exception);
}
