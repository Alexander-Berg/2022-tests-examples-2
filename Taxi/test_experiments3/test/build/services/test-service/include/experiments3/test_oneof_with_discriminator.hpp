/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

// This file was generated from file(s):
// taxi/uservices/services/test-service/experiments3/declarations/test_oneof_with_discriminator.yaml

#pragma once

#include <experiments3/models/experiment_type.hpp>

#include <string>
#include <unordered_map>
#include <variant>
#include <vector>

#include <array>
#include <boost/type_traits/has_equal_to.hpp>
#include <codegen/convert_to_json_optional.hpp>
#include <codegen/format.hpp>
#include <codegen/parsing_flags.hpp>
#include <userver/formats/json/inline.hpp>
#include <userver/formats/json/string_builder_fwd.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/logging/log_helper_fwd.hpp>

#include <codegen/parser/datetime_parser.hpp>
#include <codegen/parser/dummy_parser.hpp>  // TODO: for debug only
#include <codegen/parser/enum_parser.hpp>
#include <codegen/parser/extra_helper.hpp>
#include <codegen/parser/null_swallow.hpp>
#include <codegen/parser/nullable_helper.hpp>
#include <codegen/parser/parser_converter.hpp>
#include <codegen/parser/parser_dom.hpp>
#include <codegen/parser/parser_empty.hpp>
#include <codegen/parser/parser_non_null_ptr.hpp>
#include <codegen/parser/validator.hpp>
#include <codegen/parser/value_builder_helper.hpp>
#include <userver/formats/json/parser/parser.hpp>

