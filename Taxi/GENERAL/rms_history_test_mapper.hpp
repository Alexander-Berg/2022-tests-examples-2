// This is the example implementation of Enricher
// Please do not use it in production as this particular handler is not tested
// For higher loads. For more information check "external_enrich_mapper.hpp"

#pragma once

#include <eventus/mappers/details/external_enrich_mapper.hpp>

namespace eventus::mappers {

namespace handler = clients::rider_metrics_storage::v1_events_history::post;

typedef details::ClientWrapper<handler::Body, handler::Request,
                               handler::Response200>
    HistoryClientWrapper;

typedef details::ExternalEnrichMapper<HistoryClientWrapper> HistoryEnricher;

struct RmsHistoryMapper final : public HistoryEnricher {
  using Client = clients::rider_metrics_storage::Client;

  static constexpr const char* kName = "set_json_value";

 private:
  static std::shared_ptr<HistoryClientWrapper> CreateClientWrapperPtr(
      Client& client);

 public:
  virtual std::string GetName() const override { return kName; }

  RmsHistoryMapper(
      Client& client, const formats::json::Value& default_request,
      const std::unordered_map<std::string, std::string>& request_mapping,
      const std::unordered_map<std::string, std::string>& response_mapping)
      : HistoryEnricher{CreateClientWrapperPtr(client), default_request,
                        request_mapping, response_mapping} {}
};

}  // namespace eventus::mappers
