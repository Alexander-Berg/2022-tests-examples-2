#include <kibana-url-generator/kibana-url-generator.hpp>
#include <userver/utest/utest.hpp>

namespace kibana_url_generator {

static const std::string kSomeServiceIndex =
    "f8e70880-c75c-11e9-8a12-ddb2ef5a51ea";

TEST(KibanaURLGenerator, OneFilter) {
  auto const url = ConstructKibanaURL(
      kSomeServiceIndex, {{"module", Filter::Is{"HandleRequest"}}});

  // clang-format off
  EXPECT_EQ(url, "https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters'%3A!()%2C'time'%3A('from'%3A'now-15m'%2C'to'%3A'now'))&_a=('columns'%3A!('_source')%2C'filters'%3A!(('%24state'%3A('store'%3A'appState')%2C'meta'%3A('alias'%3A!n%2C'disabled'%3A!f%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'key'%3A'module'%2C'negate'%3A!f%2C'params'%3A('query'%3A'HandleRequest')%2C'type'%3A'phrase'%2C'value'%3A'HandleRequest')%2C'query'%3A('match'%3A('module'%3A('query'%3A'HandleRequest'%2C'type'%3A'phrase')))))%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'interval'%3A'auto'%2C'query'%3A('language'%3A'kuery'%2C'query'%3A'')%2C'sort'%3A!('%40timestamp'%2C'desc'))");
  // clang-format on
}

TEST(KibanaURLGenerator, SeveralFilters) {
  auto const url = ConstructKibanaURL(kSomeServiceIndex,
                                      {{"module", Filter::Is{"HandleRequest"}},
                                       {"level", Filter::Is{"ERROR"}}});

  // clang-format off
  EXPECT_EQ(url, "https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters'%3A!()%2C'time'%3A('from'%3A'now-15m'%2C'to'%3A'now'))&_a=('columns'%3A!('_source')%2C'filters'%3A!(('%24state'%3A('store'%3A'appState')%2C'meta'%3A('alias'%3A!n%2C'disabled'%3A!f%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'key'%3A'module'%2C'negate'%3A!f%2C'params'%3A('query'%3A'HandleRequest')%2C'type'%3A'phrase'%2C'value'%3A'HandleRequest')%2C'query'%3A('match'%3A('module'%3A('query'%3A'HandleRequest'%2C'type'%3A'phrase'))))%2C('%24state'%3A('store'%3A'appState')%2C'meta'%3A('alias'%3A!n%2C'disabled'%3A!f%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'key'%3A'level'%2C'negate'%3A!f%2C'params'%3A('query'%3A'ERROR')%2C'type'%3A'phrase'%2C'value'%3A'ERROR')%2C'query'%3A('match'%3A('level'%3A('query'%3A'ERROR'%2C'type'%3A'phrase')))))%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'interval'%3A'auto'%2C'query'%3A('language'%3A'kuery'%2C'query'%3A'')%2C'sort'%3A!('%40timestamp'%2C'desc'))");
  // clang-format on
}

TEST(KibanaURLGenerator, FilterWithSeveralValues) {
  auto const url = ConstructKibanaURL(
      kSomeServiceIndex, {{"module", Filter::Is{"HandleRequest"}},
                          {"level", Filter::IsOneOf{"ERROR", "WARNING"}}});

  // clang-format off
  EXPECT_EQ(url, "https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters'%3A!()%2C'time'%3A('from'%3A'now-15m'%2C'to'%3A'now'))&_a=('columns'%3A!('_source')%2C'filters'%3A!(('%24state'%3A('store'%3A'appState')%2C'meta'%3A('alias'%3A!n%2C'disabled'%3A!f%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'key'%3A'module'%2C'negate'%3A!f%2C'params'%3A('query'%3A'HandleRequest')%2C'type'%3A'phrase'%2C'value'%3A'HandleRequest')%2C'query'%3A('match'%3A('module'%3A('query'%3A'HandleRequest'%2C'type'%3A'phrase'))))%2C('%24state'%3A('store'%3A'appState')%2C'meta'%3A('alias'%3A!n%2C'disabled'%3A!f%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'key'%3A'level'%2C'negate'%3A!f%2C'params'%3A!('ERROR'%2C'WARNING')%2C'type'%3A'phrase'%2C'value'%3A'ERROR%2CWARNING')%2C'query'%3A('bool'%3A('minimum_should_match'%3A1%2C'should'%3A!(('match_phrase'%3A('level'%3A'ERROR'))%2C('match_phrase'%3A('level'%3A'WARNING')))))))%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'interval'%3A'auto'%2C'query'%3A('language'%3A'kuery'%2C'query'%3A'')%2C'sort'%3A!('%40timestamp'%2C'desc'))");
  // clang-format on
}

TEST(KibanaURLGenerator, FilterIsNot) {
  auto const url =
      ConstructKibanaURL(kSomeServiceIndex, {{"level", Filter::IsNot{"INFO"}}});

  // clang-format off
  EXPECT_EQ(url, "https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters'%3A!()%2C'time'%3A('from'%3A'now-15m'%2C'to'%3A'now'))&_a=('columns'%3A!('_source')%2C'filters'%3A!(('%24state'%3A('store'%3A'appState')%2C'meta'%3A('alias'%3A!n%2C'disabled'%3A!f%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'key'%3A'level'%2C'negate'%3A!t%2C'params'%3A('query'%3A'INFO')%2C'type'%3A'phrase'%2C'value'%3A'INFO')%2C'query'%3A('match'%3A('level'%3A('query'%3A'INFO'%2C'type'%3A'phrase')))))%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'interval'%3A'auto'%2C'query'%3A('language'%3A'kuery'%2C'query'%3A'')%2C'sort'%3A!('%40timestamp'%2C'desc'))");
  // clang-format on
}

TEST(KibanaURLGenerator, FilterIsNotOf) {
  auto const url = ConstructKibanaURL(
      kSomeServiceIndex, {{"level", Filter::IsNotOneOf{"INFO", "WARNING"}}});

  // clang-format off
  EXPECT_EQ(url, "https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters'%3A!()%2C'time'%3A('from'%3A'now-15m'%2C'to'%3A'now'))&_a=('columns'%3A!('_source')%2C'filters'%3A!(('%24state'%3A('store'%3A'appState')%2C'meta'%3A('alias'%3A!n%2C'disabled'%3A!f%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'key'%3A'level'%2C'negate'%3A!t%2C'params'%3A!('INFO'%2C'WARNING')%2C'type'%3A'phrase'%2C'value'%3A'INFO%2CWARNING')%2C'query'%3A('bool'%3A('minimum_should_match'%3A1%2C'should'%3A!(('match_phrase'%3A('level'%3A'INFO'))%2C('match_phrase'%3A('level'%3A'WARNING')))))))%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'interval'%3A'auto'%2C'query'%3A('language'%3A'kuery'%2C'query'%3A'')%2C'sort'%3A!('%40timestamp'%2C'desc'))");
  // clang-format on
}

TEST(KibanaURLGenerator, QuerySearchWithFilter) {
  auto const url =
      ConstructKibanaURL(kSomeServiceIndex,
                         {{"level", Filter::IsNotOneOf{"INFO", "WARNING"}},
                          {"module", Filter::Is{"HandleRequest"}}},
                         Host::kProduction, QuerySearch{"\"Error during:\""});

  // clang-format off
  EXPECT_EQ(url, "https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters'%3A!()%2C'time'%3A('from'%3A'now-15m'%2C'to'%3A'now'))&_a=('columns'%3A!('_source')%2C'filters'%3A!(('%24state'%3A('store'%3A'appState')%2C'meta'%3A('alias'%3A!n%2C'disabled'%3A!f%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'key'%3A'level'%2C'negate'%3A!t%2C'params'%3A!('INFO'%2C'WARNING')%2C'type'%3A'phrase'%2C'value'%3A'INFO%2CWARNING')%2C'query'%3A('bool'%3A('minimum_should_match'%3A1%2C'should'%3A!(('match_phrase'%3A('level'%3A'INFO'))%2C('match_phrase'%3A('level'%3A'WARNING'))))))%2C('%24state'%3A('store'%3A'appState')%2C'meta'%3A('alias'%3A!n%2C'disabled'%3A!f%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'key'%3A'module'%2C'negate'%3A!f%2C'params'%3A('query'%3A'HandleRequest')%2C'type'%3A'phrase'%2C'value'%3A'HandleRequest')%2C'query'%3A('match'%3A('module'%3A('query'%3A'HandleRequest'%2C'type'%3A'phrase')))))%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'interval'%3A'auto'%2C'query'%3A('language'%3A'kuery'%2C'query'%3A'%22Error%20during%3A%22')%2C'sort'%3A!('%40timestamp'%2C'desc'))");
  // clang-format on
}

TEST(KibanaURLGenerator, WithTime) {
  const auto some_moment = std::chrono::system_clock::from_time_t(1585251769);
  const auto some_moment_day_ago = some_moment - std::chrono::hours(24);
  auto const url = ConstructKibanaURL(
      kSomeServiceIndex, {{"level", Filter::IsNotOneOf{"INFO", "WARNING"}}},
      some_moment_day_ago, some_moment);

  // clang-format off
  EXPECT_EQ(url, "https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters'%3A!()%2C'time'%3A('from'%3A'2020-03-25T19%3A42%3A49Z'%2C'to'%3A'2020-03-26T19%3A42%3A49Z'))&_a=('columns'%3A!('_source')%2C'filters'%3A!(('%24state'%3A('store'%3A'appState')%2C'meta'%3A('alias'%3A!n%2C'disabled'%3A!f%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'key'%3A'level'%2C'negate'%3A!t%2C'params'%3A!('INFO'%2C'WARNING')%2C'type'%3A'phrase'%2C'value'%3A'INFO%2CWARNING')%2C'query'%3A('bool'%3A('minimum_should_match'%3A1%2C'should'%3A!(('match_phrase'%3A('level'%3A'INFO'))%2C('match_phrase'%3A('level'%3A'WARNING')))))))%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'interval'%3A'auto'%2C'query'%3A('language'%3A'kuery'%2C'query'%3A'')%2C'sort'%3A!('%40timestamp'%2C'desc'))");
  // clang-format on
}

TEST(KibanaURLGenerator, EmptyFilter) {
  auto const url = ConstructKibanaURL(
      kSomeServiceIndex, {{"level", Filter::IsNotOneOf{}},
                          {"module", Filter::Is{"HandleRequest"}}});

  // clang-format off
  EXPECT_EQ(url, "https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters'%3A!()%2C'time'%3A('from'%3A'now-15m'%2C'to'%3A'now'))&_a=('columns'%3A!('_source')%2C'filters'%3A!(('%24state'%3A('store'%3A'appState')%2C'meta'%3A('alias'%3A!n%2C'disabled'%3A!f%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'key'%3A'module'%2C'negate'%3A!f%2C'params'%3A('query'%3A'HandleRequest')%2C'type'%3A'phrase'%2C'value'%3A'HandleRequest')%2C'query'%3A('match'%3A('module'%3A('query'%3A'HandleRequest'%2C'type'%3A'phrase')))))%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'interval'%3A'auto'%2C'query'%3A('language'%3A'kuery'%2C'query'%3A'')%2C'sort'%3A!('%40timestamp'%2C'desc'))");
  // clang-format on
}

TEST(KibanaURLGenerator, TestingEnvirement) {
  auto const url = ConstructKibanaURL(kSomeServiceIndex,
                                      {{"module", Filter::Is{"HandleRequest"}}},
                                      Host::kTesting);

  // clang-format off
  EXPECT_EQ(url, "https://kibana.taxi.tst.yandex-team.ru/app/kibana#/discover?_g=('filters'%3A!()%2C'time'%3A('from'%3A'now-15m'%2C'to'%3A'now'))&_a=('columns'%3A!('_source')%2C'filters'%3A!(('%24state'%3A('store'%3A'appState')%2C'meta'%3A('alias'%3A!n%2C'disabled'%3A!f%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'key'%3A'module'%2C'negate'%3A!f%2C'params'%3A('query'%3A'HandleRequest')%2C'type'%3A'phrase'%2C'value'%3A'HandleRequest')%2C'query'%3A('match'%3A('module'%3A('query'%3A'HandleRequest'%2C'type'%3A'phrase')))))%2C'index'%3A'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea'%2C'interval'%3A'auto'%2C'query'%3A('language'%3A'kuery'%2C'query'%3A'')%2C'sort'%3A!('%40timestamp'%2C'desc'))");
  // clang-format on
}

}  // namespace kibana_url_generator
