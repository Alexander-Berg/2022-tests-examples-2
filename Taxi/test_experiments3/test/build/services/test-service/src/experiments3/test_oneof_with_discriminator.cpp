/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

// This file was generated from file(s):
// taxi/uservices/services/test-service/experiments3/declarations/test_oneof_with_discriminator.yaml

#include <experiments3/test_oneof_with_discriminator.hpp>

#include <userver/formats/json/serialize_container.hpp>
#include <userver/formats/json/serialize_variant.hpp>
#include <userver/formats/parse/common_containers.hpp>
#include <userver/formats/parse/variant.hpp>

#include <codegen/impl/convert.hpp>
#include <codegen/impl/get_validation_length.hpp>
#include <codegen/impl/optional_convert.hpp>
#include <codegen/impl/parsers.hpp>
#include <cstring>
#include <unordered_set>
#include <userver/formats/common/meta.hpp>
#include <userver/formats/json/string_builder.hpp>
#include <userver/logging/log.hpp>
#include <userver/utils/assert.hpp>
#include <userver/utils/datetime/from_string_saturating.hpp>
#include <userver/utils/underlying_value.hpp>

#include <codegen/impl/convert.hpp>

namespace experiments3::test_oneof_with_discriminator {

static const std::unordered_set<std::string> kValueMapNonExtraKeys = {};

experiments3::test_oneof_with_discriminator::ValueMap Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<experiments3::test_oneof_with_discriminator::ValueMap>,
    [[maybe_unused]] ::codegen::ParsingFlags flags) {
  experiments3::test_oneof_with_discriminator::ValueMap result;

  elem.CheckNotMissing();
  elem.CheckObjectOrNull();

  if (flags == ::codegen::ParsingFlags::kParseExtra)
  {
    for (auto it = elem.begin(); it != elem.end(); ++it) {
      const auto& name = it.GetName();
      /* Skip 'properties', they don't go to additionalProperties */
      if (kValueMapNonExtraKeys.count(name) > 0) continue;

      result.extra.emplace(
          name,
          [](const formats::json::Value& value) -> ::std::size_t {
            auto tmp = value.As<int>();

            if (!(0 <= tmp)) {
              auto msg =
                  "out of bounds, must be 0 (limit) <= " + std::to_string(tmp) +
                  " (value)";
              throw formats::json::Value::ParseException(
                  "Value of '" + value.GetPath() + "': " + msg);
            }

            return ::codegen::impl::Convert<::std::size_t>(tmp);
          }((*it))

      );
    }
  }

  return result;
}

namespace parser {
template <class To>
template <class From>
To PValueMap::ParserLocalConverterTrait<To>::Convert(From&& from) {
  return ::codegen::impl::Convert<To>(std::forward<From>(from));
}

template <class To>
To PValueMap::ParserLocalDomToType<To>::Convert(
    ::formats::json::Value&& value) {
  return std::move(value).As<To>();
}

PValueMap::PValueMap()
{
  f_extra_.Subscribe(f_extra_helper_);
}

void PValueMap::Reset()
{
  state_ = State::kStart;
  result_ = {};
}

void PValueMap::StartObject() {
  switch (state_) {
    case State::kStart:
      state_ = State::kInside;
      break;

    case State::kInside:
      Throw("{");
  }
}

void PValueMap::Key([[maybe_unused]] std::string_view key)
{
  key_ = key;
  if (false) {
  } else {
    f_extra_.Reset();
    f_extra_helper_.SetKey(key);
    parser_state_->PushParser(f_extra_.GetParser());
  }
}

void PValueMap::EndObject()
{
  switch (state_) {
    case State::kStart:
      Throw("}");

    case State::kInside:
      // If an exception is thrown below, we must not set .old_key
      key_.clear();

      result_.extra = f_extra_helper_.ExtractValue();

      SetResult(std::move(result_));
      break;
  }
}

std::string PValueMap::Expected() const {
  switch (state_) {
    case State::kStart:
      return "object";

    case State::kInside:
      return "field name";
  }
}

std::string PValueMap::GetPathItem() const { return key_; }
}

}

namespace experiments3::test_oneof_with_discriminator {

experiments3::test_oneof_with_discriminator::ConstValueType Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<
        experiments3::test_oneof_with_discriminator::ConstValueType>) {
  const auto& value = elem.As<std::string>();
  if (value == "const") {
    return experiments3::test_oneof_with_discriminator::ConstValueType::kConst;
  } else {
    throw formats::json::ParseException("Value of '" + elem.GetPath() + "' (" +
                                        value + ") is not parseable into enum");
  }
}

