#include "models.hpp"

#include <common/test_config.hpp>
#include <config/config.hpp>

#include <gtest/gtest.h>

using models::FormatPhoneNumber;
using models::NormalizeData;
using models::ShouldBeCenzored;

TEST(NormalizeData, One) {
  EXPECT_STREQ("ABBGDEEZH3IIKLMH0", NormalizeData("абвгдеёжзийклмно").c_str());
  EXPECT_STREQ("PPCTYFXCCHSHSCHJIJE", NormalizeData("прстуфхцчшщъыьэ").c_str());
  EXPECT_STREQ("YUYA784055", NormalizeData("юя784O55").c_str());
  EXPECT_STREQ("H658TK116", NormalizeData("Н658ТК/116").c_str());
  EXPECT_STREQ("437P4PA74PSCHBI88ABCDE",
               NormalizeData("437р4па74..ПЩвы88%$@abcde").c_str());
  EXPECT_STREQ("9900154527",
               NormalizeData("9900154527\363\240\203\250").c_str());
}

TEST(ShouldBeCenzored, One) {
  config::Config config = config::DocsMapForTest();
  EXPECT_TRUE(
      ShouldBeCenzored("авыа ! авыа аы а. https://www.youtube.com/watch"
                       "?v=bj9JoTRgbtQ (change.org) авыаыв",
                       config));
  EXPECT_TRUE(
      ShouldBeCenzored(" авыа ! авыа аы а. ffff.com/watch ?"
                       "v=bj9JoTRgbtQ авыаыв",
                       config));
  EXPECT_FALSE(
      ShouldBeCenzored("авыа ! авыа аы а. https://www.youtube.com"
                       "/watch?v=bj9JoTRgbtQ авыаыв",
                       config));
  EXPECT_FALSE(
      ShouldBeCenzored(" авыа ! авыа аы а. driver.yandex/watch"
                       "?v=bj9JoTRgbtQ авыаыв",
                       config));
  EXPECT_FALSE(ShouldBeCenzored("http?аыалыра раырв оар ыоора http", config));
  EXPECT_FALSE(
      ShouldBeCenzored("<img src=\"\"/assets/emoticons/0001.png\"\">"
                       "<img src=\"\"/assets/emoticons/0001.png\"\">"
                       "fds",
                       config));
  EXPECT_FALSE(ShouldBeCenzored("https://youtu.be/5U6V7VP3JGc", config));
  EXPECT_FALSE(
      ShouldBeCenzored("<img src=\"\"/assets/emoticons/0118.png\"\">"
                       "<img src=\"\"/assets/emoticons/0118.png\"\">"
                       "<img src=\"\"/assets/emoticons/0119.png\"\">"
                       "<img src=\"\"/assets/emoticons/0087.png\"\">"
                       "<img src=\"\"/assets/emoticons/26a0.png\"\">"
                       "<img src=\"\"/assets/emoticons/26a0.png\"\">"
                       "<img src=\"\"/assets/emoticons/260.png\"\">",
                       config));
  EXPECT_TRUE(
      ShouldBeCenzored("Чувак, зацени видос pornolab.net/forum/"
                       "viewtopic.php?t=2000779",
                       config));
  EXPECT_FALSE(ShouldBeCenzored("driver@pornhub.com", config));
  EXPECT_TRUE(ShouldBeCenzored("http://youtube.com@pornhub.com", config));
  EXPECT_TRUE(ShouldBeCenzored("http://youtube.com.pornhub.com", config));
}

TEST(FormatPhoneNumber, One) {
  EXPECT_STREQ("+38 (0622) 123-45-67",
               FormatPhoneNumber("[+3806221234567]").c_str());
  EXPECT_STREQ("+7 (0000) 123-45-67",
               FormatPhoneNumber("#.^700001234567^.#").c_str());
  EXPECT_STREQ("+7 (926) 123-45-67", FormatPhoneNumber("89261234567").c_str());
  EXPECT_STREQ("+7 (926) 123-45-67",
               FormatPhoneNumber("926-123-45-67").c_str());
  EXPECT_STREQ("[1488]", FormatPhoneNumber("Какая-то дичь, 1488").c_str());
  EXPECT_STREQ("", FormatPhoneNumber("Какой-то текст").c_str());
}
