#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/datetime/date.hpp>
#include <userver/utils/mock_now.hpp>

#include <taxi_config/variables/BANK_APPLICATIONS_DATA_VALIDATION_PARAMETERS.hpp>

#include "validators.hpp"

namespace form_validators::tests {

TEST(TestOperator, FormDataValidation) {
  EXPECT_EQ(validators::NormalizeName("", "-"), "");
  EXPECT_EQ(validators::NormalizeName("          ", "-"), "");
  EXPECT_EQ(validators::NormalizeName("      ", "-"), "      ");
  EXPECT_EQ(validators::NormalizeName("   Анна ", "-"), "   Анна");
  EXPECT_EQ(validators::NormalizeName("\n\t Анна ", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName("Анна \n\t", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName("анна", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName(" анна", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName("\nанна", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName("\tанна", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName("   анна", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName("\t\t\tанна", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName("\n\n\nанна", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName("\t\n анна", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName(" анна ", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName("анна   ", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName("анна\t", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName("анна\n", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName("анна\n\n\n", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName("анна\t\t\t", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName("анна \n\t", "-"), "Анна");
  EXPECT_EQ(validators::NormalizeName("ан на", "-"), "Ан на");
  EXPECT_EQ(validators::NormalizeName("-анна", "-"), "-Анна");
  EXPECT_EQ(validators::NormalizeName("-анна ", "-"), "-Анна");
  EXPECT_EQ(validators::NormalizeName("анна-мария ", "-"), "Анна-Мария");
  EXPECT_EQ(validators::NormalizeName("анна--мария", "-"), "Анна-Мария");
  EXPECT_EQ(validators::NormalizeName(" анна----мария", "-"), "Анна-Мария");
  EXPECT_EQ(validators::NormalizeName("анна мария", "-"), "Анна мария");
  EXPECT_EQ(validators::NormalizeName("анна   мария", "-"), "Анна   мария");
  EXPECT_EQ(validators::NormalizeName("анна ??мария", "-"), "Анна ??мария");
  EXPECT_EQ(validators::NormalizeName("??анна мария?", "-"), "??анна мария?");
  EXPECT_EQ(validators::NormalizeName("ан%а-мария", "-"), "Ан%а-Мария");
  EXPECT_EQ(validators::NormalizeName("Анна-мария", "-"), "Анна-Мария");
  EXPECT_EQ(validators::NormalizeName("   Анна--мария", "-"), "Анна-Мария");
  EXPECT_EQ(validators::NormalizeName("анна--Мария", "-"), "Анна-Мария");
  EXPECT_EQ(validators::NormalizeName("анна--Мария", "-"), "Анна-Мария");
  EXPECT_EQ(validators::NormalizeName("Анна-Мария", "-"), "Анна-Мария");
  EXPECT_EQ(validators::NormalizeName("ИВАН", "-"), "Иван");
  EXPECT_EQ(validators::NormalizeName("ИвАн", "-"), "Иван");
  EXPECT_EQ(validators::NormalizeName("ИвАН", "-"), "Иван");
  EXPECT_EQ(validators::NormalizeName(" ива: ", "-"), "Ива:");
  EXPECT_EQ(validators::NormalizeName("ив:н", "-"), "Ив:н");
  EXPECT_EQ(validators::NormalizeName("Иван оглы", " "), "Иван оглы");
  EXPECT_EQ(validators::NormalizeName("Иван   оглы", " "), "Иван оглы");
  EXPECT_EQ(validators::NormalizeName("Иван : оглы", " "), "Иван : оглы");
  EXPECT_EQ(validators::NormalizeName("анна- Мария", "- "), "Анна-Мария");
  EXPECT_EQ(validators::NormalizeName("анна -Мария", "- "), "Анна Мария");
  EXPECT_EQ(validators::NormalizeName("Леонардо да Винчи", "- "),
            "Леонардо да Винчи");
  EXPECT_EQ(validators::NormalizeName("Леонардо Да Винчи", "- "),
            "Леонардо Да Винчи");

  EXPECT_EQ(validators::NormalizeNumber("123"), "123");
  EXPECT_EQ(validators::NormalizeNumber("123   "), "123");
  EXPECT_EQ(validators::NormalizeNumber("123   "), "123   ");
  EXPECT_EQ(validators::NormalizeNumber("   123"), "123");
  EXPECT_EQ(validators::NormalizeNumber("   123"), "   123");
  EXPECT_EQ(validators::NormalizeNumber("1 23"), "1 23");
  EXPECT_EQ(validators::NormalizeNumber("123\n\n\n"), "123");
  EXPECT_EQ(validators::NormalizeNumber("\n\n\n123"), "123");
  EXPECT_EQ(validators::NormalizeNumber("123\n\n\n"), "123");
  EXPECT_EQ(validators::NormalizeNumber("123\t\t"), "123");
  EXPECT_EQ(validators::NormalizeNumber("123\n\n\n"), "123");
  EXPECT_EQ(validators::NormalizeNumber("123  $#"), "123$#");
  EXPECT_EQ(validators::NormalizeNumber(";*12  3"), ";*123");
  EXPECT_EQ(validators::NormalizeNumber("@#$@#1#$@23#@$@#"),
            "@#$@#1#$@23#@$@#");
  EXPECT_EQ(validators::NormalizeNumber("#$@#$@@fopjwgf"), "#$@#$@@fopjwgf");
  EXPECT_EQ(validators::NormalizeNumber("          "), "");
  EXPECT_EQ(validators::NormalizeNumber("      "), "      ");

  utils::datetime::MockNowSet(utils::datetime::Date(2022, 3, 28).GetSysDays());

  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto passport_length =
      config[taxi_config::BANK_APPLICATIONS_DATA_VALIDATION_PARAMETERS]
          .passport_length;
  const auto snils_length =
      config[taxi_config::BANK_APPLICATIONS_DATA_VALIDATION_PARAMETERS]
          .snils_length;
  const auto inn_length =
      config[taxi_config::BANK_APPLICATIONS_DATA_VALIDATION_PARAMETERS]
          .inn_length;
  const auto max_name_length =
      config[taxi_config::BANK_APPLICATIONS_DATA_VALIDATION_PARAMETERS]
          .max_name_length;
  const auto max_summary_name_length =
      config[taxi_config::BANK_APPLICATIONS_DATA_VALIDATION_PARAMETERS]
          .max_summary_name_length;
  const auto min_valid_age =
      config[taxi_config::BANK_APPLICATIONS_DATA_VALIDATION_PARAMETERS]
          .min_valid_age;
  const auto max_valid_age =
      config[taxi_config::BANK_APPLICATIONS_DATA_VALIDATION_PARAMETERS]
          .max_valid_age;

  EXPECT_EQ(
      validators::CheckName(
          max_name_length,
          "Ббббббббббббббббббббббббббббббббббббббббббббббббббббббббббббб", "- ")
          .value(),
      "Name is too long");
  EXPECT_EQ(
      validators::CheckName(
          max_name_length,
          "Бббббббббббббббббббббббббббббббббббббббббббббббббббббббббббббб",
          "- ")
          .value(),
      "Name is too long");
  EXPECT_EQ(validators::CheckName(max_name_length, "", "-").value(),
            "String is empty");
  EXPECT_EQ(validators::CheckName(max_name_length, "АннА-Мария", "-").value(),
            "Upper symbol inside string");
  EXPECT_EQ(validators::CheckName(max_name_length, "ИвАн", "-").value(),
            "Upper symbol inside string");
  EXPECT_EQ(validators::CheckName(max_name_length, "ИваН", "-").value(),
            "Upper symbol inside string");
  EXPECT_EQ(validators::CheckName(max_name_length, "Анна--Мария", "-").value(),
            "Adjacent special chars");
  EXPECT_EQ(validators::CheckName(max_name_length, "Иван  оглы", " ").value(),
            "Adjacent special chars");
  EXPECT_EQ(validators::CheckName(max_name_length, "Иван оглы  ", " ").value(),
            "Adjacent special chars");
  EXPECT_EQ(validators::CheckName(max_name_length, "И---------", "-").value(),
            "Adjacent special chars");
  EXPECT_EQ(validators::CheckName(max_name_length, "Анна-мария", "-").value(),
            "Not upper symbol after hyphen");
  EXPECT_EQ(validators::CheckName(max_name_length, "Егор-ка", "-").value(),
            "Not upper symbol after hyphen");
  EXPECT_EQ(validators::CheckName(max_name_length, "Егор-к", "-").value(),
            "Not upper symbol after hyphen");
  EXPECT_EQ(validators::CheckName(max_name_length, "-Иван", "-").value(),
            "First symbol is not upper cyrillic");
  EXPECT_EQ(validators::CheckName(max_name_length, "Ivan", "-").value(),
            "First symbol is not upper cyrillic");
  EXPECT_EQ(validators::CheckName(max_name_length, "Iван", "-").value(),
            "First symbol is not upper cyrillic");
  EXPECT_EQ(validators::CheckName(max_name_length, " ", "- ").value(),
            "First symbol is not upper cyrillic");
  EXPECT_EQ(validators::CheckName(max_name_length, "    ", "- ").value(),
            "First symbol is not upper cyrillic");
  EXPECT_EQ(validators::CheckName(max_name_length, "-", "-").value(),
            "First symbol is not upper cyrillic");
  EXPECT_EQ(validators::CheckName(max_name_length, "--", "-").value(),
            "First symbol is not upper cyrillic");
  EXPECT_EQ(validators::CheckName(max_name_length, "----------", "-").value(),
            "First symbol is not upper cyrillic");
  EXPECT_EQ(validators::CheckName(max_name_length, "иван", "-").value(),
            "First symbol is not upper cyrillic");
  EXPECT_EQ(validators::CheckName(max_name_length, "1111", "-").value(),
            "First symbol is not upper cyrillic");
  EXPECT_EQ(validators::CheckName(max_name_length, "Иван-", "-").value(),
            "Invalid last symbol");
  EXPECT_EQ(validators::CheckName(max_name_length, "Ива%", "-").value(),
            "Invalid symbol inside string");
  EXPECT_EQ(validators::CheckName(max_name_length, "Ива!", "-").value(),
            "Invalid symbol inside string");
  EXPECT_EQ(validators::CheckName(max_name_length, "Ива#", "-").value(),
            "Invalid symbol inside string");
  EXPECT_EQ(validators::CheckName(max_name_length, "Ива;", "-").value(),
            "Invalid symbol inside string");
  EXPECT_EQ(validators::CheckName(max_name_length, "Ива&", "-").value(),
            "Invalid symbol inside string");
  EXPECT_EQ(validators::CheckName(max_name_length, "Ива4", "-").value(),
            "Invalid symbol inside string");
  EXPECT_EQ(validators::CheckName(max_name_length, "Ив4н", "-").value(),
            "Invalid symbol inside string");
  EXPECT_EQ(validators::CheckName(max_name_length, "Иvan", "-").value(),
            "Invalid symbol inside string");
  EXPECT_EQ(validators::CheckName(max_name_length, "Ив%н", "-").value(),
            "Invalid symbol inside string");
  EXPECT_EQ(validators::CheckName(max_name_length, "Ив$н", "-").value(),
            "Invalid symbol inside string");
  EXPECT_EQ(validators::CheckName(max_name_length, "Ив^н", "-").value(),
            "Invalid symbol inside string");
  EXPECT_EQ(validators::CheckName(max_name_length, "Ив*н", "-").value(),
            "Invalid symbol inside string");
  EXPECT_EQ(validators::CheckSummaryNameLength(
                max_summary_name_length,
                "аааа-aaaa-aaaa-aaaa-aaaaаааа-aaaa-aaaa-aaaa-aaaaaaaa-aaaa-"
                "aaaa-aaaa-aaaa",
                "aaaa-aaaa-aaaa-aaaa-aaaaаааа-aaaa-aaaa-aaaa-aaaaаааа-aaaa-"
                "aaaa-aaaa-aaaa",
                "а"),
            false);
  EXPECT_EQ(validators::CheckSummaryNameLength(
                max_summary_name_length,
                "аааа-aaaa-aaaa-aaaa-aaaaаааа-aaaa-aaaa-aaaa-aaaaaaaa-aaaa-"
                "aaaa-aaaa-aaaa",
                "aaaa-aaaa-aaaa-aaaa-aaaaаааа-aaaa-aaaa-aaaa-aaaaаааа-aaaa-"
                "aaaa-aaaa-aaaaааааа",
                std::nullopt),
            false);
  EXPECT_EQ(validators::CheckSummaryNameLength(
                max_summary_name_length,
                "аааа-aaaa-aaaa-aaaa-aaaaаааа-aaaa-aaaa-aaaa-aaaaaaaa-aaaa-"
                "aaaa-aaaa-aaaa",
                "aaaa-aaaa-aaaa-aaaa-aaaaаааа-aaaa-aaaa-aaaa-aaaaаааа-aaaa-"
                "aaaa-aaaa-aaaa",
                "аааааааааа"),
            false);

  EXPECT_EQ(validators::CheckName(max_name_length, "Петров Петр", "- "),
            std::nullopt);
  EXPECT_EQ(validators::CheckName(max_name_length, "Артём", "-"), std::nullopt);
  EXPECT_EQ(validators::CheckName(max_name_length, "Ёж", "-"), std::nullopt);
  EXPECT_EQ(validators::CheckName(max_name_length, "Анна-А", "-"),
            std::nullopt);
  EXPECT_EQ(validators::CheckName(max_name_length, "Анна-Ан", "-"),
            std::nullopt);
  EXPECT_EQ(
      validators::CheckName(
          max_name_length,
          "Бббббббббббббббббббббббббббббббббббббббббббббббббббббббббббб", "-"),
      std::nullopt);
  EXPECT_EQ(validators::CheckName(max_name_length, "Анна-Мария", "-"),
            std::nullopt);
  EXPECT_EQ(validators::CheckName(max_name_length, "Иван оглы", " "),
            std::nullopt);
  EXPECT_EQ(validators::CheckName(max_name_length, "Иван оглы а", " "),
            std::nullopt);
  EXPECT_EQ(validators::CheckName(max_name_length, "Иван Оглы", " "),
            std::nullopt);
  EXPECT_EQ(validators::CheckName(max_name_length, "Леонардо Да Винчи", "- "),
            std::nullopt);
  EXPECT_EQ(validators::CheckName(max_name_length, "Леонардо да Винчи", "- "),
            std::nullopt);
  EXPECT_EQ(validators::CheckSummaryNameLength(max_summary_name_length, "аааа",
                                               "aaaa", "aaaa"),
            true);
  EXPECT_EQ(
      validators::CheckSummaryNameLength(max_summary_name_length, "", "", ""),
      true);
  EXPECT_EQ(validators::CheckSummaryNameLength(max_summary_name_length, "", "",
                                               std::nullopt),
            true);
  EXPECT_EQ(validators::CheckSummaryNameLength(
                max_summary_name_length,
                "аааа-aaaa-aaaa-aaaa-aaaaаааа-aaaa-aaaa-aaaa-aaaa",
                "aaaa-aaaa-aaaa-aaaa-aaaaаааа-aaaa-aaaa-aaaa-aaaa",
                "aaaa-aaaa-aaaa-aaaa-aaaaаааа-aaaa-aaaa-aaaa-aaaa"),
            true);
  EXPECT_EQ(
      validators::CheckSummaryNameLength(
          max_summary_name_length,
          "аааа-aaaa-aaaa-aaaa-aaaaаааа-aaaa-aaaa-aaaa-aaaaaaaa-aaaa-aaaa-aaaa-"
          "aaaaаааа-aaaa-aaaa-aaaa-aaaa",
          "aaaa-aaaa-aaaa-aaaa-aaaaаааа-aaaa-aaaa-aaaa-aaaa", std::nullopt),
      true);

  EXPECT_EQ(validators::CheckPassport(passport_length, "").value(),
            "Invalid length");
  EXPECT_EQ(validators::CheckPassport(passport_length, "1").value(),
            "Invalid length");
  EXPECT_EQ(
      validators::CheckPassport(passport_length, "11111111111111").value(),
      "Invalid length");
  EXPECT_EQ(validators::CheckPassport(passport_length, "1bcdefghij").value(),
            "Only digits are possible");
  EXPECT_EQ(validators::CheckPassport(passport_length, "абвг22").value(),
            "Only digits are possible");
  EXPECT_EQ(validators::CheckPassport(passport_length, "абвгд").value(),
            "Only digits are possible");
  EXPECT_EQ(validators::CheckPassport(passport_length, "1111 11111").value(),
            "Only digits are possible");
  EXPECT_EQ(validators::CheckPassport(passport_length, "111111111%").value(),
            "Only digits are possible");

  EXPECT_EQ(validators::CheckPassport(passport_length, "1111111111"),
            std::nullopt);

  EXPECT_EQ(validators::CheckSnils(snils_length, "").value(), "Invalid length");
  EXPECT_EQ(validators::CheckSnils(snils_length, "1").value(),
            "Invalid length");
  EXPECT_EQ(validators::CheckSnils(snils_length, "11111111111111").value(),
            "Invalid length");
  EXPECT_EQ(validators::CheckSnils(snils_length, "00111111111").value(),
            "First zeros");
  EXPECT_EQ(validators::CheckSnils(snils_length, "1bcdefghij1").value(),
            "Only digits are possible");
  EXPECT_EQ(validators::CheckSnils(snils_length, "эёщзг1").value(),
            "Only digits are possible");
  EXPECT_EQ(validators::CheckSnils(snils_length, "33333333333").value(),
            "Invalid checksum");
  EXPECT_EQ(validators::CheckSnils(snils_length, "07169439996").value(),
            "Invalid checksum");

  EXPECT_EQ(validators::CheckSnils(snils_length, "07169439995"), std::nullopt);

  EXPECT_EQ(validators::CheckInn(inn_length, "").value(), "Invalid length");
  EXPECT_EQ(validators::CheckInn(inn_length, "1").value(), "Invalid length");
  EXPECT_EQ(validators::CheckInn(inn_length, "11111111111111").value(),
            "Invalid length");
  EXPECT_EQ(validators::CheckInn(inn_length, "002222222222").value(),
            "First zeros");
  EXPECT_EQ(validators::CheckInn(inn_length, "2bcdefghij11").value(),
            "Only digits are possible");
  EXPECT_EQ(validators::CheckInn(inn_length, "юъшщцй").value(),
            "Only digits are possible");
  EXPECT_EQ(validators::CheckInn(inn_length, "444444444444").value(),
            "Invalid checksum");
  EXPECT_EQ(validators::CheckInn(inn_length, "564264570532").value(),
            "Invalid checksum");

  EXPECT_EQ(validators::CheckInn(inn_length, "564264570531"), std::nullopt);

  const auto kMinValidAgeFormatString =
      fmt::format("Age is less than {} years", min_valid_age);
  const auto kMaxValidAgeFormatString =
      fmt::format("Age is greater than {} years", max_valid_age);

  EXPECT_EQ(validators::CheckBirthday(min_valid_age, max_valid_age,
                                      utils::datetime::Date(2022, 3, 1))
                .value(),
            kMinValidAgeFormatString);
  EXPECT_EQ(validators::CheckBirthday(min_valid_age, max_valid_age,
                                      utils::datetime::Date(2500, 1, 1))
                .value(),
            kMinValidAgeFormatString);
  EXPECT_EQ(validators::CheckBirthday(min_valid_age, max_valid_age,
                                      utils::datetime::Date(2004, 3, 29))
                .value(),
            kMinValidAgeFormatString);
  EXPECT_EQ(validators::CheckBirthday(min_valid_age, max_valid_age,
                                      utils::datetime::Date(2004, 3, 28))
                .value(),
            kMinValidAgeFormatString);
  EXPECT_EQ(validators::CheckBirthday(min_valid_age, max_valid_age,
                                      utils::datetime::Date(2122, 3, 28))
                .value(),
            kMinValidAgeFormatString);
  EXPECT_EQ(validators::CheckBirthday(min_valid_age, max_valid_age,
                                      utils::datetime::Date(1922, 3, 28))
                .value(),
            kMaxValidAgeFormatString);
  EXPECT_EQ(validators::CheckBirthday(min_valid_age, max_valid_age,
                                      utils::datetime::Date(1700, 1, 1))
                .value(),
            kMaxValidAgeFormatString);

  EXPECT_EQ(validators::CheckBirthday(min_valid_age, max_valid_age,
                                      utils::datetime::Date(2000, 1, 1)),
            std::nullopt);
  EXPECT_EQ(validators::CheckBirthday(min_valid_age, max_valid_age,
                                      utils::datetime::Date(2004, 3, 27)),
            std::nullopt);
  EXPECT_EQ(validators::CheckBirthday(min_valid_age, max_valid_age,
                                      utils::datetime::Date(1922, 3, 29)),
            std::nullopt);
}

}  // namespace form_validators::tests
