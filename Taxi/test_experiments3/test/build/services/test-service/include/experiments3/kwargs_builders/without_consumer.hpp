#pragma once

#include <string>
#include <unordered_set>

#include <experiments3_common/models/kwargs.hpp>
#include <ua_parser/application.hpp>

#include <experiments3/kwargs_names.hpp>

namespace experiments3::kwargs_builders {

namespace impl {
class DeprecatedWithoutConsumerFlatKwargs final
    : public experiments3::models::KwargsBase {
 public:
  enum class Index: size_t {
    kFApplication,
    kFApplicationVersion,
    kFBool,
    kFDouble,
    kFInt,
    kFPoint,
    kFSetInt,
    kFSetString,
    kFString,
    kFTimepoint,
  };
  static constexpr size_t kNKwargs = 10;
  using KwargName = experiments3::models::KwargName;
  using KwargValue = experiments3::models::KwargValue;
  using ValuesArray = std::array<std::optional<KwargValue>, kNKwargs>;
  using IndexByName = std::unordered_map<std::string, Index>;

  void UpdateByIndex(Index index, KwargValue value);
  void Update(const KwargName& name, KwargValue value) override;
  const KwargValue* FindOptional(const KwargName& name) const override;
  void ForEach(const ForEachFunction& func) const override;

 private:
  ValuesArray values_;
};
}

// Specify consumer in kwargs builder's config yaml to avoid deprecated
// KwargsBuilder usage
class DeprecatedWithoutConsumer final
    : public ::experiments3::models::KwargsBuilderBase {
 public:
  using KwargName = experiments3::models::KwargName;
  using KwargValue = experiments3::models::KwargValue;

  const experiments3::models::Kwargs& Build() const override;

  void UpdateFApplication(const models::KwargTypeString& f_application);
  void UpdateFApplication(models::KwargTypeString&& f_application);
  void UpdateFApplicationVersion(
      const models::KwargTypeAppVersion& f_application_version);
  void UpdateFApplicationVersion(
      models::KwargTypeAppVersion&& f_application_version);
  void UpdateFBool(const models::KwargTypeBool& f_bool);
  void UpdateFBool(models::KwargTypeBool&& f_bool);
  void UpdateFDouble(const models::KwargTypeDouble& f_double);
  void UpdateFDouble(models::KwargTypeDouble&& f_double);
  void UpdateFInt(const models::KwargTypeInt& f_int);
  void UpdateFInt(models::KwargTypeInt&& f_int);
  void UpdateFPoint(const models::KwargTypePoint& f_point);
  void UpdateFPoint(models::KwargTypePoint&& f_point);
  void UpdateFSetInt(const models::KwargTypeSetInt& f_set_int);
  void UpdateFSetInt(models::KwargTypeSetInt&& f_set_int);
  void UpdateFSetString(const models::KwargTypeSetString& f_set_string);
  void UpdateFSetString(models::KwargTypeSetString&& f_set_string);
  void UpdateFString(const models::KwargTypeString& f_string);
  void UpdateFString(models::KwargTypeString&& f_string);
  void UpdateFTimepoint(const models::KwargTypeTimePoint& f_timepoint);
  void UpdateFTimepoint(models::KwargTypeTimePoint&& f_timepoint);

  const ::experiments3::models::KwargsSchema& GetSchema() const override;
  bool ShouldAddDefaultHostKwargs() const override { return false; }
  bool ShouldAddDefaultBaseKwargs() const override { return false; }

 private:
  // `ignore_schema` not used for flat kwargs
  void Update(const KwargName& name, KwargValue value,
              bool /* ignore_schema */) override;

  impl::DeprecatedWithoutConsumerFlatKwargs kwargs_;
};
}  // namespace experiments3::kwargs_builders
