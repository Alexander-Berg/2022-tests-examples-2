#include <experiments3/kwargs_builders/without_consumer.hpp>

#include <userver/utils/assert.hpp>

namespace experiments3::kwargs_builders {

namespace impl {

namespace {

using KwargName = experiments3::models::KwargName;
using KwargValue = experiments3::models::KwargValue;

const DeprecatedWithoutConsumerFlatKwargs::IndexByName kIndexByName = {
    {kwargs_names::kFApplication,
     DeprecatedWithoutConsumerFlatKwargs::Index::kFApplication},
    {kwargs_names::kFApplicationVersion,
     DeprecatedWithoutConsumerFlatKwargs::Index::kFApplicationVersion},
    {kwargs_names::kFBool, DeprecatedWithoutConsumerFlatKwargs::Index::kFBool},
    {kwargs_names::kFDouble,
     DeprecatedWithoutConsumerFlatKwargs::Index::kFDouble},
    {kwargs_names::kFInt, DeprecatedWithoutConsumerFlatKwargs::Index::kFInt},
    {kwargs_names::kFPoint,
     DeprecatedWithoutConsumerFlatKwargs::Index::kFPoint},
    {kwargs_names::kFSetInt,
     DeprecatedWithoutConsumerFlatKwargs::Index::kFSetInt},
    {kwargs_names::kFSetString,
     DeprecatedWithoutConsumerFlatKwargs::Index::kFSetString},
    {kwargs_names::kFString,
     DeprecatedWithoutConsumerFlatKwargs::Index::kFString},
    {kwargs_names::kFTimepoint,
     DeprecatedWithoutConsumerFlatKwargs::Index::kFTimepoint},
};

}

void DeprecatedWithoutConsumerFlatKwargs::UpdateByIndex(Index index,
                                                        KwargValue value) {
  values_[static_cast<size_t>(index)] = std::move(value);
}
void DeprecatedWithoutConsumerFlatKwargs::Update(const KwargName& name,
                                                 KwargValue value) {
  values_[static_cast<size_t>(kIndexByName.at(name))] = std::move(value);
}
const KwargValue* DeprecatedWithoutConsumerFlatKwargs::FindOptional(
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

void DeprecatedWithoutConsumerFlatKwargs::ForEach(
    const ForEachFunction& func) const {
  for (const auto& [name, index] : kIndexByName) {
    if (const auto& value_opt = values_[static_cast<size_t>(index)]) {
      func(name, *value_opt);
    }
  }
}

}

const ::experiments3::models::KwargsSchema&
DeprecatedWithoutConsumer::GetSchema() const {
  static const auto kSchema = []() {
    ::experiments3::models::KwargsSchema schema = {
        {kwargs_names::kFApplication,
         {typeid(models::KwargTypeString), true, true}},
        {kwargs_names::kFApplicationVersion,
         {typeid(models::KwargTypeAppVersion), false, false}},
        {kwargs_names::kFBool, {typeid(models::KwargTypeBool), true, false}},
        {kwargs_names::kFDouble,
         {typeid(models::KwargTypeDouble), false, true}},
        {kwargs_names::kFInt, {typeid(models::KwargTypeInt), true, true}},
        {kwargs_names::kFPoint, {typeid(models::KwargTypePoint), false, true}},
        {kwargs_names::kFSetInt,
         {typeid(models::KwargTypeSetInt), true, false}},
        {kwargs_names::kFSetString,
         {typeid(models::KwargTypeSetString), false, false}},
        {kwargs_names::kFString,
         {typeid(models::KwargTypeString), false, true}},
        {kwargs_names::kFTimepoint,
         {typeid(models::KwargTypeTimePoint), true, true}},
    };
    return schema;
  }();
  return kSchema;
}

void DeprecatedWithoutConsumer::UpdateFApplication(
    const models::KwargTypeString& f_application) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFApplication,
      f_application);
}

