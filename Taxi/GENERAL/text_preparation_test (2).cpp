#include <userver/utest/utest.hpp>

#include "text_preparation.hpp"

const std::string kUnicodeWhitespaces =
    "\x20\xe1\x9a\x80\xe2\x80\x80\xe2\x80\x81\xe2\x80\x82\xe2\x80\x83\xe2\x80"
    "\x84\xe2\x80\x85\xe2\x80\x86\xe2\x80\x88\xe2\x80\x89\xe2\x80\x8a\xe2\x81"
    "\x9f\xe3\x80\x80\xe2\x80\xa8\xe2\x80\xa9\x09\x0a\x0b\x0c\x0d";

TEST(TextPreparation, MakeLower) {
  using utils::text::MakeLower;

  EXPECT_EQ(MakeLower(" ABC fd  "), " abc fd  ");
  EXPECT_EQ(MakeLower("  AB   і C  fd  "), "  ab   і c  fd  ");
  EXPECT_EQ(MakeLower("   ABCfd  "), "   abcfd  ");
  EXPECT_EQ(MakeLower("abcd"), "abcd");
  EXPECT_EQ(MakeLower("ABCD"), "abcd");
  EXPECT_EQ(std::string(""), MakeLower(""));
}

TEST(TextPreparation, MakeUpper) {
  using utils::text::MakeUpper;

  EXPECT_EQ(MakeUpper(" ABC fd  "), " ABC FD  ");
  EXPECT_EQ(MakeUpper("  AB   i C  fd  "), "  AB   I C  FD  ");
  EXPECT_EQ(MakeUpper("   ABCfd  "), "   ABCFD  ");
  EXPECT_EQ(MakeUpper("abcd"), "ABCD");
  EXPECT_EQ(MakeUpper("ABCD"), "ABCD");
  EXPECT_EQ(std::string(""), MakeUpper(""));
}

TEST(TextPreparation, RemoveWhitespaces) {
  const auto& kWs = kUnicodeWhitespaces;
  using utils::text::RemoveWhitespaces;

  EXPECT_EQ(RemoveWhitespaces(" ABC fd  "), "ABCfd");
  EXPECT_EQ(RemoveWhitespaces("  AB   і C  fd  "), "ABіCfd");
  EXPECT_EQ(RemoveWhitespaces("   ABCfd  "), "ABCfd");
  EXPECT_EQ(std::string(""), RemoveWhitespaces(kWs));
  EXPECT_EQ(std::string("ab"), RemoveWhitespaces(kWs + "a" + kWs + "b" + kWs));
  EXPECT_EQ(std::string("אגamaמ"),
            RemoveWhitespaces("א" + kWs + "ג" + kWs + "ama" + "  מ"));
}

TEST(TextPreparation, TrimWhitespaces) {
  const auto& kWs = kUnicodeWhitespaces;
  using utils::text::TrimWhitespaces;

  EXPECT_EQ(TrimWhitespaces(" ABC fd  "), "ABC fd");
  EXPECT_EQ(TrimWhitespaces("ABC fd"), "ABC fd");
  EXPECT_EQ(TrimWhitespaces("   ABCfd  "), "ABCfd");
  EXPECT_EQ(std::string(""), TrimWhitespaces(kWs));
  EXPECT_EQ(std::string("a" + kWs + "b"),
            TrimWhitespaces(kWs + "a" + kWs + "b" + kWs));
}
