#pragma once

#include <string>
#include <unordered_set>

#include <experiments3_common/models/kwargs.hpp>
#include <ua_parser/application.hpp>

#include <experiments3/kwargs_names.hpp>

namespace experiments3::kwargs_builders {

namespace impl {
class WithLibraryIncludeFlatKwargs final
    : public experiments3::models::KwargsBase {
 public:
  enum class Index: size_t {
    kCommonKwarg,
    kUniqueKwarg,
  };
  static constexpr size_t kNKwargs = 2;
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

class WithLibraryInclude final
    : public ::experiments3::models::KwargsBuilderWithConsumer {
 public:
  using KwargName = experiments3::models::KwargName;
  using KwargValue = experiments3::models::KwargValue;

  static constexpr auto kConsumer = "consumer_from_service";
  const std::string& GetConsumer() const override;

  const experiments3::models::Kwargs& Build() const override;

  void UpdateCommonKwarg(const models::KwargTypeInt& common_kwarg);
  void UpdateCommonKwarg(models::KwargTypeInt&& common_kwarg);
  void UpdateUniqueKwarg(const models::KwargTypeInt& unique_kwarg);
  void UpdateUniqueKwarg(models::KwargTypeInt&& unique_kwarg);

  const ::experiments3::models::KwargsSchema& GetSchema() const override;

 private:
  // `ignore_schema` not used for flat kwargs
  void Update(const KwargName& name, KwargValue value,
              bool /* ignore_schema */) override;

  impl::WithLibraryIncludeFlatKwargs kwargs_;
};
}  // namespace experiments3::kwargs_builders
