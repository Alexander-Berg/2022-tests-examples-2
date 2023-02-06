#include <userver/formats/parse/common_containers.hpp>
#include <userver/utest/utest.hpp>

#include <common/utils/identifiers.hpp>

TEST(ShardChoosingTest, HashByDriverId) {
  size_t hits_by_shard[] = {0, 0};
  size_t attempts = 1000;
  for (size_t id = 0; id < attempts; id++) {
    auto shard =
        billing_time_events::utils::driver_id::ToShardId(2, std::to_string(id));
    hits_by_shard[shard]++;
  }
  EXPECT_NEAR(hits_by_shard[0], attempts / 2, attempts * 0.01);
  EXPECT_NEAR(hits_by_shard[1], attempts / 2, attempts * 0.01);
}
