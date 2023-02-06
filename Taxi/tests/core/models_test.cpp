#include <gtest/gtest.h>

#include "models_test.hpp"

namespace plus_plaque::tests {

namespace {

experiments3::models::ExperimentResult MakeExperimentResult(
    const formats::json::Value& value) {
  experiments3::models::ExperimentResult exp_result;
  exp_result.value = value;
  return exp_result;
}

}  // namespace

core::Experiments MakeExperiments(
    const std::unordered_map<std::string, std::string>& mapped_results) {
  core::ExpMappedData mapped_data;
  for (const auto& [exp_name, exp_value] : mapped_results) {
    mapped_data[exp_name] =
        MakeExperimentResult(formats::json::FromString(exp_value));
  }
  return {std::move(mapped_data)};
}

core::Experiments MakeExperiments(
    const std::unordered_map<std::string, formats::json::Value>&
        mapped_results) {
  core::ExpMappedData mapped_data;
  for (const auto& [exp_name, exp_value] : mapped_results) {
    mapped_data[exp_name] = MakeExperimentResult(exp_value);
  }
  return {std::move(mapped_data)};
}

core::Experiments MakeExperiments() { return {core::ExpMappedData()}; }

core::TranslationData MakeTranslationData(const std::string& key) {
  return core::MakeTranslation({l10n::keysets::kClientMessages, key});
}

core::AttributedTranslationData MakeAttributedTranslationData(
    const std::string& key) {
  return core::MakeAttributedTranslation({l10n::keysets::kClientMessages, key});
}

core::Wallet MakeWallet(const std::string& wallet_id,
                        const std::string& balance,
                        const std::string& currency) {
  return {wallet_id, currency,
          decimal64::Decimal<4>::FromStringPermissive(balance)};
}

}  // namespace plus_plaque::tests

namespace plus_plaque::core {

bool operator==(const std::optional<TankerKey>& left,
                const std::optional<TankerKey>& right) {
  if ((left && !right) || (!left && right)) {
    return false;
  }
  if (!left && !right) {
    return true;
  }
  return left->keyset == right->keyset && left->key == right->key &&
         left->args == right->args && left->count == right->count;
}

bool operator==(const TranslationData& left, const TranslationData& right) {
  return left.type == right.type && left.text == right.text &&
         left.main_key == right.main_key &&
         left.fallback_key == right.fallback_key;
}

bool operator==(const std::optional<TranslationData>& left,
                const std::optional<TranslationData>& right) {
  if ((left && !right) || (!left && right)) {
    return false;
  }
  if (!left && !right) {
    return true;
  }
  return left.value() == right.value();
}

bool operator==(const Wallet& left, const Wallet& right) {
  return left.wallet_id == right.wallet_id && left.currency == right.currency &&
         left.balance == right.balance;
}

void AssertWallet(const std::optional<core::Wallet>& left,
                  const std::optional<core::Wallet>& right) {
  if (!left && !right) {
    SUCCEED();
    return;
  }

  if (!left || !right) {
    FAIL();
    return;
  }

  ASSERT_EQ(left->wallet_id, right->wallet_id);
  ASSERT_EQ(left->balance, right->balance);
  ASSERT_EQ(left->currency, right->currency);
}

}  // namespace plus_plaque::core
