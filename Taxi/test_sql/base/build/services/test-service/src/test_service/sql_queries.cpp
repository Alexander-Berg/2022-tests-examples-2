/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

#include <test_service/sql_queries.hpp>

namespace test_service::sql {

// Generated from services/test-service/src/some_query.sql
const storages::postgres::Query kSomeQuery = {
R"-(
SELECT
    id
FROM
    "table"
)-",
    storages::postgres::Query::Name("some_query"),
    storages::postgres::Query::LogMode::kFull
};


}  // namespace test_service::sql
