#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include <taxi_config/taxi_config.hpp>
#include <taxi_config/variables/USERVER_SAMPLE_CLIENT_QOS.hpp>

UTEST(Config, DefaultTaxiConfig) {
  const auto config = dynamic_config::GetDefaultSnapshot();
  EXPECT_EQ(config[taxi_config::USERVER_SAMPLE_CLIENT_QOS]
                .GetDefaultValue()
                .timeout_ms,
            std::chrono::milliseconds{200});
}

namespace {

template <typename T, typename = void>
struct has_candidates_base_url : std::false_type {};

template <typename T>
struct has_candidates_base_url<
    T, utils::void_t<decltype(std::declval<T>().candidates_base_url)>>
    : std::true_type {};

}  // namespace

TEST(Config, CodegenIgnoreNames) {
  EXPECT_FALSE(has_candidates_base_url<taxi_config::TaxiConfig>::value);
}
