#include <gtest/gtest.h>

#include <psql/query/aggregates.hpp>
#include <psql/query/all.hpp>
#include <psql/query/any.hpp>
#include <psql/query/between.hpp>
#include <psql/query/delete.hpp>
#include <psql/query/geometry.hpp>
#include <psql/query/in.hpp>
#include <psql/query/insert.hpp>
#include <psql/query/is_null.hpp>
#include <psql/query/like.hpp>
#include <psql/query/operators.hpp>
#include <psql/query/select.hpp>
#include <psql/query/update.hpp>
#include <psql/query/with.hpp>
#include <psql/schema.hpp>

#ifndef USERVER
#include <utils/geometry.hpp>  // Y_IGNORE
#endif

namespace {

struct Extended {
  double element1;
  std::string element2;
  std::optional<std::string> element3;
};

}  // namespace

#ifdef USERVER
namespace utils {
namespace geometry {
struct Point {
  double lon;
  double lat;
};
}  // namespace geometry
}  // namespace utils
#endif

EXPAND_TYPE(Extended, "", element1, element2, element3);
EXPAND_TYPE_AS(utils::geometry::Point, "db::geopoint",  //
               (lon, "longitude"), (lat, "latitude"));

namespace {

PSQL_ALIAS(Res);

PSQL_SCHEMA(test) {
  PSQL_VIEW(view,                                 //
            (int, field1),                        //
            (std::string, field2),                //
            (std::optional<std::string>, field3)  //
  );

  PSQL_TABLE(table,                              //
             (int, field1),                      //
             (std::string, field2),              //
             (Extended, field3),                 //
             (std::optional<Extended>, field4),  //

             (int, i),         //
             (double, d),      //
             (char, c),        //
             (std::string, s)  //
  );

  PSQL_TABLE(table2,                //
             (int, field1),         //
             (std::string, field2)  //
  );

  PSQL_TABLE(geopoints, (int, id),               //
             (utils::geometry::Point, location)  //
  );
}

template <int i>
using Int = std::integral_constant<int, i>;
template <char c>
using Char = std::integral_constant<char, c>;

}  // namespace

TEST(Query, SelectView) {
  const auto& q = psql::Select(test::view.field1).From(test::view);
  EXPECT_EQ(q.Query(), "SELECT test.view.field1 FROM test.view");
  EXPECT_TRUE(
      (std::is_same<psql::ResultTypeT<std::decay_t<decltype(q)>>, int>::value));
}

TEST(Query, SelectTable) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table");
}

TEST(Query, SelectTableOnly) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table, psql::kOnly)
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM ONLY test.table");
}

TEST(Query, SelectExtendedFields) {
  EXPECT_EQ(
      psql::Select(test::table.field3.element1, test::table.field3.element2,
                   test::table.field3.element3)
          .From(test::table)
          .Query(),
      "SELECT "
      "(test.table.field3).element1,(test.table.field3).element2,(test."
      "table.field3).element3 FROM "
      "test.table");
}

TEST(Query, SelectExtendedFieldsOptional) {
  EXPECT_EQ(
      psql::Select(test::table.field4.element1, test::table.field4.element2,
                   test::table.field4.element3)
          .From(test::table)
          .Query(),
      "SELECT "
      "(test.table.field4).element1,(test.table.field4).element2,(test."
      "table.field4).element3 FROM "
      "test.table");
}

TEST(Query, SelectTableOrderBy) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .OrderBy(test::table.field1, psql::kAsc, psql::kNullsFirst)(
                    test::table.field2, psql::kDesc, psql::kNullsLast)
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "ORDER BY test.table.field1 ASC NULLS FIRST, test.table.field2 "
            "DESC NULLS LAST");
}

TEST(Query, SelectTableOrderByDefault) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .OrderBy(test::table.field1, psql::kDesc)(test::table.field2)
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "ORDER BY test.table.field1 DESC, test.table.field2 ASC");
}

TEST(Query, SelectFor) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .For(psql::kUpdate)
                .Of(test::table, test::table2)
                .SkipLocked()
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "FOR UPDATE OF table,table2 SKIP LOCKED");
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .For(psql::kShare)
                .NoWait()
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "FOR SHARE NOWAIT");
}

TEST(Query, SelectLimitOffset) {
  EXPECT_EQ(psql::Select(test::table.field1)
                .From(test::table)
                .Limit(psql::_2)
                .Offset(psql::_1)
                .Query(),
            "SELECT test.table.field1 FROM test.table LIMIT $2 OFFSET $1");
}

TEST(Query, SelectOrderByLimitOffset) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .OrderBy(test::table.field1)(test::table.field2, psql::kDesc)
                .Limit(psql::_2)
                .Offset(psql::_1)
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "ORDER BY test.table.field1 ASC, test.table.field2 DESC LIMIT $2 "
            "OFFSET $1");
}

TEST(Query, SelectWhereOrderByLimitOffset) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .Where(test::table.field1 == psql::_1)
                .OrderBy(test::table.field1)(test::table.field2, psql::kDesc)
                .Limit(psql::_2)
                .Offset(psql::_1)
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "WHERE (test.table.field1 = $1) "
            "ORDER BY test.table.field1 ASC, test.table.field2 DESC LIMIT $2 "
            "OFFSET $1");
}

