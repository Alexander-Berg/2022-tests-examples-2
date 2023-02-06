#include <gtest/gtest.h>

#include <radio/blocks/commutation/entry_points.hpp>
#include <radio/blocks/modifiers/fill_data_holes.hpp>
#include <radio/blocks/utils/buffer_sample.hpp>
#include <userver/formats/json/serialize_container.hpp>

namespace hejmdal::radio::blocks {

namespace {

struct Env {
  std::unique_ptr<DataEntryPoint> entry;
  std::unique_ptr<FillDataHoles> fdh;
  std::vector<std::shared_ptr<BufferSample>> buffers;
};

Env CreateEnv(int period_sec, std::string method = "linear") {
  formats::json::ValueBuilder json;
  json["id"] = "test_fill";
  json["debug"] = std::vector<std::string>{"data"};
  json["period_sec"] = period_sec;
  json["method"] = method;
  auto entry = std::make_unique<DataEntryPoint>("test_entry");
  auto fdh = std::make_unique<FillDataHoles>(json.ExtractValue());
  entry->OnDataOut(fdh.get());
  auto buffers = fdh->CreateDebugBuffers(1000);
  return Env{std::move(entry), std::move(fdh), std::move(buffers)};
}

}  // namespace

TEST(TestFillDataHoles, MainTest) {
  auto now = time::Now();
  auto env = CreateEnv(60);
  env.entry->DataIn(Meta::kNull, now, -1.);
  env.entry->DataIn(Meta::kNull, now + time::Minutes(1), 0.);
  env.entry->DataIn(Meta::kNull, now + time::Minutes(11), 10.);
  env.entry->DataIn(Meta::kNull, now + time::Minutes(12), 11.);

  ASSERT_EQ(env.buffers.size(), 1u);
  for (const auto& buffer : env.buffers) {
    auto ts_map = buffer->ExtractTimeSeries();
    ASSERT_EQ(ts_map.size(), 1u);
    for (const auto& [name, ts] : ts_map) {
      ASSERT_EQ(ts.size(), 13u);
      for (int i = 0; i < 13; i++) {
        EXPECT_EQ(ts[i].GetTime(), now + time::Minutes(i));
        EXPECT_EQ(ts[i].GetValue(), (double)i - 1.);
      }
    }
  }
}

TEST(TestFillDataHoles, TestDelay) {
  auto now = time::Now();
  auto env = CreateEnv(60);
  env.entry->DataIn(Meta::kNull, now, 0.);
  env.entry->DataIn(Meta::kNull, now + time::Minutes(1) + time::Seconds(15),
                    1.);
  env.entry->DataIn(Meta::kNull, now + time::Minutes(2), 2.);

  ASSERT_EQ(env.buffers.size(), 1u);
  for (const auto& buffer : env.buffers) {
    auto ts_map = buffer->ExtractTimeSeries();
    ASSERT_EQ(ts_map.size(), 1u);
    for (const auto& [name, ts] : ts_map) {
      ASSERT_EQ(ts.size(), 3u);
      EXPECT_EQ(ts[0].GetTime(), now);
      EXPECT_EQ(ts[0].GetValue(), 0.);
      EXPECT_EQ(ts[1].GetTime(), now + time::Minutes(1) + time::Seconds(15));
      EXPECT_EQ(ts[1].GetValue(), 1.);
      EXPECT_EQ(ts[2].GetTime(), now + time::Minutes(2));
      EXPECT_EQ(ts[2].GetValue(), 2.);
    }
  }
}

}  // namespace hejmdal::radio::blocks
