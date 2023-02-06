#include <endpoints/full/plugins/title/common/title_serializable.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::full::title {

void TestSerializable(const std::optional<std::string>& title,
                      const std::optional<std::string>& expected_result) {
  const auto serializable = TitleSerializable(title);

  handlers::ServiceLevel sl_resp;
  plugins::common::ResultWrapper<handlers::ServiceLevel> wrapper(sl_resp);
  serializable.SerializeInPlace(wrapper);

  ASSERT_EQ(expected_result, sl_resp.title);
}

TEST(TitleSerializable, valid) { TestSerializable("some_title", "some_title"); }

TEST(TitleSerializable, empty) { TestSerializable("", ""); }

TEST(TitleSerializable, nullopt) {
  TestSerializable(std::nullopt, std::nullopt);
}

}  // namespace routestats::full::title
