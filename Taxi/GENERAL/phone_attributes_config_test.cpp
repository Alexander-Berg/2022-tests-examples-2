#include <gtest/gtest.h>

#include <base-proxy-passport/cache/phone_attributes_config.hpp>
#include <clients/passport/client.hpp>

#include <userver/components/component_config.hpp>
#include <userver/formats/yaml/serialize.hpp>

namespace {
clients::passport::Client::PhoneAttributes RunFor(const std::string& yaml) {
  formats::yaml::Value cfg = formats::yaml::FromString(yaml);
  return base_proxy_passport::cache::ParsePhoneAttributes(
      yaml_config::YamlConfig(cfg, {}), {});
}
void CheckParsedInto(const std::string& yaml,
                     clients::passport::Client::PhoneAttributes attr) {
  formats::yaml::Value cfg = formats::yaml::FromString(yaml);
  EXPECT_EQ(RunFor(yaml), attr);
}

}  // namespace

TEST(PhoneAttributesParsing, NewSettingTest) {
  CheckParsedInto("phone_attributes: all",
                  clients::passport::Client::PhoneAttributes::kAll);
  CheckParsedInto("phone_attributes: no",
                  clients::passport::Client::PhoneAttributes::kWithout);
  CheckParsedInto(
      "phone_attributes: with_confirmation",
      clients::passport::Client::PhoneAttributes::kDefaultConfirmation);
  CheckParsedInto("phone_attributes: with_bank",
                  clients::passport::Client::PhoneAttributes::kWithIsBank);
  CheckParsedInto("phone_attributes: default_with_bank",
                  clients::passport::Client::PhoneAttributes::kDefaultWithBank);
  CheckParsedInto(
      "phone_attributes: confirmation_with_bank",
      clients::passport::Client::PhoneAttributes::kConfirmationWithBank);
  CheckParsedInto("phone_attributes: just_is_secured",
                  clients::passport::Client::PhoneAttributes::kJustIsSecured);
  CheckParsedInto("phone_attributes: default",
                  clients::passport::Client::PhoneAttributes::kDefault);
}

TEST(PhoneAttributesParsing, WithPhoneAttributesTest) {
  CheckParsedInto(
      "with_phone_attributes: true",
      clients::passport::Client::PhoneAttributes::kDefaultConfirmation);
  CheckParsedInto("with_phone_attributes: false",
                  clients::passport::Client::PhoneAttributes::kWithout);
}

TEST(PhoneAttributesParsing, WithPhoneConfirmationTimeTest) {
  CheckParsedInto("with_phone_confirmation_time: true",
                  clients::passport::Client::PhoneAttributes::kDefault);
  CheckParsedInto("with_phone_confirmation_time: false",
                  clients::passport::Client::PhoneAttributes::kWithout);
}

TEST(PhoneAttributesParsing, MissingDefaultValueTest) {
  for (auto attr : {clients::passport::Client::PhoneAttributes::kWithout,
                    clients::passport::Client::PhoneAttributes::kDefault}) {
    EXPECT_EQ(base_proxy_passport::cache::ParsePhoneAttributes(
                  yaml_config::YamlConfig({}, {}), attr),
              attr);
  }
}

TEST(PhoneAttributesParsing, InvalidSettingsTest) {
  EXPECT_ANY_THROW(
      RunFor("phone_attributes: all\nwith_phone_attributes: true"));
  EXPECT_ANY_THROW(RunFor("phone_attributes: true"));
}
