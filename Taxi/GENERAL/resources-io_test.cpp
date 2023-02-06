#include <userver/utest/utest.hpp>

#include <userver/formats/yaml/serialize.hpp>
#include <userver/yaml_config/yaml_config.hpp>

#include <agl/core/constants.hpp>
#include <agl/sourcing/resources-io.hpp>

namespace agl::sourcing::tests {

namespace {

std::string ToString(clients::http::HttpMethod method) {
  switch (method) {
    case clients::http::HttpMethod::kDelete:
      return "delete";
    case clients::http::HttpMethod::kGet:
      return "GET";
    case clients::http::HttpMethod::kHead:
      return "Head";
    case clients::http::HttpMethod::kPost:
      return "POST";
    case clients::http::HttpMethod::kPut:
      return "put";
    case clients::http::HttpMethod::kPatch:
      return "Patch";
    case clients::http::HttpMethod::kOptions:
      return "opTIONs";
  }
  throw std::runtime_error("unexpected method");
}

}  // namespace

class ResourcesYamlParsing
    : public testing::TestWithParam<std::tuple<
          std::string, std::optional<std::string>, clients::http::HttpMethod,
          std::optional<int>, std::optional<std::string>, std::optional<int>,
          std::optional<std::string>, std::optional<std::string>>> {};

TEST_P(ResourcesYamlParsing, Test) {
  auto [url, tvm_name, method, timeout, timeout_taxi_config, max_retries,
        max_retries_taxi_config, qos_taxi_config] = GetParam();

  std::string in_str;
  in_str += ("url: " + url + "\n");
  if (tvm_name) in_str += ("tvm-name: " + *tvm_name + "\n");
  in_str += ("method: " + ToString(method) + "\n");
  if (timeout) in_str += ("timeout: " + std::to_string(*timeout) + "\n");
  if (timeout_taxi_config)
    in_str += ("timeout-taxi-config: " + *timeout_taxi_config + "\n");
  if (max_retries)
    in_str += ("max-retries: " + std::to_string(*max_retries) + "\n");
  if (max_retries_taxi_config)
    in_str += ("max-retries-taxi-config: " + *max_retries_taxi_config + "\n");
  if (qos_taxi_config) in_str += ("qos-config: " + *qos_taxi_config + "\n");

  const yaml_config::YamlConfig input{formats::yaml::FromString(in_str), {}};

  const auto parsed = input.As<Resource>();
  EXPECT_EQ(parsed.url.Template(), url);
  EXPECT_EQ(parsed.tvm_name, tvm_name);
  EXPECT_EQ(parsed.method, method);
  EXPECT_EQ(parsed.timeout, timeout);
  EXPECT_EQ(parsed.timeout_taxi_config, timeout_taxi_config);
  EXPECT_EQ(parsed.max_retries, max_retries);
  EXPECT_EQ(parsed.max_retries_taxi_config, max_retries_taxi_config);
  EXPECT_EQ(parsed.qos_taxi_config, qos_taxi_config);
}

TEST(TestResourcesIO, TestQos) {
  const std::string resources_contents = R"(
    - id: foo-get
      url: foo.com/get
      tvm-name: foo
      method: get
      qos-config: FOO_QOS
      caching-enabled: true
    - id: foo-post
      url: foo.com/post
      tvm-name: foo
      method: post
      qos-config: FOO_QOS
      rps-limit: 3000
    - id: bar-post
      url: bar.com/post
      tvm-name: bar
      method: post
      timeout-taxi-config: LEGACY_BAR_TIMEOUT_MS
      max-retries-taxi-config: LEGACY_BAR_RETRIES
      qos-config: BAR_QOS
  )";
  const yaml_config::YamlConfig input{
      formats::yaml::FromString(resources_contents), {}};

  const auto parsed = input.As<ResourcesStorage>();

  const auto& foo_get = parsed.GetResource("foo-get");
  EXPECT_EQ(foo_get.qos_taxi_config, "FOO_QOS");
  const auto& foo_post = parsed.GetResource("foo-post");
  EXPECT_EQ(foo_post.qos_taxi_config, "FOO_QOS");
  const auto& bar_post = parsed.GetResource("bar-post");
  EXPECT_EQ(bar_post.qos_taxi_config, "BAR_QOS");

  const std::set<std::string> expected_configs{
      "FOO_QOS", "BAR_QOS", "LEGACY_BAR_TIMEOUT_MS", "LEGACY_BAR_RETRIES"};
  const std::set<std::string> expected_qos_configs{"FOO_QOS", "BAR_QOS"};

  ::agl::core::variant::Dependencies deps;
  parsed.GetDependencies(deps);
  EXPECT_EQ(deps.GetItems(::agl::core::kConfigsDep), expected_configs);
  EXPECT_EQ(deps.GetItems(::agl::core::kQosConfigsDep), expected_qos_configs);
}

INSTANTIATE_TEST_SUITE_P(
    YamlParsing, ResourcesYamlParsing,
    testing::Combine(testing::Values(std::string("test-url")),
                     testing::Values(std::nullopt, "some-tvm"),
                     testing::Values(clients::http::HttpMethod::kDelete,
                                     clients::http::HttpMethod::kGet,
                                     clients::http::HttpMethod::kHead,
                                     clients::http::HttpMethod::kPost,
                                     clients::http::HttpMethod::kPut,
                                     clients::http::HttpMethod::kPatch,
                                     clients::http::HttpMethod::kOptions),
                     testing::Values(std::nullopt, 10),
                     testing::Values(std::nullopt, "timeout-config"),
                     testing::Values(std::nullopt, 20),
                     testing::Values(std::nullopt, "retires-config"),
                     testing::Values(std::nullopt, "qos-config")));

}  // namespace agl::sourcing::tests
