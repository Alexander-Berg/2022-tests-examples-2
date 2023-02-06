#pragma once

#include <exception>
#include <string>
#include <unordered_map>
#include <vector>

#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>

#include <clients/billing-subventions-x/client_mock_base.hpp>
#include <clients/billing-subventions-x/responses.hpp>

#include "common.hpp"

namespace mocks {

namespace bsx = clients::billing_subventions_x;
class BSXClient final : public bsx::ClientMockBase {
 public:
  virtual bsx::v2_rules_match::post::Response V2RulesMatch(
      const bsx::v2_rules_match::post::Request& request,
      const bsx::CommandControl&) const final {
    calls_["V2RulesMatch"].push_back(request.GetBody());

    if (auto it = responses.find("V2RulesMatch"); it != responses.end()) {
      EXPECT_LT(calls_counter_["V2RulesMatch"], it->second.size());

      return bsx::v2_rules_match::post::Parse(
          formats::json::FromString(
              it->second.at(calls_counter_["V2RulesMatch"]++)),
          formats::parse::To<bsx::v2_rules_match::post::Response200>());
    } else {
      return {};
    }
  }
  virtual bsx::v2_rules_select::post::Response V2RulesSelect(
      const bsx::v2_rules_select::post::Request& request,
      const bsx::CommandControl&) const final {
    calls_["V2RulesSelect"].push_back(request.GetBody());

    return {};
  }

  std::multiset<std::string> GetCalls(const std::string& handle) const {
    const auto it = calls_.find(handle);
    if (it == calls_.end()) {
      return {};
    }

    auto as_vector = it->second;

    return std::multiset<std::string>(as_vector.begin(), as_vector.end());
  }

  std::unordered_map<std::string, std::vector<std::string>> responses;

 private:
  mutable std::unordered_map<std::string, std::vector<std::string>> calls_;
  mutable std::unordered_map<std::string, uint32_t> calls_counter_;
};

}  // namespace mocks
