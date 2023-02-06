#include <userver/utest/utest.hpp>

#include <gzip/gzip.hpp>
#include <userver/crypto/base64.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/formats/parse/common_containers.hpp>

const std::string JSON_VALUE{"{\"id\":123, \"alias_id\":null}"};
const auto performer = formats::json::FromString(JSON_VALUE);

TEST(GzipBase64, Encode) {
  formats::json::ValueBuilder vb(formats::json::Type::kObject);

  formats::json::ValueBuilder cc(formats::json::Type::kObject);
  cc.EmplaceNocheck("some_key", "some_value");
  vb.EmplaceNocheck("compressed_content", cc);

  const auto value = vb.ExtractValue();
  const auto str = formats::json::ToString(value);

  EXPECT_EQ(str, R"|({"compressed_content":{"some_key":"some_value"}})|");

  const auto gzipped_data = gzip::Compress(str);
  auto final_data = crypto::base64::Base64Encode(gzipped_data);
  EXPECT_EQ(final_data,
            "H4sIAAAAAAAC/"
            "6tWSs7PLShKLS5OTYlPzs8rSc0rUbKqVirOz02Nz06tVLKCMMsSc0pTlWprAUdgOlM"
            "wAAAA");
}

TEST(GzipBase64, Decode) {
  // this string is encoded+compressed content from IOS
  const std::string_view data{
      "H4sIAAAAAAAAA6tWSs7PLShKLS5OTYlPzs8rSc0rUbKqVirOz02Nz06tVLKCMMsSc0pTlWpr"
      "AUdgOlMwAAAA"};
  const auto after_base64 = crypto::base64::Base64Decode(data);
  const auto raw_data = gzip::Decompress(after_base64);
  EXPECT_EQ(raw_data, R"|({"compressed_content":{"some_key":"some_value"}})|");
}

TEST(JsonValue, NullValueAsString) {
  const auto alias_id_value = performer["alias_id"].As<std::string>("");

  EXPECT_EQ(alias_id_value, "");
}

TEST(JsonValue, NullValueAsOptionalString) {
  const auto alias_id_value =
      performer["alias_id"].As<std::optional<std::string>>().value_or("");

  EXPECT_EQ(alias_id_value, "");
}
