#include <gtest/gtest.h>

#include <utility>

#include <clients/graphite.hpp>
#include <clients/yt.hpp>
#include <clients/yt/query.hpp>
#include <config/config.hpp>
#include <secdist/secdist.hpp>
#include <threads/async.hpp>

namespace {

utils::Async& async() {
  static utils::Async async_pool(1, "", false);
  return async_pool;
}

std::shared_ptr<secdist::SecdistConfig> GetSecdist() {
  return std::make_shared<secdist::SecdistConfig>(std::string(SECDIST_PATH));
}

const utils::http::Client& http_client() {
  static const utils::http::Client client(async(), 1, "test_http_client",
                                          false);
  return client;
}

}  // namespace

TEST(YT, query_simple) {
  clients::yt::Client client(http_client(), async(), {}, *GetSecdist(), {});
  auto query = client.CreateQuery();
  query.All().From("test").Where("a < b").Limit(10);
  EXPECT_EQ("* FROM [test] WHERE a < b LIMIT 10", query.GetString(""));
}

TEST(YT, fields) {
  clients::yt::Client client(http_client(), async(), {}, *GetSecdist(), {});
  auto query = client.CreateQuery();
  query.Fields({"a", "b", "c"}).From("test").Where("a < b").Limit(10);
  EXPECT_EQ("a, b, c FROM [test] WHERE a < b LIMIT 10", query.GetString(""));
}

TEST(YT, and_test) {
  clients::yt::Client client(http_client(), async(), {}, *GetSecdist(), {});
  auto query = client.CreateQuery();
  auto predicate = clients::yt::And({"a < b", "a > c"});
  query.Fields({"a", "b", "c"}).From("test").Where(predicate);
  EXPECT_EQ("a, b, c FROM [test] WHERE (a < b AND a > c)", query.GetString(""));
}

TEST(YT, or_test) {
  clients::yt::Client client(http_client(), async(), {}, *GetSecdist(), {});
  auto query = client.CreateQuery();
  auto predicate = clients::yt::Or({"a < b", "a > c"});
  query.Fields({"a", "b", "c"}).From("test").Where(predicate);
  EXPECT_EQ("a, b, c FROM [test] WHERE (a < b OR a > c)", query.GetString(""));
}

TEST(YT, join_test) {
  clients::yt::Client client(http_client(), async(), {}, *GetSecdist(), {});
  auto query = client.CreateQuery();
  query.Fields({"A.a", "A.b", "B.c"}).From("index", "A").Join("test", "B");
  EXPECT_EQ("A.a, A.b, B.c FROM [index] AS A JOIN [test] AS B",
            query.GetString(""));
}

TEST(YT, order_by_simple_test) {
  clients::yt::Client client(http_client(), async(), {}, *GetSecdist(), {});
  auto query = client.CreateQuery();
  query.All().From("test").Where("a < b").OrderBy({"c", "d", "e"});
  EXPECT_EQ("* FROM [test] WHERE a < b ORDER BY c, d, e", query.GetString(""));
}

TEST(YT, order_by_paired_form_test) {
  clients::yt::Client client(http_client(), async(), {}, *GetSecdist(), {});
  auto query = client.CreateQuery();
  query.All().From("test").Where("a < b").OrderBy(
      {std::make_pair("c", clients::yt::SortOrder::Ascending),
       std::make_pair("d", clients::yt::SortOrder::Descending)});
  EXPECT_EQ("* FROM [test] WHERE a < b ORDER BY c ASC, d DESC",
            query.GetString(""));
}

TEST(YT, prefix_test) {
  clients::yt::Client client(http_client(), async(), {}, *GetSecdist(), {});
  auto query = client.CreateQuery();
  query.All().From("test").Where("a < b");
  EXPECT_EQ("* FROM [//prefix/test] WHERE a < b", query.GetString("//prefix"));
}

TEST(YT, escape_add_quotes_test) {
  const auto escaped = clients::yt::Escape("12345");
  EXPECT_EQ("\"12345\"", escaped);
}

TEST(YT, no_escape_test) {
  const auto escaped = clients::yt::Escape("12345", false);
  EXPECT_EQ("12345", escaped);
}

TEST(YT, escape_backslash_test) {
  const auto escaped = clients::yt::Escape("123\\45", false);
  EXPECT_EQ("123\\\\45", escaped);
}

TEST(YT, escape_quote_test) {
  const auto escaped = clients::yt::Escape("123\"45", false);
  EXPECT_EQ("123\\\"45", escaped);
}

TEST(YT, escape_non_prontable_r_test) {
  const auto escaped = clients::yt::Escape("123\r45", false);
  EXPECT_EQ("123\\r45", escaped);
}

TEST(YT, escape_non_prontable_n_test) {
  const auto escaped = clients::yt::Escape("123\n45", false);
  EXPECT_EQ("123\\n45", escaped);
}

TEST(YT, escape_non_prontable_t_test) {
  const auto escaped = clients::yt::Escape("123\t45", false);
  EXPECT_EQ("123\\t45", escaped);
}
