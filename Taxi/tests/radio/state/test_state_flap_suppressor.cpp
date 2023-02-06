#include <gtest/gtest.h>

#include <userver/formats/serialize/common_containers.hpp>

#include <radio/blocks/commutation/entry_points.hpp>
#include <radio/blocks/state/state_flap_suppressor.hpp>
#include <radio/blocks/utils/buffer_sample.hpp>

namespace hejmdal::radio::blocks {

namespace {

struct Env {
  StateEntryPoint entry;
  StateFlapSuppressor test_block;
  std::vector<std::shared_ptr<BufferSample>> buffers;
};

Env CreateEnv(int stable_time, int critical_time) {
  formats::json::ValueBuilder json;
  json["id"] = "test_block";
  json["debug"] = std::vector<std::string>{"state"};
  json["stable_time_sec"] = stable_time;
  json["critical_time_sec"] = critical_time;
  Env env{StateEntryPoint("test_entry"),
          StateFlapSuppressor(json.ExtractValue()),
          {}};
  env.entry.OnStateOut(&env.test_block);
  env.buffers = env.test_block.CreateDebugBuffers(1000);
  return env;
}

}  // namespace

TEST(TestStateFlapSuppressor, MainTest) {
  auto now = time::Now();
  auto env = CreateEnv(300, 900);
  env.entry.StateIn(Meta::kNull, now, State::kOk);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{1}, State::kOk);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{2}, State::kWarn);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{3}, State::kWarn);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{4}, State::kOk);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{5}, State::kCritical);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{6}, State::kCritical);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{7}, State::kOk);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{8}, State::kWarn);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{9}, State::kWarn);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{10}, State::kOk);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{11}, State::kOk);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{12}, State::kOk);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{13}, State::kOk);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{14}, State::kWarn);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{15}, State::kWarn);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{16}, State::kOk);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{17}, State::kOk);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{18}, State::kOk);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{19}, State::kOk);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{20}, State::kOk);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{21}, State::kOk);
  env.entry.StateIn(Meta::kNull, now + time::Minutes{22}, State::kOk);

  ASSERT_EQ(env.buffers.size(), 1u);
  for (const auto& buffer : env.buffers) {
    auto ts_map = buffer->ExtractTimeSeries();
    ASSERT_EQ(ts_map.size(), 1u);
    for (const auto& [name, ts] : ts_map) {
      ASSERT_EQ(ts.size(), 23u);
      for (int i = 0; i < 23; i++) {
        EXPECT_EQ(ts[i].GetTime(), now + time::Minutes(i));
        if (i < 13 || i >= 21) {
          EXPECT_EQ(ts[i].GetValue(), static_cast<double>(State::kOk));
        } else {
          EXPECT_EQ(ts[i].GetValue(), static_cast<double>(State::kCritical));
        }
      }
    }
  }
}

}  // namespace hejmdal::radio::blocks