ConstValueType Parse(std::string_view value, formats::parse::To<ConstValueType>)
{
  static const std::unordered_map<
      std::string_view,
      experiments3::test_oneof_with_discriminator::ConstValueType>
      map = {
          {"const",
           experiments3::test_oneof_with_discriminator::ConstValueType::kConst},
      };
  auto it = map.find(value);
  if (it != map.end()) return it->second;

  throw std::runtime_error(
      "Value '" + std::string{value} +
      "' is not parseable into "
      "experiments3::test_oneof_with_discriminator::ConstValueType");
}

std::string ToString(
    experiments3::test_oneof_with_discriminator::ConstValueType value) {
  switch (value) {
    case experiments3::test_oneof_with_discriminator::ConstValueType::kConst:
      return "const";
  }
  throw std::runtime_error(
      "Detected an attempt to serialize a corrupted "
      "'experiments3::test_oneof_with_discriminator::ConstValueType' (" +
      std::to_string(utils::UnderlyingValue(value)) + ")");
}

}

namespace experiments3::test_oneof_with_discriminator {

experiments3::test_oneof_with_discriminator::ConstValue Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<
        experiments3::test_oneof_with_discriminator::ConstValue>) {
  experiments3::test_oneof_with_discriminator::ConstValue result;

  elem.CheckNotMissing();
  elem.CheckObjectOrNull();

  result.type =
      elem["type"]
          .As<experiments3::test_oneof_with_discriminator::ConstValueType>();
  result.value = [](const formats::json::Value& value) -> int {
    auto tmp = value.As<int>();

    if (!(0 <= tmp)) {
      auto msg = "out of bounds, must be 0 (limit) <= " + std::to_string(tmp) +
                 " (value)";
      throw formats::json::Value::ParseException("Value of '" +
                                                 value.GetPath() + "': " + msg);
    }

    return tmp;
  }(elem["value"])

      ;

  return result;
}

namespace parser {
template <class To>
template <class From>
To PConstValue::ParserLocalConverterTrait<To>::Convert(From&& from) {
  return ::codegen::impl::Convert<To>(std::forward<From>(from));
}

template <class To>
To PConstValue::ParserLocalDomToType<To>::Convert(
    ::formats::json::Value&& value) {
  return std::move(value).As<To>();
}

PConstValue::PConstValue()
{
  f_type_.Subscribe(sink_type_);

  f_value_.Subscribe(sink_value_);
}

void PConstValue::Reset()
{
  state_ = State::kStart;
  result_ = {};

  s_type_ = false;
  s_value_ = false;
}

void PConstValue::StartObject() {
  switch (state_) {
    case State::kStart:
      state_ = State::kInside;
      break;

    case State::kInside:
      Throw("{");
  }
}

void PConstValue::Key([[maybe_unused]] std::string_view key)
{
  key_ = key;
  if (false) {
  } else if (key == "type") {
    s_type_ = true;
    f_type_.Reset();

    parser_state_->PushParser(f_type_.GetParser());
  }

  else if (key == "value") {
    s_value_ = true;
    f_value_.Reset();

    parser_state_->PushParser(f_value_.GetParser());
  } else {
    /* Eat and ignore unknown value */
    ff_empty_.Reset();
    parser_state_->PushParser(ff_empty_.GetParser());
  }
}

void PConstValue::EndObject()
{
  switch (state_) {
    case State::kStart:
      Throw("}");

    case State::kInside:
      // If an exception is thrown below, we must not set .old_key
      key_.clear();

      if (!s_type_) {
        throw ::formats::json::parser::InternalParseError(
            "missing required field 'type'");
      }
      if (!s_value_) {
        throw ::formats::json::parser::InternalParseError(
            "missing required field 'value'");
      }

      SetResult(std::move(result_));
      break;
  }
}

std::string PConstValue::Expected() const {
  switch (state_) {
    case State::kStart:
      return "object";

    case State::kInside:
      return "field name";
  }
}

std::string PConstValue::GetPathItem() const { return key_; }
}

}

