#include <security/gideon/pam_gideon/lib/ssh_utils.h>

#include <library/cpp/testing/gtest/gtest.h>

using namespace NGideon::NSsh;

namespace NGideon::NSsh {
    void PrintTo(const TAuthInfo &authInfo, ::std::ostream *os) {
        (*os) << "{.AuthMethod="sv
              << AuthMethodName(authInfo.AuthMethod)
              << ", .KeyTypeName="sv << authInfo.KeyTypeName
              << ", .Fingerprint="sv << authInfo.Fingerprint
              << "}"sv;
    }
}

class ParseAuthInfoParametersTests : public ::testing::TestWithParam<std::tuple<TString, TAuthInfo>> {
};

TEST_P(ParseAuthInfoParametersTests, Parse) {
    TString authInfo = std::get<0>(GetParam());
    TAuthInfo expected = std::get<1>(GetParam());

    TAuthInfo actual = ParseAuthInfo(authInfo);
    EXPECT_EQ(actual, expected);
}

INSTANTIATE_TEST_SUITE_P(
    ParseAuthInfoTests,
    ParseAuthInfoParametersTests,
    ::testing::Values(
        std::make_tuple(
            "password",
            TAuthInfo{.AuthMethod = EAuthMethod::Password}
        ),
        std::make_tuple(
            "password\n",
            TAuthInfo{.AuthMethod = EAuthMethod::Password}
        ),
        std::make_tuple(
            "password\nlalala",
            TAuthInfo{.AuthMethod = EAuthMethod::Password}
        ),
        std::make_tuple(
            "publickey ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDD5skB0CnUQOBUMFdiwQRzf0Zg/B9gKsAsB+3IuPPP+OS5qeq1YkFjq3BtQiV+AwhKUIk/72+H4usTul2Z2BQ+BQeuzua9/Ht7VhdlqJYgC4h2mJ/hPeWnSPjzzjvY5Ar9G+EuGEtYyMaQ3fZ+0XqnvrXs4ENEpQ5angPfD77XDX1xzTw3JjjdIFqnFH/F/P3VJuypx9eTwVLqCH0yFQsUC+qFy1pQJYB8DUrMHtVPsl27Zd2EwZnCyC1ADEQiV1xTb+kiBK6jejydWpZqjHEDVaU8TDkkfk11NzhJx8+3hvcsA4/y5L+VECkUhQB3JhloOuQd0QKSrEMrcdEzp+o7",
            TAuthInfo{
                .AuthMethod = EAuthMethod::PublicKey,
                .KeyTypeName = "ssh-rsa",
                .Fingerprint = "SHA256:C0Q14mSJLVITEyGsP6QLE1Z/GfTwEq1mLzVemnVch0E",
            }
        ),
        std::make_tuple(
            "publickey ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDD5skB0CnUQOBUMFdiwQRzf0Zg/B9gKsAsB+3IuPPP+OS5qeq1YkFjq3BtQiV+AwhKUIk/72+H4usTul2Z2BQ+BQeuzua9/Ht7VhdlqJYgC4h2mJ/hPeWnSPjzzjvY5Ar9G+EuGEtYyMaQ3fZ+0XqnvrXs4ENEpQ5angPfD77XDX1xzTw3JjjdIFqnFH/F/P3VJuypx9eTwVLqCH0yFQsUC+qFy1pQJYB8DUrMHtVPsl27Zd2EwZnCyC1ADEQiV1xTb+kiBK6jejydWpZqjHEDVaU8TDkkfk11NzhJx8+3hvcsA4/y5L+VECkUhQB3JhloOuQd0QKSrEMrcdEzp+o7\n",
            TAuthInfo{
                    .AuthMethod = EAuthMethod::PublicKey,
                    .KeyTypeName = "ssh-rsa",
                    .Fingerprint = "SHA256:C0Q14mSJLVITEyGsP6QLE1Z/GfTwEq1mLzVemnVch0E",
            }
        ),
        std::make_tuple(
            "publickey ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBNBDSGHXl/8R/FloaVY5e4w50n6zqkRdlm3aacXRRk5poJGsJqxc1iBcNzCUBsKMPX5FiKBpV7i+iOvGGFlt018=",
            TAuthInfo{
                    .AuthMethod = EAuthMethod::PublicKey,
                    .KeyTypeName = "ecdsa-sha2-nistp256",
                    .Fingerprint = "SHA256:9QmY2M1VK5llyKo8E2L72hwTIF9AhAwL4evqf+/DFEQ",
            }
        )
    ));


class ParseAuthInfoFailParametersTests : public ::testing::TestWithParam<TString> {
};

TEST_P(ParseAuthInfoFailParametersTests, Parse) {
    EXPECT_ANY_THROW(ParseAuthInfo(GetParam()));
}

INSTANTIATE_TEST_SUITE_P(
        ParseAuthInfoFail,
        ParseAuthInfoFailParametersTests,
        ::testing::Values(
                "",
                "#"
                "\n"
                "foobar",
                "foo bar",
                "foo bar baz",
                "publickey",
                "publickey lala",
                "publickey ssh-rsa"
        ));
