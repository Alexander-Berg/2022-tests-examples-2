#include "utils/redis/bulk_fetch.hpp"

#include <atomic>

#include <userver/storages/redis/mock_client_base.hpp>
#include <userver/utils/assert.hpp>

namespace {

class MockClient : public storages::redis::MockClientBase {
 public:
  explicit MockClient(size_t shards_count) : shards_count_(shards_count) {}

  size_t ShardsCount() const override { return shards_count_; }

  size_t ShardByKey(const std::string& key) const override {
    return key.size() % shards_count_;
  }

  storages::redis::ScanRequest<storages::redis::ScanTag::kScan> Scan(
      size_t shard, storages::redis::ScanOptions options,
      const storages::redis::CommandControl&) override {
    auto pattern = options.ExtractMatch();
    UASSERT(!!pattern);
    EXPECT_EQ(pattern->Get(), "*");
    static const std::string kKeyPrefix = "key_key_...";
    ++scan_counter_;
    std::vector<std::string> keys;
    for (size_t i = 0; i < shard + 1; ++i) {
      keys.push_back(kKeyPrefix.substr(0, (shard + shards_count_ - 1)) +
                     std::to_string(i + 1));
    }
    return storages::redis::CreateMockRequestScan<
        storages::redis::ScanTag::kScan>(keys);
  }

  storages::redis::RequestMget Mget(
      std::vector<std::string> keys,
      const storages::redis::CommandControl&) override {
    ++mget_counter_;
    static const std::string kValuePrefix = "val_val_...";
    std::vector<std::optional<std::string>> result;
    for (const auto& key : keys) {
      UASSERT(!key.empty());
      result.push_back(kValuePrefix.substr(0, key.size() - 1) + key.back());
    }
    return storages::redis::CreateMockRequest<storages::redis::RequestMget>(
        std::move(result));
  }

  size_t ScanCount() const { return scan_counter_; }

  size_t MgetCount() const { return mget_counter_; }

 private:
  const size_t shards_count_;
  std::atomic<size_t> scan_counter_{0};
  std::atomic<size_t> mget_counter_{0};
};

const int kShards = 3;
const std::vector<std::vector<std::string>> kKeysByShard = {
    {"ke1"}, {"key1", "key2"}, {"key_1", "key_2", "key_3"}};

}  // namespace

UTEST(BulkFetch, FetchKeysByShard) {
  auto client = std::make_shared<MockClient>(kShards);

  auto keys = utils::redis::FetchKeysByShard("*", *client);
  EXPECT_EQ(keys, kKeysByShard);
  EXPECT_EQ(client->ScanCount(), kShards);
  EXPECT_EQ(client->MgetCount(), 0);
}

UTEST(BulkFetch, FetchValuesByShard) {
  auto client = std::make_shared<MockClient>(kShards);

  auto values = utils::redis::FetchValuesByShard(kKeysByShard, *client);
  const std::vector<std::vector<std::optional<std::string>>> expected = {
      {std::string{"va1"}},
      {std::string{"val1"}, std::string{"val2"}},
      {std::string{"val_1"}, std::string{"val_2"}, std::string{"val_3"}}};
  EXPECT_EQ(values, expected);
  EXPECT_EQ(client->ScanCount(), 0);
  EXPECT_EQ(client->MgetCount(), kShards);
}

UTEST(BulkFetch, FetchKeyValues) {
  auto client = std::make_shared<MockClient>(kShards);

  auto key_values = utils::redis::FetchKeyValues("*", *client);
  const std::unordered_map<std::string, std::string> expected = {
      {"ke1", "va1"},     {"key1", "val1"},   {"key2", "val2"},
      {"key_1", "val_1"}, {"key_2", "val_2"}, {"key_3", "val_3"}};
  EXPECT_EQ(key_values, expected);
  EXPECT_EQ(client->ScanCount(), kShards);
  EXPECT_EQ(client->MgetCount(), kShards);
}