namespace experiments3::test_oneof_with_discriminator {

experiments3::test_oneof_with_discriminator::DefaultCustomValueBySubTypeType
Parse([[maybe_unused]] const formats::json::Value& elem,
      formats::parse::To<experiments3::test_oneof_with_discriminator::
                             DefaultCustomValueBySubTypeType>) {
  const auto& value = elem.As<std::string>();
  if (value == "by_subtype") {
    return experiments3::test_oneof_with_discriminator::
        DefaultCustomValueBySubTypeType::kBySubtype;
  } else {
    throw formats::json::ParseException("Value of '" + elem.GetPath() + "' (" +
                                        value + ") is not parseable into enum");
  }
}

DefaultCustomValueBySubTypeType Parse(
    std::string_view value, formats::parse::To<DefaultCustomValueBySubTypeType>)
{
  static const std::unordered_map<std::string_view,
                                  experiments3::test_oneof_with_discriminator::
                                      DefaultCustomValueBySubTypeType>
      map = {
          {"by_subtype", experiments3::test_oneof_with_discriminator::
                             DefaultCustomValueBySubTypeType::kBySubtype},
      };
  auto it = map.find(value);
  if (it != map.end()) return it->second;

  throw std::runtime_error("Value '" + std::string{value} +
                           "' is not parseable into "
                           "experiments3::test_oneof_with_discriminator::"
                           "DefaultCustomValueBySubTypeType");
}

std::string ToString(
    experiments3::test_oneof_with_discriminator::DefaultCustomValueBySubTypeType
        value) {
  switch (value) {
    case experiments3::test_oneof_with_discriminator::
        DefaultCustomValueBySubTypeType::kBySubtype:
      return "by_subtype";
  }
  throw std::runtime_error(
      "Detected an attempt to serialize a corrupted "
      "'experiments3::test_oneof_with_discriminator::"
      "DefaultCustomValueBySubTypeType' (" +
      std::to_string(utils::UnderlyingValue(value)) + ")");
}

}

namespace experiments3::test_oneof_with_discriminator {

experiments3::test_oneof_with_discriminator::DefaultCustomValueBySubType Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<experiments3::test_oneof_with_discriminator::
                           DefaultCustomValueBySubType>) {
  experiments3::test_oneof_with_discriminator::DefaultCustomValueBySubType
      result;

  elem.CheckNotMissing();
  elem.CheckObjectOrNull();

  result.type = elem["type"]
                    .As<experiments3::test_oneof_with_discriminator::
                            DefaultCustomValueBySubTypeType>();
  result.value =
      elem["value"].As<experiments3::test_oneof_with_discriminator::ValueMap>();

  return result;
}

namespace parser {
template <class To>
template <class From>
To PDefaultCustomValueBySubType::ParserLocalConverterTrait<To>::Convert(
    From&& from) {
  return ::codegen::impl::Convert<To>(std::forward<From>(from));
}

template <class To>
To PDefaultCustomValueBySubType::ParserLocalDomToType<To>::Convert(
    ::formats::json::Value&& value) {
  return std::move(value).As<To>();
}

PDefaultCustomValueBySubType::PDefaultCustomValueBySubType()
{
  f_type_.Subscribe(sink_type_);

  f_value_.Subscribe(sink_value_);
}

void PDefaultCustomValueBySubType::Reset()
{
  state_ = State::kStart;
  result_ = {};

  s_type_ = false;
  s_value_ = false;
}

void PDefaultCustomValueBySubType::StartObject() {
  switch (state_) {
    case State::kStart:
      state_ = State::kInside;
      break;

    case State::kInside:
      Throw("{");
  }
}

void PDefaultCustomValueBySubType::Key([[maybe_unused]] std::string_view key)
{
  key_ = key;
  if (false) {
  } else if (key == "type") {
    s_type_ = true;
    f_type_.Reset();

    parser_state_->PushParser(f_type_.GetParser());
  }

  else if (key == "value") {
    s_value_ = true;
    f_value_.Reset();

    parser_state_->PushParser(f_value_.GetParser());
  } else {
    /* Eat and ignore unknown value */
    ff_empty_.Reset();
    parser_state_->PushParser(ff_empty_.GetParser());
  }
}

void PDefaultCustomValueBySubType::EndObject()
{
  switch (state_) {
    case State::kStart:
      Throw("}");

    case State::kInside:
      // If an exception is thrown below, we must not set .old_key
      key_.clear();

      if (!s_type_) {
        throw ::formats::json::parser::InternalParseError(
            "missing required field 'type'");
      }
      if (!s_value_) {
        throw ::formats::json::parser::InternalParseError(
            "missing required field 'value'");
      }

      SetResult(std::move(result_));
      break;
  }
}

std::string PDefaultCustomValueBySubType::Expected() const {
  switch (state_) {
    case State::kStart:
      return "object";

    case State::kInside:
      return "field name";
  }
}

std::string PDefaultCustomValueBySubType::GetPathItem() const { return key_; }
}

}

namespace experiments3::test_oneof_with_discriminator {

experiments3::test_oneof_with_discriminator::DefaultCustomValue Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<
        experiments3::test_oneof_with_discriminator::DefaultCustomValue>) {
  const auto discriminator = elem["type"].As<std::string>();
  if (discriminator == "by_subtype") {
    return experiments3::test_oneof_with_discriminator::DefaultCustomValue{
        elem.As<experiments3::test_oneof_with_discriminator::
                    DefaultCustomValueBySubType>(),
    };
  } else if (discriminator == "const") {
    return experiments3::test_oneof_with_discriminator::DefaultCustomValue{
        elem.As<experiments3::test_oneof_with_discriminator::ConstValue>(),
    };
  } else {
    throw formats::json::Value::ParseException(
        "Value of discriminator '" + discriminator + "' for path '" +
        elem.GetPath() +
        "' does not match any known mapping from ['by_subtype', 'const']");
  }
}

