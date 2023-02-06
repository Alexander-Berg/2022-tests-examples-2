#include <gmock/gmock.h>
#include <chrono>
#include <clients/latvia-eds/client.hpp>
#include <clients/latvia-eds/client_gmock.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include "models/eds_auth_secret.hpp"

#include "cache/eds_token_cache.hpp"

using ::testing::_;
using ::testing::Return;
using ::testing::Throw;

namespace {
constexpr auto kBearer{"Bearer "};
}

TEST(TokenCacheManagerTest, OldToken) {
  // Prepare for the test
  const auto now = utils::datetime::MockNow();
  utils::datetime::MockNowSet(now);

  formats::json::Value sec(formats::json::FromString(
      R"=({"eds-secrets": {"101": "TEST_CLIENT_SECRET"}})="));
  latvia_rides_reports::models::secdist::EdsAuthSecret edsAuthSecret(sec);

  clients::latvia_eds::AuthResult token1{"token1", "bearer", 120};

  clients::latvia_eds::ClientGMock client;
  EXPECT_CALL(client, Auth(_, _))
      .WillOnce(Return(
          clients::latvia_eds::api_taxi_auth::post::Response200(token1)));

  cache::TokenCacheComponent::Manager manager(edsAuthSecret, client,
                                              std::chrono::seconds(1));

  std::string clientId = "101";

  std::string oldToken = manager.GetAuthToken(clientId);
  EXPECT_EQ(kBearer + token1.access_token, oldToken) << "Pretesting error";

  // Run test
  std::string newToken = manager.GetAuthToken(clientId);
  EXPECT_EQ(oldToken, newToken);

  utils::datetime::MockNowUnset();
}

TEST(TokenCacheManagerTest, NewToken) {
  // Prepare for the test
  const auto now = utils::datetime::MockNow();
  utils::datetime::MockNowSet(now);

  formats::json::Value sec(formats::json::FromString(
      R"=({"eds-secrets": {"201": "TEST_CLIENT_SECRET"}})="));
  latvia_rides_reports::models::secdist::EdsAuthSecret edsAuthSecret(sec);

  clients::latvia_eds::AuthResult token1{"token1", "bearer", 120};
  clients::latvia_eds::AuthResult token2{"token2", "bearer", 120};

  clients::latvia_eds::ClientGMock client;
  EXPECT_CALL(client, Auth(_, _))
      .WillOnce(
          Return(clients::latvia_eds::api_taxi_auth::post::Response200(token1)))
      .WillOnce(Return(
          clients::latvia_eds::api_taxi_auth::post::Response200(token2)));

  cache::TokenCacheComponent::Manager manager(edsAuthSecret, client,
                                              std::chrono::seconds(1));

  std::string oldClientId = "201";
  std::string oldToken = manager.GetAuthToken(oldClientId);
  EXPECT_EQ(kBearer + token1.access_token, oldToken) << "Pretesting error";

  utils::datetime::MockSleep(std::chrono::seconds(300));

  // Run test
  std::string newClientId = "201";
  std::string newToken = manager.GetAuthToken(newClientId);
  EXPECT_EQ(kBearer + token2.access_token, newToken);

  utils::datetime::MockNowUnset();
}

TEST(TokenCacheManagerTest, NoToken) {
  // Prepare for the test
  const auto now = utils::datetime::MockNow();
  utils::datetime::MockNowSet(now);

  formats::json::Value sec(formats::json::FromString(
      R"=({"eds-secrets": {"301": "TEST_CLIENT_SECRET"}})="));
  latvia_rides_reports::models::secdist::EdsAuthSecret edsAuthSecret(sec);

  clients::latvia_eds::ClientGMock client;
  EXPECT_CALL(client, Auth(_, _))
      .WillOnce(Throw(clients::latvia_eds::api_taxi_auth::post::Response400()));

  cache::TokenCacheComponent::Manager manager(edsAuthSecret, client,
                                              std::chrono::seconds(1));

  // Run test
  std::string clientId = "301";
  auto token = manager.GetAuthToken(clientId);
  EXPECT_EQ(std::string(""), token);

  utils::datetime::MockNowUnset();
}

TEST(TokenCacheManagerTest, NotTokenCollisionById) {
  // Prepare for the test
  const auto now = utils::datetime::MockNow();
  utils::datetime::MockNowSet(now);

  formats::json::Value sec(formats::json::FromString(
      R"=({"eds-secrets": {"401": "TEST_CLIENT_SECRET", "402": "TEST_CLIENT_SECRET"}})="));
  latvia_rides_reports::models::secdist::EdsAuthSecret edsAuthSecret(sec);

  clients::latvia_eds::AuthResult token1{"token1", "bearer", 120};
  clients::latvia_eds::AuthResult token2{"token2", "bearer", 120};

  clients::latvia_eds::ClientGMock client;
  EXPECT_CALL(client, Auth(_, _))
      .WillOnce(
          Return(clients::latvia_eds::api_taxi_auth::post::Response200(token1)))
      .WillOnce(Return(
          clients::latvia_eds::api_taxi_auth::post::Response200(token2)));

  cache::TokenCacheComponent::Manager manager(edsAuthSecret, client,
                                              std::chrono::seconds(1));

  std::string oldClientId = "401";
  std::string oldToken = manager.GetAuthToken(oldClientId);
  EXPECT_EQ(kBearer + token1.access_token, oldToken) << "Pretesting error";

  // Run test
  std::string newClientId = "402";
  std::string newToken = manager.GetAuthToken(newClientId);
  EXPECT_EQ(kBearer + token2.access_token, newToken);

  utils::datetime::MockNowUnset();
}

TEST(TokenCacheManagerTest, DeleteAuthToken) {
  // Prepare for the test
  const auto now = utils::datetime::MockNow();
  utils::datetime::MockNowSet(now);

  formats::json::Value sec(formats::json::FromString(
      R"=({"eds-secrets": {"501": "TEST_CLIENT_SECRET"}})="));
  latvia_rides_reports::models::secdist::EdsAuthSecret edsAuthSecret(sec);

  clients::latvia_eds::AuthResult token1{"token1", "bearer", 120};

  clients::latvia_eds::ClientGMock client;
  EXPECT_CALL(client, Auth(_, _))
      .WillOnce(
          Return(clients::latvia_eds::api_taxi_auth::post::Response200(token1)))
      .WillOnce(Throw(clients::latvia_eds::api_taxi_auth::post::Response400()));

  cache::TokenCacheComponent::Manager manager(edsAuthSecret, client,
                                              std::chrono::seconds(1));

  std::string clientId = "501";
  std::string oldToken = manager.GetAuthToken(clientId);
  EXPECT_EQ(kBearer + token1.access_token, oldToken) << "Pretesting error";

  // Run test
  manager.DeleteAuthToken(clientId);
  std::string newToken = manager.GetAuthToken(clientId);
  EXPECT_EQ(std::string(""), newToken);

  utils::datetime::MockNowUnset();
}
