#include "check_for_card_number.hpp"

#include <gtest/gtest.h>

using fleet_parks::utils::CheckCardGroup;
using fleet_parks::utils::HasCardNumber;
using fleet_parks::utils::IsValidCard;

bool Luhn(const std::vector<std::wstring>& v) {
  return IsValidCard(v.cbegin(), v.cend());
}

TEST(CheckCardNumberInTextTest, IsValidCard) {
  EXPECT_TRUE(Luhn({L"639002409027598966"}));
  EXPECT_TRUE(Luhn({L"63900", L"2409027598966", L""}));
  EXPECT_FALSE(Luhn({L"639002409027598967"}));
  EXPECT_FALSE(Luhn({L"6390024090", L"27598967", L""}));
}

TEST(CheckCardNumberInTextTest, CheckCardGroup) {
  EXPECT_TRUE(CheckCardGroup({L"5469700013493448"}, 16));
  EXPECT_TRUE(CheckCardGroup({L"1234", L"546970001349", L"3448", L"1234"}, 16));
  EXPECT_TRUE(
      CheckCardGroup({L"5469", L"7000", L"1349", L"3448", L"1234"}, 16));
  EXPECT_TRUE(
      CheckCardGroup({L"1234", L"5469", L"7000", L"1349", L"3448"}, 16));

  EXPECT_FALSE(CheckCardGroup(
      {L"1234", L"15469", L"7000", L"1349", L"344", L"1234"}, 16));

  EXPECT_FALSE(CheckCardGroup({L"5469700013493448"}, 17));
  EXPECT_FALSE(
      CheckCardGroup({L"1234", L"546970001349", L"3448", L"1234"}, 17));
  EXPECT_FALSE(
      CheckCardGroup({L"5469", L"7000", L"1349", L"3448", L"1234"}, 17));
  EXPECT_FALSE(
      CheckCardGroup({L"1234", L"5469", L"7000", L"1349", L"3448"}, 17));

  EXPECT_FALSE(CheckCardGroup({L"5469700013493448"}, 15));
  EXPECT_FALSE(
      CheckCardGroup({L"1234", L"546970001349", L"3448", L"1234"}, 15));
  EXPECT_FALSE(
      CheckCardGroup({L"5469", L"7000", L"1349", L"3448", L"1234"}, 15));
  EXPECT_FALSE(
      CheckCardGroup({L"1234", L"5469", L"7000", L"1349", L"3448"}, 15));
}

TEST(CheckCardNumberInTextTest, HasCardNumber) {
  EXPECT_FALSE(HasCardNumber("043601607#40817810254409357320#A331#LAZAREV"));
  EXPECT_TRUE(HasCardNumber("6390 0240 9027 5989 66"));
  EXPECT_TRUE(HasCardNumber("Card with 19 digits: 6390 0240 9027 5989 657"));
  EXPECT_FALSE(HasCardNumber("6390 0240 9027 5989"));
  EXPECT_FALSE(HasCardNumber("4276 3O0О O da 3860 569О "));
  EXPECT_TRUE(HasCardNumber("5336a6900a6144a4321  Sergeevich"));
  EXPECT_TRUE(HasCardNumber("5336a69OOa6144a4321  Petrovich"));
  EXPECT_TRUE(HasCardNumber("5469700013493448 sber"));
  EXPECT_TRUE(HasCardNumber("546970ОO13493448"));
  EXPECT_FALSE(HasCardNumber("546970ОO13493449"));
  EXPECT_TRUE(HasCardNumber("5469700013493448"));
  EXPECT_TRUE(HasCardNumber("1234 5469-7000-1349-3448 sber"));
  EXPECT_TRUE(HasCardNumber("1234 5469    -   7000-1349-3448 sber"));
  EXPECT_FALSE(HasCardNumber("1234 5469 eto 7000-1349-3448 sber"));
  EXPECT_FALSE(HasCardNumber("1234 5469 a eto 7000-1349-3448 net"));
  EXPECT_FALSE(HasCardNumber("1234 5469-7000-1349-3449 Ne korektnii sber"));
  EXPECT_FALSE(
      HasCardNumber("Some words 6000 a 22.11/ about 4000 16 some "
                    "250/thing 6250/ 250 we 25 dont care"));
  EXPECT_TRUE(
      HasCardNumber("A eto uge 6000 ne 22.11 4000 16  250 6250 250"
                    " tak 25 horosho "));

  // the same with russian letters
  EXPECT_FALSE(HasCardNumber("043601607#40817810254409357320#A331#LAZAREV"));
  EXPECT_TRUE(HasCardNumber("6390 0240 9027 5989 66"));
  EXPECT_FALSE(HasCardNumber("6390 0240 +9027 5989 66"));
  EXPECT_TRUE(HasCardNumber("Карта с 19 цифрами: 6390 0240 9027 5989 657"));
  EXPECT_FALSE(HasCardNumber("6390 0240 9027 5989"));
  EXPECT_TRUE(HasCardNumber("5336a6900a6144a4321  Сергеевич"));
  EXPECT_TRUE(HasCardNumber("5469700013493448 сбер"));
  EXPECT_TRUE(HasCardNumber("5469700013493448"));
  EXPECT_TRUE(HasCardNumber("1234 5469-7000-1349-3448 сбер"));
  EXPECT_TRUE(HasCardNumber("1234 5469    -   7000-1349-3448 сбер"));
  EXPECT_FALSE(HasCardNumber("1234 5469 это 7000-1349-3448 сбер (нет)"));
  EXPECT_TRUE(HasCardNumber("1234 5469 эт 7000-1349-3448 сбер"));
  EXPECT_FALSE(HasCardNumber("1234 5469 а это 7000-1349-3448 нет"));
  EXPECT_FALSE(
      HasCardNumber("ПН - ПТ 10:00 - 19:00 СБ 10:00 - 16:00 ВС 10:00 - 16:00"));
  EXPECT_FALSE(HasCardNumber("9-00 до 18-00:  +7 906 135 58 78,"));
  EXPECT_FALSE(HasCardNumber("1234 5469-7000-1349-3449 Ne korektnii сбер"));
  EXPECT_FALSE(
      HasCardNumber("Разбивка долга 6000 с 22.11/ разбивка долга 4000"
                    " 16 дней по 250/Разбивка долга 6250/ 250 на 25 "
                    "дней "));
  EXPECT_TRUE(
      HasCardNumber("Разбивка долга 6000 с 22.11 4000 16  250 6250 250 "
                    "на 25 дней "));
  EXPECT_FALSE(HasCardNumber("пн-пт с 63:90 до 02:40 вс 90:27 5989 66"));
  EXPECT_TRUE(HasCardNumber("пн-пт с 6390 до 0240 вс 9027 5989 66"));
}