namespace parser {
experiments3::test_oneof_with_discriminator::DefaultCustomValue
PDefaultCustomValueDomToType::Convert(::formats::json::Value&& value) {
  return std::move(value)
      .As<experiments3::test_oneof_with_discriminator::DefaultCustomValue>();
}
}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

static const std::unordered_set<std::string>
    kByProviderCustomValueNonExtraKeys = {};

experiments3::test_oneof_with_discriminator::ByProviderCustomValue Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<
        experiments3::test_oneof_with_discriminator::ByProviderCustomValue>,
    [[maybe_unused]] ::codegen::ParsingFlags flags) {
  experiments3::test_oneof_with_discriminator::ByProviderCustomValue result;

  elem.CheckNotMissing();
  elem.CheckObjectOrNull();

  if (flags == ::codegen::ParsingFlags::kParseExtra)
  {
    for (auto it = elem.begin(); it != elem.end(); ++it) {
      const auto& name = it.GetName();
      /* Skip 'properties', they don't go to additionalProperties */
      if (kByProviderCustomValueNonExtraKeys.count(name) > 0) continue;

      result.extra.emplace(name,
                           (*it)
                               .As<experiments3::test_oneof_with_discriminator::
                                       DefaultCustomValue>());
    }
  }

  return result;
}

namespace parser {
template <class To>
template <class From>
To PByProviderCustomValue::ParserLocalConverterTrait<To>::Convert(From&& from) {
  return ::codegen::impl::Convert<To>(std::forward<From>(from));
}

template <class To>
To PByProviderCustomValue::ParserLocalDomToType<To>::Convert(
    ::formats::json::Value&& value) {
  return std::move(value).As<To>();
}

PByProviderCustomValue::PByProviderCustomValue()
{
  f_extra_.Subscribe(f_extra_helper_);
}

void PByProviderCustomValue::Reset()
{
  state_ = State::kStart;
  result_ = {};
}

void PByProviderCustomValue::StartObject() {
  switch (state_) {
    case State::kStart:
      state_ = State::kInside;
      break;

    case State::kInside:
      Throw("{");
  }
}

void PByProviderCustomValue::Key([[maybe_unused]] std::string_view key)
{
  key_ = key;
  if (false) {
  } else {
    f_extra_.Reset();
    f_extra_helper_.SetKey(key);
    parser_state_->PushParser(f_extra_.GetParser());
  }
}

void PByProviderCustomValue::EndObject()
{
  switch (state_) {
    case State::kStart:
      Throw("}");

    case State::kInside:
      // If an exception is thrown below, we must not set .old_key
      key_.clear();

      result_.extra = f_extra_helper_.ExtractValue();

      SetResult(std::move(result_));
      break;
  }
}

std::string PByProviderCustomValue::Expected() const {
  switch (state_) {
    case State::kStart:
      return "object";

    case State::kInside:
      return "field name";
  }
}

std::string PByProviderCustomValue::GetPathItem() const { return key_; }
}

}

namespace experiments3::test_oneof_with_discriminator {

experiments3::test_oneof_with_discriminator::CustomValueType Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<
        experiments3::test_oneof_with_discriminator::CustomValueType>) {
  const auto& value = elem.As<std::string>();
  if (value == "value") {
    return experiments3::test_oneof_with_discriminator::CustomValueType::kValue;
  } else {
    throw formats::json::ParseException("Value of '" + elem.GetPath() + "' (" +
                                        value + ") is not parseable into enum");
  }
}

CustomValueType Parse(std::string_view value,
                      formats::parse::To<CustomValueType>)
{
  static const std::unordered_map<
      std::string_view,
      experiments3::test_oneof_with_discriminator::CustomValueType>
      map = {
          {"value", experiments3::test_oneof_with_discriminator::
                        CustomValueType::kValue},
      };
  auto it = map.find(value);
  if (it != map.end()) return it->second;

  throw std::runtime_error(
      "Value '" + std::string{value} +
      "' is not parseable into "
      "experiments3::test_oneof_with_discriminator::CustomValueType");
}

std::string ToString(
    experiments3::test_oneof_with_discriminator::CustomValueType value) {
  switch (value) {
    case experiments3::test_oneof_with_discriminator::CustomValueType::kValue:
      return "value";
  }
  throw std::runtime_error(
      "Detected an attempt to serialize a corrupted "
      "'experiments3::test_oneof_with_discriminator::CustomValueType' (" +
      std::to_string(utils::UnderlyingValue(value)) + ")");
}

}

