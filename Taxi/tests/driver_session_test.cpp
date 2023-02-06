#include <userver/utest/utest.hpp>
#include <userver/utils/assert.hpp>

#include <atomic>
#include <chrono>

#include <testing/taxi_config.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <models/driver_session/driver_session.hpp>
#include <models/driver_session/driver_session_common.hpp>
#include <userver/storages/redis/mock_client_base.hpp>

namespace ds = driver_authorizer::models::driver_session;

namespace {

using driver_authorizer::models::driver_session::EatsCourierId;

const std::string kClientId = "uberdriver";
const std::string kClientIdTaximeter = "taximeter";
const std::string kClientIdVezet = "vezet";
const std::string kParkId = "park234";
const std::string kUuid = "park345";
const std::string kDriverAppProfileId = "driver_app_profile567";
const std::string kEatsCourierId = "eats_courier_id678";
const std::string kSession = "session456";
const size_t kTtlSeconds = 1800;

const std::string kDriverDataKey = "Driver:P" + kParkId + ":U" + kUuid;

std::string SessionDataKey(const std::string& session) {
  return "DriverSession:P" + kParkId + ":S" + session;
}

const std::string kSessionDataKey = SessionDataKey(kSession);

size_t GetScoreForNow() {
  return std::chrono::duration_cast<std::chrono::seconds>(
             utils::datetime::Now().time_since_epoch())
      .count();
}

template <typename MockClient>
class DriverSessionTest : public ds::DriverSession {
 public:
  DriverSessionTest() : DriverSessionTest(std::make_shared<MockClient>()) {}

  const MockClient& Client() const { return *client_; }
  MockClient& Client() { return *client_; }

 private:
  explicit DriverSessionTest(std::shared_ptr<MockClient> client)
      : ds::DriverSession(ds::DriverSessionBases(client)), client_(client) {}

  std::shared_ptr<MockClient> client_;
};

}  // namespace

UTEST(DriverSession, SessionNew) {
  class MockClient : public storages::redis::MockClientBase {
   public:
    ~MockClient() {
      EXPECT_EQ(hget_counter_, 1);
      EXPECT_EQ(hset_counter_, 1);
      EXPECT_EQ(hmset_counter_, 1);
      EXPECT_EQ(zadd_counter_, 1);
    }

    storages::redis::RequestHget Hget(
        std::string key, std::string field,
        const storages::redis::CommandControl&) override {
      ++hget_counter_;
      EXPECT_TRUE(key == kDriverDataKey);
      EXPECT_EQ(field, "Session");
      return storages::redis::CreateMockRequest<storages::redis::RequestHget>(
          session_);
    }

    storages::redis::RequestHset Hset(
        std::string key, std::string field, std::string value,
        const storages::redis::CommandControl&) override {
      ++hset_counter_;
      EXPECT_EQ(key, kDriverDataKey);
      EXPECT_EQ(field, "Session");
      EXPECT_EQ(value.size(), 32);
      session_ = value;
      return storages::redis::CreateMockRequest<storages::redis::RequestHset>(
          storages::redis::HsetReply::kCreated);
    }

    storages::redis::RequestHmset Hmset(
        std::string key,
        std::vector<std::pair<std::string, std::string>> field_values,
        const storages::redis::CommandControl&) override {
      ++hmset_counter_;
      EXPECT_EQ(key, SessionDataKey(*session_));
      std::vector<std::pair<std::string, std::string>> expected{
          {"driver_profile_id", kUuid},
          {"client_id", kClientId},
      };
      EXPECT_EQ(field_values, expected);
      return storages::redis::CreateMockRequest<
          storages::redis::RequestHmset>();
    }

    storages::redis::RequestZadd Zadd(
        std::string key, double score, std::string member,
        const storages::redis::CommandControl&) override {
      ++zadd_counter_;
      EXPECT_EQ(key, "DriverSessionsTtl{a}");

      const size_t expected_score = GetScoreForNow() + kTtlSeconds;
      EXPECT_EQ(score, expected_score);
      UASSERT(!!session_);
      EXPECT_EQ(member, SessionDataKey(*session_));
      return storages::redis::CreateMockRequest<storages::redis::RequestZadd>(
          1);
    }

    const std::optional<std::string>& Session() const { return session_; }

   private:
    std::optional<std::string> session_;
    std::atomic<size_t> hget_counter_{0};
    std::atomic<size_t> hset_counter_{0};
    std::atomic<size_t> hmset_counter_{0};
    std::atomic<size_t> zadd_counter_{0};
  };

  utils::datetime::MockNowSet(std::chrono::system_clock::now());

  DriverSessionTest<MockClient> driver_session;

  ds::DriverProfileKey driver_profile_key;
  driver_profile_key.uuid = kUuid;
  auto ttl = std::chrono::seconds(1800);

  auto session = driver_session.SessionNew(
      kClientId, kParkId, driver_profile_key, ttl, {}, {},
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>());
  EXPECT_FALSE(session.empty());
  UASSERT(!!driver_session.Client().Session());
  EXPECT_EQ(session, *driver_session.Client().Session());
}

