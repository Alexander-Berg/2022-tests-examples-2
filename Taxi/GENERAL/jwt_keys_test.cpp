#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <common/jwt_keys.hpp>

namespace {

namespace common = bank_h2h::common;

const std::chrono::system_clock::time_point mock_now =
    utils::datetime::FromRfc3339StringSaturating(
        "2022-01-01T19:31:00.100+00:00");

common::config_jwt_key::JwtKey ES256Config() {
  // -----BEGIN PRIVATE KEY-----
  // MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgevZzL1gdAFr88hb2
  // OF/2NxApJCzGCEDdfSp6VQO30hyhRANCAAQRWz+jn65BtOMvdyHKcvjBeBSDZH2r
  // 1RTwjmYSi9R/zpBnuQ4EiMnCqfMPWiZqB4QdbAd0E7oH50VpuZ1P087G
  // -----END PRIVATE KEY-----

  common::config_jwt_key::JwtKey jwt_key;
  jwt_key.algorithm = "ES256";
  jwt_key.public_key =
      "-----BEGIN PUBLIC KEY-----\n"
      "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEEVs/o5+uQbTjL3chynL4wXgUg2R9\n"
      "q9UU8I5mEovUf86QZ7kOBIjJwqnzD1omageEHWwHdBO6B+dFabmdT9POxg==\n"
      "-----END PUBLIC KEY-----\n";
  jwt_key.end_rotation_date = utils::datetime::Date(2022, 1, 2);
  return jwt_key;
}

common::config_jwt_key::JwtKey RS256Config() {
  // -----BEGIN PRIVATE KEY-----
  // MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQC7VJTUt9Us8cKj
  // MzEfYyjiWA4R4/M2bS1GB4t7NXp98C3SC6dVMvDuictGeurT8jNbvJZHtCSuYEvu
  // NMoSfm76oqFvAp8Gy0iz5sxjZmSnXyCdPEovGhLa0VzMaQ8s+CLOyS56YyCFGeJZ
  // qgtzJ6GR3eqoYSW9b9UMvkBpZODSctWSNGj3P7jRFDO5VoTwCQAWbFnOjDfH5Ulg
  // p2PKSQnSJP3AJLQNFNe7br1XbrhV//eO+t51mIpGSDCUv3E0DDFcWDTH9cXDTTlR
  // ZVEiR2BwpZOOkE/Z0/BVnhZYL71oZV34bKfWjQIt6V/isSMahdsAASACp4ZTGtwi
  // VuNd9tybAgMBAAECggEBAKTmjaS6tkK8BlPXClTQ2vpz/N6uxDeS35mXpqasqskV
  // laAidgg/sWqpjXDbXr93otIMLlWsM+X0CqMDgSXKejLS2jx4GDjI1ZTXg++0AMJ8
  // sJ74pWzVDOfmCEQ/7wXs3+cbnXhKriO8Z036q92Qc1+N87SI38nkGa0ABH9CN83H
  // mQqt4fB7UdHzuIRe/me2PGhIq5ZBzj6h3BpoPGzEP+x3l9YmK8t/1cN0pqI+dQwY
  // dgfGjackLu/2qH80MCF7IyQaseZUOJyKrCLtSD/Iixv/hzDEUPfOCjFDgTpzf3cw
  // ta8+oE4wHCo1iI1/4TlPkwmXx4qSXtmw4aQPz7IDQvECgYEA8KNThCO2gsC2I9PQ
  // DM/8Cw0O983WCDY+oi+7JPiNAJwv5DYBqEZB1QYdj06YD16XlC/HAZMsMku1na2T
  // N0driwenQQWzoev3g2S7gRDoS/FCJSI3jJ+kjgtaA7Qmzlgk1TxODN+G1H91HW7t
  // 0l7VnL27IWyYo2qRRK3jzxqUiPUCgYEAx0oQs2reBQGMVZnApD1jeq7n4MvNLcPv
  // t8b/eU9iUv6Y4Mj0Suo/AU8lYZXm8ubbqAlwz2VSVunD2tOplHyMUrtCtObAfVDU
  // AhCndKaA9gApgfb3xw1IKbuQ1u4IF1FJl3VtumfQn//LiH1B3rXhcdyo3/vIttEk
  // 48RakUKClU8CgYEAzV7W3COOlDDcQd935DdtKBFRAPRPAlspQUnzMi5eSHMD/ISL
  // DY5IiQHbIH83D4bvXq0X7qQoSBSNP7Dvv3HYuqMhf0DaegrlBuJllFVVq9qPVRnK
  // xt1Il2HgxOBvbhOT+9in1BzA+YJ99UzC85O0Qz06A+CmtHEy4aZ2kj5hHjECgYEA
  // mNS4+A8Fkss8Js1RieK2LniBxMgmYml3pfVLKGnzmng7H2+cwPLhPIzIuwytXywh
  // 2bzbsYEfYx3EoEVgMEpPhoarQnYPukrJO4gwE2o5Te6T5mJSZGlQJQj9q4ZB2Dfz
  // et6INsK0oG8XVGXSpQvQh3RUYekCZQkBBFcpqWpbIEsCgYAnM3DQf3FJoSnXaMhr
  // VBIovic5l0xFkEHskAjFTevO86Fsz1C2aSeRKSqGFoOQ0tmJzBEs1R6KqnHInicD
  // TQrKhArgLXX4v3CddjfTRJkFWDbE/CkvKZNOrcf1nhaGCPspRJj2KUkj1Fhl9Cnc
  // dn/RsYEONbwQSjIfMPkvxF+8HQ==
  // -----END PRIVATE KEY-----

  common::config_jwt_key::JwtKey jwt_key;
  jwt_key.algorithm = "RS256";
  jwt_key.public_key =
      "-----BEGIN PUBLIC KEY-----\n"
      "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCozMxH2Mo\n"
      "4lgOEePzNm0tRgeLezV6ffAt0gunVTLw7onLRnrq0/IzW7yWR7QkrmBL7jTKEn5u\n"
      "+qKhbwKfBstIs+bMY2Zkp18gnTxKLxoS2tFczGkPLPgizskuemMghRniWaoLcyeh\n"
      "kd3qqGElvW/VDL5AaWTg0nLVkjRo9z+40RQzuVaE8AkAFmxZzow3x+VJYKdjykkJ\n"
      "0iT9wCS0DRTXu269V264Vf/3jvredZiKRkgwlL9xNAwxXFg0x/XFw005UWVRIkdg\n"
      "cKWTjpBP2dPwVZ4WWC+9aGVd+Gyn1o0CLelf4rEjGoXbAAEgAqeGUxrcIlbjXfbc\n"
      "mwIDAQAB\n"
      "-----END PUBLIC KEY-----\n";
  jwt_key.end_rotation_date = utils::datetime::Date(2022, 1, 2);
  return jwt_key;
}

std::vector<common::config_jwt_key::JwtKey> MakeConfig(
    std::initializer_list<common::config_jwt_key::JwtKey> lst) {
  std::vector<common::config_jwt_key::JwtKey> config;
  for (auto& jwt_rule : lst) {
    config.emplace_back(std::move(jwt_rule));
  }
  return config;
}

}  // namespace