void DeprecatedWithoutConsumer::UpdateFApplication(
    models::KwargTypeString&& f_application) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFApplication,
      std::move(f_application));
}
void DeprecatedWithoutConsumer::UpdateFApplicationVersion(
    const models::KwargTypeAppVersion& f_application_version) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFApplicationVersion,
      f_application_version);
}

void DeprecatedWithoutConsumer::UpdateFApplicationVersion(
    models::KwargTypeAppVersion&& f_application_version) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFApplicationVersion,
      std::move(f_application_version));
}
void DeprecatedWithoutConsumer::UpdateFBool(
    const models::KwargTypeBool& f_bool) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFBool, f_bool);
}

void DeprecatedWithoutConsumer::UpdateFBool(models::KwargTypeBool&& f_bool) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFBool,
      std::move(f_bool));
}
void DeprecatedWithoutConsumer::UpdateFDouble(
    const models::KwargTypeDouble& f_double) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFDouble, f_double);
}

void DeprecatedWithoutConsumer::UpdateFDouble(
    models::KwargTypeDouble&& f_double) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFDouble,
      std::move(f_double));
}
void DeprecatedWithoutConsumer::UpdateFInt(const models::KwargTypeInt& f_int) {
  kwargs_.UpdateByIndex(impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFInt,
                        f_int);
}

void DeprecatedWithoutConsumer::UpdateFInt(models::KwargTypeInt&& f_int) {
  kwargs_.UpdateByIndex(impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFInt,
                        std::move(f_int));
}
void DeprecatedWithoutConsumer::UpdateFPoint(
    const models::KwargTypePoint& f_point) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFPoint, f_point);
}

void DeprecatedWithoutConsumer::UpdateFPoint(models::KwargTypePoint&& f_point) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFPoint,
      std::move(f_point));
}
void DeprecatedWithoutConsumer::UpdateFSetInt(
    const models::KwargTypeSetInt& f_set_int) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFSetInt, f_set_int);
}

void DeprecatedWithoutConsumer::UpdateFSetInt(
    models::KwargTypeSetInt&& f_set_int) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFSetInt,
      std::move(f_set_int));
}
void DeprecatedWithoutConsumer::UpdateFSetString(
    const models::KwargTypeSetString& f_set_string) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFSetString,
      f_set_string);
}

void DeprecatedWithoutConsumer::UpdateFSetString(
    models::KwargTypeSetString&& f_set_string) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFSetString,
      std::move(f_set_string));
}
void DeprecatedWithoutConsumer::UpdateFString(
    const models::KwargTypeString& f_string) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFString, f_string);
}

void DeprecatedWithoutConsumer::UpdateFString(
    models::KwargTypeString&& f_string) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFString,
      std::move(f_string));
}
void DeprecatedWithoutConsumer::UpdateFTimepoint(
    const models::KwargTypeTimePoint& f_timepoint) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFTimepoint,
      f_timepoint);
}

void DeprecatedWithoutConsumer::UpdateFTimepoint(
    models::KwargTypeTimePoint&& f_timepoint) {
  kwargs_.UpdateByIndex(
      impl::DeprecatedWithoutConsumerFlatKwargs::Index::kFTimepoint,
      std::move(f_timepoint));
}

const experiments3::models::Kwargs& DeprecatedWithoutConsumer::Build() const {
  const auto& schema = GetSchema();
  for (const auto& [kwarg_name, kwarg_schema] : schema) {
    if (kwarg_schema.is_kwarg_mandatory && !kwargs_.FindOptional(kwarg_name)) {
      throw std::runtime_error(
          fmt::format("Missing mandatory key {} for kwarg builder "
                      "DeprecatedWithoutConsumer", kwarg_name));
    }
  }
  return kwargs_;
}

void DeprecatedWithoutConsumer::Update(const KwargName& name, KwargValue value,
                                       bool /* ignore_schema */) {
  kwargs_.Update(name, std::move(value));
}

}  // namespace experiments3::kwargs_builders