namespace experiments3::test_oneof_with_discriminator {

struct ValueMap {
  ::std::unordered_map<std::string, ::std::size_t> extra{};
};

ValueMap Parse(
    const formats::json::Value& elem, formats::parse::To<ValueMap>,
    ::codegen::ParsingFlags flags = ::codegen::ParsingFlags::kParseExtra);

namespace parser {
class PValueMap final
    : public ::formats::json::parser::TypedParser<
          experiments3::test_oneof_with_discriminator::ValueMap> {
 public:
  PValueMap();

  void Reset() override;

  void StartObject() override;

  void Key(std::string_view key) override;

  void EndObject() override;

 private:
  std::string Expected() const override;

  std::string GetPathItem() const override;

  experiments3::test_oneof_with_discriminator::ValueMap result_;
  std::string key_;

  template <class To>
  struct ParserLocalConverterTrait {
    template <class From>
    static To Convert(From&& from);
  };

  template <class To>
  struct ParserLocalDomToType {
    static To Convert(::formats::json::Value&& value);
  };

  /* validation: ValidationData(minimum=0, maximum=None, exclusiveMinimum=False,
   * exclusiveMaximum=False, minItems=None, maxItems=None, minLength=None,
   * maxLength=None, pattern=None)
   */
  // .cpp_type: int
  // .optional_subtype: None
  // cpp_type: int
  ::formats::json::parser::IntegralParser<int> f_t_v_extra_;

  struct f_t_v_val_extra_ {
    void Validate(const int& value) {
      if (!(0 <= value)) {
        auto msg =
            "out of bounds, must be 0 (limit) <= " + std::to_string(value) +
            " (value)";
        throw std::runtime_error(msg);
      }
    }
  };
  ::codegen::parser::Validator<decltype(f_t_v_extra_), f_t_v_val_extra_>
      f_t_extra_{f_t_v_extra_};
  ::codegen::parser::Converter<::std::size_t, decltype(f_t_extra_),
                               ParserLocalConverterTrait<::std::size_t>>
      f_extra_{f_t_extra_};
  ::codegen::parser::ExtraHelper<::std::size_t,
                                 std::unordered_map<std::string, ::std::size_t>>
      f_extra_helper_;

  enum class State {
    kStart,
    kInside,
  };
  State state_;
};

}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

enum class ConstValueType { kConst };

inline constexpr std::array<ConstValueType, 1> kConstValueTypeValues = {
    ConstValueType::kConst,
};

std::string ToString(
    experiments3::test_oneof_with_discriminator::ConstValueType value);

ConstValueType Parse(const formats::json::Value& elem,
                     formats::parse::To<ConstValueType>);

ConstValueType Parse(std::string_view elem, formats::parse::To<ConstValueType>);

namespace parser {
using PConstValueType = ::codegen::parser::EnumParser<
    experiments3::test_oneof_with_discriminator::ConstValueType>;

}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

struct ConstValue {
  ::experiments3::test_oneof_with_discriminator::ConstValueType type{};
  int value{};
};

ConstValue Parse(const formats::json::Value& elem,
                 formats::parse::To<ConstValue>);

namespace parser {
class PConstValue final
    : public ::formats::json::parser::TypedParser<
          experiments3::test_oneof_with_discriminator::ConstValue> {
 public:
  PConstValue();

  void Reset() override;

  void StartObject() override;

  void Key(std::string_view key) override;

  void EndObject() override;

 private:
  std::string Expected() const override;

  std::string GetPathItem() const override;

  experiments3::test_oneof_with_discriminator::ConstValue result_;
  std::string key_;

  template <class To>
  struct ParserLocalConverterTrait {
    template <class From>
    static To Convert(From&& from);
  };

  template <class To>
  struct ParserLocalDomToType {
    static To Convert(::formats::json::Value&& value);
  };

  // type
  // .cpp_type: experiments3::test_oneof_with_discriminator::ConstValueType
  // .optional_subtype: None
  // cpp_type: experiments3::test_oneof_with_discriminator::ConstValueType
  experiments3::test_oneof_with_discriminator::parser::PConstValueType f_type_;

  ::formats::json::parser::SubscriberSink<
      experiments3::test_oneof_with_discriminator::ConstValueType>
      sink_type_{result_.type};

  bool s_type_{false};

  // value
  /* validation: ValidationData(minimum=0, maximum=None, exclusiveMinimum=False,
   * exclusiveMaximum=False, minItems=None, maxItems=None, minLength=None,
   * maxLength=None, pattern=None)
   */
  // .cpp_type: int
  // .optional_subtype: None
  // cpp_type: int
  ::formats::json::parser::IntegralParser<int> f_v_value_;

  struct f_v_val_value_ {
    void Validate(const int& value) {
      if (!(0 <= value)) {
        auto msg =
            "out of bounds, must be 0 (limit) <= " + std::to_string(value) +
            " (value)";
        throw std::runtime_error(msg);
      }
    }
  };
  ::codegen::parser::Validator<decltype(f_v_value_), f_v_val_value_> f_value_{
      f_v_value_};
  ::formats::json::parser::SubscriberSink<int> sink_value_{result_.value};

  bool s_value_{false};

  ::codegen::parser::EmptyParser ff_empty_;

  enum class State {
    kStart,
    kInside,
  };
  State state_;
};

}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

enum class DefaultCustomValueBySubTypeType { kBySubtype };

inline constexpr std::array<DefaultCustomValueBySubTypeType, 1>
    kDefaultCustomValueBySubTypeTypeValues = {
        DefaultCustomValueBySubTypeType::kBySubtype,
};

std::string ToString(
    experiments3::test_oneof_with_discriminator::DefaultCustomValueBySubTypeType
        value);

DefaultCustomValueBySubTypeType Parse(
    const formats::json::Value& elem,
    formats::parse::To<DefaultCustomValueBySubTypeType>);

DefaultCustomValueBySubTypeType Parse(
    std::string_view elem, formats::parse::To<DefaultCustomValueBySubTypeType>);

namespace parser {
using PDefaultCustomValueBySubTypeType =
    ::codegen::parser::EnumParser<experiments3::test_oneof_with_discriminator::
                                      DefaultCustomValueBySubTypeType>;

}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

struct DefaultCustomValueBySubType {
  ::experiments3::test_oneof_with_discriminator::DefaultCustomValueBySubTypeType
      type{};
  ::experiments3::test_oneof_with_discriminator::ValueMap value{};
};

DefaultCustomValueBySubType Parse(
    const formats::json::Value& elem,
    formats::parse::To<DefaultCustomValueBySubType>);

namespace parser {
class PDefaultCustomValueBySubType final
    : public ::formats::json::parser::TypedParser<
          experiments3::test_oneof_with_discriminator::
              DefaultCustomValueBySubType> {
 public:
  PDefaultCustomValueBySubType();

  void Reset() override;

  void StartObject() override;

  void Key(std::string_view key) override;

  void EndObject() override;

 private:
  std::string Expected() const override;

  std::string GetPathItem() const override;

  experiments3::test_oneof_with_discriminator::DefaultCustomValueBySubType
      result_;
  std::string key_;

  template <class To>
  struct ParserLocalConverterTrait {
    template <class From>
    static To Convert(From&& from);
  };

  template <class To>
  struct ParserLocalDomToType {
    static To Convert(::formats::json::Value&& value);
  };

  // type
  // .cpp_type:
  // experiments3::test_oneof_with_discriminator::DefaultCustomValueBySubTypeType
  // .optional_subtype: None
  // cpp_type:
  // experiments3::test_oneof_with_discriminator::DefaultCustomValueBySubTypeType
  experiments3::test_oneof_with_discriminator::parser::
      PDefaultCustomValueBySubTypeType f_type_;

  ::formats::json::parser::SubscriberSink<
      experiments3::test_oneof_with_discriminator::
          DefaultCustomValueBySubTypeType>
      sink_type_{result_.type};

  bool s_type_{false};

  // value
  // .cpp_type: experiments3::test_oneof_with_discriminator::ValueMap
  // .optional_subtype: None
  // cpp_type: experiments3::test_oneof_with_discriminator::ValueMap
  experiments3::test_oneof_with_discriminator::parser::PValueMap f_value_;

  ::formats::json::parser::SubscriberSink<
      experiments3::test_oneof_with_discriminator::ValueMap>
      sink_value_{result_.value};

  bool s_value_{false};

  ::codegen::parser::EmptyParser ff_empty_;

  enum class State {
    kStart,
    kInside,
  };
  State state_;
};

}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

class DefaultCustomValue {
 public:
  using Variant = std::variant<
      experiments3::test_oneof_with_discriminator::DefaultCustomValueBySubType,
      experiments3::test_oneof_with_discriminator::ConstValue>;

