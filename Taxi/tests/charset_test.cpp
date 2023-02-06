#include <userver/utest/utest.hpp>

#include <charset.hpp>

namespace charset {

const auto text_utf8 = "текст";
const auto text_utf8sig = "\xEF\xBB\xBFтекст";
const auto text_cp1251 = "\xF2\xE5\xEA\xF1\xF2";

TEST(TestCharset, EncodeUTF8) {
  const auto text_encoded = charset::Charset("UTF-8").Encode(text_utf8);
  ASSERT_EQ(text_encoded, text_utf8);
}

TEST(TestCharset, EncodeUTF8SIG) {
  const auto text_encoded = charset::Charset("UTF-8-SIG").Encode(text_utf8);
  ASSERT_EQ(text_encoded, text_utf8sig);
}

TEST(TestCharset, EncodeCP1251) {
  const auto text_encoded = charset::Charset("cp1251").Encode(text_utf8);
  ASSERT_EQ(text_encoded, text_cp1251);
}

TEST(TestCharset, DecodeUTF8) {
  const auto text_decoded = charset::Charset("UTF-8").Decode(text_utf8);
  ASSERT_EQ(text_decoded, text_utf8);
}

TEST(TestCharset, DecodeUTF8SIG) {
  const auto text_decoded = charset::Charset("UTF-8-SIG").Decode(text_utf8sig);
  ASSERT_EQ(text_decoded, text_utf8);
}

TEST(TestCharset, DecodeCP1251) {
  const auto text_decoded = charset::Charset("cp1251").Decode(text_cp1251);
  ASSERT_EQ(text_decoded, text_utf8);
}

}  // namespace charset
