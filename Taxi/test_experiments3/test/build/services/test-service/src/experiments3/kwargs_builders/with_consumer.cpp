#include <experiments3/kwargs_builders/with_consumer.hpp>

#include <userver/utils/assert.hpp>

namespace experiments3::kwargs_builders {

namespace impl {

namespace {

using KwargName = experiments3::models::KwargName;
using KwargValue = experiments3::models::KwargValue;

const WithConsumerFlatKwargs::IndexByName kIndexByName = {
    {kwargs_names::kApplication, WithConsumerFlatKwargs::Index::kApplication},
    {kwargs_names::kApplicationBrand,
     WithConsumerFlatKwargs::Index::kApplicationBrand},
    {kwargs_names::kApplicationFullVersion,
     WithConsumerFlatKwargs::Index::kApplicationFullVersion},
    {kwargs_names::kApplicationName,
     WithConsumerFlatKwargs::Index::kApplicationName},
    {kwargs_names::kApplicationPlatform,
     WithConsumerFlatKwargs::Index::kApplicationPlatform},
    {kwargs_names::kApplicationPlatformFullVersion,
     WithConsumerFlatKwargs::Index::kApplicationPlatformFullVersion},
    {kwargs_names::kApplicationPlatformVersion,
     WithConsumerFlatKwargs::Index::kApplicationPlatformVersion},
    {kwargs_names::kBuildType, WithConsumerFlatKwargs::Index::kBuildType},
    {kwargs_names::kDeviceMake, WithConsumerFlatKwargs::Index::kDeviceMake},
    {kwargs_names::kDeviceModel, WithConsumerFlatKwargs::Index::kDeviceModel},
    {kwargs_names::kField1, WithConsumerFlatKwargs::Index::kField1},
    {kwargs_names::kField2, WithConsumerFlatKwargs::Index::kField2},
    {kwargs_names::kField3, WithConsumerFlatKwargs::Index::kField3},
    {kwargs_names::kVersion, WithConsumerFlatKwargs::Index::kVersion},
};

}

void WithConsumerFlatKwargs::UpdateByIndex(Index index, KwargValue value) {
  values_[static_cast<size_t>(index)] = std::move(value);
}
void WithConsumerFlatKwargs::Update(const KwargName& name, KwargValue value) {
  values_[static_cast<size_t>(kIndexByName.at(name))] = std::move(value);
}
const KwargValue* WithConsumerFlatKwargs::FindOptional(
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

void WithConsumerFlatKwargs::ForEach(const ForEachFunction& func) const {
  for (const auto& [name, index] : kIndexByName) {
    if (const auto& value_opt = values_[static_cast<size_t>(index)]) {
      func(name, *value_opt);
    }
  }
}

}

const ::experiments3::models::KwargsSchema& WithConsumer::GetSchema() const {
  static const auto kSchema = []() {
    ::experiments3::models::KwargsSchema schema = {
        {kwargs_names::kApplication,
         {typeid(models::KwargTypeString), false, true}},
        {kwargs_names::kApplicationBrand,
         {typeid(models::KwargTypeString), false, true}},
        {kwargs_names::kApplicationFullVersion,
         {typeid(models::KwargTypeString), false, true}},
        {kwargs_names::kApplicationName,
         {typeid(models::KwargTypeString), false, true}},
        {kwargs_names::kApplicationPlatform,
         {typeid(models::KwargTypeString), false, true}},
        {kwargs_names::kApplicationPlatformFullVersion,
         {typeid(models::KwargTypeString), false, true}},
        {kwargs_names::kApplicationPlatformVersion,
         {typeid(models::KwargTypeAppVersion), false, true}},
        {kwargs_names::kBuildType,
         {typeid(models::KwargTypeString), false, true}},
        {kwargs_names::kDeviceMake,
         {typeid(models::KwargTypeString), false, true}},
        {kwargs_names::kDeviceModel,
         {typeid(models::KwargTypeString), false, true}},
        {kwargs_names::kField1, {typeid(models::KwargTypeString), true, false}},
        {kwargs_names::kField2,
         {typeid(models::KwargTypeDouble), false, false}},
        {kwargs_names::kField3, {typeid(models::KwargTypeInt), false, true}},
        {kwargs_names::kVersion,
         {typeid(models::KwargTypeAppVersion), false, true}},
    };
    schema.insert(
        experiments3::models::schema_extensions::kDefaultSchemaExtension
            .begin(),
        experiments3::models::schema_extensions::kDefaultSchemaExtension.end());
    return schema;
  }();
  return kSchema;
}

const std::string& WithConsumer::GetConsumer() const {
  static const std::string kConsumerName{kConsumer};
  return kConsumerName;
}

void WithConsumer::UpdateField1(const models::KwargTypeString& field1) {
  kwargs_.UpdateByIndex(impl::WithConsumerFlatKwargs::Index::kField1, field1);
}

void WithConsumer::UpdateField1(models::KwargTypeString&& field1) {
  kwargs_.UpdateByIndex(impl::WithConsumerFlatKwargs::Index::kField1,
                        std::move(field1));
}
void WithConsumer::UpdateField2(const models::KwargTypeDouble& field2) {
  kwargs_.UpdateByIndex(impl::WithConsumerFlatKwargs::Index::kField2, field2);
}

void WithConsumer::UpdateField2(models::KwargTypeDouble&& field2) {
  kwargs_.UpdateByIndex(impl::WithConsumerFlatKwargs::Index::kField2,
                        std::move(field2));
}
void WithConsumer::UpdateField3(const models::KwargTypeInt& field3) {
  kwargs_.UpdateByIndex(impl::WithConsumerFlatKwargs::Index::kField3, field3);
}

void WithConsumer::UpdateField3(models::KwargTypeInt&& field3) {
  kwargs_.UpdateByIndex(impl::WithConsumerFlatKwargs::Index::kField3,
                        std::move(field3));
}

const experiments3::models::Kwargs& WithConsumer::Build() const {
  const auto& schema = GetSchema();
  for (const auto& [kwarg_name, kwarg_schema] : schema) {
    if (kwarg_schema.is_kwarg_mandatory && !kwargs_.FindOptional(kwarg_name)) {
      throw std::runtime_error(
          fmt::format("Missing mandatory key {} for kwarg builder WithConsumer",
                      kwarg_name));
    }
  }
  return kwargs_;
}

void WithConsumer::Update(const KwargName& name, KwargValue value,
                          bool /* ignore_schema */) {
  kwargs_.Update(name, std::move(value));
}

}  // namespace experiments3::kwargs_builders