TEST(Query, SelectLogicalWhereOrderByLimitOffset) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .Where(test::table.field1 == psql::_1 &&
                       test::table.field2 == psql::_2)
                .OrderBy(test::table.field1)(test::table.field2, psql::kDesc)
                .Limit(psql::_3)
                .Offset(psql::_4)
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "WHERE ((test.table.field1 = $1) AND (test.table.field2 = $2)) "
            "ORDER BY test.table.field1 ASC, test.table.field2 DESC LIMIT $3 "
            "OFFSET $4");
}

TEST(Query, SelectWhereLimitOffset) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .Where(test::table.field1 == psql::_1)
                .Limit(psql::_2)
                .Offset(psql::_3)
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "WHERE (test.table.field1 = $1) LIMIT $2 OFFSET $3");
}

TEST(Query, SelectWhereAny) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .Where(test::table.field1 == psql::Any(psql::_1))
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "WHERE (test.table.field1 = ANY($1))");
}

TEST(Query, SelectWhereNotAll) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .Where(test::table.field1 != psql::All(psql::_1))
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "WHERE (test.table.field1 <> ALL($1))");
}

TEST(Query, SelectWhereBetween) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .Where(test::table.field1 == psql::Between(psql::_1, psql::_2))
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "WHERE (test.table.field1 BETWEEN $1 AND $2)");
}

TEST(Query, SelectLikeLeftRight) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .Where(psql::Like(test::table.field2, psql::_1) ||
                       psql::Like(psql::_2, test::table.field2))
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "WHERE ((test.table.field2 LIKE $1) OR "
            "($2 LIKE test.table.field2))");
}

TEST(Query, SelectLikePlaceholders) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .Where(psql::Like(psql::_1, psql::_2))
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "WHERE ($1 LIKE $2)");
}

TEST(Query, SelectBinaryLike) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .Where(psql::Like(test::table.field1, test::table.field2))
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "WHERE (test.table.field1 LIKE test.table.field2)");
}

TEST(Query, SelectLeftJoinLike) {
  EXPECT_EQ(psql::Select(test::view.field1)
                .From(test::view)
                .LeftJoin(test::table)
                .On(test::view.field3 == test::table.field2)
                .Where(psql::Like(test::table.field2, psql::_1))
                .Query(),
            "SELECT test.view.field1 FROM test.view LEFT JOIN test.table ON "
            "(test.view.field3 = test.table.field2) "
            "WHERE (test.table.field2 LIKE $1)");
}

TEST(Query, SelectFromLogicalWhereLimitOffset) {
  EXPECT_EQ(psql::Select(test::table.field1, test::table.field2)
                .From(test::table)
                .Where(test::table.field1 == psql::_1 ||
                       test::table.field2 == psql::_2)
                .Limit(psql::_3)
                .Offset(psql::_4)
                .Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "WHERE ((test.table.field1 = $1) OR (test.table.field2 = $2)) "
            "LIMIT $3 OFFSET $4");
}

TEST(Query, LimitOffsetPlaceholders) {
  const auto& query = psql::Select(test::table.field1, test::table.field2)
                          .From(test::table)
                          .Limit(psql::_1)
                          .Offset(psql::_2);
  using ParamsT = psql::RealParamsT<std::decay_t<decltype(query)>>;

  EXPECT_EQ(query.Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "LIMIT $1 OFFSET $2");
  EXPECT_TRUE((std::is_same<
               std::decay_t<decltype(std::declval<ParamsT>())>,
               psql::TypeList<psql::detail::BoundParameter<1ul, int>,
                              psql::detail::BoundParameter<2ul, int>>>::value));
}

TEST(Query, LimitOffsetConstants) {
  const auto& query = psql::Select(test::table.field1, test::table.field2)
                          .From(test::table)
                          .Limit(Int<128>())
                          .Offset(Int<1024>());
  using ParamsT = psql::RealParamsT<std::decay_t<decltype(query)>>;

  EXPECT_EQ(query.Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "LIMIT 128 OFFSET 1024");
  EXPECT_TRUE((std::is_same<std::decay_t<decltype(std::declval<ParamsT>())>,
                            psql::TypeList<>>::value));
}

TEST(Query, LimitOffsetExpressions) {
  const auto& limit = psql::Select(psql::Count(test::table.field1))
                          .From(test::table)
                          .Where(test::table.field2 == psql::_1);
  using LimitParamsT = psql::RealParamsT<std::decay_t<decltype(limit)>>;

  const auto& offset = psql::Select(psql::Count(test::table.field2))
                           .From(test::table)
                           .Where(test::table.field1 == psql::_2);
  using OffsetParamsT = psql::RealParamsT<std::decay_t<decltype(offset)>>;

  const auto& query = psql::Select(test::table.field1, test::table.field2)
                          .From(test::table)
                          .Limit(limit)
                          .Offset(offset);
  using ParamsT = psql::RealParamsT<std::decay_t<decltype(query)>>;

  EXPECT_EQ(limit.Query(),
            "SELECT COUNT(test.table.field1) FROM test.table WHERE "
            "(test.table.field2 = $1)");
  EXPECT_EQ(offset.Query(),
            "SELECT COUNT(test.table.field2) FROM test.table WHERE "
            "(test.table.field1 = $2)");

  EXPECT_EQ(query.Query(),
            "SELECT test.table.field1,test.table.field2 FROM test.table "
            "LIMIT (" +
                limit.Query() +
                ") "
                "OFFSET (" +
                offset.Query() + ")");

  EXPECT_TRUE(
      (std::is_same<
          std::decay_t<decltype(std::declval<ParamsT>())>,
          psql::detail::ConcatParamsT<LimitParamsT, OffsetParamsT>>::value));
}