  DefaultCustomValue() = default;

  template <
      class T,
      class = std::enable_if_t<
          std::is_same<std::decay_t<T>, Variant>::value ||
          std::is_same<std::decay_t<T>,
                       experiments3::test_oneof_with_discriminator::
                           DefaultCustomValueBySubType>::value ||
          std::is_same<
              std::decay_t<T>,
              experiments3::test_oneof_with_discriminator::ConstValue>::value>>
  explicit DefaultCustomValue(T&& value)
      : data_(std::forward<T>(value))
  {}

  template <
      class T,
      class = std::enable_if_t<
          std::is_same<std::decay_t<T>, Variant>::value ||
          std::is_same<std::decay_t<T>,
                       experiments3::test_oneof_with_discriminator::
                           DefaultCustomValueBySubType>::value ||
          std::is_same<
              std::decay_t<T>,
              experiments3::test_oneof_with_discriminator::ConstValue>::value>>
  DefaultCustomValue& operator=(T&& value) {
    data_ = std::forward<T>(value);
    return *this;
  }

  template <class Target>
  Target& As() {
    return std::get<Target>(data_);
  }

  template <class Target>
  const Target& As() const {
    return std::get<Target>(data_);
  }

  Variant& AsVariant() { return data_; }
  const Variant& AsVariant() const { return data_; }

