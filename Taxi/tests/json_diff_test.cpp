#include <agl/util/json-diff.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>

namespace agl::core::tests {
namespace {

std::string HumanReadableDiff(const std::string& lhs, const std::string& rhs) {
  return json_diff::HumanReadableDiffValues(formats::json::FromString(lhs),
                                            formats::json::FromString(rhs));
}

};  // namespace

TEST(Json, Diff) {
  EXPECT_EQ(HumanReadableDiff("1", "2"),
            "- 1\n"
            "+ 2");

  EXPECT_EQ(HumanReadableDiff("{\n"
                              "    \"old\": false,\n"
                              "    \"mod\": 123\n,"
                              "    \"add\": [1, 2],"
                              "    \"del\": [1, 2]"
                              "}",
                              "{\n"
                              "    \"mod\": \"abc\",\n"
                              "    \"del\": [2],"
                              "    \"add\": [1, 3, 4],"
                              "    \"new\": true\n"
                              "}"),
            "{\n"
            "  add: [\n"
            "    1:\n"
            "    - 2\n"
            "    + 3\n"
            "  + 2: 4\n"
            "  ]\n"
            "  del: [\n"
            "    0:\n"
            "    - 1\n"
            "    + 2\n"
            "  - 1: 2\n"
            "  ]\n"
            "  mod:\n"
            "  - 123\n"
            "  + \"abc\"\n"
            "- old: false\n"
            "+ new: true\n"
            "}");
}

}  // namespace agl::core::tests
