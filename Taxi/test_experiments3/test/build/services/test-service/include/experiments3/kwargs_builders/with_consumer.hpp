#pragma once

#include <string>
#include <unordered_set>

#include <experiments3_common/models/kwargs.hpp>
#include <ua_parser/application.hpp>

#include <experiments3/kwargs_names.hpp>

namespace experiments3::kwargs_builders {

namespace impl {
class WithConsumerFlatKwargs final: public experiments3::models::KwargsBase {
 public:
  enum class Index: size_t {
    kApplication,
    kApplicationBrand,
    kApplicationFullVersion,
    kApplicationName,
    kApplicationPlatform,
    kApplicationPlatformFullVersion,
    kApplicationPlatformVersion,
    kBuildType,
    kDeviceMake,
    kDeviceModel,
    kField1,
    kField2,
    kField3,
    kVersion,
  };
  static constexpr size_t kNKwargs = 14;
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

class WithConsumer final
    : public ::experiments3::models::KwargsBuilderWithConsumer,
      public ::experiments3::models::KwargsBuilderWithAppSupport {
 public:
  using KwargName = experiments3::models::KwargName;
  using KwargValue = experiments3::models::KwargValue;

  static constexpr auto kConsumer = "consumer";
  const std::string& GetConsumer() const override;

  const experiments3::models::Kwargs& Build() const override;

  void UpdateField1(const models::KwargTypeString& field1);
  void UpdateField1(models::KwargTypeString&& field1);
  void UpdateField2(const models::KwargTypeDouble& field2);
  void UpdateField2(models::KwargTypeDouble&& field2);
  void UpdateField3(const models::KwargTypeInt& field3);
  void UpdateField3(models::KwargTypeInt&& field3);

  const ::experiments3::models::KwargsSchema& GetSchema() const override;

 private:
  // `ignore_schema` not used for flat kwargs
  void Update(const KwargName& name, KwargValue value,
              bool /* ignore_schema */) override;

  impl::WithConsumerFlatKwargs kwargs_;
};
}  // namespace experiments3::kwargs_builders
