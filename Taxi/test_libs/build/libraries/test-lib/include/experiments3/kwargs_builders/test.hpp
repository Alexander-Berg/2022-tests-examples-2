#pragma once

#include <string>
#include <unordered_set>

#include <experiments3_common/models/kwargs.hpp>
#include <ua_parser/application.hpp>

#include <experiments3/kwargs_names.hpp>

namespace experiments3::kwargs_builders {

namespace impl {
class TestFlatKwargs final: public experiments3::models::KwargsBase {
 public:
  enum class Index: size_t {
    kName,
  };
  static constexpr size_t kNKwargs = 1;
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

class Test final: public ::experiments3::models::KwargsBuilderWithConsumer {
 public:
  using KwargName = experiments3::models::KwargName;
  using KwargValue = experiments3::models::KwargValue;

  static constexpr auto kConsumer = "consumer_from_lib";
  const std::string& GetConsumer() const override;

  const experiments3::models::Kwargs& Build() const override;

  void UpdateName(const models::KwargTypeString& name);
  void UpdateName(models::KwargTypeString&& name);

  const ::experiments3::models::KwargsSchema& GetSchema() const override;

 private:
  // `ignore_schema` not used for flat kwargs
  void Update(const KwargName& name, KwargValue value,
              bool /* ignore_schema */) override;

  impl::TestFlatKwargs kwargs_;
};
}  // namespace experiments3::kwargs_builders
