#include <gtest/gtest.h>

#include <hashidsxx/hashids.hpp>

TEST(HashidsTest, ValidId) {
  std::string id = "LkQWjnegglewZ1p0";

  hashidsxx::Hashids generator{};
  const auto decoded_id = generator.decode(id);

  EXPECT_TRUE(decoded_id.size() == 1);
  EXPECT_TRUE(decoded_id[0] == 1488);
}

TEST(HashidsTest, InvalidId) {
  std::string id = "йцукенгшщзфывапр";

  hashidsxx::Hashids generator{};

  EXPECT_THROW(generator.decode(id), hashidsxx::HashidsDecodeException);
}

TEST(HashidsTest, TooSHortId) {
  std::string id = "short";

  hashidsxx::Hashids generator{};

  EXPECT_THROW(generator.decode(id), hashidsxx::HashidsDecodeException);
}