namespace experiments3::test_oneof_with_discriminator {

experiments3::test_oneof_with_discriminator::CustomValue Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<
        experiments3::test_oneof_with_discriminator::CustomValue>) {
  experiments3::test_oneof_with_discriminator::CustomValue result;

  elem.CheckNotMissing();
  elem.CheckObjectOrNull();

  result.by_provider = elem["by_provider"]
                           .As<experiments3::test_oneof_with_discriminator::
                                   ByProviderCustomValue>();
  result.type =
      elem["type"]
          .As<experiments3::test_oneof_with_discriminator::CustomValueType>();

  return result;
}

namespace parser {
template <class To>
template <class From>
To PCustomValue::ParserLocalConverterTrait<To>::Convert(From&& from) {
  return ::codegen::impl::Convert<To>(std::forward<From>(from));
}

template <class To>
To PCustomValue::ParserLocalDomToType<To>::Convert(
    ::formats::json::Value&& value) {
  return std::move(value).As<To>();
}

PCustomValue::PCustomValue()
{
  f_by_provider_.Subscribe(sink_by_provider_);

  f_type_.Subscribe(sink_type_);
}

void PCustomValue::Reset()
{
  state_ = State::kStart;
  result_ = {};

  s_by_provider_ = false;
  s_type_ = false;
}

void PCustomValue::StartObject() {
  switch (state_) {
    case State::kStart:
      state_ = State::kInside;
      break;

    case State::kInside:
      Throw("{");
  }
}

void PCustomValue::Key([[maybe_unused]] std::string_view key)
{
  key_ = key;
  if (false) {
  } else if (key == "by_provider") {
    s_by_provider_ = true;
    f_by_provider_.Reset();

    parser_state_->PushParser(f_by_provider_.GetParser());
  }

  else if (key == "type") {
    s_type_ = true;
    f_type_.Reset();

    parser_state_->PushParser(f_type_.GetParser());
  } else {
    /* Eat and ignore unknown value */
    ff_empty_.Reset();
    parser_state_->PushParser(ff_empty_.GetParser());
  }
}

void PCustomValue::EndObject()
{
  switch (state_) {
    case State::kStart:
      Throw("}");

    case State::kInside:
      // If an exception is thrown below, we must not set .old_key
      key_.clear();

      if (!s_by_provider_) {
        throw ::formats::json::parser::InternalParseError(
            "missing required field 'by_provider'");
      }
      if (!s_type_) {
        throw ::formats::json::parser::InternalParseError(
            "missing required field 'type'");
      }

      SetResult(std::move(result_));
      break;
  }
}

std::string PCustomValue::Expected() const {
  switch (state_) {
    case State::kStart:
      return "object";

    case State::kInside:
      return "field name";
  }
}

std::string PCustomValue::GetPathItem() const { return key_; }
}

}

namespace experiments3::test_oneof_with_discriminator {

experiments3::test_oneof_with_discriminator::MultipliedHashType Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<
        experiments3::test_oneof_with_discriminator::MultipliedHashType>) {
  const auto& value = elem.As<std::string>();
  if (value == "mult_hash") {
    return experiments3::test_oneof_with_discriminator::MultipliedHashType::
        kMultHash;
  } else {
    throw formats::json::ParseException("Value of '" + elem.GetPath() + "' (" +
                                        value + ") is not parseable into enum");
  }
}

MultipliedHashType Parse(std::string_view value,
                         formats::parse::To<MultipliedHashType>)
{
  static const std::unordered_map<
      std::string_view,
      experiments3::test_oneof_with_discriminator::MultipliedHashType>
      map = {
          {"mult_hash", experiments3::test_oneof_with_discriminator::
                            MultipliedHashType::kMultHash},
      };
  auto it = map.find(value);
  if (it != map.end()) return it->second;

  throw std::runtime_error(
      "Value '" + std::string{value} +
      "' is not parseable into "
      "experiments3::test_oneof_with_discriminator::MultipliedHashType");
}

std::string ToString(
    experiments3::test_oneof_with_discriminator::MultipliedHashType value) {
  switch (value) {
    case experiments3::test_oneof_with_discriminator::MultipliedHashType::
        kMultHash:
      return "mult_hash";
  }
  throw std::runtime_error(
      "Detected an attempt to serialize a corrupted "
      "'experiments3::test_oneof_with_discriminator::MultipliedHashType' (" +
      std::to_string(utils::UnderlyingValue(value)) + ")");
}

}

namespace experiments3::test_oneof_with_discriminator {

experiments3::test_oneof_with_discriminator::MultipliedHash Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<
        experiments3::test_oneof_with_discriminator::MultipliedHash>) {
  experiments3::test_oneof_with_discriminator::MultipliedHash result;

  elem.CheckNotMissing();
  elem.CheckObjectOrNull();

  result.by_provider =
      elem["by_provider"]
          .As<experiments3::test_oneof_with_discriminator::ValueMap>();
  result.type = elem["type"]
                    .As<experiments3::test_oneof_with_discriminator::
                            MultipliedHashType>();

  return result;
}

