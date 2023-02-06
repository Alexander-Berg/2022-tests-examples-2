#include <gtest/gtest.h>

#include "text_preparation.hpp"

const std::string kUnicodeWhitespaces =
    u8"\x20\xe1\x9a\x80\xe2\x80\x80\xe2\x80\x81\xe2\x80\x82\xe2\x80\x83\xe2\x80"
    u8"\x84\xe2\x80\x85\xe2\x80\x86\xe2\x80\x88\xe2\x80\x89\xe2\x80\x8a\xe2\x81"
    u8"\x9f\xe3\x80\x80\xe2\x80\xa8\xe2\x80\xa9\x09\x0a\x0b\x0c\x0d";

TEST(TextPreparation, RemoveWhitespaces) {
  using utils::RemoveWhitespaces;
  const auto& kWs = kUnicodeWhitespaces;
  EXPECT_EQ(RemoveWhitespaces(" ABC fd  "), "ABCfd");
  EXPECT_EQ(RemoveWhitespaces("  AB   і C  fd  "), "ABіCfd");
  EXPECT_EQ(RemoveWhitespaces("   ABCfd  "), "ABCfd");
  EXPECT_EQ(std::string(""), RemoveWhitespaces(kWs));
  EXPECT_EQ(std::string("ab"), RemoveWhitespaces(kWs + "a" + kWs + "b" + kWs));
  EXPECT_EQ(std::string("אגamaמ"),
            RemoveWhitespaces("א" + kWs + "ג" + kWs + "ama" + "  מ"));
}

TEST(TextPreparation, TrimWhitespaces) {
  using utils::TrimWhitespaces;
  const auto& kWs = kUnicodeWhitespaces;
  EXPECT_EQ(TrimWhitespaces(" ABC fd  "), "ABC fd");
  EXPECT_EQ(TrimWhitespaces("ABC fd"), "ABC fd");
  EXPECT_EQ(TrimWhitespaces("   ABCfd  "), "ABCfd");
  EXPECT_EQ(std::string(""), TrimWhitespaces(kWs));
  EXPECT_EQ(std::string("a" + kWs + "b"),
            TrimWhitespaces(kWs + "a" + kWs + "b" + kWs));
}

TEST(TextPreparation, MakeAsDocumentNumber) {
  using utils::MakeAsDocumentNumber;
  EXPECT_EQ("ABCEHKMOPTXY", MakeAsDocumentNumber(u8"АВСЕНКМОРТХУ"));
  EXPECT_EQ("Y123Y", MakeAsDocumentNumber(u8"У123Y"));
  EXPECT_EQ("Y123Y", MakeAsDocumentNumber(u8"Y123У"));
  EXPECT_EQ("1Y2Y3", MakeAsDocumentNumber(u8"1Y2У3"));
  EXPECT_EQ("HBAA123124", MakeAsDocumentNumber(u8"нвAA123124"));
  EXPECT_EQ("HBAA123124", MakeAsDocumentNumber(u8"нвaa123124"));
  EXPECT_EQ("HPTCCMM", MakeAsDocumentNumber(u8"нртCCмм"));
  EXPECT_EQ(u8"ЯЯ", MakeAsDocumentNumber(u8"яЯ"));
}

TEST(TextPreparation, MakeNormalizationForKey) {
  const std::string kTestKey =
      u8"^ абвгдеёжзийклмнопрстуфхцчшщъыьэюя"   //
      u8"   abcdefghijklmnopqrstuvwxyz  %"      //
      u8"   ABCDEFGHIJKLMNOPQRSTUVWXYZ "        //
      u8"  АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ "  //
      u8" 01 2  3   456789 */ ";
  const std::string kExpectedKey =
      "ABBGDEEZH3IIKLMH0PPCTYFXCCHSHSCHJIJEYUYA"  //
      "ABCDEFGHIJKLMN0PQRSTUVWXYZ"                //
      "ABCDEFGHIJKLMN0PQRSTUVWXYZ"                //
      "ABBGDEEZH3IIKLMH0PPCTYFXCCHSHSCHJIJEYUYA"  //
      "0123456789";
  EXPECT_EQ(kExpectedKey, utils::MakeNormalizationForKey(kTestKey));
}

TEST(TextPreparation, CheckIfFormatAllowed) {
  using utils::CheckIfFormatAllowed;
  EXPECT_EQ(true, CheckIfFormatAllowed(u8"Э228ЭЭ750", {"L111LL111", "shit"}));
  EXPECT_EQ(true, CheckIfFormatAllowed(u8"ЭЭЭЭЭЭ", {"L111LL111", "QWERTY"}));
  EXPECT_EQ(true, CheckIfFormatAllowed(u8"1-2-3-4", {"L111LL111", "4-3-1-2"}));
  EXPECT_EQ(false, CheckIfFormatAllowed(u8"1-2-3-4", {"C", "L"}));
  EXPECT_EQ(true, CheckIfFormatAllowed(u8"----", {"L111LL111", "----"}));
  EXPECT_EQ(false, CheckIfFormatAllowed(u8"1234", {"AAAA"}));
  EXPECT_EQ(false, CheckIfFormatAllowed(u8"----", {"C", "W"}));
  EXPECT_EQ(true, CheckIfFormatAllowed(u8"1-Ъ-2-Ю", {"0-X-0-X", "shit"}));
  EXPECT_EQ(false, CheckIfFormatAllowed(u8"1-Ъ-2-Ю", {"0-X-0-X-", "shit"}));
}

TEST(TextPreparation, CheckIfCharsAllowed) {
  using utils::CheckIfCharsAllowed;
  EXPECT_EQ(true, CheckIfCharsAllowed(u8"абв", {L'а', L'б', L'в'}));
  EXPECT_EQ(false, CheckIfCharsAllowed(u8"абвд", {L'а', L'б', L'в'}));
  EXPECT_EQ(true,
            CheckIfCharsAllowed(u8"аааааааааааааббббббббббб", {L'а', L'б'}));
}