TEST(Query, SelectViewWhere) {
  EXPECT_EQ(
      psql::Select(test::view.field1)
          .From(test::view)
          .Where(psql::_1 == test::view.field2)
          .Query(),
      "SELECT test.view.field1 FROM test.view WHERE ($1 = test.view.field2)");
  EXPECT_EQ(
      psql::Select(test::view.field1)
          .From(test::view)
          .Where(test::view.field2 == psql::_1)
          .Query(),
      "SELECT test.view.field1 FROM test.view WHERE (test.view.field2 = $1)");
}

TEST(Query, SelectViewWhereNull) {
  EXPECT_EQ(
      psql::Select(test::view.field1)
          .From(test::view)
          .Where(psql::IsNull(test::view.field2))
          .Query(),
      "SELECT test.view.field1 FROM test.view WHERE test.view.field2 IS NULL");
  EXPECT_EQ(psql::Select(test::view.field1)
                .From(test::view)
                .Where(psql::IsNotNull(test::view.field2))
                .Query(),
            "SELECT test.view.field1 FROM test.view WHERE test.view.field2 IS "
            "NOT NULL");
}

TEST(Query, SelectViewOperators) {
  EXPECT_EQ(
      psql::Select(test::view.field1)
          .From(test::view)
          .Where(test::view.field2 + test::view.field1 >= test::view.field1)
          .Query(),
      "SELECT test.view.field1 FROM test.view WHERE ((test.view.field2 + "
      "test.view.field1) >= test.view.field1)");

  EXPECT_EQ(
      psql::Select(test::view.field1)
          .From(test::view)
          .Where(test::view.field2 - test::view.field1 >= test::view.field1)
          .Query(),
      "SELECT test.view.field1 FROM test.view WHERE ((test.view.field2 - "
      "test.view.field1) >= test.view.field1)");

  EXPECT_EQ(
      psql::Select(test::view.field1)
          .From(test::view)
          .Where(test::view.field2 * test::view.field1 >= test::view.field1)
          .Query(),
      "SELECT test.view.field1 FROM test.view WHERE ((test.view.field2 * "
      "test.view.field1) >= test.view.field1)");

  EXPECT_EQ(
      psql::Select(test::view.field1)
          .From(test::view)
          .Where(test::view.field2 / test::view.field1 >= test::view.field1)
          .Query(),
      "SELECT test.view.field1 FROM test.view WHERE ((test.view.field2 / "
      "test.view.field1) >= test.view.field1)");

  EXPECT_EQ(
      psql::Select(test::view.field1)
          .From(test::view)
          .Where((test::view.field2 | test::view.field1) >= test::view.field1)
          .Query(),
      "SELECT test.view.field1 FROM test.view WHERE ((test.view.field2 | "
      "test.view.field1) >= test.view.field1)");

  EXPECT_EQ(
      psql::Select(test::view.field1)
          .From(test::view)
          .Where((test::view.field2 & test::view.field1) >= test::view.field1)
          .Query(),
      "SELECT test.view.field1 FROM test.view WHERE ((test.view.field2 & "
      "test.view.field1) >= test.view.field1)");
}

TEST(Query, SelectDistinctViewWhere) {
  EXPECT_EQ(psql::SelectDistinct(test::view.field1)
                .From(test::view)
                .Where(psql::_1 == test::view.field2)
                .Query(),
            "SELECT DISTINCT test.view.field1 FROM test.view "
            "WHERE ($1 = test.view.field2)");
  EXPECT_EQ(psql::SelectDistinct(test::view.field1)
                .From(test::view)
                .Where(test::view.field2 == psql::_1)
                .Query(),
            "SELECT DISTINCT test.view.field1 FROM test.view "
            "WHERE (test.view.field2 = $1)");
}

TEST(Query, SelectDistinctOnViewWhere) {
  EXPECT_EQ(
      psql::SelectDistinctOn(test::view.field2)(test::view.field1)
          .From(test::view)
          .Where(psql::_1 == test::view.field2)
          .Query(),
      "SELECT DISTINCT ON (test.view.field2) test.view.field1 FROM test.view "
      "WHERE ($1 = test.view.field2)");
  EXPECT_EQ(psql::SelectDistinct(test::view.field1)
                .From(test::view)
                .Where(test::view.field2 == psql::_1)
                .Query(),
            "SELECT DISTINCT test.view.field1 FROM test.view "
            "WHERE (test.view.field2 = $1)");
}

TEST(Query, SelectLeftJoin) {
  const auto& q = psql::Select(test::table.field2, test::view.field3)
                      .From(test::view)
                      .LeftJoin(test::table)
                      .On(test::table.field1 == test::view.field1 &&
                          test::table.field2 != psql::_1);
  EXPECT_EQ(
      q.Query(),
      "SELECT test.table.field2,test.view.field3 FROM test.view LEFT JOIN "
      "test.table ON ((test.table.field1 = test.view.field1) AND "
      "(test.table.field2 <> $1))");

  EXPECT_TRUE((std::is_same<                    //
               psql::ResultTypeT<decltype(q)>,  //
               psql::Row<psql::detail::Cell<decltype(test::table.field2),
                                            std::optional<std::string>>,
                         psql::detail::Cell<decltype(test::view.field3),
                                            std::optional<std::string>>>  //
               >::value                                                   //
               ));

  EXPECT_EQ(psql::Select(test::table.field2, test::view.field3)
                .From(test::view)
                .LeftJoin(test::table, psql::kOnly)
                .On(test::table.field1 == test::view.field1 &&
                    test::table.field2 != psql::_2)
                .Where(test::view.field3 == psql::_1)
                .Query(),
            "SELECT test.table.field2,test.view.field3 FROM test.view "
            "LEFT JOIN ONLY test.table ON ((test.table.field1 = "
            "test.view.field1) AND "
            "(test.table.field2 <> $2)) "
            "WHERE (test.view.field3 = $1)");
}

