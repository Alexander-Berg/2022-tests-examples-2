#include <userver/utest/utest.hpp>

#include <test/common.hpp>
#include <test/mocks/unique_drivers_client_mock.hpp>

#include <eventus/mappers/remote/fetch_unique_driver_profiles_mapper.hpp>

namespace {

const auto kDestinationKey = "unique_driver_profiles";
const auto kServiceName = "the-greatest-service-name-ever";

}  // namespace

TEST(MappersSuite, FetchUniqueDriverProfilesMapperTest) {
  using test::mocks::UniqueDriversClient;
  using Response = clients::unique_drivers::
      v1_driver_profiles_retrieve_by_uniques::post::Response200;

  UniqueDriversClient unique_driver_client_mock;

  using namespace test::common;
  [[maybe_unused]] auto mapper =
      MakeOperation<eventus::mappers::remote::FetchUniqueDriverProfilesMapper>(
          OperationArgsV{
              {"src", "unique_driver_id"},
              {"dst", kDestinationKey},
              {"debug", "yes"},
          },
          unique_driver_client_mock, kServiceName);

  const auto consumer_check = testing::Field(
      &clients::unique_drivers::v1_driver_profiles_retrieve_by_uniques::post::
          Request::consumer,
      testing::StrEq(kServiceName));

  EXPECT_CALL(unique_driver_client_mock,
              V1DriverProfilesRetrieveByUniques(consumer_check, testing::_))
      .WillOnce(testing::Return(Parse(formats::json::FromString(R"({
                  "profiles":[]
                })"),
                                      formats::parse::To<Response>())))
      .WillOnce(testing::Return(Parse(formats::json::FromString(R"({
                  "profiles":[
                    {
                      "unique_driver_id":"bcde",
                      "data":[
                        {
                          "park_id":"park-id",
                          "driver_profile_id":"driver-profile-id",
                          "park_driver_profile_id":"park-driver-profile-id"
                        }
                      ]
                    }
                  ]
                })"),
                                      formats::parse::To<Response>())));

  {
    eventus::mappers::Event event({});
    event.Set("unique_driver_id", "abcd");
    mapper->Map(event);

    ASSERT_TRUE(event.HasKey(kDestinationKey));
    ASSERT_EQ(event.Get<std::vector<formats::json::Value>>(kDestinationKey),
              std::vector<formats::json::Value>{});
  }

  {
    eventus::mappers::Event event({});
    event.Set("unique_driver_id", "bcde");
    mapper->Map(event);

    ASSERT_TRUE(event.HasKey(kDestinationKey));
    ASSERT_EQ(event.Get<formats::json::Value>(kDestinationKey),
              formats::json::FromString(R"(
                    [{
                      "park_id":"park-id",
                      "driver_profile_id":"driver-profile-id",
                      "park_driver_profile_id":"park-driver-profile-id"
                    }])"));
  }
}