namespace parser {
template <class To>
template <class From>
To PMultipliedHash::ParserLocalConverterTrait<To>::Convert(From&& from) {
  return ::codegen::impl::Convert<To>(std::forward<From>(from));
}

template <class To>
To PMultipliedHash::ParserLocalDomToType<To>::Convert(
    ::formats::json::Value&& value) {
  return std::move(value).As<To>();
}

PMultipliedHash::PMultipliedHash()
{
  f_by_provider_.Subscribe(sink_by_provider_);

  f_type_.Subscribe(sink_type_);
}

void PMultipliedHash::Reset()
{
  state_ = State::kStart;
  result_ = {};

  s_by_provider_ = false;
  s_type_ = false;
}

void PMultipliedHash::StartObject() {
  switch (state_) {
    case State::kStart:
      state_ = State::kInside;
      break;

    case State::kInside:
      Throw("{");
  }
}

void PMultipliedHash::Key([[maybe_unused]] std::string_view key)
{
  key_ = key;
  if (false) {
  } else if (key == "by_provider") {
    s_by_provider_ = true;
    f_by_provider_.Reset();

    parser_state_->PushParser(f_by_provider_.GetParser());
  }

  else if (key == "type") {
    s_type_ = true;
    f_type_.Reset();

    parser_state_->PushParser(f_type_.GetParser());
  } else {
    /* Eat and ignore unknown value */
    ff_empty_.Reset();
    parser_state_->PushParser(ff_empty_.GetParser());
  }
}

void PMultipliedHash::EndObject()
{
  switch (state_) {
    case State::kStart:
      Throw("}");

    case State::kInside:
      // If an exception is thrown below, we must not set .old_key
      key_.clear();

      if (!s_by_provider_) {
        throw ::formats::json::parser::InternalParseError(
            "missing required field 'by_provider'");
      }
      if (!s_type_) {
        throw ::formats::json::parser::InternalParseError(
            "missing required field 'type'");
      }

      SetResult(std::move(result_));
      break;
  }
}

std::string PMultipliedHash::Expected() const {
  switch (state_) {
    case State::kStart:
      return "object";

    case State::kInside:
      return "field name";
  }
}

std::string PMultipliedHash::GetPathItem() const { return key_; }
}

}

namespace experiments3::test_oneof_with_discriminator {

experiments3::test_oneof_with_discriminator::PriorityItemPayload Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<
        experiments3::test_oneof_with_discriminator::PriorityItemPayload>) {
  const auto discriminator = elem["type"].As<std::string>();
  if (discriminator == "mult_hash") {
    return experiments3::test_oneof_with_discriminator::PriorityItemPayload{
        elem.As<experiments3::test_oneof_with_discriminator::MultipliedHash>(),
    };
  } else if (discriminator == "value") {
    return experiments3::test_oneof_with_discriminator::PriorityItemPayload{
        elem.As<experiments3::test_oneof_with_discriminator::CustomValue>(),
    };
  } else {
    throw formats::json::Value::ParseException(
        "Value of discriminator '" + discriminator + "' for path '" +
        elem.GetPath() +
        "' does not match any known mapping from ['mult_hash', 'value']");
  }
}

namespace parser {
experiments3::test_oneof_with_discriminator::PriorityItemPayload
PPriorityItemPayloadDomToType::Convert(::formats::json::Value&& value) {
  return std::move(value)
      .As<experiments3::test_oneof_with_discriminator::PriorityItemPayload>();
}
}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

experiments3::test_oneof_with_discriminator::PriorityItem Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<
        experiments3::test_oneof_with_discriminator::PriorityItem>) {
  experiments3::test_oneof_with_discriminator::PriorityItem result;

  elem.CheckNotMissing();
  elem.CheckObjectOrNull();

  result.name = elem["name"].As<std::string>();
  result.payload = elem["payload"]
                       .As<experiments3::test_oneof_with_discriminator::
                               PriorityItemPayload>();

  return result;
}