 private:
  Variant data_{};
};

DefaultCustomValue Parse(const formats::json::Value& elem,
                         formats::parse::To<DefaultCustomValue>);

namespace parser {
struct PDefaultCustomValueDomToType {
  static experiments3::test_oneof_with_discriminator::DefaultCustomValue
  Convert(::formats::json::Value&& value);
};
using PDefaultCustomValue = ::codegen::parser::ParserDom<
    experiments3::test_oneof_with_discriminator::DefaultCustomValue,
    PDefaultCustomValueDomToType>;

}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

struct ByProviderCustomValue {
  ::std::unordered_map<
      std::string,
      ::experiments3::test_oneof_with_discriminator::DefaultCustomValue>
      extra{};
};

ByProviderCustomValue Parse(
    const formats::json::Value& elem, formats::parse::To<ByProviderCustomValue>,
    ::codegen::ParsingFlags flags = ::codegen::ParsingFlags::kParseExtra);

namespace parser {
class PByProviderCustomValue final
    : public ::formats::json::parser::TypedParser<
          experiments3::test_oneof_with_discriminator::ByProviderCustomValue> {
 public:
  PByProviderCustomValue();

  void Reset() override;

  void StartObject() override;

  void Key(std::string_view key) override;

  void EndObject() override;

 private:
  std::string Expected() const override;

  std::string GetPathItem() const override;

  experiments3::test_oneof_with_discriminator::ByProviderCustomValue result_;
  std::string key_;

  template <class To>
  struct ParserLocalConverterTrait {
    template <class From>
    static To Convert(From&& from);
  };

  template <class To>
  struct ParserLocalDomToType {
    static To Convert(::formats::json::Value&& value);
  };

  ::codegen::parser::ParserDom<
      experiments3::test_oneof_with_discriminator::DefaultCustomValue,
      ParserLocalDomToType<
          experiments3::test_oneof_with_discriminator::DefaultCustomValue>>
      f_extra_;

  ::codegen::parser::ExtraHelper<
      experiments3::test_oneof_with_discriminator::DefaultCustomValue,
      std::unordered_map<
          std::string,
          ::experiments3::test_oneof_with_discriminator::DefaultCustomValue>>
      f_extra_helper_;

  enum class State {
    kStart,
    kInside,
  };
  State state_;
};

}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

enum class CustomValueType { kValue };

inline constexpr std::array<CustomValueType, 1> kCustomValueTypeValues = {
    CustomValueType::kValue,
};

std::string ToString(
    experiments3::test_oneof_with_discriminator::CustomValueType value);

CustomValueType Parse(const formats::json::Value& elem,
                      formats::parse::To<CustomValueType>);

CustomValueType Parse(std::string_view elem,
                      formats::parse::To<CustomValueType>);

namespace parser {
using PCustomValueType = ::codegen::parser::EnumParser<
    experiments3::test_oneof_with_discriminator::CustomValueType>;

}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

struct CustomValue {
  ::experiments3::test_oneof_with_discriminator::ByProviderCustomValue
      by_provider{};
  ::experiments3::test_oneof_with_discriminator::CustomValueType type{};
};

CustomValue Parse(const formats::json::Value& elem,
                  formats::parse::To<CustomValue>);

namespace parser {
class PCustomValue final
    : public ::formats::json::parser::TypedParser<
          experiments3::test_oneof_with_discriminator::CustomValue> {
 public:
  PCustomValue();

  void Reset() override;

  void StartObject() override;

  void Key(std::string_view key) override;

  void EndObject() override;

 private:
  std::string Expected() const override;

  std::string GetPathItem() const override;

  experiments3::test_oneof_with_discriminator::CustomValue result_;
  std::string key_;

  template <class To>
  struct ParserLocalConverterTrait {
    template <class From>
    static To Convert(From&& from);
  };

  template <class To>
  struct ParserLocalDomToType {
    static To Convert(::formats::json::Value&& value);
  };

  // by_provider
  // .cpp_type:
  // experiments3::test_oneof_with_discriminator::ByProviderCustomValue
  // .optional_subtype: None
  // cpp_type:
  // experiments3::test_oneof_with_discriminator::ByProviderCustomValue
  experiments3::test_oneof_with_discriminator::parser::PByProviderCustomValue
      f_by_provider_;

  ::formats::json::parser::SubscriberSink<
      experiments3::test_oneof_with_discriminator::ByProviderCustomValue>
      sink_by_provider_{result_.by_provider};

  bool s_by_provider_{false};

  // type
  // .cpp_type: experiments3::test_oneof_with_discriminator::CustomValueType
  // .optional_subtype: None
  // cpp_type: experiments3::test_oneof_with_discriminator::CustomValueType
  experiments3::test_oneof_with_discriminator::parser::PCustomValueType f_type_;

  ::formats::json::parser::SubscriberSink<
      experiments3::test_oneof_with_discriminator::CustomValueType>
      sink_type_{result_.type};

  bool s_type_{false};

  ::codegen::parser::EmptyParser ff_empty_;

  enum class State {
    kStart,
    kInside,
  };
  State state_;
};

}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

enum class MultipliedHashType { kMultHash };

inline constexpr std::array<MultipliedHashType, 1> kMultipliedHashTypeValues = {
    MultipliedHashType::kMultHash,
};

std::string ToString(
    experiments3::test_oneof_with_discriminator::MultipliedHashType value);

MultipliedHashType Parse(const formats::json::Value& elem,
                         formats::parse::To<MultipliedHashType>);

MultipliedHashType Parse(std::string_view elem,
                         formats::parse::To<MultipliedHashType>);

namespace parser {
using PMultipliedHashType = ::codegen::parser::EnumParser<
    experiments3::test_oneof_with_discriminator::MultipliedHashType>;

}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

struct MultipliedHash {
  ::experiments3::test_oneof_with_discriminator::ValueMap by_provider{};
  ::experiments3::test_oneof_with_discriminator::MultipliedHashType type{};
};

MultipliedHash Parse(const formats::json::Value& elem,
                     formats::parse::To<MultipliedHash>);

namespace parser {
class PMultipliedHash final
    : public ::formats::json::parser::TypedParser<
          experiments3::test_oneof_with_discriminator::MultipliedHash> {
 public:
  PMultipliedHash();

  void Reset() override;

  void StartObject() override;

  void Key(std::string_view key) override;

  void EndObject() override;

 private:
  std::string Expected() const override;

  std::string GetPathItem() const override;

  experiments3::test_oneof_with_discriminator::MultipliedHash result_;
  std::string key_;

  template <class To>
  struct ParserLocalConverterTrait {
    template <class From>
    static To Convert(From&& from);
  };

  template <class To>
  struct ParserLocalDomToType {
    static To Convert(::formats::json::Value&& value);
  };

  // by_provider
  // .cpp_type: experiments3::test_oneof_with_discriminator::ValueMap
  // .optional_subtype: None
  // cpp_type: experiments3::test_oneof_with_discriminator::ValueMap
  experiments3::test_oneof_with_discriminator::parser::PValueMap f_by_provider_;

  ::formats::json::parser::SubscriberSink<
      experiments3::test_oneof_with_discriminator::ValueMap>
      sink_by_provider_{result_.by_provider};

  bool s_by_provider_{false};

  // type
  // .cpp_type: experiments3::test_oneof_with_discriminator::MultipliedHashType
  // .optional_subtype: None
  // cpp_type: experiments3::test_oneof_with_discriminator::MultipliedHashType
  experiments3::test_oneof_with_discriminator::parser::PMultipliedHashType
      f_type_;

  ::formats::json::parser::SubscriberSink<
      experiments3::test_oneof_with_discriminator::MultipliedHashType>
      sink_type_{result_.type};

  bool s_type_{false};

  ::codegen::parser::EmptyParser ff_empty_;

  enum class State {
    kStart,
    kInside,
  };
  State state_;
};

}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

class PriorityItemPayload {
 public:
  using Variant =
      std::variant<experiments3::test_oneof_with_discriminator::MultipliedHash,
                   experiments3::test_oneof_with_discriminator::CustomValue>;

