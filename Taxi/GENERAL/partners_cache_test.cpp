#include <chrono>
#include <clients/eats-vendor/client_gmock.hpp>
#include <userver/storages/redis/mock_client_google.hpp>
#include <userver/storages/redis/mock_request.hpp>
#include <userver/utest/utest.hpp>

#include "partners_cache.hpp"

namespace helpers::partners_cache {

TEST(GetPartnerPlacesFromCache, PlacesInCache) {
  storages::redis::GMockClient redis_mock;
  clients::eats_vendor::ClientGMock vendor_mock;
  std::chrono::seconds ttl{1000};

  std::unordered_set<std::string> cache;
  cache.insert("1");

  EXPECT_CALL(redis_mock, Smembers)
      .WillOnce([cache](std::string, const storages::redis::CommandControl&) {
        return storages::redis::CreateMockRequest<
            storages::redis::RequestSmembers>(cache);
      });

  const auto places =
      GetPartnerPlacesFromCache(redis_mock, vendor_mock, ttl, 111);
  ASSERT_EQ(places, cache);
}

TEST(GetPartnerPlacesFromCache, PlacesNotInCache) {
  storages::redis::GMockClient redis_mock;
  clients::eats_vendor::ClientGMock vendor_mock;
  std::chrono::seconds ttl{1000};
  using VendorResponse =
      clients::eats_vendor::api_v1_server_users_partnerid::get::Response;

  VendorResponse server_result;
  server_result.issuccess = true;
  server_result.payload.restaurants = {1, 2};
  server_result.payload.roles = {
      {3, "operator", clients::eats_vendor::RoleRole::kRoleOperator}};
  EXPECT_CALL(vendor_mock, ApiV1ServerUsersPartneridGet)
      .WillOnce(::testing::Return(server_result));

  EXPECT_CALL(redis_mock, Smembers)
      .WillOnce([](std::string, const storages::redis::CommandControl&) {
        return storages::redis::CreateMockRequest<
            storages::redis::RequestSmembers>({});
      });
  EXPECT_CALL(redis_mock,
              Sadd("partner:places:111", testing::A<std::vector<std::string>>(),
                   testing::_))
      .WillOnce([](std::string, std::vector<std::string>,
                   const storages::redis::CommandControl&) {
        return storages::redis::CreateMockRequest<storages::redis::RequestSadd>(
            0);
      });
  EXPECT_CALL(redis_mock,
              Sadd("partner:roles:111", testing::A<std::vector<std::string>>(),
                   testing::_))
      .WillOnce([](std::string, std::vector<std::string>,
                   const storages::redis::CommandControl&) {
        return storages::redis::CreateMockRequest<storages::redis::RequestSadd>(
            0);
      });
  EXPECT_CALL(redis_mock, Expire)
      .WillRepeatedly([](std::string, std::chrono::seconds,
                         const storages::redis::CommandControl&) {
        return storages::redis::CreateMockRequest<
            storages::redis::RequestExpire>(
            storages::redis::ExpireReply::kKeyDoesNotExist);
      });

  const auto res = GetPartnerPlacesFromCache(redis_mock, vendor_mock, ttl, 111);
  std::unordered_set<std::string> expected_result;
  expected_result.insert({"1", "2"});
  ASSERT_EQ(res, expected_result);
}

TEST(GetPartnerRolesFromCache, RolesInCache) {
  storages::redis::GMockClient redis_mock;
  clients::eats_vendor::ClientGMock vendor_mock;
  std::chrono::seconds ttl{1000};

  std::unordered_set<std::string> cache;
  cache.insert("ROLE_OPERATOR");

  EXPECT_CALL(redis_mock, Smembers)
      .WillOnce([cache](std::string, const storages::redis::CommandControl&) {
        return storages::redis::CreateMockRequest<
            storages::redis::RequestSmembers>(cache);
      });

  const auto roles =
      GetPartnerRolesFromCache(redis_mock, vendor_mock, ttl, 111);
  ASSERT_EQ(roles, cache);
}

TEST(GetPartnerRolesFromCache, RolesNotInCache) {
  storages::redis::GMockClient redis_mock;
  clients::eats_vendor::ClientGMock vendor_mock;
  std::chrono::seconds ttl{1000};
  using VendorResponse =
      clients::eats_vendor::api_v1_server_users_partnerid::get::Response;

  VendorResponse server_result;
  server_result.issuccess = true;
  server_result.payload.restaurants = {1, 2};
  server_result.payload.roles = {
      {3, "operator", clients::eats_vendor::RoleRole::kRoleOperator},
      {4, "manager", clients::eats_vendor::RoleRole::kRoleManager}};
  EXPECT_CALL(vendor_mock, ApiV1ServerUsersPartneridGet)
      .WillOnce(::testing::Return(server_result));

  EXPECT_CALL(redis_mock, Smembers)
      .WillOnce([](std::string, const storages::redis::CommandControl&) {
        return storages::redis::CreateMockRequest<
            storages::redis::RequestSmembers>({});
      });
  EXPECT_CALL(redis_mock,
              Sadd("partner:places:111", testing::A<std::vector<std::string>>(),
                   testing::_))
      .WillOnce([](std::string, std::vector<std::string>,
                   const storages::redis::CommandControl&) {
        return storages::redis::CreateMockRequest<storages::redis::RequestSadd>(
            0);
      });
  EXPECT_CALL(redis_mock,
              Sadd("partner:roles:111", testing::A<std::vector<std::string>>(),
                   testing::_))
      .WillOnce([](std::string, std::vector<std::string>,
                   const storages::redis::CommandControl&) {
        return storages::redis::CreateMockRequest<storages::redis::RequestSadd>(
            0);
      });
  EXPECT_CALL(redis_mock, Expire)
      .WillRepeatedly([](std::string, std::chrono::seconds,
                         const storages::redis::CommandControl&) {
        return storages::redis::CreateMockRequest<
            storages::redis::RequestExpire>(
            storages::redis::ExpireReply::kKeyDoesNotExist);
      });

  const auto res = GetPartnerRolesFromCache(redis_mock, vendor_mock, ttl, 111);
  std::unordered_set<std::string> expected_result;
  expected_result.insert({"ROLE_MANAGER", "ROLE_OPERATOR"});
  ASSERT_EQ(res, expected_result);
}

}  // namespace helpers::partners_cache
