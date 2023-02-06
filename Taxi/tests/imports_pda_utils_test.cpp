#include <gtest/gtest.h>

#include "api-over-data/utils/imports_pda.hpp"

#include <mongo/bson/bsonmisc.h>
#include <mongo/mongo.hpp>

::mongo::BSONObj MakeTestDocument() {
  ::mongo::BSONObjBuilder builder;
  builder.append("empty_array", ::mongo::BSONArrayBuilder().arr())
      .append("array", BSON_ARRAY("1"
                                  << "2"))
      .append("empty_object", ::mongo::BSONObjBuilder().obj())
      .append("object", BSON("1"
                             << "2"))
      .append("string", "string")
      .append("empty_string", "")
      .append("int", 1)
      .append("zero_int", 0)
      .append("double", 1.0)
      .append("zero_double", 0.0);
  builder << "null" << ::mongo::BSONNULL;

  return builder.obj();
}

TEST(ImportsPdaUtils, FieldValidationTest) {
  const auto test_doc = MakeTestDocument();
  EXPECT_TRUE(api_over_data::utils::PythonGetCheck(test_doc["array"]));
  EXPECT_TRUE(api_over_data::utils::PythonGetCheck(test_doc["object"]));
  EXPECT_TRUE(api_over_data::utils::PythonGetCheck(test_doc["string"]));
  EXPECT_TRUE(api_over_data::utils::PythonGetCheck(test_doc["int"]));
  EXPECT_TRUE(api_over_data::utils::PythonGetCheck(test_doc["double"]));

  EXPECT_FALSE(api_over_data::utils::PythonGetCheck(test_doc["empty_array"]));
  EXPECT_FALSE(api_over_data::utils::PythonGetCheck(test_doc["empty_object"]));
  EXPECT_FALSE(api_over_data::utils::PythonGetCheck(test_doc["null"]));
  EXPECT_FALSE(api_over_data::utils::PythonGetCheck(test_doc["empty_string"]));
  EXPECT_FALSE(api_over_data::utils::PythonGetCheck(test_doc["zero_int"]));
  EXPECT_FALSE(api_over_data::utils::PythonGetCheck(test_doc["zero_double"]));
}