TEST(JwtKeys, EmptyJwtKeys) {
  EXPECT_UINVARIANT_FAILURE(bank_h2h::common::JwtKeys(MakeConfig({})));
}

TEST(JwtKeys, SingleJwtKey) {
  EXPECT_NO_THROW(bank_h2h::common::JwtKeys(MakeConfig({{"none", ""}})));
}

TEST(JwtKeys, ES256Key) {
  utils::datetime::MockNowSet(mock_now);
  const auto& keys = bank_h2h::common::JwtKeys(MakeConfig({ES256Config()}));

  auto jwt = keys.Parse(
      "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9."
      "eyJuYW1lIjoiZGVuaXMiLCJqb2IiOiJzb2Z0d2FyZSBkZXZlbG9wZXIifQ."
      "YzBUAn0HEpGDB7a9xahtu_6jb2F8ubvI973D4waGeJMmd13MG1mDDBQoWi0q_"
      "RjQo7vwv6JFg1tn4X0rhjjK0A");
  EXPECT_TRUE(jwt);
  EXPECT_EQ((*jwt)["name"].As<std::string>(), "denis");
  EXPECT_EQ((*jwt)["job"].As<std::string>(), "software developer");

  jwt = keys.Parse(
      "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9."
      "eyJuYW1lIjoiYWxpY2UiLCJhZ2UiOjI1fQ."
      "2bKRpES0o_8F-R49qPSOAB78E4WRZ4ZCN0ftmHZGsOoVGIHdDNTWjp0Y9KGPvg_-"
      "3GNdvQgsPmu6TIO1mrX5XQ");
  EXPECT_TRUE(jwt);
  EXPECT_EQ((*jwt)["name"].As<std::string>(), "alice");
  EXPECT_EQ((*jwt)["age"].As<uint64_t>(), 25);
}