  PriorityItemPayload() = default;

  template <
      class T,
      class = std::enable_if_t<
          std::is_same<std::decay_t<T>, Variant>::value ||
          std::is_same<std::decay_t<T>,
                       experiments3::test_oneof_with_discriminator::
                           MultipliedHash>::value ||
          std::is_same<
              std::decay_t<T>,
              experiments3::test_oneof_with_discriminator::CustomValue>::value>>
  explicit PriorityItemPayload(T&& value)
      : data_(std::forward<T>(value))
  {}

  template <
      class T,
      class = std::enable_if_t<
          std::is_same<std::decay_t<T>, Variant>::value ||
          std::is_same<std::decay_t<T>,
                       experiments3::test_oneof_with_discriminator::
                           MultipliedHash>::value ||
          std::is_same<
              std::decay_t<T>,
              experiments3::test_oneof_with_discriminator::CustomValue>::value>>
  PriorityItemPayload& operator=(T&& value) {
    data_ = std::forward<T>(value);
    return *this;
  }

  template <class Target>
  Target& As() {
    return std::get<Target>(data_);
  }

  template <class Target>
  const Target& As() const {
    return std::get<Target>(data_);
  }

  Variant& AsVariant() { return data_; }
  const Variant& AsVariant() const { return data_; }

