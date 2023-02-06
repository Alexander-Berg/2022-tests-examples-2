#pragma once

#include <string>

#include <userver/formats/json/value_builder.hpp>

namespace metrix::labels {

struct EmptyLabels {
  std::string metric_name{""};
};

formats::json::ValueBuilder ValueBuilderAt(formats::json::ValueBuilder& builder,
                                           const EmptyLabels& key);

bool operator==(const EmptyLabels& lhs, const EmptyLabels& rhs);

struct Labels0 {
  std::string metric_name{""};
  std::string agglomeration{""};
  std::string service{"taxi"};
};

formats::json::ValueBuilder ValueBuilderAt(formats::json::ValueBuilder& builder,
                                           const Labels0& key);

bool operator==(const Labels0& lhs, const Labels0& rhs);

struct Labels1 {
  std::string metric_name{""};
  std::string agglomeration{""};
  std::string dispatch_statuses{""};
  std::string tariff_group{""};
  std::string service{"taxi"};
};

formats::json::ValueBuilder ValueBuilderAt(formats::json::ValueBuilder& builder,
                                           const Labels1& key);

bool operator==(const Labels1& lhs, const Labels1& rhs);

}

namespace std {
template <>
struct hash<::metrix::labels::EmptyLabels> {
  size_t operator()(const ::metrix::labels::EmptyLabels& key) const noexcept;
};

template <>
struct hash<::metrix::labels::Labels0> {
  size_t operator()(const ::metrix::labels::Labels0& key) const noexcept;
};

template <>
struct hash<::metrix::labels::Labels1> {
  size_t operator()(const ::metrix::labels::Labels1& key) const noexcept;
};

}  // namespace std
