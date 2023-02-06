#include <userver/utest/utest.hpp>

#include <db/format_query.hpp>

TEST(FormatQuery, Basic) {
  const storages::postgres::Query kSelectTemplated = {
      R"-(SELECT * FROM table_{postfix} WHERE x = $1)-",
      storages::postgres::Query::Name("select_templated"),
      storages::postgres::Query::LogMode::kFull,
  };

  const auto query = driver_metrics_storage::db::FormatQueryTemplate(
      kSelectTemplated, fmt::arg("postfix", "y2021m10"));
  ASSERT_EQ(std::string("SELECT * FROM table_y2021m10 WHERE x = $1"),
            query.Statement());
}
