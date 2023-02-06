#include <gtest/gtest.h>

#include "json_adapter.hpp"
#include "struct_adapter.hpp"

namespace utils {
namespace dsvs {
class TestAccess {
 public:
  template <typename T>
  static std::string Format(const T& elem) {
    return utils::dsvs::FileWriter<std::vector<T>>::Format(elem);
  }
};
}  // namespace dsvs
}  // namespace utils

namespace {

struct TestStruct {
  std::string StringField1;
  int IntField1;
  double DoubleField1;
};

JSON_SERIALIZABLE(TestStruct, StringField1, IntField1, DoubleField1)

struct TestStruct2 {
  std::string StringField1;
  TestStruct StructField1;
};

}  // namespace

DEFINE_LOGGABLE_STRUCT(TestStruct, StringField1, IntField1, DoubleField1)
DEFINE_LOGGABLE_STRUCT(TestStruct2, StringField1, StructField1)

TEST(struct_adapter, test_flat) {
  TestStruct st{"String1", 42, 3.14};

  ASSERT_EQ(utils::dsvs::TestAccess::Format(st),
            "StringField1=String1\tIntField1=42\tDoubleField1=3.140000\n");
}

TEST(struct_adapter, test_compound) {
  TestStruct2 st{"String1", {"String1", 42, 3.14}};

  ASSERT_STREQ(
      "StringField1=String1\tStructField1={\"DoubleField1\":3.1400000000000001,"
      "\"IntField1\":42,\"StringField1\":\"String1\"}\n",
      utils::dsvs::TestAccess::Format(st).c_str());
}
