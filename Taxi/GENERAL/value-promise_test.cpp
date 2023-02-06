#include <userver/utest/utest.hpp>

#include <core/variant/io/value-promise.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

namespace agl::modules::tests {

struct JsonPromiseTrait {
  using Value = formats::json::Value;
  using ParseException = formats::json::ParseException;

  static std::string ToString(const Value& value) {
    return formats::json::ToString(value);
  }

  static Value FromString(std::string_view data) {
    return formats::json::FromString(data);
  }
};

UTEST(TestValuePromise, FromJsonValue) {
  using Promised = core::variant::io::ValuePromise<JsonPromiseTrait>;

  formats::json::ValueBuilder sample_builder;
  sample_builder["foo"] = "bar";
  formats::json::Value sample = sample_builder.ExtractValue();
  std::string sample_str = formats::json::ToString(sample);

  Promised promise(sample);
  EXPECT_EQ(promise.AsString().data, sample_str);
  EXPECT_EQ(promise.AsParsed(), sample);
}

UTEST(TestValuePromise, FromJsonString) {
  using Promised = core::variant::io::ValuePromise<JsonPromiseTrait>;

  formats::json::ValueBuilder sample_builder;
  sample_builder["foo"] = "bar";
  formats::json::Value sample = sample_builder.ExtractValue();
  std::string sample_str = formats::json::ToString(sample);

  Promised promise(sample_str, "", true);
  EXPECT_EQ(promise.AsString().data, sample_str);
  EXPECT_EQ(promise.AsParsed(), sample);
}

UTEST(TestValuePromise, FromJsonGzipString) {
  using Promised = core::variant::io::ValuePromise<JsonPromiseTrait>;

  formats::json::ValueBuilder sample_builder;
  sample_builder["foo"] = "bar";
  formats::json::Value sample = sample_builder.ExtractValue();
  std::string sample_str = gzip::Compress(formats::json::ToString(sample));

  Promised promise(sample_str, "gzip", true);
  EXPECT_EQ(promise.AsString().data, sample_str);
  EXPECT_EQ(promise.AsParsed(), sample);
}

}  // namespace agl::modules::tests
