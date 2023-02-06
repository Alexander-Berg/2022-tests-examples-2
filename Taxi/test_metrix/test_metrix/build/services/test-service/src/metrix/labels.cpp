#include <metrix/labels.hpp>

#include <boost/functional/hash.hpp>

#include <userver/utils/statistics/percentile_format_json.hpp>

namespace {
struct LabelDescr {
  std::string value;
  std::optional<std::string> name;
};

template <typename... Args>
bool Any(Args&&...) {
  return !!sizeof...(Args);
}

template <typename T, typename Arg>
auto At(T&& builder, Arg&& first) {
  if (first.name) {
    ::utils::statistics::SolomonChildrenAreLabelValues(builder, *first.name);
  }
  return builder[first.value];
}

template <typename T, typename Arg, typename... Args>
auto At(T&& builder, Arg&& first, Args&&... rest) {
  if (Any(rest...)) {
    if (first.name) {
      ::utils::statistics::SolomonChildrenAreLabelValues(builder, *first.name);
    }
    return At(builder[first.value], std::forward<Args>(rest)...);
  } else {
    return At(std::forward<T>(builder), std::forward<Arg>(first));
  }
}

auto Introspect(const ::metrix::labels::EmptyLabels& descr) {
  return std::tie(descr.metric_name);
}

auto Introspect(const ::metrix::labels::Labels0& descr) {
  return std::tie(descr.metric_name, descr.agglomeration, descr.service);
}

auto Introspect(const ::metrix::labels::Labels1& descr) {
  return std::tie(descr.metric_name, descr.agglomeration,
                  descr.dispatch_statuses, descr.tariff_group, descr.service);
}

}  // namespace

namespace metrix::labels {
bool operator==(const EmptyLabels& lhs, const EmptyLabels& rhs) {
  return Introspect(lhs) == Introspect(rhs);
}

formats::json::ValueBuilder ValueBuilderAt(formats::json::ValueBuilder& builder,
                                           const EmptyLabels& key) {
  return At(builder, LabelDescr{key.metric_name, std::nullopt});
}

bool operator==(const Labels0& lhs, const Labels0& rhs) {
  return Introspect(lhs) == Introspect(rhs);
}

formats::json::ValueBuilder ValueBuilderAt(formats::json::ValueBuilder& builder,
                                           const Labels0& key) {
  return At(builder, LabelDescr{key.metric_name, std::nullopt},
            LabelDescr{key.agglomeration, "agglomeration"},
            LabelDescr{key.service, "service"});
}

bool operator==(const Labels1& lhs, const Labels1& rhs) {
  return Introspect(lhs) == Introspect(rhs);
}

formats::json::ValueBuilder ValueBuilderAt(formats::json::ValueBuilder& builder,
                                           const Labels1& key) {
  return At(builder, LabelDescr{key.metric_name, std::nullopt},
            LabelDescr{key.agglomeration, "agglomeration"},
            LabelDescr{key.dispatch_statuses, "dispatch_statuses"},
            LabelDescr{key.tariff_group, "tariff_group"},
            LabelDescr{key.service, "service"});
}

}

namespace std {
size_t hash<::metrix::labels::EmptyLabels>::operator()(
    const ::metrix::labels::EmptyLabels& key) const noexcept {
  std::size_t result = 0;

  boost::hash_combine(result, key.metric_name);
  return result;
}

size_t hash<::metrix::labels::Labels0>::operator()(
    const ::metrix::labels::Labels0& key) const noexcept {
  std::size_t result = 0;

  boost::hash_combine(result, key.metric_name);
  boost::hash_combine(result, key.agglomeration);
  boost::hash_combine(result, key.service);
  return result;
}

size_t hash<::metrix::labels::Labels1>::operator()(
    const ::metrix::labels::Labels1& key) const noexcept {
  std::size_t result = 0;

  boost::hash_combine(result, key.metric_name);
  boost::hash_combine(result, key.agglomeration);
  boost::hash_combine(result, key.dispatch_statuses);
  boost::hash_combine(result, key.tariff_group);
  boost::hash_combine(result, key.service);
  return result;
}

;

}  // namespace std
