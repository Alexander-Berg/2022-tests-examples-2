#include <optional>
#include <unordered_map>
#include <userver/formats/json.hpp>

#include <userver/utest/utest.hpp>

#include "verification/detect_currency.hpp"

namespace {
static std::unordered_map<std::string, std::string> kBinToCurrencyMap{
    {"123456", "UZS"}};
constexpr auto kPayloadBad = "[1,2,3]";
constexpr auto kPayloadNoCardNumber = "{\"foo\": \"bar\"}";
constexpr auto kPayloadCardNumberNotString =
    "{\"card_number\": {\"foo\": \"bar\"}}";
constexpr auto kPayloadNullCardNumber = "{\"card_number\": null}";
constexpr auto kPayloadCardNumber = "{\"card_number\": \"654321****987\"}";
constexpr auto kPayloadUzCardNumber = "{\"card_number\": \"123456****789\"}";
}  // namespace

namespace cardstorage::tests {

namespace verification = cardstorage::verification;
namespace json = formats::json;

class MockConfig : public verification::Config {
 public:
  MockConfig(verification::DetectCurrencyAlgo algo)
      : algo_(algo), bin_to_currency_map_(kBinToCurrencyMap) {}
  verification::DetectCurrencyAlgo GetDetectCurrencyAlgo() { return algo_; }

  std::optional<std::string> GetBinCurrency(const std::string& bin) {
    auto it = bin_to_currency_map_.find(bin);
    if (it == bin_to_currency_map_.end()) {
      return std::nullopt;
    }
    return {it->second};
  }

 private:
  verification::DetectCurrencyAlgo algo_;
  std::unordered_map<std::string, std::string> bin_to_currency_map_;
};

TEST(TestVerificationDetectCurrency, TestWhenDisabled) {
  MockConfig config{verification::DetectCurrencyAlgo::kNone};
  std::optional<std::string> expected_currency{};
  auto actual_currency = verification::DetectCurrency(
      config, {json::FromString(kPayloadUzCardNumber)});
  ASSERT_EQ(actual_currency.value_or(""), expected_currency.value_or(""));
}

TEST(TestVerificationDetectCurrency, TestByBinWhenNoPayload) {
  MockConfig config{verification::DetectCurrencyAlgo::kByBin};
  std::optional<std::string> expected_currency{};
  auto actual_currency = verification::DetectCurrency(config, {});
  ASSERT_EQ(actual_currency.value_or(""), expected_currency.value_or(""));
}

TEST(TestVerificationDetectCurrency, TestByBinWhenBadPayload) {
  MockConfig config{verification::DetectCurrencyAlgo::kByBin};
  std::optional<std::string> expected_currency{};
  auto actual_currency =
      verification::DetectCurrency(config, {json::FromString(kPayloadBad)});
  ASSERT_EQ(actual_currency.value_or(""), expected_currency.value_or(""));
}

TEST(TestVerificationDetectCurrency, TestByBinWhenNoCardNumber) {
  MockConfig config{verification::DetectCurrencyAlgo::kByBin};
  std::optional<std::string> expected_currency{};
  auto actual_currency = verification::DetectCurrency(
      config, {json::FromString(kPayloadNoCardNumber)});
  ASSERT_EQ(actual_currency.value_or(""), expected_currency.value_or(""));
}

TEST(TestVerificationDetectCurrency, TestByBinWhenCardNumberNotString) {
  MockConfig config{verification::DetectCurrencyAlgo::kByBin};
  std::optional<std::string> expected_currency{};
  auto actual_currency = verification::DetectCurrency(
      config, {json::FromString(kPayloadCardNumberNotString)});
  ASSERT_EQ(actual_currency.value_or(""), expected_currency.value_or(""));
}

TEST(TestVerificationDetectCurrency, TestByBinWhenNullCardNumber) {
  MockConfig config{verification::DetectCurrencyAlgo::kByBin};
  std::optional<std::string> expected_currency{};
  auto actual_currency = verification::DetectCurrency(
      config, {json::FromString(kPayloadNullCardNumber)});
  ASSERT_EQ(actual_currency.value_or(""), expected_currency.value_or(""));
}

TEST(TestVerificationDetectCurrency, TestByBinWhenNotUzCardNumber) {
  MockConfig config{verification::DetectCurrencyAlgo::kByBin};
  std::optional<std::string> expected_currency{};
  auto actual_currency = verification::DetectCurrency(
      config, {json::FromString(kPayloadCardNumber)});
  ASSERT_EQ(actual_currency.value_or(""), expected_currency.value_or(""));
}

TEST(TestVerificationDetectCurrency, TestByBinWhenUzCardNumber) {
  MockConfig config{verification::DetectCurrencyAlgo::kByBin};
  std::optional<std::string> expected_currency{"UZS"};
  auto actual_currency = verification::DetectCurrency(
      config, {json::FromString(kPayloadUzCardNumber)});
  ASSERT_EQ(actual_currency.value_or(""), expected_currency.value_or(""));
}

}  // namespace cardstorage::tests