TEST(Query, Coalesce) {
  const auto& q =
      psql::Select(psql::Coalesce(test::view.field2, test::view.field3))
          .From(test::view);

  EXPECT_EQ(
      q.Query(),
      "SELECT COALESCE(test.view.field2,test.view.field3) FROM test.view");

  EXPECT_TRUE((std::is_same<                                  //
               psql::ResultTypeT<std::decay_t<decltype(q)>>,  //
               std::string                                    //
               >::value                                       //
               ));
}

TEST(Query, TableAs) {
  struct Alias {};
  EXPECT_EQ(
      psql::Select(test::table.As<Alias>().field1,
                   test::table.As<Alias>().field2)
          .From(test::table.As<Alias>())
          .Query(),
      "SELECT _alias_0.field1,_alias_0.field2 FROM test.table AS _alias_0");
}

TEST(Query, Insert) {
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1, test::table.field2)
          .Query(),
      "INSERT INTO test.table (\"field1\",\"field2\") VALUES ($1,$2)");
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1, test::table.field2)
          .Values(psql::_1, psql::_2)
          .Query(),
      "INSERT INTO test.table (\"field1\",\"field2\") VALUES ($1,$2)");
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1, test::table.field2)
          .Select(test::table2.field1, test::table2.field2)
          .From(test::table2)
          .Query(),
      "INSERT INTO test.table (\"field1\",\"field2\") SELECT "
      "test.table2.field1,test.table2.field2 FROM test.table2");
}

TEST(Query, InsertReturning) {
  EXPECT_EQ(psql::InsertInto(test::table)(test::table.field1)
                .Returning(test::table.field1)
                .Query(),
            "INSERT INTO test.table (\"field1\") VALUES ($1) RETURNING "
            "test.table.field1");
  EXPECT_EQ(psql::InsertInto(test::table)(test::table.field1)
                .Values(psql::_1)
                .Returning(test::table.field1)
                .Query(),
            "INSERT INTO test.table (\"field1\") VALUES ($1) RETURNING "
            "test.table.field1");
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1)
          .Select(test::table2.field1)
          .From(test::table2)
          .Returning(test::table.field1)
          .Query(),
      "INSERT INTO test.table (\"field1\") SELECT test.table2.field1 FROM "
      "test.table2 RETURNING test.table.field1");
}

TEST(Query, InsertReturningTwo) {
  EXPECT_EQ(psql::InsertInto(test::table)(test::table.field1)
                .Returning(test::table.field1, test::table.field2)
                .Query(),
            "INSERT INTO test.table (\"field1\") VALUES ($1) RETURNING "
            "test.table.field1,test.table.field2");
  EXPECT_EQ(psql::InsertInto(test::table)(test::table.field1)
                .Values(psql::_1)
                .Returning(test::table.field1, test::table.field2)
                .Query(),
            "INSERT INTO test.table (\"field1\") VALUES ($1) RETURNING "
            "test.table.field1,test.table.field2");
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1)
          .Select(test::table2.field1)
          .From(test::table2)
          .Returning(test::table.field1, test::table.field2)
          .Query(),
      "INSERT INTO test.table (\"field1\") SELECT test.table2.field1 FROM "
      "test.table2 RETURNING test.table.field1,test.table.field2");
}

