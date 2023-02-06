#pragma once

#include <core/experiments.hpp>
#include <core/sdk_client.hpp>
#include <core/translator.hpp>
#include <core/wallets.hpp>

namespace plus_plaque::core {
const std::string kExpEnabled = R"({"enabled": true})";
const std::string kExpDisabled = R"({"enabled": false})";
const std::string kDefaultClientId = "taxi.test";
const std::string kDefaultServiceId = "taxi";
const std::string kDefaultPlatform = "ios";

const core::SDKVersion kSDKVersion{1, 0, 0};
const core::SDKClient kDefaultSdkClient{
    kDefaultClientId, kDefaultServiceId, kDefaultPlatform, kSDKVersion, {}};
}  // namespace plus_plaque::core

namespace plus_plaque::tests {

namespace defaults {
const std::string kDefaultCurrency = "RUB";
const std::string kDefaultLocale = "ru";
}  // namespace defaults

/// @brief Makes Experiments out of pairs of `{exp_name, exp_value}`.
core::Experiments MakeExperiments(
    const std::unordered_map<std::string, std::string>& mapped_results);
core::Experiments MakeExperiments(
    const std::unordered_map<std::string, formats::json::Value>&
        mapped_results);
core::Experiments MakeExperiments();

core::TranslationData MakeTranslationData(const std::string& key);

core::AttributedTranslationData MakeAttributedTranslationData(
    const std::string& key);

core::Wallet MakeWallet(
    const std::string& wallet_id, const std::string& balance,
    const std::string& currency = defaults::kDefaultCurrency);

}  // namespace plus_plaque::tests

namespace plus_plaque::core {

bool operator==(const TranslationData& left, const TranslationData& right);

bool operator==(const std::optional<TankerKey>& left,
                const std::optional<TankerKey>& right);

bool operator==(const std::optional<TranslationData>& left,
                const std::optional<TranslationData>& right);

bool operator==(const Wallet& left, const Wallet& right);
void AssertWallet(const std::optional<core::Wallet>& left,
                  const std::optional<core::Wallet>& right);

}  // namespace plus_plaque::core
