#include <gtest/gtest.h>

#include "dsvs.hpp"

namespace {

void AddStringField(utils::dsvs::DSVStringBuilder& builder,
                    const std::string& key, const std::string& value) {
  builder.AddField(key, value);
}

}  // namespace

TEST(DSVStringBuilder, test_inf) {
  utils::dsvs::DSVStringBuilder builder;
  builder.AddField("key1", std::numeric_limits<double>::infinity());
  builder.AddField("key2", -std::numeric_limits<double>::infinity());
  builder.AddField("key3", 3.0);
  EXPECT_EQ("key3=3.000000\n", builder.str());
}

TEST(DSVStringBuilder, test_nan) {
  utils::dsvs::DSVStringBuilder builder;
  builder.AddField("key1", std::numeric_limits<double>::quiet_NaN());
  builder.AddField("key2", std::numeric_limits<double>::signaling_NaN());
  builder.AddField("key3", 3.0);
  EXPECT_EQ("key3=3.000000\n", builder.str());
}

TEST(DSVStringBuilder, add_string_simple) {
  utils::dsvs::DSVStringBuilder builder;
  AddStringField(builder, "key1", "value1");
  AddStringField(builder, "key2", "value2");
  EXPECT_EQ("key1=value1\tkey2=value2\n", builder.str());
}

TEST(DSVStringBuilder, add_string_escape_backslash_value) {
  utils::dsvs::DSVStringBuilder builder;
  AddStringField(builder, "key1", "\\value1");
  AddStringField(builder, "key2", "val\\ue2");
  AddStringField(builder, "key3", "value3\\");
  EXPECT_EQ("key1=\\\\value1\tkey2=val\\\\ue2\tkey3=value3\\\\\n",
            builder.str());
}

TEST(DSVStringBuilder, add_string_escape_n_value) {
  utils::dsvs::DSVStringBuilder builder;
  AddStringField(builder, "key1", "\nvalue1");
  AddStringField(builder, "key2", "val\nue2");
  AddStringField(builder, "key3", "value3\n");
  EXPECT_EQ("key1=\\nvalue1\tkey2=val\\nue2\tkey3=value3\\n\n", builder.str());
}

TEST(DSVStringBuilder, add_string_escape_r_value) {
  utils::dsvs::DSVStringBuilder builder;
  AddStringField(builder, "key1", "\rvalue1");
  AddStringField(builder, "key2", "val\rue2");
  AddStringField(builder, "key3", "value3\r");
  EXPECT_EQ("key1=\\rvalue1\tkey2=val\\rue2\tkey3=value3\\r\n", builder.str());
}

TEST(DSVStringBuilder, add_string_escape_t_value) {
  utils::dsvs::DSVStringBuilder builder;
  AddStringField(builder, "key1", "\tvalue1");
  AddStringField(builder, "key2", "val\tue2");
  AddStringField(builder, "key3", "value3\t");
  EXPECT_EQ("key1=\\tvalue1\tkey2=val\\tue2\tkey3=value3\\t\n", builder.str());
}

TEST(DSVStringBuilder, add_string_escape_0_value) {
  utils::dsvs::DSVStringBuilder builder;
  AddStringField(builder, "key1", std::string("\0value1", 7));
  AddStringField(builder, "key2", std::string("val\0ue2", 7));
  AddStringField(builder, "key3", std::string("value3\0", 7));
  EXPECT_EQ("key1=\\0value1\tkey2=val\\0ue2\tkey3=value3\\0\n", builder.str());
}

TEST(DSVStringBuilder, add_string_escape_assignment_key) {
  utils::dsvs::DSVStringBuilder builder;
  AddStringField(builder, "=key1", "value1");
  AddStringField(builder, "ke=y2", "value2");
  AddStringField(builder, "key3=", "value3");
  EXPECT_EQ("\\=key1=value1\tke\\=y2=value2\tkey3\\==value3\n", builder.str());
}

TEST(DSVStringBuilder, add_string_escape_backslash_key) {
  utils::dsvs::DSVStringBuilder builder;
  AddStringField(builder, "\\key1", "value1");
  AddStringField(builder, "ke\\y2", "value2");
  AddStringField(builder, "key3\\", "value3");
  EXPECT_EQ("\\\\key1=value1\tke\\\\y2=value2\tkey3\\\\=value3\n",
            builder.str());
}

TEST(DSVStringBuilder, add_string_escape_n_key) {
  utils::dsvs::DSVStringBuilder builder;
  AddStringField(builder, "\nkey1", "value1");
  AddStringField(builder, "ke\ny2", "value2");
  AddStringField(builder, "key3\n", "value3");
  EXPECT_EQ("\\nkey1=value1\tke\\ny2=value2\tkey3\\n=value3\n", builder.str());
}

TEST(DSVStringBuilder, add_string_escape_r_key) {
  utils::dsvs::DSVStringBuilder builder;
  AddStringField(builder, "\rkey1", "value1");
  AddStringField(builder, "ke\ry2", "value2");
  AddStringField(builder, "key3\r", "value3");
  EXPECT_EQ("\\rkey1=value1\tke\\ry2=value2\tkey3\\r=value3\n", builder.str());
}

TEST(DSVStringBuilder, add_string_escape_t_key) {
  utils::dsvs::DSVStringBuilder builder;
  AddStringField(builder, "\tkey1", "value1");
  AddStringField(builder, "ke\ty2", "value2");
  AddStringField(builder, "key3\t", "value3");
  EXPECT_EQ("\\tkey1=value1\tke\\ty2=value2\tkey3\\t=value3\n", builder.str());
}

TEST(DSVStringBuilder, add_string_escape_0_key) {
  utils::dsvs::DSVStringBuilder builder;
  AddStringField(builder, std::string("\0key1", 5), "value1");
  AddStringField(builder, std::string("ke\0y2", 5), "value2");
  AddStringField(builder, std::string("key3\0", 5), "value3");
  EXPECT_EQ("\\0key1=value1\tke\\0y2=value2\tkey3\\0=value3\n", builder.str());
}