TEST(Query, InsertOnConflict) {
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1)
          .OnConflict(test::table.field1)
          .DoNothing()
          .Query(),
      "INSERT INTO test.table (\"field1\") VALUES ($1) ON CONFLICT (field1) "
      "DO NOTHING");
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1)
          .Values(psql::_1)
          .OnConflict(test::table.field1)
          .DoNothing()
          .Query(),
      "INSERT INTO test.table (\"field1\") VALUES ($1) ON CONFLICT (field1) "
      "DO NOTHING");
  EXPECT_EQ(psql::InsertInto(test::table)(test::table.field1)
                .Select(test::table2.field1)
                .From(test::table2)
                .OnConflict(test::table.field1)
                .DoNothing()
                .Query(),
            "INSERT INTO test.table (\"field1\") SELECT test.table2.field1 "
            "FROM test.table2 ON CONFLICT (field1) DO NOTHING");

  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1)
          .OnConflict(test::table.field1)
          .DoNothing()
          .Returning(test::table.field1)
          .Query(),
      "INSERT INTO test.table (\"field1\") VALUES ($1) ON CONFLICT (field1) "
      "DO NOTHING RETURNING test.table.field1");
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1)
          .Values(psql::_1)
          .OnConflict(test::table.field1)
          .DoNothing()
          .Returning(test::table.field1)
          .Query(),
      "INSERT INTO test.table (\"field1\") VALUES ($1) ON CONFLICT (field1) "
      "DO NOTHING RETURNING test.table.field1");
  EXPECT_EQ(psql::InsertInto(test::table)(test::table.field1)
                .Select(test::table2.field1)
                .From(test::table2)
                .OnConflict(test::table.field1)
                .DoNothing()
                .Returning(test::table.field1)
                .Query(),
            "INSERT INTO test.table (\"field1\") SELECT test.table2.field1 "
            "FROM test.table2 ON CONFLICT (field1) DO NOTHING RETURNING "
            "test.table.field1");

  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1, test::table.field2)
          .OnConflict(test::table.field1)
          .DoUpdateSet(test::table.field1 = psql::_1,
                       test::table.field2 = psql::_2)
          .Query(),
      "INSERT INTO test.table (\"field1\",\"field2\") VALUES ($1,$2) "
      "ON CONFLICT (field1) DO UPDATE SET \"field1\" = $1,\"field2\" = $2");
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1, test::table.field2)
          .Values(psql::_1, psql::_2)
          .OnConflict(test::table.field1)
          .DoUpdateSet(test::table.field1 = psql::_1,
                       test::table.field2 = psql::_2)
          .Query(),
      "INSERT INTO test.table (\"field1\",\"field2\") VALUES ($1,$2) "
      "ON CONFLICT (field1) DO UPDATE SET \"field1\" = $1,\"field2\" = $2");
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1, test::table.field2)
          .Select(test::table2.field1, test::table2.field2)
          .From(test::table2)
          .OnConflict(test::table.field1)
          .DoUpdateSet(test::table.field1 = psql::Excluded(test::table.field1),
                       test::table.field2 = psql::Excluded(test::table.field2))
          .Query(),
      "INSERT INTO test.table (\"field1\",\"field2\") SELECT "
      "test.table2.field1,test.table2.field2 FROM test.table2 "
      "ON CONFLICT (field1) DO UPDATE SET \"field1\" = "
      "EXCLUDED.\"field1\",\"field2\" = EXCLUDED.\"field2\"");

  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1, test::table.field2)
          .OnConflict(test::table.field1, test::table.field2)
          .DoUpdateSet(test::table.field2 = psql::_2)
          .Where(test::table.field1 == psql::_1)
          .Query(),
      "INSERT INTO test.table (\"field1\",\"field2\") VALUES ($1,$2) "
      "ON CONFLICT (field1,field2) DO UPDATE SET \"field2\" = $2 "
      "WHERE (test.table.field1 = $1)");
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1, test::table.field2)
          .Values(psql::_1, psql::_2)
          .OnConflict(test::table.field1, test::table.field2)
          .Where(test::table.field1 != test::table.field2)
          .DoUpdateSet(test::table.field2 = psql::_2)
          .Where(test::table.field1 == psql::_1)
          .Query(),
      "INSERT INTO test.table (\"field1\",\"field2\") VALUES ($1,$2) "
      "ON CONFLICT (field1,field2) WHERE (field1 <> field2) DO UPDATE SET "
      "\"field2\" = $2 "
      "WHERE (test.table.field1 = $1)");

  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1, test::table.field2)
          .OnConflict(test::table.field1, test::table.field2)
          .DoUpdateSet(test::table.field2 = psql::_2)
          .Returning(test::table.field1)
          .Query(),
      "INSERT INTO test.table (\"field1\",\"field2\") VALUES ($1,$2) "
      "ON CONFLICT (field1,field2) DO UPDATE SET \"field2\" = $2 "
      "RETURNING test.table.field1");
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1, test::table.field2)
          .Values(psql::_1, psql::_2)
          .OnConflict(test::table.field1, test::table.field2)
          .DoUpdateSet(test::table.field2 = psql::_2)
          .Returning(test::table.field1)
          .Query(),
      "INSERT INTO test.table (\"field1\",\"field2\") VALUES ($1,$2) "
      "ON CONFLICT (field1,field2) DO UPDATE SET \"field2\" = $2 "
      "RETURNING test.table.field1");
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1, test::table.field2)
          .Select(test::table2.field1, test::table2.field2)
          .From(test::table2)
          .OnConflict(test::table.field1)
          .DoUpdateSet(test::table.field1 = psql::Excluded(test::table.field1),
                       test::table.field2 = psql::Excluded(test::table.field2))
          .Returning(test::table.field1)
          .Query(),
      "INSERT INTO test.table (\"field1\",\"field2\") SELECT "
      "test.table2.field1,test.table2.field2 FROM test.table2 "
      "ON CONFLICT (field1) DO UPDATE SET \"field1\" = "
      "EXCLUDED.\"field1\",\"field2\" = EXCLUDED.\"field2\" RETURNING "
      "test.table.field1");

  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1, test::table.field2)
          .OnConflict(test::table.field1)
          .DoUpdateSet(test::table.field2 = psql::_2)
          .Where(test::table.field1 == psql::_1)
          .Returning(test::table.field1)
          .Query(),
      "INSERT INTO test.table (\"field1\",\"field2\") VALUES ($1,$2) "
      "ON CONFLICT (field1) DO UPDATE SET \"field2\" = $2 WHERE "
      "(test.table.field1 "
      "= $1) RETURNING test.table.field1");
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1, test::table.field2)
          .Values(psql::_1, psql::_2)
          .OnConflict(test::table.field1)
          .DoUpdateSet(test::table.field2 = psql::_2)
          .Where(test::table.field1 == psql::_1)
          .Returning(test::table.field1)
          .Query(),
      "INSERT INTO test.table (\"field1\",\"field2\") VALUES ($1,$2) "
      "ON CONFLICT (field1) DO UPDATE SET \"field2\" = $2 WHERE "
      "(test.table.field1 "
      "= $1) RETURNING test.table.field1");
}

