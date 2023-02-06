#include <userver/utest/utest.hpp>

#include <clickhouse_http_client/mocks/mock_client.hpp>
#include <userver/formats/json/value_builder.hpp>

TEST(ClickhouseHttpClientTest, ClientInsertTest) {
  clickhouse_http_client::mocks::MockClient client;
  clickhouse_http_client::TableIdentifier table_ident{"table_name_1"};

  std::vector<formats::json::Value> values;
  {
    formats::json::ValueBuilder builder;
    builder["field"] = "value1";
    builder["dleif"] = "value1";
    values.push_back(builder.ExtractValue());
  }
  {
    formats::json::ValueBuilder builder;
    builder["field"] = "value2";
    values.push_back(builder.ExtractValue());
  }

  // Not-empty query
  EXPECT_THROW(client.Insert(table_ident, values),
               clickhouse_http_client::mocks::QueryMismatchException);

  client.ExpectQuery(
      "INSERT INTO table_name_1 FORMAT JSONEachRow "
      "{\"field\":\"value1\",\"dleif\":\"value1\"} "
      "{\"field\":\"value2\"}");
  auto response = client.Insert(table_ident, values);
  ASSERT_EQ(response.rows["code"].As<int>(0), 200);
}