 private:
  Variant data_{};
};

PriorityItemPayload Parse(const formats::json::Value& elem,
                          formats::parse::To<PriorityItemPayload>);

namespace parser {
struct PPriorityItemPayloadDomToType {
  static experiments3::test_oneof_with_discriminator::PriorityItemPayload
  Convert(::formats::json::Value&& value);
};
using PPriorityItemPayload = ::codegen::parser::ParserDom<
    experiments3::test_oneof_with_discriminator::PriorityItemPayload,
    PPriorityItemPayloadDomToType>;

}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

struct PriorityItem {
  ::std::string name{};
  ::experiments3::test_oneof_with_discriminator::PriorityItemPayload payload{};
};

PriorityItem Parse(const formats::json::Value& elem,
                   formats::parse::To<PriorityItem>);

namespace parser {
class PPriorityItem final
    : public ::formats::json::parser::TypedParser<
          experiments3::test_oneof_with_discriminator::PriorityItem> {
 public:
  PPriorityItem();

  void Reset() override;

  void StartObject() override;

  void Key(std::string_view key) override;

  void EndObject() override;

 private:
  std::string Expected() const override;

  std::string GetPathItem() const override;

  experiments3::test_oneof_with_discriminator::PriorityItem result_;
  std::string key_;

  template <class To>
  struct ParserLocalConverterTrait {
    template <class From>
    static To Convert(From&& from);
  };

  template <class To>
  struct ParserLocalDomToType {
    static To Convert(::formats::json::Value&& value);
  };

  // name
  // .cpp_type: std::string
  // .optional_subtype: None
  // cpp_type: std::string
  ::formats::json::parser::StringParser f_name_;

  ::formats::json::parser::SubscriberSink<std::string> sink_name_{result_.name};

  bool s_name_{false};

  // payload

  ::codegen::parser::ParserDom<
      experiments3::test_oneof_with_discriminator::PriorityItemPayload,
      ParserLocalDomToType<
          experiments3::test_oneof_with_discriminator::PriorityItemPayload>>
      f_payload_;

  ::formats::json::parser::SubscriberSink<
      experiments3::test_oneof_with_discriminator::PriorityItemPayload>
      sink_payload_{result_.payload};

  bool s_payload_{false};

  ::codegen::parser::EmptyParser ff_empty_;

  enum class State {
    kStart,
    kInside,
  };
  State state_;
};

}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

/// Тут задаем содержимое кортежа приоритетов и конкретные значение для
/// провайдеров
struct PrioritySettings {
  ::std::vector<experiments3::test_oneof_with_discriminator::PriorityItem>
      priorities_tuple{};
};

PrioritySettings Parse(const formats::json::Value& elem,
                       formats::parse::To<PrioritySettings>);

namespace parser {
class PPrioritySettings final
    : public ::formats::json::parser::TypedParser<
          experiments3::test_oneof_with_discriminator::PrioritySettings> {
 public:
  PPrioritySettings();

  void Reset() override;

  void StartObject() override;

  void Key(std::string_view key) override;

  void EndObject() override;

 private:
  std::string Expected() const override;

  std::string GetPathItem() const override;

  experiments3::test_oneof_with_discriminator::PrioritySettings result_;
  std::string key_;

  template <class To>
  struct ParserLocalConverterTrait {
    template <class From>
    static To Convert(From&& from);
  };

  template <class To>
  struct ParserLocalDomToType {
    static To Convert(::formats::json::Value&& value);
  };

  // priorities_tuple
  // .cpp_type: experiments3::test_oneof_with_discriminator::PriorityItem
  // .optional_subtype: None
  // cpp_type: experiments3::test_oneof_with_discriminator::PriorityItem
  experiments3::test_oneof_with_discriminator::parser::PPriorityItem
      f_priorities_tuple_i_;

  ::formats::json::parser::ArrayParser<
      experiments3::test_oneof_with_discriminator::PriorityItem,
      decltype(f_priorities_tuple_i_),
      std::vector<experiments3::test_oneof_with_discriminator::PriorityItem>>
      f_priorities_tuple_{f_priorities_tuple_i_};

  ::formats::json::parser::SubscriberSink<
      std::vector<experiments3::test_oneof_with_discriminator::PriorityItem>>
      sink_priorities_tuple_{result_.priorities_tuple};

  bool s_priorities_tuple_{false};

  ::codegen::parser::EmptyParser ff_empty_;

  enum class State {
    kStart,
    kInside,
  };
  State state_;
};

}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

/// Screen
struct ValueExtra {
  ::std::unordered_map<
      std::string,
      ::experiments3::test_oneof_with_discriminator::PrioritySettings>
      extra{};
};

ValueExtra Parse(
    const formats::json::Value& elem, formats::parse::To<ValueExtra>,
    ::codegen::ParsingFlags flags = ::codegen::ParsingFlags::kParseExtra);

namespace parser {
class PValueExtra final
    : public ::formats::json::parser::TypedParser<
          experiments3::test_oneof_with_discriminator::ValueExtra> {
 public:
  PValueExtra();

  void Reset() override;

  void StartObject() override;

  void Key(std::string_view key) override;

  void EndObject() override;

 private:
  std::string Expected() const override;

  std::string GetPathItem() const override;

  experiments3::test_oneof_with_discriminator::ValueExtra result_;
  std::string key_;

  template <class To>
  struct ParserLocalConverterTrait {
    template <class From>
    static To Convert(From&& from);
  };

  template <class To>
  struct ParserLocalDomToType {
    static To Convert(::formats::json::Value&& value);
  };

  // .cpp_type: experiments3::test_oneof_with_discriminator::PrioritySettings
  // .optional_subtype: None
  // cpp_type: experiments3::test_oneof_with_discriminator::PrioritySettings
  experiments3::test_oneof_with_discriminator::parser::PPrioritySettings
      f_extra_;

  ::codegen::parser::ExtraHelper<
      experiments3::test_oneof_with_discriminator::PrioritySettings,
      std::unordered_map<
          std::string,
          ::experiments3::test_oneof_with_discriminator::PrioritySettings>>
      f_extra_helper_;

  enum class State {
    kStart,
    kInside,
  };
  State state_;
};

}  // namespace parser

}

