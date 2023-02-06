#include <serialization/string_view.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <gtest/gtest.h>

namespace test {

TEST(SerializeStringView, SerializeSV) {
  auto reference = std::string_view{"data"};

  auto json_object = formats::json::ValueBuilder(reference).ExtractValue();

  // parse
  auto test_data = json_object.As<std::string>();

  EXPECT_EQ(reference, test_data);
}

}  // namespace test
