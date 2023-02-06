#include "test_params.hpp"

#include <experiments3/kwargs_builders/contractor_merch_payments_test_params.hpp>

namespace contractor_merch_payments::utils {

experiments3::ContractorMerchPaymentsTestParams::Value GetTestParams(
    const std::string& park_id, const std::string& contractor_id,
    const std::optional<std::string>& merchant_id,
    const experiments3::models::CacheManager& experiments3) {
  experiments3::kwargs_builders::ContractorMerchPaymentsTestParams
      kwargs_builder;
  kwargs_builder.UpdateParkId(park_id);
  kwargs_builder.UpdateContractorId(contractor_id);
  if (merchant_id) {
    kwargs_builder.UpdateMerchantId(*merchant_id);
  }

  auto result =
      experiments3.GetValue<experiments3::ContractorMerchPaymentsTestParams>(
          kwargs_builder);
  if (!result) {
    throw std::runtime_error(
        "GetTestParams. No config for ContractorMerchPaymentsTestParams");
  }

  return *result;
}

}  // namespace contractor_merch_payments::utils
