#include <algorithm>
#include <fstream>
#include <string>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>

#include <taxi_config/variables/EATS_PLACE_RATING_XLS_REPORT_HEAD.hpp>
#include <utils/xls/document.hpp>

namespace eats_place_rating::utils::xls {
std::string XlsTitle(const std::string name);
}

TEST(GenerateXLS, Title) {
  EXPECT_EQ(
      eats_place_rating::utils::xls::XlsTitle("Баррикадная улица, 2/1c/1"),
      "Баррикадная улиц");
  EXPECT_EQ(
      eats_place_rating::utils::xls::XlsTitle("Русскийтекстбезоднобайтных"),
      "Русскийтекстбез");
  EXPECT_EQ(
      eats_place_rating::utils::xls::XlsTitle("1Русскийтекстсоднобайтным"),
      "1Русскийтекстсод");
  EXPECT_EQ(eats_place_rating::utils::xls::XlsTitle("😊😣👽😎😊😣👽😎😊😣👽😎"), "😊😣👽😎😊😣👽");
}
TEST(GenerateXLS, TitleLong) {
  std::string address = {"12345678910111213141516171819202122232425262728"};
  std::string title = eats_place_rating::utils::xls::XlsTitle(address);
  ASSERT_EQ(title.length(), 31);
}

void Save(std::string& content, std::string path) {
  std::ofstream outfile;
  outfile.open(path, std::ios_base::app);
  outfile << content;
}
TEST(GenerateXLS, SheetByAddress) {
  const auto storage = dynamic_config::GetDefaultSource();
  auto user_timezone = "Europe/Moscow";
  auto taxi_config = storage.GetSnapshot();

  const auto t1 = ::utils::datetime::Stringtime("2020-01-01T20:15:01Z", "UTC");
  const auto t2 = ::utils::datetime::Stringtime("2020-02-02T22:12:02Z", "UTC");
  const auto t3 = ::utils::datetime::Stringtime("2020-03-02T22:12:02Z", "UTC");

  std::vector<::eats_place_rating::models::ReportLine> report = {
      ::eats_place_rating::models::ReportLine{{},
                                              "Баррикадная улица, 2/1c/1",
                                              4,
                                              1,
                                              "123",
                                              t1,
                                              "my_comment",
                                              std::nullopt},
      ::eats_place_rating::models::ReportLine{
          {},
          "length of this line more than allowed at xls title",
          5,
          std::nullopt,
          "321",
          t2,
          "my comment \"quotes\"",
          "some1,some2"},
      ::eats_place_rating::models::ReportLine{
          {},
          "length of this line more than allowed at xls title",
          1,
          2,
          "5632",
          t3,
          "njn comment\ttab",
          "some1,some2,some3"},
  };
  auto content =
      ::eats_place_rating::utils::xls::Document{taxi_config, user_timezone}
          .Generate(std::move(report));
  // Save(content, "report_old.xls");
}
TEST(GenerateXLS, ChangedColumnsConfig) {
  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::EATS_PLACE_RATING_XLS_REPORT_HEAD,
        {"Имя", "Адрес", "Оценка", "Вес в рейтинге", "Номер заказа",
         "Время создания отзыва", "Отзыв", "Предвыбранные комментарии"}}});
  auto user_timezone = "Europe/Moscow";
  auto taxi_config = storage.GetSnapshot();

  const auto t1 = ::utils::datetime::Stringtime("2020-01-01T20:15:01Z", "UTC");
  const auto t2 = ::utils::datetime::Stringtime("2020-02-02T22:12:02Z", "UTC");
  const auto t3 = ::utils::datetime::Stringtime("2020-03-02T22:12:02Z", "UTC");

  std::vector<::eats_place_rating::models::ReportLine> report = {
      ::eats_place_rating::models::ReportLine{
          "Имя 1", "Баррикадная улица, 2/1c/1", 4, 1, "123", t1, "my_comment",
          std::nullopt},
      ::eats_place_rating::models::ReportLine{
          "Имя 1", "Баррикадная улица, 2/1c/1", 5, std::nullopt, "321", t2,
          "my comment \"quotes\"", "some1,some2"},
      ::eats_place_rating::models::ReportLine{
          "Имя 2", "Другая улица, 2/1c/1", 1, 2, "5632", t3, "njn comment\ttab",
          "some1,some2,some3"},
  };
  auto content =
      ::eats_place_rating::utils::xls::Document{taxi_config, user_timezone}
          .Generate(std::move(report));
  // Save(content, "report_new.xls");
}