UTEST(DriverSession, SessionNewWithEatsCourierId) {
  class MockClient : public storages::redis::MockClientBase {
   public:
    ~MockClient() {
      EXPECT_EQ(hget_counter_, 1);
      EXPECT_EQ(hset_counter_, 1);
      EXPECT_EQ(hmset_counter_, 1);
      EXPECT_EQ(zadd_counter_, 1);
    }

    storages::redis::RequestHget Hget(
        std::string key, std::string field,
        const storages::redis::CommandControl&) override {
      ++hget_counter_;
      EXPECT_TRUE(key == kDriverDataKey);
      EXPECT_EQ(field, "Session");
      return storages::redis::CreateMockRequest<storages::redis::RequestHget>(
          session_);
    }

    storages::redis::RequestHset Hset(
        std::string key, std::string field, std::string value,
        const storages::redis::CommandControl&) override {
      ++hset_counter_;
      EXPECT_EQ(key, kDriverDataKey);
      EXPECT_EQ(field, "Session");
      EXPECT_EQ(value.size(), 32);
      session_ = value;
      return storages::redis::CreateMockRequest<storages::redis::RequestHset>(
          storages::redis::HsetReply::kCreated);
    }

    storages::redis::RequestHmset Hmset(
        std::string key,
        std::vector<std::pair<std::string, std::string>> field_values,
        const storages::redis::CommandControl&) override {
      ++hmset_counter_;
      EXPECT_EQ(key, SessionDataKey(*session_));
      std::vector<std::pair<std::string, std::string>> expected{
          {"driver_profile_id", kUuid},
          {"client_id", kClientId},
          {"eats_courier_id", kEatsCourierId},
      };
      EXPECT_EQ(field_values, expected);
      return storages::redis::CreateMockRequest<
          storages::redis::RequestHmset>();
    }

    storages::redis::RequestZadd Zadd(
        std::string key, double score, std::string member,
        const storages::redis::CommandControl&) override {
      ++zadd_counter_;
      EXPECT_EQ(key, "DriverSessionsTtl{a}");

      const size_t expected_score = GetScoreForNow() + kTtlSeconds;
      EXPECT_EQ(score, expected_score);
      UASSERT(!!session_);
      EXPECT_EQ(member, SessionDataKey(*session_));
      return storages::redis::CreateMockRequest<storages::redis::RequestZadd>(
          1);
    }

    const std::optional<std::string>& Session() const { return session_; }

   private:
    std::optional<std::string> session_;
    std::atomic<size_t> hget_counter_{0};
    std::atomic<size_t> hset_counter_{0};
    std::atomic<size_t> hmset_counter_{0};
    std::atomic<size_t> zadd_counter_{0};
  };

  utils::datetime::MockNowSet(std::chrono::system_clock::now());

  DriverSessionTest<MockClient> driver_session;

  ds::DriverProfileKey driver_profile_key;
  driver_profile_key.uuid = kUuid;
  auto ttl = std::chrono::seconds(1800);

  auto session = driver_session.SessionNew(
      kClientId, kParkId, driver_profile_key, ttl,
      EatsCourierId{kEatsCourierId}, {},
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>());
  EXPECT_FALSE(session.empty());
  UASSERT(!!driver_session.Client().Session());
  EXPECT_EQ(session, *driver_session.Client().Session());
}

