#include <gtest/gtest.h>

#include <utils/one_line_sql.hpp>

const std::string kSqlSelect1Multi =
    "\n"
    "SELECT\n"
    "  candidate, generation\n"
    " FROM lookup.order\n"
    " WHERE id = $1\n";

const std::string kSqlSelect1Single =
    " "
    "SELECT "
    "  candidate, generation "
    " FROM lookup.order "
    " WHERE id = $1 "
    "";

using utils::MakeOneLineSql;

TEST(OneLineSql, Simple) {
  EXPECT_EQ(MakeOneLineSql(kSqlSelect1Multi), kSqlSelect1Single);
  EXPECT_EQ(MakeOneLineSql(kSqlSelect1Single), kSqlSelect1Single);
}
