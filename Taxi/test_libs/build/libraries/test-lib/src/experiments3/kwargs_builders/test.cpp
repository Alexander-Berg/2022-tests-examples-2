#include <experiments3/kwargs_builders/test.hpp>

#include <userver/utils/assert.hpp>

namespace experiments3::kwargs_builders {

namespace impl {

namespace {

using KwargName = experiments3::models::KwargName;
using KwargValue = experiments3::models::KwargValue;

const TestFlatKwargs::IndexByName kIndexByName = {
    {kwargs_names::kName, TestFlatKwargs::Index::kName},
};

}

void TestFlatKwargs::UpdateByIndex(Index index, KwargValue value) {
  values_[static_cast<size_t>(index)] = std::move(value);
}
void TestFlatKwargs::Update(const KwargName& name, KwargValue value) {
  values_[static_cast<size_t>(kIndexByName.at(name))] = std::move(value);
}
const KwargValue* TestFlatKwargs::FindOptional(const KwargName& name) const {
  auto it = kIndexByName.find(name);
  if (it == kIndexByName.end()) {
    return nullptr;
  }
  const auto& value_opt = values_[static_cast<size_t>(it->second)];
  if (!value_opt) {
    return nullptr;
  }
  return &value_opt.value();
}

void TestFlatKwargs::ForEach(const ForEachFunction& func) const {
  for (const auto& [name, index] : kIndexByName) {
    if (const auto& value_opt = values_[static_cast<size_t>(index)]) {
      func(name, *value_opt);
    }
  }
}

}

const ::experiments3::models::KwargsSchema& Test::GetSchema() const {
  static const auto kSchema = []() {
    ::experiments3::models::KwargsSchema schema = {
        {kwargs_names::kName, {typeid(models::KwargTypeString), true, true}},
    };
    schema.insert(
        experiments3::models::schema_extensions::kDefaultSchemaExtension
            .begin(),
        experiments3::models::schema_extensions::kDefaultSchemaExtension.end());
    return schema;
  }();
  return kSchema;
}

const std::string& Test::GetConsumer() const {
  static const std::string kConsumerName{kConsumer};
  return kConsumerName;
}

void Test::UpdateName(const models::KwargTypeString& name) {
  kwargs_.UpdateByIndex(impl::TestFlatKwargs::Index::kName, name);
}

void Test::UpdateName(models::KwargTypeString&& name) {
  kwargs_.UpdateByIndex(impl::TestFlatKwargs::Index::kName, std::move(name));
}

const experiments3::models::Kwargs& Test::Build() const {
  const auto& schema = GetSchema();
  for (const auto& [kwarg_name, kwarg_schema] : schema) {
    if (kwarg_schema.is_kwarg_mandatory && !kwargs_.FindOptional(kwarg_name)) {
      throw std::runtime_error(fmt::format(
          "Missing mandatory key {} for kwarg builder Test", kwarg_name));
    }
  }
  return kwargs_;
}

void Test::Update(const KwargName& name, KwargValue value,
                  bool /* ignore_schema */) {
  kwargs_.Update(name, std::move(value));
}

}  // namespace experiments3::kwargs_builders
