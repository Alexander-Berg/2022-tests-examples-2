#include <experiments3/kwargs_builders/with_library_include.hpp>

#include <userver/utils/assert.hpp>

namespace experiments3::kwargs_builders {

namespace impl {

namespace {

using KwargName = experiments3::models::KwargName;
using KwargValue = experiments3::models::KwargValue;

const WithLibraryIncludeFlatKwargs::IndexByName kIndexByName = {
    {kwargs_names::kCommonKwarg,
     WithLibraryIncludeFlatKwargs::Index::kCommonKwarg},
    {kwargs_names::kUniqueKwarg,
     WithLibraryIncludeFlatKwargs::Index::kUniqueKwarg},
};

}

void WithLibraryIncludeFlatKwargs::UpdateByIndex(Index index,
                                                 KwargValue value) {
  values_[static_cast<size_t>(index)] = std::move(value);
}
void WithLibraryIncludeFlatKwargs::Update(const KwargName& name,
                                          KwargValue value) {
  values_[static_cast<size_t>(kIndexByName.at(name))] = std::move(value);
}
const KwargValue* WithLibraryIncludeFlatKwargs::FindOptional(
    const KwargName& name) const {
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

void WithLibraryIncludeFlatKwargs::ForEach(const ForEachFunction& func) const {
  for (const auto& [name, index] : kIndexByName) {
    if (const auto& value_opt = values_[static_cast<size_t>(index)]) {
      func(name, *value_opt);
    }
  }
}

}

const ::experiments3::models::KwargsSchema& WithLibraryInclude::GetSchema()
    const {
  static const auto kSchema = []() {
    ::experiments3::models::KwargsSchema schema = {
        {kwargs_names::kCommonKwarg,
         {typeid(models::KwargTypeInt), true, true}},
        {kwargs_names::kUniqueKwarg,
         {typeid(models::KwargTypeInt), true, true}},
    };
    schema.insert(
        experiments3::models::schema_extensions::kDefaultSchemaExtension
            .begin(),
        experiments3::models::schema_extensions::kDefaultSchemaExtension.end());
    return schema;
  }();
  return kSchema;
}

const std::string& WithLibraryInclude::GetConsumer() const {
  static const std::string kConsumerName{kConsumer};
  return kConsumerName;
}

void WithLibraryInclude::UpdateCommonKwarg(
    const models::KwargTypeInt& common_kwarg) {
  kwargs_.UpdateByIndex(impl::WithLibraryIncludeFlatKwargs::Index::kCommonKwarg,
                        common_kwarg);
}

void WithLibraryInclude::UpdateCommonKwarg(
    models::KwargTypeInt&& common_kwarg) {
  kwargs_.UpdateByIndex(impl::WithLibraryIncludeFlatKwargs::Index::kCommonKwarg,
                        std::move(common_kwarg));
}
void WithLibraryInclude::UpdateUniqueKwarg(
    const models::KwargTypeInt& unique_kwarg) {
  kwargs_.UpdateByIndex(impl::WithLibraryIncludeFlatKwargs::Index::kUniqueKwarg,
                        unique_kwarg);
}

void WithLibraryInclude::UpdateUniqueKwarg(
    models::KwargTypeInt&& unique_kwarg) {
  kwargs_.UpdateByIndex(impl::WithLibraryIncludeFlatKwargs::Index::kUniqueKwarg,
                        std::move(unique_kwarg));
}

const experiments3::models::Kwargs& WithLibraryInclude::Build() const {
  const auto& schema = GetSchema();
  for (const auto& [kwarg_name, kwarg_schema] : schema) {
    if (kwarg_schema.is_kwarg_mandatory && !kwargs_.FindOptional(kwarg_name)) {
      throw std::runtime_error(fmt::format(
          "Missing mandatory key {} for kwarg builder WithLibraryInclude",
          kwarg_name));
    }
  }
  return kwargs_;
}

void WithLibraryInclude::Update(const KwargName& name, KwargValue value,
                                bool /* ignore_schema */) {
  kwargs_.Update(name, std::move(value));
}

}  // namespace experiments3::kwargs_builders
