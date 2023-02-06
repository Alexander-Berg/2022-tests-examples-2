#include "remove_mds_url.hpp"

#include <gtest/gtest.h>

void Check(const std::string& href, const std::string& expected) {
  ASSERT_EQ(helpers::RemoveMdsUrl(href, LogExtra{}), expected);
}

TEST(RemoveMdsUrl, Test) {
  Check("", "");
  Check("asd", "asd");
  Check("https://storage.mds.yandex.net/get-taximeter/asd", "asd");
  Check("https://storage.mdst.yandex.net/get-taximeter/asd", "asd");
  Check("http://storage.mds.yandex.net/get-taximeter/asd", "asd");
  Check("http://storage.mdst.yandex.net/get-taximeter/asd", "asd");
  Check("some random prefix http://storage.mdst.yandex.net/get-taximeter/asd",
        "asd");
  Check(
      "https://storage.mds.yandex.net/get-taximeter/"
      "https://storage.mds.yandex.net/get-taximeter/"
      "https://storage.mds.yandex.net/get-taximeter/"
      "3325/6a255a958d234fa497d99c21b4a1f166_small.jpg",
      "3325/6a255a958d234fa497d99c21b4a1f166_small.jpg");
}
