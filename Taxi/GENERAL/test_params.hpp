#pragma once

#include <optional>
#include <string>

#include <experiments3/contractor_merch_payments_test_params.hpp>
#include <experiments3/models/cache_manager.hpp>

namespace contractor_merch_payments::utils {

experiments3::ContractorMerchPaymentsTestParams::Value GetTestParams(
    const std::string& park_id, const std::string& contractor_id,
    const std::optional<std::string>& merchant_id,
    const experiments3::models::CacheManager& experiments3);

}  // namespace contractor_merch_payments::utils