TEST(JwtKeys, RS256Key) {
  utils::datetime::MockNowSet(mock_now);
  const auto& keys = bank_h2h::common::JwtKeys(MakeConfig({RS256Config()}));

  auto jwt = keys.Parse(
      "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
      "eyJhZG1pbiI6dHJ1ZX0."
      "bObcR8k0BtGYrpDKdzKwiCuZ7rMNwzJG17HxM_ay1Ss2IPFnD4Uv3_"
      "HTP0QPYnBbBKISPT9oeyoQvsJhAmMq7YM8RxHmsrYbbyv34o0KQ56ULoUN2NxpOK38Gc7ifE"
      "9fSkr7N8uF-srpGQVyO4A9uMuxLFfoskHYKz0jKg_HdHJbB--EMjbMgVUhMsFOrs_GPLm-"
      "wrB6V7pF0QLYd0ErcZ95B6hBGKJGK4H2s9s4SQ2G89wZmD4EOFiYBrWvo0I4FAEmITntl7Mv"
      "P0uNHtrfrRBoBnRZ23bpfcXqpxmpsR6F7nT1LMYBQ81yzktVGJiY_"
      "glg8CYYhkkY7FkZIIMxkg");
  EXPECT_TRUE(jwt);
  EXPECT_EQ((*jwt)["admin"].As<bool>(), true);
}

TEST(JwtKeys, Multiple) {
  utils::datetime::MockNowSet(mock_now);
  const auto& keys =
      bank_h2h::common::JwtKeys(MakeConfig({RS256Config(), ES256Config()}));

  // RS256
  auto jwt = keys.Parse(
      "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
      "eyJyb2xlIjoiYWRtaW4ifQ."
      "RXZuvW7P8JitzuC9ukKx72N_KQfEwUcpVBs2fTH4FSkU1k0lhQ1NbOdGyBZho1Te-d-"
      "R0Cjprpz8w2i79aEE8h2_c5pgK8JODgMPZItkqEO9xKTSzD0c4GUq_"
      "rNYpGuZ0nihHURIC7dEwZE6O_fmvo8yHmxV2aHp9jgg1n-"
      "RukAX6s1w0yQYhSnOZFWKmfWqyrq0VZrm3AQjfFV20s0XcajgHZ61pr8i5Zs6JCk-"
      "h5L7wRq4c4HrgXb3FWbqB7kW6YZLuWE3k05ThST6d6oluoc6dLXHDT5DgmKFwtvz0U-"
      "fq8vlMsBWh1cwVSE-eumFxX1mnIz2rT4hp4ZACBXrnw");
  EXPECT_TRUE(jwt);
  EXPECT_EQ((*jwt)["role"].As<std::string>(), "admin");

  // ES256
  jwt = keys.Parse(
      "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9."
      "eyJyb2xlIjoiYWRtaW4ifQ."
      "cU1g4s6tlLP_Y91yxIqExCnLDCPChpY5JHctRLzu3myoDnr1BNs7dgQk9I-"
      "Yd9qlVxlYwG8cPg39BoUdf2lPNQ");
  EXPECT_TRUE(jwt);
  EXPECT_EQ((*jwt)["role"].As<std::string>(), "admin");

  // Unknown PS256
  std::string data =
      "eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9."
      "eyJyb2xlIjoiYWRtaW4ifQ."
      "lAULwKQAsNV8gQZBQ1j4rKQ0voq8KEJMTN0OEYIdCyOse0Jm8I_aSCLsOtB9YxvZqwsC7-"
      "NUyNjkdF68dYJlocFXeSFp3tkFQu75KAJm4zvxqmYP-vWVvv_-"
      "4GwlSpUYUy8uphcZMnqf9SKso0HlBEfCm3DqA9ujNHOWT7qfSFYmmfU7MzQOfpqJAW40MTOG"
      "SMsJqmKHyiORBacfgDUirFWtyjj3zKTxXSbrrnJxq1bfVIDEQ5AX6oqe31VL6FNKBqiw_"
      "vMd9zNdOlG3Gz35F61H_bT6DtGBBBIXC1KWIUQF2L9XzqNcP58C_DRFAgA-"
      "L1uIn05ILqtEND96VZCqpA";
  EXPECT_FALSE(keys.Parse(data));
}