namespace experiments3::test_oneof_with_discriminator {

/// Mode
struct Value {
  ::std::unordered_map<
      std::string, ::experiments3::test_oneof_with_discriminator::ValueExtra>
      extra{};
};

Value Parse(
    const formats::json::Value& elem, formats::parse::To<Value>,
    ::codegen::ParsingFlags flags = ::codegen::ParsingFlags::kParseExtra);

namespace parser {
class PValue final: public ::formats::json::parser::TypedParser<
                        experiments3::test_oneof_with_discriminator::Value> {
 public:
  PValue();

  void Reset() override;

  void StartObject() override;

  void Key(std::string_view key) override;

  void EndObject() override;

 private:
  std::string Expected() const override;

  std::string GetPathItem() const override;

  experiments3::test_oneof_with_discriminator::Value result_;
  std::string key_;

  template <class To>
  struct ParserLocalConverterTrait {
    template <class From>
    static To Convert(From&& from);
  };

  template <class To>
  struct ParserLocalDomToType {
    static To Convert(::formats::json::Value&& value);
  };

  // .cpp_type: experiments3::test_oneof_with_discriminator::ValueExtra
  // .optional_subtype: None
  // cpp_type: experiments3::test_oneof_with_discriminator::ValueExtra
  experiments3::test_oneof_with_discriminator::parser::PValueExtra f_extra_;

  ::codegen::parser::ExtraHelper<
      experiments3::test_oneof_with_discriminator::ValueExtra,
      std::unordered_map<
          std::string,
          ::experiments3::test_oneof_with_discriminator::ValueExtra>>
      f_extra_helper_;

  enum class State {
    kStart,
    kInside,
  };
  State state_;
};

}  // namespace parser

}

namespace experiments3 {
struct TestOneofWithDiscriminator {
  using Value = experiments3::test_oneof_with_discriminator::Value;
  enum class Type { kExperiment, kConfig, kUnion };
  static constexpr auto kType = Type::kConfig;
  static constexpr bool kCacheResult = false;
  static const std::string kName;
};
}