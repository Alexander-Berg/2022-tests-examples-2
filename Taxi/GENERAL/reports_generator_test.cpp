#include <fstream>

#include <reports/reports_generator.hpp>
#include <taxi_config/taxi_config.hpp>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>

namespace eats_place_rating::reports::reports_generator {
std::string GenerateCSV(std::vector<models::ReportLine> report,
                        const std::string& timezone,
                        const dynamic_config::Snapshot& config);
}

namespace eats_place_rating::reports::reports_generator::tests {
void Save(std::string& content, std::string path) {
  std::ofstream outfile;
  outfile.open(path, std::ios_base::app);
  outfile << content;
}
TEST(GenerateCSV, Basic) {
  const auto source = dynamic_config::GetDefaultSource();
  const auto snapshot = source.GetSnapshot();

  auto content_empty =
      GenerateCSV(std::vector<models::ReportLine>{}, "Europe/Moscow", snapshot);

  constexpr char output_empty[] =
      "\xEF\xBB\xBF"
      "Address;Rating;Weight;Order nr;Created at;Custom comment;Predefined "
      "comments";

  EXPECT_EQ(content_empty, output_empty);

  const auto timestamp_1 =
      ::utils::datetime::Stringtime("2020-01-01T20:15:01Z", "UTC");
  const auto timestamp_2 =
      ::utils::datetime::Stringtime("2020-02-02T22:12:02Z", "UTC");
  const auto timestamp_3 =
      ::utils::datetime::Stringtime("2020-03-02T22:12:02Z", "UTC");

  std::vector<models::ReportLine> report = {
      models::ReportLine{
          {}, "address1", 4, 1, "123", timestamp_1, "my_comment", std::nullopt},
      models::ReportLine{{},
                         "address2",
                         5,
                         std::nullopt,
                         "321",
                         timestamp_2,
                         "'my' comment \"quotes\"",
                         "some1,some2"},
      models::ReportLine{{},
                         "address3",
                         1,
                         2,
                         "5632",
                         timestamp_3,
                         "njn comment\ttab",
                         "some1,some2,some3"},
  };

  auto content = GenerateCSV(std::move(report), "Europe/Moscow", snapshot);

  constexpr char output[] =
      "\xEF\xBB\xBF"
      "Address;Rating;Weight;Order nr;Created at;Custom comment;Predefined "
      "comments\r\n"
      "address1;4;1;123;2020-01-01T23:15:01+0300;my_comment;\r\n"
      "address2;5;;321;2020-02-03T01:12:02+0300;\"'my' comment "
      "\"\"quotes\"\"\";some1,some2\r\n"
      "address3;1;2;5632;2020-03-03T01:12:02+0300;\"njn "
      "comment\ttab\";some1,some2,some3";

  EXPECT_EQ(content, output);
}
TEST(GenerateCSV, ChangedColumnsConfig) {
  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::EATS_PLACE_RATING_XLS_REPORT_HEAD,
        {"Имя", "Адрес", "Оценка", "Вес в рейтинге", "Номер заказа",
         "Время создания отзыва", "Отзыв", "Предвыбранные комментарии"}}});
  const auto snapshot = storage.GetSnapshot();

  auto content_empty =
      GenerateCSV(std::vector<models::ReportLine>{}, "Europe/Moscow", snapshot);

  constexpr char output_empty[] =
      "\xEF\xBB\xBF"
      "Имя;Адрес;Оценка;Вес в рейтинге;Номер заказа;Время создания "
      "отзыва;Отзыв;Предвыбранные комментарии";

  EXPECT_EQ(content_empty, output_empty);

  const auto timestamp_1 =
      ::utils::datetime::Stringtime("2020-01-01T20:15:01Z", "UTC");
  const auto timestamp_2 =
      ::utils::datetime::Stringtime("2020-02-02T22:12:02Z", "UTC");
  const auto timestamp_3 =
      ::utils::datetime::Stringtime("2020-03-02T22:12:02Z", "UTC");

  std::vector<models::ReportLine> report = {
      models::ReportLine{"имя1", "address1", 4, 1, "123", timestamp_1,
                         "my_comment", std::nullopt},
      models::ReportLine{"имя1", "address2", 5, std::nullopt, "321",
                         timestamp_2, "'my' comment \"quotes\"", "some1,some2"},
      models::ReportLine{"имя2", "address3", 1, 2, "5632", timestamp_3,
                         "njn comment\ttab", "some1,some2,some3"},
  };

  auto content = GenerateCSV(std::move(report), "Europe/Moscow", snapshot);
  // Save(content, "report_new.csv");

  constexpr char output[] =
      "\xEF\xBB\xBF"
      "Имя;Адрес;Оценка;Вес в рейтинге;Номер заказа;Время создания "
      "отзыва;Отзыв;Предвыбранные комментарии\r\n"
      "имя1;address1;4;1;123;2020-01-01T23:15:01+0300;my_comment;\r\n"
      "имя1;address2;5;;321;2020-02-03T01:12:02+0300;\"'my' comment "
      "\"\"quotes\"\"\";some1,some2\r\n"
      "имя2;address3;1;2;5632;2020-03-03T01:12:02+0300;\"njn "
      "comment\ttab\";some1,some2,some3";

  EXPECT_EQ(content, output);
}

}  // namespace eats_place_rating::reports::reports_generator::tests
