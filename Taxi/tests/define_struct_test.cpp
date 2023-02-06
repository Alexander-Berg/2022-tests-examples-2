#include <userver/utest/utest.hpp>

#include <utils/define_struct.hpp>

namespace eats_report_storage::utils {

TEST(DefibeStruct,
     get_class_attributes_names_should_return_fields_names_of_class) {
  DEFINE_STRUCT(TestClass, (int, field1)(bool, field2))
  ASSERT_EQ(GetClassAttributesNames<TestClass>(),
            std::string("field1, field2"));
}

}  // namespace eats_report_storage::utils
