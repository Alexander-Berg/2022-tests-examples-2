#include <userver/utest/utest.hpp>

#include "check_card_number.hpp"

TEST(DriverProfileValidatorsTest, HasCardNumber) {
  using utils::validators::HasCardNumber;

  EXPECT_FALSE(HasCardNumber("043601607#40817810254409357320#A331#LAZAREV"));
  EXPECT_TRUE(HasCardNumber("6390 0240 9027 5989 66"));
  EXPECT_TRUE(HasCardNumber("Card with 19 digits: 6390 0240 9027 5989 657"));
  EXPECT_FALSE(HasCardNumber("6390 0240 9027 5989"));
  EXPECT_TRUE(HasCardNumber("5336a6900a6144a4321  Sergeevich"));
  EXPECT_TRUE(HasCardNumber("5469700013493448 sber"));
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
  EXPECT_TRUE(HasCardNumber("Карта с 19 цифрами: 6390 0240 9027 5989 657"));
  EXPECT_FALSE(HasCardNumber("6390 0240 9027 5989"));
  EXPECT_TRUE(HasCardNumber("5336a6900a6144a4321  Сергеевич"));
  EXPECT_TRUE(HasCardNumber("5469700013493448 сбер"));
  EXPECT_TRUE(HasCardNumber("5469700013493448"));
  EXPECT_TRUE(HasCardNumber("1234 5469-7000-1349-3448 сбер"));
  EXPECT_TRUE(HasCardNumber("1234 5469    -   7000-1349-3448 сбер"));
  EXPECT_FALSE(HasCardNumber("1234 5469 это 7000-1349-3448 сбер"));
  EXPECT_FALSE(HasCardNumber("1234 5469 а это 7000-1349-3448 нет"));
  EXPECT_FALSE(HasCardNumber("1234 5469-7000-1349-3449 Ne korektnii сбер"));
  EXPECT_FALSE(
      HasCardNumber("Разбивка долга 6000 с 22.11/ разбивка долга 4000"
                    " 16 дней по 250/Разбивка долга 6250/ 250 на 25 "
                    "дней "));
  EXPECT_TRUE(
      HasCardNumber("Разбивка долга 6000 с 22.11 4000 16  250 6250 250 "
                    "на 25 дней "));
}
