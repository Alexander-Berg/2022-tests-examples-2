#include <endpoints/full/plugins/subtitle/common/subtitle_serializable.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::plugins::subtitle {

void TestSerializable(const std::optional<std::string>& subtitle,
                      const std::optional<std::string>& expected_result) {
  const auto serializable = SubtitleSerializable(subtitle);

  handlers::ServiceLevel sl_resp;
  common::ResultWrapper<handlers::ServiceLevel> wrapper(sl_resp);
  serializable.SerializeInPlace(wrapper);

  ASSERT_EQ(expected_result, sl_resp.subtitle);
}

TEST(SubtitleSerializable, valid) {
  TestSerializable("some_subtitle", "some_subtitle");
}

TEST(SubtitleSerializable, empty) { TestSerializable("", ""); }

TEST(SubtitleSerializable, nullopt) {
  TestSerializable(std::nullopt, std::nullopt);
}

}  // namespace routestats::plugins::subtitle
