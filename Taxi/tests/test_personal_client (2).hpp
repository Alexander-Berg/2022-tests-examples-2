#pragma once

#include "clients/personal/personal_client_interface.hpp"

namespace callcenter_stats::unit_tests {

class TestPersonalClient : public clients::IPersonalClient {
 public:
  std::optional<std::string> GetPhoneIdByPhone(
      const std::string& phone) const override {
    if (!phone.empty()) {
      return phone;
    }
    return std::nullopt;
  }

  std::string StorePhone(const std::string& phone) const override {
    return phone;
  }

  std::unordered_map<std::string, std::string> RetrievePhonesByPhoneIds(
      const std::vector<std::string>& phone_ids) const override {
    std::unordered_map<std::string, std::string> result;
    result.reserve(phone_ids.size());
    for (const auto& phone_id : phone_ids) {
      result[phone_id] = phone_id;
    }
    return result;
  }

  std::unordered_map<std::string, std::string> BulkStorePhone(
      std::vector<std::string> phones, bool use_unsuccessfull_phones,
      size_t chunk_size, bool use_async) const override {
    std::unordered_map<std::string, std::string> result;
    result.reserve(phones.size());
    for (const auto& phone : phones) {
      result[phone] = phone;
    }
    return result;
  }
};
}  // namespace callcenter_stats::unit_tests
