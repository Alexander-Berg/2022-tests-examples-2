#include <gtest/gtest.h>

#include <boost/regex.hpp>

#include <boost/algorithm/string.hpp>

#include <db/query/builder.hpp>
#include <stdexcept>
#include "db/query/filter.hpp"

namespace db::query {

namespace {

std::string FormatQuery(const std::string& query) {
  boost::regex re("[\\s]+");
  auto single_spaced = boost::regex_replace(query, re, " ");
  return boost::algorithm::trim_copy(single_spaced);
}

void CheckQueriesEqual(const std::string& lhs, const std::string& rhs) {
  EXPECT_EQ(FormatQuery(lhs), FormatQuery(rhs));
}

ColumnValueValidator DefaultValidator() {
  return {"0123456789abcdefghijklmnopqrstuvwxyz _+-:"};
}

}  // namespace

TEST(TestColumnValueValidator, Simple) {
  auto validator = ColumnValueValidator("abacaba-123");

  const std::vector<std::pair<std::string, bool>> inputs = {
      {"", true},         {"abc-123", true},  {"---123abcba321---", true},
      {"abc+123", false}, {"abc 123", false}, {"xyz-123", false},
      {"ABC-123", false},
  };

  for (const auto& [input, expected_is_valid] : inputs) {
    EXPECT_EQ(validator.IsValueValid(input), expected_is_valid);
  }
}

TEST(TestSelectQuery, Simple) {
  auto query_builder =
      SelectQueryBuilder("schema", "table", DefaultValidator());

  CheckQueriesEqual(query_builder.GetQuery(),
                    R"-(SELECT * FROM schema.table)-");
}

TEST(TestSelectQuery, SelectColumns) {
  auto query_builder = SelectQueryBuilder("schema", "table", DefaultValidator())
                           .AddSelectColumn("a")
                           .AddSelectColumn("b")
                           .AddSelectColumn("c");

  CheckQueriesEqual(query_builder.GetQuery(),
                    R"-(SELECT a, b, c FROM schema.table)-");
}

TEST(TestSelectQuery, GroupByColumns) {
  auto query_builder = SelectQueryBuilder("schema", "table", DefaultValidator())
                           .AddSelectColumn("a")
                           .AddSelectColumn("b")
                           .AddSelectColumn("COUNT(*)")
                           .AddGroupByColumn("a")
                           .AddGroupByColumn("b");

  CheckQueriesEqual(
      query_builder.GetQuery(),
      R"-(SELECT a, b, COUNT(*) FROM schema.table GROUP BY a, b)-");
}

TEST(TestSelectQuery, OrderByColumns) {
  auto query_builder = SelectQueryBuilder("schema", "table", DefaultValidator())
                           .AddOrderByColumn("a")
                           .AddOrderByColumn("b");

  CheckQueriesEqual(query_builder.GetQuery(),
                    R"-(SELECT * FROM schema.table ORDER BY a, b)-");
}

TEST(TestSelectQuery, Limit) {
  auto query_builder =
      SelectQueryBuilder("schema", "table", DefaultValidator()).SetLimit(100);

  CheckQueriesEqual(query_builder.GetQuery(),
                    R"-(SELECT * FROM schema.table LIMIT 100)-");
}

TEST(TestSelectQuery, NegativeLimit) {
  EXPECT_THROW(
      SelectQueryBuilder("schema", "table", DefaultValidator()).SetLimit(-1),
      std::invalid_argument);
}

TEST(TestSelectQuery, FilterColumns) {
  auto query_builder =
      SelectQueryBuilder("schema", "table", DefaultValidator())
          .AddFilterCondition(query::filter::Equal({"a", "a"}))
          .AddFilterCondition(query::filter::Equal({"b", "b"}))
          .AddFilterCondition(query::filter::Equal({"c", "c"}));

  CheckQueriesEqual(
      query_builder.GetQuery(),
      R"-(SELECT * FROM schema.table WHERE a = 'a' AND b = 'b' AND c = 'c')-");
}

TEST(TestSelectQuery, FilterTypedColumns) {
  auto query_builder =
      SelectQueryBuilder("schema", "table", DefaultValidator())
          .AddFilterCondition(query::filter::Equal({"a", "1", "int"}))
          .AddFilterCondition(
              query::filter::Equal({"b", "phone_id", "identity_type"}));

  const std::string expected_query = R"-(
    SELECT * FROM schema.table
    WHERE a = '1'::int AND b = 'phone_id'::identity_type
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

TEST(TestSelectQuery, FilterByIsNotNullCondition) {
  auto query_builder = SelectQueryBuilder("schema", "table", DefaultValidator())
                           .AddFilterCondition(query::filter::IsNotNull("a"));

  const std::string expected_query = R"-(
    SELECT * FROM schema.table
    WHERE a IS NOT NULL
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

TEST(TestSelectQuery, FilterByEmptyInCondition) {
  auto query_builder = SelectQueryBuilder("schema", "table", DefaultValidator())
                           .AddFilterCondition(query::filter::In("a", {}));

  const std::string expected_query = R"-(
    SELECT * FROM schema.table
    WHERE a IN ()
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

TEST(TestSelectQuery, FilterByInCondition) {
  auto query_builder =
      SelectQueryBuilder("schema", "table", DefaultValidator())
          .AddFilterCondition(query::filter::In("a", {"b", "c", "e"}));

  const std::string expected_query = R"-(
    SELECT * FROM schema.table
    WHERE a IN ('b', 'c', 'e')
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

TEST(TestSelectQuery, Subquery) {
  auto subquery_builder =
      SelectQueryBuilder("schema", "table", DefaultValidator())
          .AddSelectColumn("a")
          .AddOrderByColumn("a")
          .SetLimit(10);

  auto query_builder =
      SelectQueryBuilder("schema", "table", DefaultValidator())
          .AddFilterCondition(query::filter::InSubquery("a", subquery_builder));

  const std::string expected_query = R"-(
    SELECT * FROM schema.table
    WHERE a IN ( SELECT a FROM schema.table ORDER BY a LIMIT 10 )
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

TEST(TestSelectQuery, FilterByBetweenCondition) {
  auto query_builder =
      SelectQueryBuilder("schema", "table", DefaultValidator())
          .AddFilterCondition(query::filter::Between(
              "a", {"", "b", "column_type"}, {"", "c", "column_type"}));

  const std::string expected_query = R"-(
    SELECT * FROM schema.table
    WHERE a BETWEEN 'b'::column_type AND 'c'::column_type
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

TEST(TestSelectQuery, Complex) {
  auto query_builder =
      SelectQueryBuilder("schema", "table", DefaultValidator());

  query_builder.AddSelectColumn("a")
      .AddSelectColumn("COUNT(*)")
      .AddGroupByColumn("a")
      .AddFilterCondition(query::filter::IsNotNull("a"))
      .AddFilterCondition(query::filter::Equal({"b", "b"}))
      .AddFilterCondition(query::filter::In("c", {"b", "c", "e"}))
      .AddOrderByColumn("a")
      .SetLimit(10);

  const std::string expected_query = R"-(
    SELECT a, COUNT(*)
    FROM schema.table
    WHERE
      a IS NOT NULL AND
      b = 'b' AND
      c IN ('b', 'c', 'e')
    GROUP BY a
    ORDER BY a
    LIMIT 10
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

TEST(TestSelectJoinQuery, Simple) {
  auto query_builder = SelectWithJoinQueryBuilder("schema", "main_table_name",
                                                  DefaultValidator(),
                                                  "aux_table_name", "a", "b");

  query_builder.AddSelectColumn("main.a")
      .AddSelectColumn("aux.b")
      .AddSelectColumn("COUNT(*)")
      .AddGroupByColumn("main.a")
      .AddGroupByColumn("aux.b")
      .AddFilterCondition(
          query::filter::Equal({"main.some_uid", "some_uid_value"}));

  const std::string expected_query = R"-(
    SELECT main.a, aux.b, COUNT(*)
    FROM schema.main_table_name main
    JOIN schema.aux_table_name aux ON aux.b = main.a
    WHERE main.some_uid = 'some_uid_value'
    GROUP BY main.a, aux.b
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

TEST(TestSelectJoinQuery, Real) {
  auto query_builder = SelectWithJoinQueryBuilder("schema", "main_table_name",
                                                  DefaultValidator(),
                                                  "aux_table_name", "a", "b");

  query_builder.AddSelectColumn("main.a")
      .AddSelectColumn("aux.b")
      .AddSelectColumn("COUNT(*) as counter")
      .AddSelectColumn("MAX(aux.t) as maxt")
      .AddSelectColumn("MIN(aux.t) as mint")
      .AddGroupByColumn("main.a")
      .AddGroupByColumn("aux.b")
      .AddFilterCondition(
          query::filter::Equal({"main.some_uid", "some_uid_value"}))
      .AddFilterCondition(query::filter::Between(
          "aux.t", {"", "from", "t_type"}, {"", "to", "t_type"}));

  const std::string expected_query = R"-(
    SELECT main.a, aux.b, COUNT(*) as counter, MAX(aux.t) as maxt, MIN(aux.t) as mint
    FROM schema.main_table_name main
    JOIN schema.aux_table_name aux ON aux.b = main.a
    WHERE main.some_uid = 'some_uid_value' AND aux.t BETWEEN 'from'::t_type AND 'to'::t_type
    GROUP BY main.a, aux.b
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

TEST(TestDeleteQuery, Basic) {
  auto query_builder =
      DeleteQueryBuilder("schema", "table", DefaultValidator())
          .AddFilterCondition(query::filter::LessThan({"a", "1", "int"}));

  const std::string expected_query = R"-(
    DELETE FROM schema.table
    WHERE a < '1'::int
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

TEST(TestDeleteQuery, MultipleConditions) {
  auto query_builder =
      DeleteQueryBuilder("schema", "table", DefaultValidator())
          .AddFilterCondition(query::filter::LessThan({"a", "1", "int"}))
          .AddFilterCondition(query::filter::Equal({"b", "foo"}))
          .AddFilterCondition(query::filter::LessThan({"c", "bar"}))
          .AddFilterCondition(query::filter::LessThan(
              {"d", "2020-08-08 12:00:00+03", "timestamptz"}));

  const std::string expected_query = R"-(
    DELETE FROM schema.table
    WHERE a < '1'::int
    AND b = 'foo'
    AND c < 'bar'
    AND d < '2020-08-08 12:00:00+03'::timestamptz
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

TEST(TestDeleteQuery, CanDeleteAll) {
  auto query_builder =
      DeleteQueryBuilder("schema", "table", DefaultValidator());

  const std::string expected_query = R"-(
    DELETE FROM schema.table
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

TEST(TestInsertQuery, SimpleColumns) {
  auto query_builder = InsertQueryBuilder("schema", "table", DefaultValidator())
                           .AddInsertColumn({"a", "a"})
                           .AddInsertColumn({"b", "b"});

  const std::string expected_query = R"-(
    INSERT INTO schema.table (a, b) VALUES ('a', 'b')
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

TEST(TestInsertQuery, TypedColumns) {
  auto query_builder = InsertQueryBuilder("schema", "table", DefaultValidator())
                           .AddInsertColumn({"a", "1", "int"})
                           .AddInsertColumn({"b", "phone_id", "identity_type"});

  const std::string expected_query = R"-(
    INSERT INTO schema.table (a, b) VALUES ('1'::int, 'phone_id'::identity_type)
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

TEST(TestInsertQuery, OnConflictUpdate) {
  auto query_builder = InsertQueryBuilder("schema", "table", DefaultValidator())
                           .AddInsertColumn({"a", "a"})
                           .AddInsertColumn({"counter", "1", "int"})
                           .AddInsertColumn({"product", "1", "int"})
                           .AddOnConflictColumn("a")
                           .AddOnConflictUpdate("counter = counter + 1")
                           .AddOnConflictUpdate("product = product * 2");

  const std::string expected_query = R"-(
    INSERT INTO schema.table (a, counter, product)
    VALUES ('a', '1'::int, '1'::int)
    ON CONFLICT (a)
    DO UPDATE SET
      counter = counter + 1,
      product = product * 2
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

TEST(TestInsertQuery, ReturningColumns) {
  auto query_builder = InsertQueryBuilder("schema", "table", DefaultValidator())
                           .AddInsertColumn({"a", "a"})
                           .AddReturningColumn({"a"})
                           .AddReturningColumn({"id", "text"});

  const std::string expected_query = R"-(
    INSERT INTO schema.table (a)
    VALUES ('a')
    RETURNING
      a,
      id::text
  )-";
  CheckQueriesEqual(query_builder.GetQuery(), expected_query);
}

}  // namespace db::query
