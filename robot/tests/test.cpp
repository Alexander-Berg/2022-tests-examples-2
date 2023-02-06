#include <library/cpp/testing/gtest/gtest.h>
#include <robot/blrt/library/yabs_id_generator/proxy.h>

using namespace NBlrt::NYabsIdGenerator;

using ::testing::ElementsAre;
using ::testing::Return;

namespace {
    constexpr TStringBuf apple = "apple.com";
    constexpr TStringBuf yandex = "yandex.ru";
    constexpr TStringBuf facebook = "facebook.com";
    constexpr TStringBuf microsoft = "microsoft.com";

    constexpr ui64 yandex_domain_id = 17242;
}

class TClientMock : public IClient {
public:
    MOCK_METHOD((TVector<std::pair<TStringBuf, ui64>>), GetDomainIds, (const TVector<TStringBuf>&), (override));
};

class TYabsIdGeneratorMockTest : public ::testing::Test {
public:
    TYabsIdGeneratorMockTest()
        : MockClient(new TClientMock())
        , Proxy(MockClient, 3)
    {
    }

protected:
    TIntrusivePtr<TClientMock> MockClient;
    TProxy Proxy;
};

TEST_F(TYabsIdGeneratorMockTest, GetDomainIds) {
    const auto expectedResult1 = TVector<std::pair<TStringBuf, ui64>>{{yandex, 1}, {apple, 2}, {facebook, 3}};
    const auto expectedResult2 = TVector<std::pair<TStringBuf, ui64>>{{yandex, 1}, {apple, 2}, {microsoft, 4}};

    EXPECT_CALL(*MockClient, GetDomainIds(ElementsAre(yandex, apple, facebook)))
        .WillOnce(Return(expectedResult1));

    auto result = Proxy.GetDomainIds({yandex, apple, facebook});
    EXPECT_EQ(result, expectedResult1);

    EXPECT_CALL(*MockClient, GetDomainIds(ElementsAre(microsoft)))
        .WillOnce(Return(TVector<std::pair<TStringBuf, ui64>>{{microsoft, 4}}));

    result = Proxy.GetDomainIds({yandex, apple, microsoft});
    EXPECT_EQ(result, expectedResult2);

    EXPECT_CALL(*MockClient, GetDomainIds(ElementsAre(facebook)))
        .WillOnce(Return(TVector<std::pair<TStringBuf, ui64>>{{facebook, 3}}));

    result = Proxy.GetDomainIds({yandex, apple, facebook});
    EXPECT_EQ(result, expectedResult1);
}

TEST(DISABLED_TYabsIdGeneratorTest, GetDomainIds) {
    auto client = MakeIntrusive<NBlrt::NYabsIdGenerator::TBaseClient>(
        "http://yabs-id-generator-test.in.yandex-team.ru/domain"
    );
    const auto domainsWithId = client->GetDomainIds({yandex});
    ASSERT_FALSE(domainsWithId.empty());
    EXPECT_EQ(domainsWithId[0].first, yandex);
    EXPECT_EQ(domainsWithId[0].second, yandex_domain_id);
}

