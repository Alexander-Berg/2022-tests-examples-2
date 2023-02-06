#include <gtest/gtest.h>

#include <radio/blocks/block_factory.hpp>
#include <radio/blocks/commutation/entry_points.hpp>
#include <radio/blocks/utils/buffers.hpp>

namespace hejmdal::radio::blocks {

TEST(TestDescriptionFormatter, MainTest) {
  constexpr auto kMetaStr = R"=(
{
  "cpu_aggregator": {
    "aggregator_type": "worst_state_aggregator",
    "aggregation_key": "host",
    "not_ok" : [
        "host_1",
        "host_2",
        "host_3"
    ]
  }
}
)=";

  formats::json::ValueBuilder builder;
  builder["type"] = "description_formatter";
  builder["id"] = "formatter";
  builder["description_format"] =
      "Problems with {cpu_aggregator__aggregation_key}: "
      "{cpu_aggregator__not_ok}.";
  builder["args"].PushBack("cpu_aggregator__aggregation_key");
  builder["args"].PushBack("cpu_aggregator__not_ok");
  auto formatter = BlockFactory::CreateBlock(builder.ExtractValue());

  auto entry = std::make_shared<StateEntryPoint>("");
  entry->OnStateOut(formatter);
  auto out = std::make_shared<StateBuffer>("");
  formatter->OnStateOut(out);

  auto meta_value = formats::json::FromString(kMetaStr);
  entry->StateIn(Meta(meta_value), time::Now(), State::kWarn);
  EXPECT_EQ(out->LastState(), State::kWarn);
  std::string expected = "Problems with host: host_1,host_2,host_3.";
  EXPECT_EQ(out->LastState().GetDescription(), expected);
}

TEST(TestDescriptionFormatter, MainTestWithoutArgs) {
  constexpr auto kMetaStr = R"=(
{
  "cpu_aggregator": {
    "not_ok" : [
        "host_1",
        "host_2",
        "host_3"
    ]
  }
}
)=";

  formats::json::ValueBuilder builder;
  builder["type"] = "description_formatter";
  builder["id"] = "formatter";
  builder["description_format"] = "{cpu_aggregator__not_ok}";
  auto formatter = BlockFactory::CreateBlock(builder.ExtractValue());

  auto entry = std::make_shared<StateEntryPoint>("");
  entry->OnStateOut(formatter);
  auto out = std::make_shared<StateBuffer>("");
  formatter->OnStateOut(out);

  auto meta_value = formats::json::FromString(kMetaStr);
  entry->StateIn(Meta(meta_value), time::Now(), State::kWarn);
  std::string expected = "host_1,host_2,host_3";
  EXPECT_EQ(out->LastState().GetDescription(), expected);
}

TEST(TestDescriptionFormatter, ArrayFormat) {
  formats::json::ValueBuilder builder;
  builder["type"] = "description_formatter";
  builder["id"] = "formatter";
  builder["description_format"] = "{not_ok}";
  auto formatter = BlockFactory::CreateBlock(builder.ExtractValue());

  auto entry = std::make_shared<StateEntryPoint>("");
  entry->OnStateOut(formatter);
  auto out = std::make_shared<StateBuffer>("");
  formatter->OnStateOut(out);

  {
    constexpr auto kMetaStr = R"=(
{
  "not_ok" : [
    {
      "host": "host_1",
      "sate": "kWarn"
    },
    {
      "host": "host_2",
      "sate": "kError"
    }
  ]
}
)=";
    auto meta_value = formats::json::FromString(kMetaStr);
    entry->StateIn(Meta(meta_value), time::Now(), State::kWarn);
    EXPECT_EQ(out->LastState().GetDescription(), "");
  }
  {
    constexpr auto kMetaStr = R"=(
{
  "not_ok" : [
    "host_1"
  ]
}
)=";
    auto meta_value = formats::json::FromString(kMetaStr);
    entry->StateIn(Meta(meta_value), time::Now(), State::kWarn);
    EXPECT_EQ(out->LastState().GetDescription(), "host_1");
  }
  {
    constexpr auto kMetaStr = R"=(
{
  "not_ok" : [
  ]
}
)=";
    auto meta_value = formats::json::FromString(kMetaStr);
    entry->StateIn(Meta(meta_value), time::Now(), State::kWarn);
    EXPECT_EQ(out->LastState().GetDescription(), "");
  }
}

}  // namespace hejmdal::radio::blocks