namespace parser {
template <class To>
template <class From>
To PPriorityItem::ParserLocalConverterTrait<To>::Convert(From&& from) {
  return ::codegen::impl::Convert<To>(std::forward<From>(from));
}

template <class To>
To PPriorityItem::ParserLocalDomToType<To>::Convert(
    ::formats::json::Value&& value) {
  return std::move(value).As<To>();
}

PPriorityItem::PPriorityItem()
{
  f_name_.Subscribe(sink_name_);

  f_payload_.Subscribe(sink_payload_);
}

void PPriorityItem::Reset()
{
  state_ = State::kStart;
  result_ = {};

  s_name_ = false;
  s_payload_ = false;
}

void PPriorityItem::StartObject() {
  switch (state_) {
    case State::kStart:
      state_ = State::kInside;
      break;

    case State::kInside:
      Throw("{");
  }
}

void PPriorityItem::Key([[maybe_unused]] std::string_view key)
{
  key_ = key;
  if (false) {
  } else if (key == "name") {
    s_name_ = true;
    f_name_.Reset();

    parser_state_->PushParser(f_name_.GetParser());
  }

  else if (key == "payload") {
    s_payload_ = true;
    f_payload_.Reset();

    parser_state_->PushParser(f_payload_.GetParser());
  } else {
    /* Eat and ignore unknown value */
    ff_empty_.Reset();
    parser_state_->PushParser(ff_empty_.GetParser());
  }
}

void PPriorityItem::EndObject()
{
  switch (state_) {
    case State::kStart:
      Throw("}");

    case State::kInside:
      // If an exception is thrown below, we must not set .old_key
      key_.clear();

      if (!s_name_) {
        throw ::formats::json::parser::InternalParseError(
            "missing required field 'name'");
      }
      if (!s_payload_) {
        throw ::formats::json::parser::InternalParseError(
            "missing required field 'payload'");
      }

      SetResult(std::move(result_));
      break;
  }
}

std::string PPriorityItem::Expected() const {
  switch (state_) {
    case State::kStart:
      return "object";

    case State::kInside:
      return "field name";
  }
}

std::string PPriorityItem::GetPathItem() const { return key_; }
}

}

namespace experiments3::test_oneof_with_discriminator {

experiments3::test_oneof_with_discriminator::PrioritySettings Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<
        experiments3::test_oneof_with_discriminator::PrioritySettings>) {
  experiments3::test_oneof_with_discriminator::PrioritySettings result;

  elem.CheckNotMissing();
  elem.CheckObjectOrNull();

  result.priorities_tuple = [](const formats::json::Value& array)
      -> std::vector<
          experiments3::test_oneof_with_discriminator::PriorityItem> {
    std::vector<experiments3::test_oneof_with_discriminator::PriorityItem>
        result;
    array.CheckArrayOrNull();
    result.reserve(array.GetSize());
    for (const auto& item : array) {
      result.insert(
          result.end(),
          item.As<experiments3::test_oneof_with_discriminator::PriorityItem>());
    }

    return result;
  }(elem["priorities_tuple"]);

  return result;
}

namespace parser {
template <class To>
template <class From>
To PPrioritySettings::ParserLocalConverterTrait<To>::Convert(From&& from) {
  return ::codegen::impl::Convert<To>(std::forward<From>(from));
}

template <class To>
To PPrioritySettings::ParserLocalDomToType<To>::Convert(
    ::formats::json::Value&& value) {
  return std::move(value).As<To>();
}

PPrioritySettings::PPrioritySettings()
{
  f_priorities_tuple_.Subscribe(sink_priorities_tuple_);
}

void PPrioritySettings::Reset()
{
  state_ = State::kStart;
  result_ = {};

  s_priorities_tuple_ = false;
}

void PPrioritySettings::StartObject() {
  switch (state_) {
    case State::kStart:
      state_ = State::kInside;
      break;

    case State::kInside:
      Throw("{");
  }
}

void PPrioritySettings::Key([[maybe_unused]] std::string_view key)
{
  key_ = key;
  if (false) {
  } else if (key == "priorities_tuple") {
    s_priorities_tuple_ = true;
    f_priorities_tuple_.Reset();

    parser_state_->PushParser(f_priorities_tuple_.GetParser());
  } else {
    /* Eat and ignore unknown value */
    ff_empty_.Reset();
    parser_state_->PushParser(ff_empty_.GetParser());
  }
}

void PPrioritySettings::EndObject()
{
  switch (state_) {
    case State::kStart:
      Throw("}");

    case State::kInside:
      // If an exception is thrown below, we must not set .old_key
      key_.clear();

      if (!s_priorities_tuple_) {
        throw ::formats::json::parser::InternalParseError(
            "missing required field 'priorities_tuple'");
      }

      SetResult(std::move(result_));
      break;
  }
}

std::string PPrioritySettings::Expected() const {
  switch (state_) {
    case State::kStart:
      return "object";

    case State::kInside:
      return "field name";
  }
}

std::string PPrioritySettings::GetPathItem() const { return key_; }
}

}