UTEST(DriverSession, SessionGetWithTtl) {
  class MockClient : public storages::redis::MockClientBase {
   public:
    ~MockClient() {
      EXPECT_EQ(hget_counter_, 1);
      EXPECT_EQ(hgetall_counter_, 1);
      EXPECT_EQ(zscore_counter_, 1);
    }

    storages::redis::RequestHget Hget(
        std::string key, std::string field,
        const storages::redis::CommandControl&) override {
      ++hget_counter_;
      EXPECT_TRUE(key == kDriverDataKey);
      EXPECT_EQ(field, "Session");
      return storages::redis::CreateMockRequest<storages::redis::RequestHget>(
          kSession);
    }

    storages::redis::RequestHgetall Hgetall(
        std::string key, const storages::redis::CommandControl&) override {
      ++hgetall_counter_;
      EXPECT_EQ(key, kSessionDataKey);
      return storages::redis::CreateMockRequest<
          storages::redis::RequestHgetall>({
          {"client_id", kClientId},
          {"driver_profile_id", kUuid},
      });
    }

    storages::redis::RequestZscore Zscore(
        std::string key, std::string member,
        const storages::redis::CommandControl&) override {
      ++zscore_counter_;
      EXPECT_EQ(key, "DriverSessionsTtl{a}");
      EXPECT_EQ(member, SessionDataKey(kSession));
      return storages::redis::CreateMockRequest<storages::redis::RequestZscore>(
          std::optional(GetScoreForNow() + kTtlSeconds));
    }

   private:
    std::atomic<size_t> hget_counter_{0};
    std::atomic<size_t> hgetall_counter_{0};
    std::atomic<size_t> zscore_counter_{0};
  };

  utils::datetime::MockNowSet(std::chrono::system_clock::now());

  DriverSessionTest<MockClient> driver_session;

  ds::DriverProfileKey driver_profile_key;
  driver_profile_key.uuid = kUuid;

  auto session_with_ttl = driver_session.SessionGetWithTtl(
      kParkId, driver_profile_key,
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>());
  EXPECT_EQ(session_with_ttl.GetSession(), kSession);
  EXPECT_TRUE(session_with_ttl.IsSessionActive());
  EXPECT_EQ(session_with_ttl.GetTtlReply().GetExpireSeconds(), kTtlSeconds);
}

UTEST(DriverSession, SessionGetWithTtlEmpty) {
  class MockClient : public storages::redis::MockClientBase {
   public:
    ~MockClient() { EXPECT_EQ(hget_counter_, 1); }

    storages::redis::RequestHget Hget(
        std::string key, std::string field,
        const storages::redis::CommandControl&) override {
      ++hget_counter_;
      EXPECT_TRUE(key == kDriverDataKey);
      EXPECT_EQ(field, "Session");
      return storages::redis::CreateMockRequest<storages::redis::RequestHget>(
          std::nullopt);
    }

   private:
    std::atomic<size_t> hget_counter_{0};
  };

  DriverSessionTest<MockClient> driver_session;

  ds::DriverProfileKey driver_profile_key;
  driver_profile_key.uuid = kUuid;

  auto session_with_ttl = driver_session.SessionGetWithTtl(
      kParkId, driver_profile_key,
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>());
  EXPECT_TRUE(session_with_ttl.GetSession().empty());
}

UTEST(DriverSession, SessionGetWithTtlTimeout) {
  class MockClient : public storages::redis::MockClientBase {
   public:
    ~MockClient() { EXPECT_EQ(hget_counter_, 1); }

    storages::redis::RequestHget Hget(
        std::string key, std::string field,
        const storages::redis::CommandControl&) override {
      ++hget_counter_;
      EXPECT_TRUE(key == kDriverDataKey);
      EXPECT_EQ(field, "Session");
      return storages::redis::CreateMockRequestTimeout<
          storages::redis::RequestHget>();
    }

   private:
    std::atomic<size_t> hget_counter_{0};
  };

  DriverSessionTest<MockClient> driver_session;

  ds::DriverProfileKey driver_profile_key;
  driver_profile_key.uuid = kUuid;

  EXPECT_THROW(
      driver_session.SessionGetWithTtl(
          kParkId, driver_profile_key,
          dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>()),
      ::redis::RequestFailedException);
}