TEST(Query, BulkInsert) {
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1, test::table.field2)
          .Query(3u),
      "INSERT INTO test.table (\"field1\",\"field2\") VALUES "
      "($1,$2),($3,$4),($5,$6)");
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1, test::table.field2)
          .OnConflict(test::table.field2)
          .DoNothing()
          .Query(3u),
      "INSERT INTO test.table (\"field1\",\"field2\") VALUES "
      "($1,$2),($3,$4),($5,$6) ON CONFLICT (field2) DO NOTHING");
}

TEST(Query, BulkInsertReturning) {
  EXPECT_EQ(
      psql::InsertInto(test::table)(test::table.field1)
          .Returning(test::table.field1)
          .Query(3u),
      "INSERT INTO test.table (\"field1\") VALUES ($1),($2),($3) RETURNING "
      "test.table.field1");
}

TEST(Query, Delete) {
  EXPECT_EQ(psql::DeleteFrom(test::table)
                .Where(test::table.field1 == psql::_1)
                .Query(),
            "DELETE FROM test.table WHERE (test.table.field1 = $1)");

  EXPECT_EQ(psql::DeleteFrom(test::table, psql::kOnly)
                .Where(test::table.field1 == psql::_1)
                .Query(),
            "DELETE FROM ONLY test.table WHERE (test.table.field1 = $1)");
}

TEST(Query, DeleteLogicalWhere) {
  EXPECT_EQ(psql::DeleteFrom(test::table)
                .Where(test::table.field1 == psql::_1 &&
                       test::table.field2 == psql::_2)
                .Query(),
            "DELETE FROM test.table WHERE "
            "((test.table.field1 = $1) AND (test.table.field2 = $2))");
}

TEST(Query, DeleteReturning) {
  EXPECT_EQ(psql::DeleteFrom(test::table)
                .Where(test::table.field1 == psql::_1)
                .Returning(test::table.field2)
                .Query(),
            "DELETE FROM test.table WHERE (test.table.field1 = $1) "
            "RETURNING test.table.field2");
}

TEST(Query, Update) {
  EXPECT_EQ(psql::Update(test::table)
                .Set(test::table.field2 = psql::_1)
                .Where(test::table.field1 == psql::_2)
                .Query(),
            "UPDATE test.table SET \"field2\" = $1 WHERE "
            "(test.table.field1 = $2)");

  EXPECT_EQ(psql::Update(test::table, psql::kOnly)
                .Set(test::table.field2 = psql::_1)
                .Where(test::table.field1 == psql::_2)
                .Query(),
            "UPDATE ONLY test.table SET \"field2\" = $1 WHERE "
            "(test.table.field1 = $2)");

  EXPECT_EQ(
      psql::Update(test::table)
          .Set(test::table.field1 = test::table.field1 + test::table.field1,
               test::table.field2 = test::table.field2 + test::table.field1)
          .Where(test::table.field1 == test::table.field1 + test::table.field1)
          .Query(),
      "UPDATE test.table SET \"field1\" = (test.table.field1 + "
      "test.table.field1),\"field2\" = (test.table.field2 + test.table.field1) "
      "WHERE (test.table.field1 = (test.table.field1 + test.table.field1))");

  EXPECT_EQ(
      psql::Update(test::table)
          .Set(test::table.field1 = std::integral_constant<int, 123>() +
                                    std::integral_constant<char, 'a'>() +
                                    test::table.field2)
          .Query(),
      "UPDATE test.table SET \"field1\" = ((123 + 'a') + test.table.field2)");
  EXPECT_EQ(psql::Update(test::table)
                .Set(test::table.field2 = psql::_1)
                .From(test::table2)
                .Where(test::table.field1 = test::table2.field1)
                .Query(),
            "UPDATE test.table SET \"field2\" = $1 FROM test.table2 "
            "WHERE \"field1\" = test.table2.field1");
}

TEST(Query, UpdateWithInSelect) {
  const auto& select = psql::Select(test::table2.field1)
                           .From(test::table2)
                           .InnerJoin(test::table)
                           .On(test::table.field1 = test::table2.field1);
  EXPECT_EQ(psql::Update(test::table)
                .Set(test::table.field2 = psql::_1)
                .Where(psql::In(test::table.field1, select))
                .Query(),
            "UPDATE test.table SET \"field2\" = $1 WHERE test.table.field1 IN "
            "(SELECT test.table2.field1 FROM test.table2 "
            "INNER JOIN test.table ON \"field1\" = test.table2.field1)");
}

TEST(Query, With) {
  const auto res = psql::Select(test::table.field1, test::table.field2)
                       .From(test::table)
                       .As<Res>();

  const auto q = psql::With(res).Do(psql::Select(res.field2).From(res));

  const auto res_a = Res::Query();

  EXPECT_EQ(q.Query(), "WITH " + res_a +
                           " AS ("
                           "SELECT test.table.field1,test.table.field2 FROM "
                           "test.table"
                           ") "
                           "SELECT " +
                           res_a + ".field2 FROM " + res_a);
}

