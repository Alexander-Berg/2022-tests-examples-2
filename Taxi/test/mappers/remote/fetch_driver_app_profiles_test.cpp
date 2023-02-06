#include <userver/utest/utest.hpp>

#include <test/common.hpp>
#include <test/mocks/driver_profiles_client_mock.hpp>

#include <eventus/mappers/remote/fetch_driver_app_profiles_mapper.hpp>

namespace {

using Request =
    clients::driver_profiles::v1_driver_app_profiles_retrieve::post::Request;
using Response = clients::driver_profiles::v1_driver_app_profiles_retrieve::
    post::Response200;

constexpr const auto kDestinationKey = "driver_app_profile";
constexpr const auto kServiceName = "service-name";

}  // namespace

UTEST(MappersSuite, FetchDriverAppProfilesTest) {
  using test::mocks::DriverProfilesClient;
  DriverProfilesClient driver_profiles_client_mock;

  using StringV = std::vector<std::string>;
  using namespace test::common;
  OperationArgsV args{
      {"park_driver_profile_id_src_key", "park_driver_profile_id"},
      {"driver_app_profile_dst_key", kDestinationKey},
      {"data_projections",
       StringV{
           "data.taximeter_platform",
           "data.taximeter_version",
           "data.taximeter_version_type",
       }},
  };
  eventus::mappers::MapperTypePtr mapper =
      std::make_shared<eventus::mappers::remote::FetchDriverAppProfilesMapper>(
          args, driver_profiles_client_mock, kServiceName);

  const auto consumer_check = testing::Field(
      &clients::driver_profiles::v1_driver_app_profiles_retrieve::post::
          Request::consumer,
      testing::StrEq(kServiceName));

  EXPECT_CALL(driver_profiles_client_mock,
              V1DriverAppProfilesRetrieve(consumer_check, testing::_))
      .WillOnce(testing::Return(Parse(formats::json::FromString(R"({
            "profiles": [] 
        })"),
                                      formats::parse::To<Response>())))
      .WillOnce(testing::Return(Parse(formats::json::FromString(R"({
            "profiles": [
                {
                    "data": {
                        "taximeter_version": "234"
                    },
                    "park_driver_profile_id": "PROFILE_ID-2"
                },
                {
                    "data": {
                        "taximeter_platform": "",
                        "taximeter_version": "123",
                        "taximeter_version_type": "ios"
                    },
                    "park_driver_profile_id": "PROFILE_ID"
                }
            ] 
        })"),
                                      formats::parse::To<Response>())));
  {
    eventus::mappers::Event event({});
    event.Set("park_driver_profile_id", "PROFILE_ID");

    mapper->Map(event);

    ASSERT_FALSE(event.HasKey(kDestinationKey));
  }
  {
    eventus::mappers::Event event({});
    event.Set("park_driver_profile_id", "PROFILE_ID");

    mapper->Map(event);

    ASSERT_TRUE(event.HasKey(kDestinationKey));
    ASSERT_EQ(event.Get<formats::json::Value>(kDestinationKey),
              formats::json::FromString(R"({
                        "taximeter_platform": "",
                        "taximeter_version": "123",
                        "taximeter_version_type": "ios"
                    })"));
  }
}
