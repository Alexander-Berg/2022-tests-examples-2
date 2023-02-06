#include <gtest/gtest.h>

#include <jwt/jwt.hpp>

#include <jwt/unsafe.hpp>
#include <userver/crypto/base64.hpp>
#include <userver/crypto/signers.hpp>
#include <userver/crypto/verifiers.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

namespace {
extern std::string rsa_priv_key;
extern std::string rsa_pub_key;
extern std::string rsa_pub_key_invalid;
extern std::string rsa512_priv_key;
extern std::string rsa512_pub_key;
extern std::string rsa512_pub_key_invalid;
extern std::string ecdsa_priv_key;
extern std::string ecdsa_pub_key;
extern std::string ecdsa_pub_key_invalid;
extern std::string ecdsa512_priv_key;
extern std::string ecdsa512_pub_key;
extern std::string eda_rsa_pub_key;
}  // namespace

TEST(Jwt, SignerNone) {
  formats::json::ValueBuilder builder;
  builder["id"] = "test";

  ASSERT_EQ(jwt::Encode(builder.ExtractValue()),
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJpZCI6InRlc3QifQ.");

  ASSERT_EQ(jwt::Decode(
                "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJpZCI6InRlc3QifQ.")["id"]
                .As<std::string>(),
            "test");
}

TEST(Jwt, VerificationErrorData) {
  formats::json::ValueBuilder builder;
  builder["id"] = "test";
  crypto::SignerHs256 signer("secret");

  auto token = jwt::Encode(builder.ExtractValue(), signer);

  crypto::VerifierHs256 verifier("bad_secret");
  try {
    auto id = jwt::Decode(token, verifier)["id"].As<std::string>();
    ASSERT_EQ(id, "never happend");
  } catch (const jwt::SignatureVerificationError& exc) {
    ASSERT_EQ(exc.Payload()["id"].As<std::string>(), "test");
  } catch (const std::exception& e) {
    FAIL() << "unexpected exception: " << e.what();
  }

  ASSERT_THROW(jwt::Decode(token, verifier), jwt::SignatureVerificationError);
}

TEST(Jwt, SignerHS256) {
  formats::json::ValueBuilder builder;
  builder["id"] = "test";
  crypto::SignerHs256 signer("secret");

  auto token = jwt::Encode(builder.ExtractValue(), signer);
  ASSERT_EQ(token,
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6InRlc3QifQ.DUCa-"
            "36iA9SxvRuO_v5HlR17KZLHq1zn5ePAeG9ESb0");

  crypto::VerifierHs256 verifier("secret");
  ASSERT_EQ(jwt::Decode(token, verifier)["id"].As<std::string>(), "test");

  EXPECT_THROW(
      jwt::Decode("eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0=.eyJpZCI6InRlc3QifQ==.",
                  verifier)["id"]
          .As<std::string>(),
      jwt::SignatureVerificationError);
}

TEST(Jwt, SignerRs256) {
  formats::json::ValueBuilder builder;
  builder["iss"] = "auth0";

  const std::string ValidToken =
      "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJhdXRoMCJ9.tjU17DRyqSa08-"
      "wIqb4Iasr15oQWuMBobHGXWZorxm1QSp_roL28vSCPZ-AXf0YV7YwZ59Ht-"
      "4k4UUXUCQCYHusF5CszE8Cz0VKmetdpNfhOz4B4MMkvTJ-"
      "Tw9hFEC4JlrjEZR3hOtQjAac73m1hYYpnYhGLdDMSOXXmqCJ8UkrbeQpFIK6IUULBNQ10rHB"
      "7_NMqyC4WtfB3lhWJhYbuE_bX7FJgI2cLy7zFp-TWg0or7tQPdKlIASbBSksYe-"
      "OtogNpzcOKiSs4HXutwN04RmudL6RUJLswABoeEnU-"
      "bhoUTyDBMVdWjCH2lzOAzOtdP4ntrlBs2cx7vcXqLhrPWw";
  crypto::SignerRs256 signer(rsa_priv_key);

  ASSERT_EQ(jwt::Encode(builder.ExtractValue(), signer), ValidToken);

  crypto::VerifierRs256 verifier(rsa_pub_key);
  ASSERT_EQ(jwt::Decode(ValidToken, verifier)["iss"].As<std::string>(),
            "auth0");
}

TEST(Jwt, CreateTokenES256) {
  formats::json::ValueBuilder builder;
  builder["iss"] = "auth0";

  crypto::SignerEs256 signer(ecdsa_priv_key);
  auto token = jwt::Encode(builder.ExtractValue(), signer);

  // no throw,
  crypto::VerifierEs256 verifier(ecdsa_pub_key);
  ASSERT_EQ(jwt::Decode(token, verifier)["iss"].As<std::string>(), "auth0");

  // throw execption because of incorrect public key
  crypto::VerifierEs256 bad_verifier(ecdsa_pub_key_invalid);
  ASSERT_THROW(jwt::Decode(token, bad_verifier),
               jwt::SignatureVerificationError);
}

TEST(Jwt, CreateTokenES512) {
  formats::json::ValueBuilder builder;
  builder["iss"] = "auth0";

  crypto::SignerEs512 signer(ecdsa512_priv_key);
  auto token = jwt::Encode(builder.ExtractValue(), signer);

  // no throw,
  crypto::VerifierEs512 verifier(ecdsa512_pub_key);
  ASSERT_EQ(jwt::Decode(token, verifier)["iss"].As<std::string>(), "auth0");
}

TEST(Jwt, CreateTokenPS256) {
  formats::json::ValueBuilder builder;
  builder["iss"] = "auth0";

  crypto::SignerPs256 signer(rsa_priv_key);
  auto token = jwt::Encode(builder.ExtractValue(), signer);

  // no throw,
  crypto::VerifierPs256 verifier(rsa_pub_key);
  ASSERT_EQ(jwt::Decode(token, verifier)["iss"].As<std::string>(), "auth0");

  // throw execption because of incorrect public key
  crypto::VerifierPs256 bad_verifier(rsa_pub_key_invalid);
  ASSERT_THROW(jwt::Decode(token, bad_verifier),
               jwt::SignatureVerificationError);
}

TEST(Jwt, VerifyTokenPS256) {
  std::string token =
      "eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXUyJ9.eyJpc3MiOiJhdXRoMCJ9."
      "CJ4XjVWdbV6vXGZkD4GdJbtYc80SN9cmPOqRhZBRzOyDRqTFE"
      "4MsbdKyQuhAWcvuMOjn-24qOTjVMR_P_"
      "uTC1uG6WPLcucxZyLnbb56zbKnEklW2SX0mQnCGewr-93a_vDaFT6Cp45MsF_"
      "OwFPRCMaS5CJg-"
      "N5KY67UrVSr3s9nkuK9ZTQkyODHfyEUh9F_FhRCATGrb5G7_"
      "qHqBYvTvaPUXqzhhpCjN855Tocg7A24Hl0yMwM-XdasucW5xNdKjG_YCkis"
      "HX7ax--JiF5GNYCO61eLFteO4THUg-"
      "3Z0r4OlGqlppyWo5X5tjcxOZCvBh7WDWfkxA48KFZPRv0nlKA";

  crypto::VerifierPs256 verifier(rsa_pub_key);

  ASSERT_NO_THROW(jwt::Decode(token, verifier));
}

TEST(Jwt, VerifyTokenPS256Fail) {
  std::string token =
      "eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXUyJ9.eyJpc3MiOiJhdXRoMCJ9."
      "CJ4XjVWdbV6vXGZkD4GdJbtYc80SN9cmPOqRhZBRzOyDRqTFE"
      "4MsbdKyQuhAWcvuMOjn-24qOTjVMR_P_"
      "uTC1uG6WPLcucxZyLnbb56zbKnEklW2SX0mQnCGewr-93a_vDaFT6Cp45MsF_"
      "OwFPRCMaS5CJg-"
      "N5KY67UrVSr3s9nkuK9ZTQkyODHfyEUh9F_FhRCATGrb5G7_"
      "qHqBYvTvaPUXqzhhpCjN855Tocg7A24Hl0yMwM-XdasucW5xNdKjG_YCkis"
      "HX7ax--JiF5GNYCO61eLFteO4THUg-"
      "3Z0r4OlGqlppyWo5X5tjcxOZCvBh7WDWfkxA48KFZPRv0nlKA";

  crypto::VerifierPs256 bad_verifier(rsa_pub_key_invalid);

  ASSERT_THROW(jwt::Decode(token, bad_verifier),
               jwt::SignatureVerificationError);
}

TEST(Jwt, VerifyTokenES256) {
  std::string token =
      "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhdXRoMCJ9."
      "5aGgcoQFFcVigCuylkx2_WhHEb4uWE-fRZZOaS8IqK1DIvi74zDACjcvg1-"
      "w0oG1rCLOZkxrwsrr6M4DRm2UNg";

  crypto::VerifierEs256 verifier(ecdsa_pub_key);

  ASSERT_NO_THROW(jwt::Decode(token, verifier));
}

TEST(Jwt, VerifyTokenES256Fail) {
  std::string token =
      "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhdXRoMCJ9."
      "5aGgcoQFFcVigCuylkx2_WhHEb4uWE-fRZZOaS8IqK1DIvi74zDACjcvg1-"
      "w0oG1rCLOZkxrwsrr6M4DRm2UNg";

  crypto::VerifierEs256 verifier(ecdsa_pub_key_invalid);

  ASSERT_THROW(jwt::Decode(token, verifier), jwt::SignatureVerificationError);
}

TEST(Jwt, VerifyTokenES512) {
  std::string token =
      "eyJhbGciOiJFUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhdXRoMCJ9."
      "AXsBpDEyP0BByMz0X2Zb2QdsgGQPMvdji52f-dhFyNa8eOa8Ui_-dZvsLHtX_"
      "ZdVosFiwHmy6g-"
      "NAWt0twVHgXaoAb3dfjggqSfnPJiCSUbn8sXjYINLcxQWOiuitLmciW0SwLrKFUc9SHF_"
      "ZBRlJar-S_8mxyYMV0UFEqWQz6VEftfp";

  crypto::VerifierEs512 verifier(ecdsa512_pub_key);

  ASSERT_NO_THROW(jwt::Decode(token, verifier));
}

TEST(Jwt, CreateVerifier) {
  auto verifier =
      jwt::Config("HS512", jwt::Config::PrivateKey{"secret"}).CreateVerifier();
  ASSERT_NO_THROW(jwt::Decode(
      "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9."
      "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlh"
      "dCI6MTUxNjIzOTAyMn0.nZU_gPcMXkWpkCUpJceSxS7lSickF0tTImHhAR949Z-"
      "Nt69LgW8G6lid-mqd9B579tYM8C4FN2jdhR2VRMsjtA",
      *verifier));

  verifier = jwt::Config("RS256", jwt::Config::PublicKey{rsa_pub_key})
                 .CreateVerifier();
  const std::string ValidRsaToken =
      "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhdXRoMCJ9.dxXF3MdsyW-"
      "AuvwJpaQtrZ33fAde9xWxpLIg9cO2tMLH2GSRNuLAe61KsJusZhqZB9Iy7DvflcmRz-"
      "9OZndm6cj_"
      "ThGeJH2LLc90K83UEvvRPo8l85RrQb8PcanxCgIs2RcZOLygERizB3pr5icGkzR7R2y6zgNC"
      "jKJ5_NJ6EiZsGN6_nc2PRK_DbyY-"
      "Wn0QDxIxKoA5YgQJ9qafe7IN980pXvQv2Z62c3XR8dYuaXBqhthBj-AbaFHEpZapN-V-"
      "TmuLNzR2MCB6Xr7BYMuCaqWf_XU8og4XNe8f_8w9Wv5vvgqMM1KhqVpG5VdMJv4o_"
      "L4NoCROHhtUQSLRh2M9cA";
  ASSERT_NO_THROW(jwt::Decode(ValidRsaToken, *verifier));
}

TEST(Jwt, CreateSigner) {
  formats::json::ValueBuilder builder;
  builder["id"] = "test";
  const auto test_doc = builder.ExtractValue();

  auto signer =
      jwt::Config("HS512", jwt::Config::PrivateKey{"secret"}).CreateSigner();
  ASSERT_NO_THROW(jwt::Encode(test_doc, *signer));

  signer = jwt::Config("RS256", jwt::Config::PrivateKey{rsa_priv_key})
               .CreateSigner();
  ASSERT_NO_THROW(jwt::Encode(test_doc, *signer));

  EXPECT_THROW(
      jwt::Config("RS256", jwt::Config::PublicKey{rsa_pub_key}).CreateSigner(),
      jwt::ConfigError);
}

TEST(Jwt, Header) {
  crypto::SignerRs256 signer(rsa_priv_key);

  formats::json::ValueBuilder builder;
  builder["id"] = "key_id_test";
  const auto test_doc = builder.ExtractValue();

  const auto plain_jwt = jwt::Encode(test_doc, signer);
  const auto plain_header =
      formats::json::FromString(crypto::base64::Base64UrlDecode(
          plain_jwt.substr(0, plain_jwt.find('.'))));
  EXPECT_EQ("JWT", plain_header["typ"].As<std::string>(""));
  EXPECT_EQ("RS256", plain_header["alg"].As<std::string>(""));
  EXPECT_FALSE(plain_header.HasMember("kid"));

  const auto key_id_jwt = jwt::Encode(test_doc, signer, "testKey!");
  const auto key_id_header =
      formats::json::FromString(crypto::base64::Base64UrlDecode(
          key_id_jwt.substr(0, key_id_jwt.find('.'))));
  EXPECT_EQ("JWT", key_id_header["typ"].As<std::string>(""));
  EXPECT_EQ("RS256", key_id_header["alg"].As<std::string>(""));
  EXPECT_EQ("testKey!", key_id_header["kid"].As<std::string>(""));
}

TEST(Jwt, UncheckedPayload) {
  formats::json::ValueBuilder builder;
  builder["id"] = "unsafe_test";
  auto encoded_payload = crypto::base64::Base64UrlEncode(
      formats::json::ToString(builder.ExtractValue()));
  auto token = "not_a_token." + encoded_payload + ".bad_signature";

  EXPECT_EQ("unsafe_test",
            jwt::unsafe::GetUncheckedPayload(token)["id"].As<std::string>());
}

TEST(Jwt, CurveMatch) {
  EXPECT_NO_THROW(crypto::SignerEs256{ecdsa_priv_key});
  EXPECT_THROW(crypto::SignerEs256{ecdsa512_priv_key}, crypto::SignError);

  EXPECT_NO_THROW(crypto::SignerEs512{ecdsa512_priv_key});
  EXPECT_THROW(crypto::SignerEs512{ecdsa_priv_key}, crypto::SignError);

  EXPECT_NO_THROW(crypto::VerifierEs256{ecdsa_pub_key});
  EXPECT_THROW(crypto::VerifierEs256{ecdsa512_pub_key},
               crypto::VerificationError);

  EXPECT_NO_THROW(crypto::VerifierEs512{ecdsa512_pub_key});
  EXPECT_THROW(crypto::VerifierEs512{ecdsa_pub_key}, crypto::VerificationError);
}

formats::json::Value MakeExpNbfPayload(
    std::optional<std::chrono::system_clock::time_point> nbf,
    std::optional<std::chrono::system_clock::time_point> exp) {
  formats::json::ValueBuilder value_builder;
  if (exp) {
    value_builder["exp"] = std::chrono::system_clock::to_time_t(exp.value());
  }
  if (nbf) {
    value_builder["nbf"] = std::chrono::system_clock::to_time_t(nbf.value());
  }
  return value_builder.ExtractValue();
}

TEST(Jwt, IsPayloadValidAtTime) {
  using namespace std::literals;

  const auto now = utils::datetime::Now();

  EXPECT_FALSE(jwt::IsPayloadValidAtTime(
      MakeExpNbfPayload(now + 5s, std::nullopt), now));
  EXPECT_FALSE(jwt::IsPayloadValidAtTime(
      MakeExpNbfPayload(std::nullopt, now - 5s), now));

  EXPECT_TRUE(
      jwt::IsPayloadValidAtTime(MakeExpNbfPayload(now - 5s, now + 5s), now));
  EXPECT_TRUE(jwt::IsPayloadValidAtTime(
      MakeExpNbfPayload(now - 5s, std::nullopt), now));
  EXPECT_TRUE(jwt::IsPayloadValidAtTime(
      MakeExpNbfPayload(std::nullopt, now + 5s), now));
  EXPECT_TRUE(jwt::IsPayloadValidAtTime(
      MakeExpNbfPayload(std::nullopt, std::nullopt), now));
}

namespace {
std::string rsa_priv_key = R"(-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQC4ZtdaIrd1BPIJ
tfnF0TjIK5inQAXZ3XlCrUlJdP+XHwIRxdv1FsN12XyMYO/6ymLmo9ryoQeIrsXB
XYqlET3zfAY+diwCb0HEsVvhisthwMU4gZQu6TYW2s9LnXZB5rVtcBK69hcSlA2k
ZudMZWxZcj0L7KMfO2rIvaHw/qaVOE9j0T257Z8Kp2CLF9MUgX0ObhIsdumFRLaL
DvDUmBPr2zuh/34j2XmWwn1yjN/WvGtdfhXW79Ki1S40HcWnygHgLV8sESFKUxxQ
mKvPUTwDOIwLFL5WtE8Mz7N++kgmDcmWMCHc8kcOIu73Ta/3D4imW7VbKgHZo9+K
3ESFE3RjAgMBAAECggEBAJTEIyjMqUT24G2FKiS1TiHvShBkTlQdoR5xvpZMlYbN
tVWxUmrAGqCQ/TIjYnfpnzCDMLhdwT48Ab6mQJw69MfiXwc1PvwX1e9hRscGul36
ryGPKIVQEBsQG/zc4/L2tZe8ut+qeaK7XuYrPp8bk/X1e9qK5m7j+JpKosNSLgJj
NIbYsBkG2Mlq671irKYj2hVZeaBQmWmZxK4fw0Istz2WfN5nUKUeJhTwpR+JLUg4
ELYYoB7EO0Cej9UBG30hbgu4RyXA+VbptJ+H042K5QJROUbtnLWuuWosZ5ATldwO
u03dIXL0SH0ao5NcWBzxU4F2sBXZRGP2x/jiSLHcqoECgYEA4qD7mXQpu1b8XO8U
6abpKloJCatSAHzjgdR2eRDRx5PMvloipfwqA77pnbjTUFajqWQgOXsDTCjcdQui
wf5XAaWu+TeAVTytLQbSiTsBhrnoqVrr3RoyDQmdnwHT8aCMouOgcC5thP9vQ8Us
rVdjvRRbnJpg3BeSNimH+u9AHgsCgYEA0EzcbOltCWPHRAY7B3Ge/AKBjBQr86Kv
TdpTlxePBDVIlH+BM6oct2gaSZZoHbqPjbq5v7yf0fKVcXE4bSVgqfDJ/sZQu9Lp
PTeV7wkk0OsAMKk7QukEpPno5q6tOTNnFecpUhVLLlqbfqkB2baYYwLJR3IRzboJ
FQbLY93E8gkCgYB+zlC5VlQbbNqcLXJoImqItgQkkuW5PCgYdwcrSov2ve5r/Acz
FNt1aRdSlx4176R3nXyibQA1Vw+ztiUFowiP9WLoM3PtPZwwe4bGHmwGNHPIfwVG
m+exf9XgKKespYbLhc45tuC08DATnXoYK7O1EnUINSFJRS8cezSI5eHcbQKBgQDC
PgqHXZ2aVftqCc1eAaxaIRQhRmY+CgUjumaczRFGwVFveP9I6Gdi+Kca3DE3F9Pq
PKgejo0SwP5vDT+rOGHN14bmGJUMsX9i4MTmZUZ5s8s3lXh3ysfT+GAhTd6nKrIE
kM3Nh6HWFhROptfc6BNusRh1kX/cspDplK5x8EpJ0QKBgQDWFg6S2je0KtbV5PYe
RultUEe2C0jYMDQx+JYxbPmtcopvZQrFEur3WKVuLy5UAy7EBvwMnZwIG7OOohJb
vkSpADK6VPn9lbqq7O8cTedEHttm6otmLt8ZyEl3hZMaL3hbuRj6ysjmoFKx6CrX
rK0/Ikt5ybqUzKCMJZg2VKGTxg==
-----END PRIVATE KEY-----)";
std::string rsa_pub_key = R"(-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuGbXWiK3dQTyCbX5xdE4
yCuYp0AF2d15Qq1JSXT/lx8CEcXb9RbDddl8jGDv+spi5qPa8qEHiK7FwV2KpRE9
83wGPnYsAm9BxLFb4YrLYcDFOIGULuk2FtrPS512Qea1bXASuvYXEpQNpGbnTGVs
WXI9C+yjHztqyL2h8P6mlThPY9E9ue2fCqdgixfTFIF9Dm4SLHbphUS2iw7w1JgT
69s7of9+I9l5lsJ9cozf1rxrXX4V1u/SotUuNB3Fp8oB4C1fLBEhSlMcUJirz1E8
AziMCxS+VrRPDM+zfvpIJg3JljAh3PJHDiLu902v9w+Iplu1WyoB2aPfitxEhRN0
YwIDAQAB
-----END PUBLIC KEY-----)";
std::string rsa_pub_key_invalid = R"(-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxzYuc22QSst/dS7geYYK
5l5kLxU0tayNdixkEQ17ix+CUcUbKIsnyftZxaCYT46rQtXgCaYRdJcbB3hmyrOa
vkhTpX79xJZnQmfuamMbZBqitvscxW9zRR9tBUL6vdi/0rpoUwPMEh8+Bw7CgYR0
FK0DhWYBNDfe9HKcyZEv3max8Cdq18htxjEsdYO0iwzhtKRXomBWTdhD5ykd/fAC
VTr4+KEY+IeLvubHVmLUhbE5NgWXxrRpGasDqzKhCTmsa2Ysf712rl57SlH0Wz/M
r3F7aM9YpErzeYLrl0GhQr9BVJxOvXcVd4kmY+XkiCcrkyS1cnghnllh+LCwQu1s
YwIDAQAB
-----END PUBLIC KEY-----)";
std::string rsa512_priv_key = R"(-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQDdlatRjRjogo3WojgGHFHYLugdUWAY9iR3fy4arWNA1KoS8kVw
33cJibXr8bvwUAUparCwlvdbH6dvEOfou0/gCFQsHUfQrSDv+MuSUMAe8jzKE4qW
+jK+xQU9a03GUnKHkkle+Q0pX/g6jXZ7r1/xAK5Do2kQ+X5xK9cipRgEKwIDAQAB
AoGAD+onAtVye4ic7VR7V50DF9bOnwRwNXrARcDhq9LWNRrRGElESYYTQ6EbatXS
3MCyjjX2eMhu/aF5YhXBwkppwxg+EOmXeh+MzL7Zh284OuPbkglAaGhV9bb6/5Cp
uGb1esyPbYW+Ty2PC0GSZfIXkXs76jXAu9TOBvD0ybc2YlkCQQDywg2R/7t3Q2OE
2+yo382CLJdrlSLVROWKwb4tb2PjhY4XAwV8d1vy0RenxTB+K5Mu57uVSTHtrMK0
GAtFr833AkEA6avx20OHo61Yela/4k5kQDtjEf1N0LfI+BcWZtxsS3jDM3i1Hp0K
Su5rsCPb8acJo5RO26gGVrfAsDcIXKC+bQJAZZ2XIpsitLyPpuiMOvBbzPavd4gY
6Z8KWrfYzJoI/Q9FuBo6rKwl4BFoToD7WIUS+hpkagwWiz+6zLoX1dbOZwJACmH5
fSSjAkLRi54PKJ8TFUeOP15h9sQzydI8zJU+upvDEKZsZc/UhT/SySDOxQ4G/523
Y0sz/OZtSWcol/UMgQJALesy++GdvoIDLfJX5GBQpuFgFenRiRDabxrE9MNUZ2aP
FaFp+DyAe+b4nDwuJaW2LURbr8AEZga7oQj0uYxcYw==
-----END RSA PRIVATE KEY-----)";
std::string rsa512_pub_key = R"(-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDdlatRjRjogo3WojgGHFHYLugd
UWAY9iR3fy4arWNA1KoS8kVw33cJibXr8bvwUAUparCwlvdbH6dvEOfou0/gCFQs
HUfQrSDv+MuSUMAe8jzKE4qW+jK+xQU9a03GUnKHkkle+Q0pX/g6jXZ7r1/xAK5D
o2kQ+X5xK9cipRgEKwIDAQAB
-----END PUBLIC KEY-----)";
std::string rsa512_pub_key_invalid = R"(-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxzYuc22QSst/dS7geYYK
5l5kLxU0tayNdixkEQ17ix+CUcUbKIsnyftZxaCYT46rQtXgCaYRdJcbB3hmyrOa
vkhTpX79xJZnQmfuamMbZBqitvscxW9zRR9tBUL6vdi/0rpoUwPMEh8+Bw7CgYR0
FK0DhWYBNDfe9HKcyZEv3max8Cdq18htxjEsdYO0iwzhtKRXomBWTdhD5ykd/fAC
VTr4+KEY+IeLvubHVmLUhbE5NgWXxrRpGasDqzKhCTmsa2Ysf712rl57SlH0Wz/M
r3F7aM9YpErzeYLrl0GhQr9BVJxOvXcVd4kmY+XkiCcrkyS1cnghnllh+LCwQu1s
YwIDAQAB
-----END PUBLIC KEY-----)";
std::string ecdsa_priv_key = R"(-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgPGJGAm4X1fvBuC1z
SpO/4Izx6PXfNMaiKaS5RUkFqEGhRANCAARCBvmeksd3QGTrVs2eMrrfa7CYF+sX
sjyGg+Bo5mPKGH4Gs8M7oIvoP9pb/I85tdebtKlmiCZHAZE5w4DfJSV6
-----END PRIVATE KEY-----)";
std::string ecdsa_pub_key = R"(-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEQgb5npLHd0Bk61bNnjK632uwmBfr
F7I8hoPgaOZjyhh+BrPDO6CL6D/aW/yPObXXm7SpZogmRwGROcOA3yUleg==
-----END PUBLIC KEY-----)";
std::string ecdsa_pub_key_invalid = R"(-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEoBUyo8CQAFPeYPvv78ylh5MwFZjT
CLQeb042TjiMJxG+9DLFmRSMlBQ9T/RsLLc+PmpB1+7yPAR+oR5gZn3kJQ==
-----END PUBLIC KEY-----)";
std::string ecdsa512_priv_key = R"(-----BEGIN EC PRIVATE KEY-----
MIHcAgEBBEIADZbvukRPYwxbnY0RRAm7TnXV04JS3c/afpJ7kkL6FPI9S0bOjYIy
SKoARgcENeLiqm6U2wCfgC06mo2KxRfWvYOgBwYFK4EEACOhgYkDgYYABAFDGNaa
Lwb5Ra5PbFXL0I8T8E4FHtoinKCw8Lb0g/mhY79L68Lepc9zXu0ZLcKjAn9Sb6kT
UFwYEYSBmnpmabtKbwG7CkxfvyqcCkPY84+5N1mOK+kc/uzF9/wreN+q5sj/1lLh
HIZMRqqP+mZgYVH+/DmpTGOzY/EZBKGDBc/9yClIcg==
-----END EC PRIVATE KEY-----)";
std::string ecdsa512_pub_key = R"(-----BEGIN PUBLIC KEY-----
MIGbMBAGByqGSM49AgEGBSuBBAAjA4GGAAQBQxjWmi8G+UWuT2xVy9CPE/BOBR7a
IpygsPC29IP5oWO/S+vC3qXPc17tGS3CowJ/Um+pE1BcGBGEgZp6Zmm7Sm8BuwpM
X78qnApD2POPuTdZjivpHP7sxff8K3jfqubI/9ZS4RyGTEaqj/pmYGFR/vw5qUxj
s2PxGQShgwXP/cgpSHI=
-----END PUBLIC KEY-----)";
std::string eda_rsa_pub_key = R"(-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAvS066ABssjWh3ZmBB5og
aBcK9KykRv9nkuLMjwib93yLDvApk5CNlIIFMFwEw9ufaxKJWOqqDBwTgRPIlEsp
OwPmKjtVb/rUrAGp+bjKokUsR5XlYdwWg7NVDhtJjtD1GisiT9waFCZdB5mp4hQ0
KC8E4fVZqcEveRaCiiBXKwaPH0tQr42j/cDV74OVin+Wyhf5QyMh844FSgr+16Po
o0c962QNEMdNj0M5TD99+kzmrOTcTnar4lV4EDKJq4Tg7PMBXcFZovZ4W0EJK+JM
IearKRiYrTbXLfRXhRs/FULQbT7JxJBYWyIexdSPvvK1kap4+Hx8xJDKmghss8BS
yECP9zvuRMpGws5atItLY/QjI/0JxoUbJar23qHMjlju48FpHzr8bGWLUNB7mRlP
9aLABOaLKt+OgqwwUU12rhKHaSwY7XsjE365xe+gohv7nLkDPAC+lVTFDhNfbHJ2
UQK48Pgpg2RjpLhPQ7K4OYym/9gB9WtzwtCDV9Lr1LrzmR2PF3lsJc5zMm8rDo0z
IYiTFEG3z8EAsiFycX2QDoQhLg+g61x+mWu8EHKaBxdIVNagDDwK5lHqxRNIXWIp
6fotdAdbPars8Yk/oukmGajN01oQbSH5vFxJTVEkWjvZG54TCny1FCl6QiqwR/XF
jgf93lZBRaVDT7aoX7J81psCAwEAAQ==
-----END PUBLIC KEY-----)";

}  // namespace