TEST(Query, WithRecursive) {
  const auto res_a = Res::Query();
  {
    const auto res =
        psql::Select(test::table.field1, test::table.field2)
            .From(test::table)
            .Union(psql::Select(test::table.field1, test::table.field2)
                       .From(test::table))
            .As<Res>();
    const auto q1 =
        psql::WithRecursive(res).Do(psql::Select(res.field2).From(res));

    EXPECT_EQ(q1.Query(),
              "WITH RECURSIVE " + res_a +
                  " AS ("
                  "SELECT test.table.field1,test.table.field2 FROM test.table"
                  " UNION "
                  "SELECT test.table.field1,test.table.field2 FROM test.table"
                  ") "
                  "SELECT " +
                  res_a + ".field2 FROM " + res_a);
  }

  {
    const auto res =
        psql::Select(test::table.field1, test::table.field2)
            .From(test::table)
            .UnionAll(psql::Select(test::table.field1, test::table.field2)
                          .From(test::table))
            .As<Res>();
    const auto q2 =
        psql::WithRecursive(res).Do(psql::Select(res.field2).From(res));

    EXPECT_EQ(q2.Query(),
              "WITH RECURSIVE " + res_a +
                  " AS ("
                  "SELECT test.table.field1,test.table.field2 FROM test.table"
                  " UNION ALL "
                  "SELECT test.table.field1,test.table.field2 FROM test.table"
                  ") "
                  "SELECT " +
                  res_a + ".field2 FROM " + res_a);
  }
}

TEST(Query, UnionParams) {
  const auto q =
      psql::Select(test::table.field1, test::table.field2)
          .From(test::table)
          .Where(test::table.field1 <= psql::_1)
          .UnionAll(psql::Select(test::table.field1, test::table.field2)
                        .From(test::table));

  EXPECT_TRUE((std::is_same<
               psql::RealParamsT<std::decay_t<decltype(q)>>,
               psql::TypeList<psql::detail::BoundParameter<1ul, int>>>::value));
}

TEST(Query, AggregateFuncs) {
  const auto q1 = psql::Select(psql::Max(test::table.field1)).From(test::table);
  EXPECT_EQ(q1.Query(), "SELECT MAX(test.table.field1) FROM test.table");
  EXPECT_TRUE((std::is_same<psql::ResultTypeT<std::decay_t<decltype(q1)>>,
                            std::optional<int>>::value));

  const auto q2 =
      psql::Select(psql::Count(test::table.field1)).From(test::table);
  EXPECT_EQ(q2.Query(), "SELECT COUNT(test.table.field1) FROM test.table");
  EXPECT_TRUE((std::is_same<psql::ResultTypeT<std::decay_t<decltype(q2)>>,
                            int64_t>::value));

  EXPECT_EQ(psql::Select(psql::Min(test::table.field1), test::table.field2)
                .From(test::table)
                .GroupBy(test::table.field2)
                .Query(),
            "SELECT MIN(test.table.field1),test.table.field2 FROM test.table "
            "GROUP BY test.table.field2");

  EXPECT_EQ(psql::Select(psql::Avg(test::view.field1), test::view.field3)
                .From(test::view)
                .Where(psql::IsNotNull(test::view.field3))
                .GroupBy(test::view.field3)
                .Query(),
            "SELECT AVG(test.view.field1),test.view.field3 FROM test.view "
            "WHERE test.view.field3 IS NOT NULL GROUP BY test.view.field3");

  EXPECT_EQ(psql::Select(psql::Sum(test::view.field1), test::view.field2,
                         test::view.field3)
                .From(test::view)
                .GroupBy(test::view.field2, test::view.field3)
                .Query(),
            "SELECT SUM(test.view.field1),test.view.field2,test.view.field3 "
            "FROM test.view GROUP BY test.view.field2,test.view.field3");

  EXPECT_EQ(
      psql::Select(psql::Count(test::view.field1),
                   psql::Sum(test::table.field1), test::table.field2)
          .From(test::view)
          .LeftJoin(test::table)
          .On(test::table.field1 == test::view.field1)
          .Where(psql::IsNotNull(test::view.field3))
          .GroupBy(test::table.field2)
          .OrderBy(test::view.field1)
          .Limit(psql::_1)
          .Offset(psql::_2)
          .Query(),
      "SELECT COUNT(test.view.field1),SUM(test.table.field1),test.table.field2 "
      "FROM test.view LEFT JOIN test.table ON (test.table.field1 = "
      "test.view.field1) "
      "WHERE test.view.field3 IS NOT NULL GROUP BY "
      "test.table.field2 ORDER BY test.view.field1 ASC LIMIT $1 OFFSET $2");
}

