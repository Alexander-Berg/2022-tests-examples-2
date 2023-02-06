#include <simple-zookeeper/redis_zookeeper_tester.hpp>
#include <userver/hostinfo/blocking/get_hostname.hpp>
#include <userver/storages/redis/mock_client_base.hpp>
#include <userver/utils/datetime.hpp>

#include <gtest/gtest.h>

namespace {

const std::string kHostname{hostinfo::blocking::GetRealHostName()};
std::chrono::milliseconds kUpdateInterval{100500};
const std::string kMachineListKey{"machine_list_hash"};
std::chrono::seconds kMachineTimeout{100500};

class RedisMock : public storages::redis::MockClientBase {
 public:
  storages::redis::RequestHset Hset(
      std::string /*key*/, std::string field, std::string value,
      const storages::redis::CommandControl& /*command_control*/) override {
    hash_[field] = value;

    auto reply = storages::redis::HsetReply::kCreated;
    return storages::redis::CreateMockRequest<storages::redis::RequestHset>(
        std::move(reply));
  }

  storages::redis::RequestHget Hget(
      std::string /*key*/, std::string field,
      const storages::redis::CommandControl& /*command_control*/) override {
    std::optional<std::string> ret;
    auto it = hash_.find(field);
    if (it != hash_.end()) {
      ret = it->second;
    }

    return storages::redis::CreateMockRequest<storages::redis::RequestHget>(
        std::move(ret));
  }

  storages::redis::RequestHdel Hdel(
      std::string /*key*/, std::string field,
      const storages::redis::CommandControl& /*command_control*/) override {
    auto it = hash_.find(field);
    if (it != hash_.end()) {
      hash_.erase(it);
    }

    size_t reply{1};
    return storages::redis::CreateMockRequest<storages::redis::RequestHdel>(
        std::move(reply));
  }

  storages::redis::RequestHkeys Hkeys(
      std::string /*key*/,
      const storages::redis::CommandControl& /*command_control*/) override {
    std::vector<std::string> keys;
    for (const auto& item : hash_) {
      keys.push_back(item.first);
    }

    return storages::redis::CreateMockRequest<storages::redis::RequestHkeys>(
        std::move(keys));
  }

  std::size_t NumKeys() const { return hash_.size(); }

 private:
  std::unordered_map<std::string, std::string> hash_;
};

}  // namespace

UTEST(redis_list, TestAddOneMachine) {
  std::shared_ptr<RedisMock> redis_client = std::make_shared<RedisMock>();

  simple_zookeeper::RedisZookeeper::RedisConfig redis_config{{},
                                                             kMachineTimeout};
  simple_zookeeper::RedisZookeeper keeper(redis_client, kUpdateInterval,
                                          kMachineListKey, redis_config);

  simple_zookeeper::RedisZookeeperTester tester(keeper);
  tester.UpdateMachinesList();

  const auto& info = keeper.GetHostInfo();
  ASSERT_TRUE(info);
  ASSERT_EQ(info->hosts_count, 1);
  ASSERT_EQ(info->host_index, 0);
}

UTEST(redis_list, TestAddTwoMachines) {
  std::shared_ptr<RedisMock> redis_client = std::make_shared<RedisMock>();
  auto now = utils::datetime::Now();
  (void)redis_client->Hset(kMachineListKey, "aaaaa",
                           ::utils::datetime::Timestring(now),
                           storages::redis::CommandControl{});

  simple_zookeeper::RedisZookeeper::RedisConfig redis_config{{},
                                                             kMachineTimeout};
  simple_zookeeper::RedisZookeeper keeper(redis_client, kUpdateInterval,
                                          kMachineListKey, redis_config);

  simple_zookeeper::RedisZookeeperTester tester(keeper);
  tester.UpdateMachinesList();

  const auto& info = keeper.GetHostInfo();
  const auto& hosts = keeper.GetOnlineHosts();
  ASSERT_TRUE(info);
  ASSERT_EQ(info->hosts_count, 2);
  auto host_idx = std::distance(
      hosts.begin(), std::find(hosts.begin(), hosts.end(), kHostname));
  ASSERT_EQ(info->host_index, host_idx);
}

UTEST(redis_list, TestAddBetweenMachines) {
  std::shared_ptr<RedisMock> redis_client = std::make_shared<RedisMock>();
  auto now = utils::datetime::Now();
  (void)redis_client->Hset(kMachineListKey, "aaaaa",
                           ::utils::datetime::Timestring(now),
                           storages::redis::CommandControl{});
  (void)redis_client->Hset(kMachineListKey, "zzzzz",
                           ::utils::datetime::Timestring(now),
                           storages::redis::CommandControl{});

  simple_zookeeper::RedisZookeeper::RedisConfig redis_config{{},
                                                             kMachineTimeout};
  simple_zookeeper::RedisZookeeper keeper(redis_client, kUpdateInterval,
                                          kMachineListKey, redis_config);

  simple_zookeeper::RedisZookeeperTester tester(keeper);
  tester.UpdateMachinesList();

  const auto& info = keeper.GetHostInfo();
  const auto& hosts = keeper.GetOnlineHosts();
  ASSERT_TRUE(info);
  ASSERT_EQ(info->hosts_count, 3);
  auto host_idx = std::distance(
      hosts.begin(), std::find(hosts.begin(), hosts.end(), kHostname));
  ASSERT_EQ(info->host_index, host_idx);
}

UTEST(redis_list, TestAddOutdatedMachine) {
  std::shared_ptr<RedisMock> redis_client = std::make_shared<RedisMock>();
  auto now = utils::datetime::Now();
  (void)redis_client->Hset(kMachineListKey, "aaaaa",
                           ::utils::datetime::Timestring(
                               now - kMachineTimeout - std::chrono::seconds(1)),
                           storages::redis::CommandControl{});

  simple_zookeeper::RedisZookeeper::RedisConfig redis_config{{},
                                                             kMachineTimeout};
  simple_zookeeper::RedisZookeeper keeper(redis_client, kUpdateInterval,
                                          kMachineListKey, redis_config);

  simple_zookeeper::RedisZookeeperTester tester(keeper);
  tester.UpdateMachinesList();

  const auto& info = keeper.GetHostInfo();
  ASSERT_TRUE(info);
  ASSERT_EQ(info->hosts_count, 1);
  ASSERT_EQ(info->host_index, 0);
}

UTEST(redis_list, CheckDeleteMachineFromList) {
  std::shared_ptr<RedisMock> redis_client = std::make_shared<RedisMock>();

  {
    simple_zookeeper::RedisZookeeper::RedisConfig redis_config{{},
                                                               kMachineTimeout};
    simple_zookeeper::RedisZookeeper keeper(redis_client, kUpdateInterval,
                                            kMachineListKey, redis_config);

    simple_zookeeper::RedisZookeeperTester tester(keeper);
    tester.UpdateMachinesList();

    ASSERT_EQ(redis_client->NumKeys(), 1);
  }

  ASSERT_EQ(redis_client->NumKeys(), 0);
}