UTEST(DriverSession, DriverCheck) {
  class MockClient : public storages::redis::MockClientBase {
   public:
    ~MockClient() {
      EXPECT_EQ(hgetall_counter_, 1);
      EXPECT_EQ(zscore_counter_, 1);
    }

    storages::redis::RequestHgetall Hgetall(
        std::string key, const storages::redis::CommandControl&) override {
      ++hgetall_counter_;
      EXPECT_EQ(key, kSessionDataKey);
      return storages::redis::CreateMockRequest<
          storages::redis::RequestHgetall>({
          {"client_id", kClientId},
          {"driver_profile_id", kUuid},
          {"app_profile_id", kDriverAppProfileId},
      });
    }

    storages::redis::RequestZscore Zscore(
        std::string key, std::string member,
        const storages::redis::CommandControl&) override {
      ++zscore_counter_;
      EXPECT_EQ(key, "DriverSessionsTtl{a}");
      EXPECT_EQ(member, kSessionDataKey);
      return storages::redis::CreateMockRequest<storages::redis::RequestZscore>(
          GetScoreForNow() + kTtlSeconds);
    }

   private:
    std::atomic<size_t> hgetall_counter_{0};
    std::atomic<size_t> zscore_counter_{0};
  };

  DriverSessionTest<MockClient> driver_session;

  auto driver_check_result = driver_session.DriverCheck(
      kParkId, kSession,
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>());
  EXPECT_EQ(driver_check_result.driver_profile_key.uuid, kUuid);
  EXPECT_EQ(driver_check_result.driver_profile_key.driver_app_profile_id,
            kDriverAppProfileId);
  EXPECT_EQ(driver_check_result.eats_courier_id, std::nullopt);
}

UTEST(DriverSession, DriverCheckWithEatsCourierId) {
  class MockClient : public storages::redis::MockClientBase {
   public:
    ~MockClient() {
      EXPECT_EQ(hgetall_counter_, 1);
      EXPECT_EQ(zscore_counter_, 1);
    }

    storages::redis::RequestHgetall Hgetall(
        std::string key, const storages::redis::CommandControl&) override {
      ++hgetall_counter_;
      EXPECT_EQ(key, kSessionDataKey);
      return storages::redis::CreateMockRequest<
          storages::redis::RequestHgetall>({
          {"client_id", kClientId},
          {"driver_profile_id", kUuid},
          {"app_profile_id", kDriverAppProfileId},
          {"eats_courier_id", kEatsCourierId},
      });
    }

    storages::redis::RequestZscore Zscore(
        std::string key, std::string member,
        const storages::redis::CommandControl&) override {
      ++zscore_counter_;
      EXPECT_EQ(key, "DriverSessionsTtl{a}");
      EXPECT_EQ(member, kSessionDataKey);
      return storages::redis::CreateMockRequest<storages::redis::RequestZscore>(
          GetScoreForNow() + kTtlSeconds);
    }

   private:
    std::atomic<size_t> hgetall_counter_{0};
    std::atomic<size_t> zscore_counter_{0};
  };

  DriverSessionTest<MockClient> driver_session;

  auto driver_check_result = driver_session.DriverCheck(
      kParkId, kSession,
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>());
  EXPECT_EQ(driver_check_result.driver_profile_key.uuid, kUuid);
  EXPECT_EQ(driver_check_result.driver_profile_key.driver_app_profile_id,
            kDriverAppProfileId);
  EXPECT_EQ(driver_check_result.eats_courier_id.value().GetUnderlying(),
            kEatsCourierId);
}

UTEST(DriverSession, DriverCheckNotFound) {
  class MockClient : public storages::redis::MockClientBase {
   public:
    ~MockClient() {
      EXPECT_EQ(hgetall_counter_, 1);
      EXPECT_EQ(zscore_counter_, 1);
    }

    storages::redis::RequestHgetall Hgetall(
        std::string key, const storages::redis::CommandControl&) override {
      ++hgetall_counter_;
      EXPECT_EQ(key, kSessionDataKey);
      return storages::redis::CreateMockRequest<
          storages::redis::RequestHgetall>({});
    }

    storages::redis::RequestZscore Zscore(
        std::string key, std::string member,
        const storages::redis::CommandControl&) override {
      ++zscore_counter_;
      EXPECT_EQ(key, "DriverSessionsTtl{a}");
      EXPECT_EQ(member, kSessionDataKey);
      return storages::redis::CreateMockRequest<storages::redis::RequestZscore>(
          std::nullopt);
    }

   private:
    std::atomic<size_t> hgetall_counter_{0};
    std::atomic<size_t> zscore_counter_{0};
  };

  DriverSessionTest<MockClient> driver_session;

  auto driver_check_result = driver_session.DriverCheck(
      kParkId, kSession,
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>());
  EXPECT_TRUE(driver_check_result.driver_profile_key.uuid.empty());
  EXPECT_TRUE(!driver_check_result.driver_profile_key);
}