namespace experiments3::test_oneof_with_discriminator {

static const std::unordered_set<std::string> kValueExtraNonExtraKeys = {};

experiments3::test_oneof_with_discriminator::ValueExtra Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<experiments3::test_oneof_with_discriminator::ValueExtra>,
    [[maybe_unused]] ::codegen::ParsingFlags flags) {
  experiments3::test_oneof_with_discriminator::ValueExtra result;

  elem.CheckNotMissing();
  elem.CheckObjectOrNull();

  if (flags == ::codegen::ParsingFlags::kParseExtra)
  {
    for (auto it = elem.begin(); it != elem.end(); ++it) {
      const auto& name = it.GetName();
      /* Skip 'properties', they don't go to additionalProperties */
      if (kValueExtraNonExtraKeys.count(name) > 0) continue;

      result.extra.emplace(name,
                           (*it)
                               .As<experiments3::test_oneof_with_discriminator::
                                       PrioritySettings>());
    }
  }

  return result;
}

namespace parser {
template <class To>
template <class From>
To PValueExtra::ParserLocalConverterTrait<To>::Convert(From&& from) {
  return ::codegen::impl::Convert<To>(std::forward<From>(from));
}

template <class To>
To PValueExtra::ParserLocalDomToType<To>::Convert(
    ::formats::json::Value&& value) {
  return std::move(value).As<To>();
}

PValueExtra::PValueExtra()
{
  f_extra_.Subscribe(f_extra_helper_);
}

void PValueExtra::Reset()
{
  state_ = State::kStart;
  result_ = {};
}

void PValueExtra::StartObject() {
  switch (state_) {
    case State::kStart:
      state_ = State::kInside;
      break;

    case State::kInside:
      Throw("{");
  }
}

void PValueExtra::Key([[maybe_unused]] std::string_view key)
{
  key_ = key;
  if (false) {
  } else {
    f_extra_.Reset();
    f_extra_helper_.SetKey(key);
    parser_state_->PushParser(f_extra_.GetParser());
  }
}

void PValueExtra::EndObject()
{
  switch (state_) {
    case State::kStart:
      Throw("}");

    case State::kInside:
      // If an exception is thrown below, we must not set .old_key
      key_.clear();

      result_.extra = f_extra_helper_.ExtractValue();

      SetResult(std::move(result_));
      break;
  }
}

std::string PValueExtra::Expected() const {
  switch (state_) {
    case State::kStart:
      return "object";

    case State::kInside:
      return "field name";
  }
}

std::string PValueExtra::GetPathItem() const { return key_; }
}

}

namespace experiments3::test_oneof_with_discriminator {

static const std::unordered_set<std::string> kValueNonExtraKeys = {};

experiments3::test_oneof_with_discriminator::Value Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<experiments3::test_oneof_with_discriminator::Value>,
    [[maybe_unused]] ::codegen::ParsingFlags flags) {
  experiments3::test_oneof_with_discriminator::Value result;

  elem.CheckNotMissing();
  elem.CheckObjectOrNull();

  if (flags == ::codegen::ParsingFlags::kParseExtra)
  {
    for (auto it = elem.begin(); it != elem.end(); ++it) {
      const auto& name = it.GetName();
      /* Skip 'properties', they don't go to additionalProperties */
      if (kValueNonExtraKeys.count(name) > 0) continue;

      result.extra.emplace(
          name,
          (*it).As<experiments3::test_oneof_with_discriminator::ValueExtra>());
    }
  }

  return result;
}

namespace parser {
template <class To>
template <class From>
To PValue::ParserLocalConverterTrait<To>::Convert(From&& from) {
  return ::codegen::impl::Convert<To>(std::forward<From>(from));
}

template <class To>
To PValue::ParserLocalDomToType<To>::Convert(::formats::json::Value&& value) {
  return std::move(value).As<To>();
}

PValue::PValue()
{
  f_extra_.Subscribe(f_extra_helper_);
}

void PValue::Reset()
{
  state_ = State::kStart;
  result_ = {};
}

void PValue::StartObject() {
  switch (state_) {
    case State::kStart:
      state_ = State::kInside;
      break;

    case State::kInside:
      Throw("{");
  }
}

void PValue::Key([[maybe_unused]] std::string_view key)
{
  key_ = key;
  if (false) {
  } else {
    f_extra_.Reset();
    f_extra_helper_.SetKey(key);
    parser_state_->PushParser(f_extra_.GetParser());
  }
}

void PValue::EndObject()
{
  switch (state_) {
    case State::kStart:
      Throw("}");

    case State::kInside:
      // If an exception is thrown below, we must not set .old_key
      key_.clear();

      result_.extra = f_extra_helper_.ExtractValue();

      SetResult(std::move(result_));
      break;
  }
}

std::string PValue::Expected() const {
  switch (state_) {
    case State::kStart:
      return "object";

    case State::kInside:
      return "field name";
  }
}

std::string PValue::GetPathItem() const { return key_; }
}

}

namespace experiments3 {

const std::string TestOneofWithDiscriminator::kName =
    "test_oneof_with_discriminator";

}