TEST(Query, Expressions) {
  using test::table;
  const auto& update = psql::Update(table);
  EXPECT_EQ(update.Set(table.i = Int<123>()).Query(),
            "UPDATE test.table SET \"i\" = 123");
  EXPECT_EQ(update.Set(table.i = Int<123>() + Int<345>()).Query(),
            "UPDATE test.table SET \"i\" = (123 + 345)");
  EXPECT_EQ(update.Set(table.i = Int<123>() + table.i).Query(),
            "UPDATE test.table SET \"i\" = (123 + test.table.i)");
  EXPECT_EQ(update.Set(table.i = table.s).Query(),
            "UPDATE test.table SET \"i\" = test.table.s");  // wrong !!!
  EXPECT_EQ(update.Set(table.i = Int<123>() * table.s).Query(),
            "UPDATE test.table SET \"i\" = (123 * test.table.s)");  // wrong !!!
  EXPECT_EQ(update.Set(table.i = Int<123>() + table.d).Query(),
            "UPDATE test.table SET \"i\" = (123 + test.table.d)");  // wrong !!!
  EXPECT_EQ(update.Set(table.d = Char<'a'>() * table.s).Query(),
            "UPDATE test.table SET \"d\" = ('a' * test.table.s)");  // wrong !!!
  EXPECT_EQ(update.Set(table.d = Int<123>() + Char<'a'>()).Query(),
            "UPDATE test.table SET \"d\" = (123 + 'a')");  // wrong !!!
  EXPECT_EQ(update.Set(table.c = Int<123>()).Query(),
            "UPDATE test.table SET \"c\" = 123");  // wrong !!!
  EXPECT_EQ(update.Set(table.c = Char<'a'>()).Query(),
            "UPDATE test.table SET \"c\" = 'a'");
  EXPECT_EQ(update.Set(table.c = table.s).Query(),
            "UPDATE test.table SET \"c\" = test.table.s");  // wrong !!!
}

TEST(Query, GeometryTypes) {
  using namespace psql::geometry;

  const auto q1 = psql::Select(Point(test::geopoints.location.lat,
                                     test::geopoints.location.lon))
                      .From(test::geopoints);
  EXPECT_EQ(q1.Query(),
            "SELECT "
            "point((test.geopoints.location).latitude,(test.geopoints.location)"
            ".longitude) "
            "FROM test.geopoints");

  const auto q2 = psql::Select(test::geopoints.id)
                      .From(test::geopoints)
                      .Where(Point(test::geopoints.location.lat,
                                   test::geopoints.location.lon) == psql::_1);
  EXPECT_EQ(q2.Query(),
            "SELECT test.geopoints.id FROM test.geopoints WHERE "
            "(point((test.geopoints.location).latitude,(test.geopoints."
            "location).longitude) = $1)");

  const auto q3 = psql::Select(test::geopoints.id, test::geopoints.location)
                      .From(test::geopoints)
                      .Where(Point(test::geopoints.location.lat,
                                   test::geopoints.location.lon) ==
                             Contained<PolygonT>(psql::_1));
  EXPECT_EQ(q3.Query(),
            "SELECT test.geopoints.id,test.geopoints.location FROM "
            "test.geopoints WHERE "
            "(point((test.geopoints.location).latitude,(test.geopoints."
            "location).longitude) "
            "<@ $1::polygon)");
}

namespace {

PSQL_ALIAS(A);
PSQL_ALIAS(B);
PSQL_ALIAS(C);

}  // namespace

TEST(Query, FieldAlias) {
  const auto& qa = test::view.field1.As<A>();
  const auto& qb = test::view.field1.As<B>();

  const auto& q = psql::Select(qa, qb, psql::Coalesce(qa, qb).As<C>())
                      .From(test::view)
                      .Where(test::view.field1.As<A>() > psql::_1);

  const auto& a = "_alias_" + std::to_string(psql::detail::GetId<A>());
  const auto& b = "_alias_" + std::to_string(psql::detail::GetId<B>());
  const auto& c = "_alias_" + std::to_string(psql::detail::GetId<C>());

  EXPECT_NE(a, b);
  EXPECT_NE(b, c);
  EXPECT_NE(a, c);

  EXPECT_EQ(q.Query(), "SELECT test.view.field1 AS " + a +
                           ",test.view.field1 AS " + b + ",COALESCE(" + a +
                           "," + b + ") AS " + c + " FROM test.view WHERE (" +
                           a + " > $1)");

  using Result = psql::ResultTypeT<std::decay_t<decltype(q)>>;

  EXPECT_TRUE((std::is_same<std::decay_t<decltype(std::declval<Result>().A)>,
                            int>::value));
}

TEST(Query, Subquery) {
  const auto& qa = test::view.field1.As<A>();

  const auto& q =
      psql::Select(psql::Count(A())).From(psql::Select(qa).From(test::view));

  const auto& a = "_alias_" + std::to_string(psql::detail::GetId<A>());

  EXPECT_EQ(q.Query(), "SELECT COUNT(" + a +
                           ") FROM (SELECT test.view.field1 AS " + a +
                           " FROM test.view)");

  using Result = psql::ResultTypeT<std::decay_t<decltype(q)>>;

  EXPECT_TRUE((std::is_same<std::decay_t<Result>, int64_t>::value));
}

TEST(Query, OperatorAlias) {
  const auto& query =
      psql::Select((test::table.field1 > psql::_1).As<A>()).From(test::table);

  const auto& alias = "_alias_" + std::to_string(psql::detail::GetId<A>());

  EXPECT_EQ(query.Query(),
            "SELECT (test.table.field1 > $1) AS " + alias + " FROM test.table");

  using Result = psql::ResultTypeT<std::decay_t<decltype(query)>>;

  EXPECT_TRUE((std::is_same<std::decay_t<Result>, bool>::value));
}

TEST(Query, OperatorAliasType) {
  const auto& query =
      psql::Select((test::table.field2 + psql::_1).As<A>()).From(test::table);

  const auto& alias = "_alias_" + std::to_string(psql::detail::GetId<A>());

  EXPECT_EQ(query.Query(),
            "SELECT (test.table.field2 + $1) AS " + alias + " FROM test.table");

  using Result = psql::ResultTypeT<std::decay_t<decltype(query)>>;

  EXPECT_TRUE((std::is_same<std::decay_t<Result>, std::string>::value));
}
