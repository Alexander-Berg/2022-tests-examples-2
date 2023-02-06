#include <gtest/gtest.h>

#include <radio/blocks/commutation/entry_points.hpp>
#include <radio/blocks/utils/buffer_sample.hpp>
#include <radio/blocks/utils/data_delay.hpp>
#include <userver/formats/json/serialize_container.hpp>

namespace hejmdal::radio::blocks {

namespace {

struct Env {
  DataEntryPoint entry;
  DataDelay delay;
  std::vector<std::shared_ptr<BufferSample>> buffers;
};

Env CreateEnv(int delay_length) {
  formats::json::ValueBuilder json;
  json["id"] = "test_delay";
  json["debug"] = std::vector<std::string>{"data"};
  json["delay_length"] = delay_length;
  Env env{DataEntryPoint("test_entry"), DataDelay(json.ExtractValue()), {}};
  env.entry.OnDataOut(&env.delay);
  env.buffers = env.delay.CreateDebugBuffers(1000);
  return env;
}

}  // namespace

TEST(TestDataDelay, MainTest) {
  auto now = time::Now();
  auto env = CreateEnv(1);
  env.entry.DataIn(Meta::kNull, now, 0.);
  env.entry.DataIn(Meta::kNull, now + time::Minutes(1), 1.);
  env.entry.DataIn(Meta::kNull, now + time::Minutes(2), 2.);
  env.entry.DataIn(Meta::kNull, now + time::Minutes(3), 3.);

  ASSERT_EQ(env.buffers.size(), 1u);
  for (const auto& buffer : env.buffers) {
    auto ts_map = buffer->ExtractTimeSeries();
    ASSERT_EQ(ts_map.size(), 1u);
    for (const auto& [name, ts] : ts_map) {
      ASSERT_EQ(ts.size(), 3u);
      for (int i = 0; i < 3; i++) {
        EXPECT_EQ(ts[i].GetTime(), now + time::Minutes(i + 1));
        EXPECT_EQ(ts[i].GetValue(), (double)i);
      }
    }
  }
}

TEST(TestDataDelay, TestBiggerDelay) {
  auto now = time::Now();
  auto env = CreateEnv(3);
  env.entry.DataIn(Meta::kNull, now, 0.);
  env.entry.DataIn(Meta::kNull, now + time::Minutes(1), 1.);
  env.entry.DataIn(Meta::kNull, now + time::Minutes(2), 2.);
  env.entry.DataIn(Meta::kNull, now + time::Minutes(3), 3.);

  ASSERT_EQ(env.buffers.size(), 1u);
  for (const auto& buffer : env.buffers) {
    auto ts_map = buffer->ExtractTimeSeries();
    ASSERT_EQ(ts_map.size(), 1u);
    for (const auto& [name, ts] : ts_map) {
      ASSERT_EQ(ts.size(), 1u);
      EXPECT_EQ(ts[0].GetTime(), now + time::Minutes(3));
      EXPECT_EQ(ts[0].GetValue(), 0.);
    }
  }
}

}  // namespace hejmdal::radio::blocks
