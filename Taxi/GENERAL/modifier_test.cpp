#include <userver/utest/utest.hpp>

#include <array>
#include <memory>
#include <string>

#include <driver_orders_common/models/requestconfirm.hpp>
#include <l10n/l10n.hpp>
#include <storage/redis/repository.hpp>
#include <userver/formats/json/value.hpp>

#include <logic/setcar_processing/modifier.hpp>
#include <logic/setcar_processing/options.hpp>

namespace logic::setcar_processing {
namespace {

class DriverLocalizerMock : public driver_localizer::DriverLocalizerBase {
 public:
  DriverLocalizerMock() {}

  std::string GetWithFallback([[maybe_unused]] const std::string& key,
                              [[maybe_unused]] const std::string& fallback_key,
                              [[maybe_unused]] const l10n::ArgsList& args = {},
                              [[maybe_unused]] int count = 1) const override {
    std::string used_key{key};
    if (key == "subvention_declined_reason.absent.some_reason") {
      used_key = fallback_key;
    }
    auto result{"key=" + used_key + ",params="};
    for (const auto& [k, v] : args) result += k + ":" + v;
    return result;
  }

  std::string Get([[maybe_unused]] const std::string& key,
                  [[maybe_unused]] int count = 1) const override {
    throw std::logic_error{"Not implemented"};
  };
  std::string GetWithArgs([[maybe_unused]] const std::string& key,
                          [[maybe_unused]] const l10n::ArgsList& args,
                          [[maybe_unused]] int count = 1) const override {
    throw std::logic_error{"Not implemented"};
  };
};

}  // namespace

struct TestParam {
  std::string setcar;
  std::string expected;
};

class TestSetCarModification : public testing::Test,
                               public testing::WithParamInterface<TestParam> {};

TEST_P(TestSetCarModification, TestModifications) {
  const Modifier modifier{nullptr, {}, std::make_shared<DriverLocalizerMock>()};

  const auto& param = GetParam();
  ASSERT_EQ(modifier.Modify(formats::json::FromString(param.setcar), {}),
            formats::json::FromString(param.expected));
}

auto MakeAddressTestData() {
  return std::array{
      // No change
      TestParam{R"({
        "provider": 2,
        "address_from": {"Region": "somewhere"},
        "route_points": [],
        "show_address": true
      })",
                R"({
        "provider": 2,
        "address_from": {"Region": "somewhere"},
        "route_points": [],
        "show_address": true
      })"},

      // Not Yandex - don't hide the address and fix it
      TestParam{R"({
        "address_from": {"Street": "street", "House": "house"},
        "address_to": {"Street": "street", "House": "house"},
        "route_points": [],
        "show_address": false
      })",
                R"({
        "address_from": {"Street": "street, house"},
        "address_to": {"Street": "street, house"},
        "route_points": [],
        "show_address": false
      })"},

      // No House -> dont merge
      TestParam{R"({
        "address_from": {"Street": "street"}
      })",
                R"({
        "address_from": {"Street": "street"}
      })"},

      // No Street -> dont put
      TestParam{R"({
        "address_from": {"House": "street"}
      })",
                R"({
        "address_from": {"House": "street"}
      })"},

      // Yandex - fix address_to also
      TestParam{R"({
        "provider": 2,
        "address_to": {"Street": "street", "House": "house"},
        "show_address": true
      })",
                R"({
        "provider": 2,
        "address_to": {"Street": "street, house"},
        "show_address": true
      })"},

      // Yandex - hide the address
      TestParam{R"({
        "provider": 2,
        "address_from": {"Street": "street", "House": "house"},
        "address_to": {"Street": "street", "House": "house"},
        "route_points": [],
        "show_address": false
      })",
                R"({
        "provider": 2,
        "address_from": {"Street": "street, house"},
        "show_address": false
      })"},

      // Route points fix
      TestParam{R"({
        "provider": 2,
        "route_points": [
          {"Street": "s1", "House": "h1"},
          {"Street": "s2", "House": "h2"},
          {"Street": "s3"}
        ],
        "show_address": true
      })",
                R"({
        "provider": 2,
        "route_points": [
          {"Street": "s1, h1"},
          {"Street": "s2, h2"},
          {"Street": "s3"}
        ],
        "show_address": true
      })"},

  };
}

INSTANTIATE_TEST_SUITE_P(TestValidAddresses, TestSetCarModification,
                         ::testing::ValuesIn(MakeAddressTestData()));

auto MakeFixPriceTestData() {
  return std::array{
      // Test all 4 combinations
      TestParam{R"({
          "driver_fixed_price": {"show": true},
          "fixed_price": {"show": true}
      })",
                R"({
          "driver_fixed_price": {"show": true},
          "fixed_price": {"show": true}
      })"},
      TestParam{R"({
          "driver_fixed_price": {"show": true},
          "fixed_price": {"show": false}
      })",
                R"({
          "driver_fixed_price": {"show": true}
      })"},
      TestParam{R"({
          "driver_fixed_price": {"show": false},
          "fixed_price": {"show": true}
      })",
                R"({
          "fixed_price": {"show": true}
      })"},
      TestParam{R"({
          "driver_fixed_price": {"show": false},
          "fixed_price": {"show": false}
      })",
                R"({
      })"},

      // Base price removal
      TestParam{R"({
          "base_price": {}
      })",
                R"({
      })"},
      // Base price removal - user
      TestParam{R"({
          "base_price": {"user":{}}
      })",
                R"({
      })"},
      TestParam{R"({
          "base_price": {"user":{}},
          "fixed_price": {"show": false}
      })",
                R"({
      })"},
      TestParam{R"({
          "base_price": {"user":{}},
          "fixed_price": {"show": true}
      })",
                R"({
          "base_price": {"user":{}},
          "fixed_price": {"show": true}
      })"},
      // Base price removal - driver
      TestParam{R"({
          "base_price": {"driver":{}}
      })",
                R"({
      })"},
      TestParam{R"({
          "base_price": {"driver":{}},
          "driver_fixed_price": {"show": false}
      })",
                R"({
      })"},
      TestParam{R"({
          "base_price": {"driver":{}},
          "driver_fixed_price": {"show": true}
      })",
                R"({
          "base_price": {"driver":{}},
          "driver_fixed_price": {"show": true}
      })"},

  };
}

INSTANTIATE_TEST_SUITE_P(TestFixPrices, TestSetCarModification,
                         ::testing::ValuesIn(MakeFixPriceTestData()));

auto MakeSubventionsTestData() {
  // Provider is not Yandex
  return std::array{
      TestParam{R"({
        "subvention": {
          "disabled_rules": [{
            "declined_reasons":[{
              "key": "some_key",
              "reason": "some_reason",
              "parameters": {"param1": "p1_value"}
            }]
          }]
        }
      })",
                R"({
        "subvention": {
          "disabled_rules": [{
            "declined_reasons":[{
              "key": "some_key",
              "reason": "some_reason",
              "parameters": {"param1": "p1_value"}
            }]
          }]
        }
      })"},
      // Happy path
      TestParam{R"({
        "provider": 2,
        "subvention": {
          "disabled_rules": [{
            "declined_reasons":[{
              "key": "some_key",
              "reason": "some_reason",
              "parameters": {"param1": "p1_value"}
            }],
            "sum": 150,
            "type": "guarantee"
          }]
        }
      })",
                R"({
        "provider": 2,
        "subvention": {
          "disabled_rules": [{
            "declined_reasons":["key=subvention_declined_reason.some_key.some_reason,params=param1:p1_value"],
            "sum": 150,
            "type": "guarantee"
          }]
        }
      })"},
      // Absent key -> fallback
      TestParam{R"({
        "provider": 2,
        "subvention": {
          "disabled_rules": [{
            "declined_reasons":[{
              "key": "absent",
              "reason": "some_reason",
              "parameters": {"param1": "p1_value"}
            }]
          }]
        }
      })",
                R"({
        "provider": 2,
        "subvention": {
          "disabled_rules": [{
            "declined_reasons":["key=subvention_declined_reason,params=param1:p1_value"]
          }]
        }
      })"},
      // No disabled_rules
      TestParam{R"({
        "provider": 2,
        "subvention": {}
      })",
                R"({
        "provider": 2,
        "subvention": {
          "disabled_rules": []
        }
      })"},
      // declined_reasons not an array
      TestParam{R"({
        "provider": 2,
        "subvention": {
          "disabled_rules": [{
            "declined_reasons":"somevalue",
            "sum": 150,
            "type": "guarantee"
          }]
        }
      })",
                R"({
        "provider": 2,
        "subvention": {
          "disabled_rules": [{
            "declined_reasons":[],
            "sum": 150,
            "type": "guarantee"
          }]
        }
      })"},
      // other fields present in subvention
      TestParam{R"({
        "provider": 2,
        "subvention": {
          "combine": "max",
          "disabled_rules": [],
          "rules": []
        }
      })",
                R"({
        "provider": 2,
        "subvention": {
          "combine": "max",
          "disabled_rules": [],
          "rules": []
        }
      })"},
  };
}

INSTANTIATE_TEST_SUITE_P(TestSubventions, TestSetCarModification,
                         ::testing::ValuesIn(MakeSubventionsTestData()));

TEST(TestSetCarModification, TestInvalidAddresses) {
  const Modifier modifier{nullptr, {}, std::make_shared<DriverLocalizerMock>()};

  // address_to not an object
  ASSERT_THROW(modifier.Modify(formats::json::FromString(R"(
      {
        "address_to": "string",
        "route_points": []
      }
    )"),
                               {}),
               formats::json::ParseException);

  // route_points not an array
  ASSERT_THROW(modifier.Modify(formats::json::FromString(R"(
      {
        "address_to": {"Region": "somewhere"},
        "route_points": "not an array"
      }
    )"),
                               {}),
               formats::json::ParseException);
}

TEST(TestSetCarModification, TestStatusSetting) {
  const Modifier modifier{nullptr, {}, std::make_shared<DriverLocalizerMock>()};
  ASSERT_EQ(modifier.Modify(formats::json::FromString("{}"),
                            {RequestConfirmStatus::kUndefined}),
            formats::json::FromString("{}"));
  ASSERT_EQ(modifier.Modify(formats::json::FromString("{}"),
                            {RequestConfirmStatus::kDriving}),
            formats::json::FromString(R"({"status": 2})"));
}

TEST(TestSetCarModification, TestUnneededFieldsRemoval) {
  const Modifier modifier{nullptr, {}, std::make_shared<DriverLocalizerMock>()};
  ASSERT_EQ(modifier.Modify(formats::json::FromString(R"({
    "waiting_mode" : "something",
    "client_geo_sharing" : "something"
  })"),
                            {RequestConfirmStatus::kUndefined}),
            formats::json::FromString(R"({
    "waiting_mode" : "something",
    "client_geo_sharing" : "something"
  })"));

  ASSERT_EQ(modifier.Modify(formats::json::FromString(R"({
    "provider": 2,
    "waiting_mode" : "something",
    "client_geo_sharing" : "something"
  })"),
                            {RequestConfirmStatus::kUndefined}),
            formats::json::FromString(R"({
    "provider": 2
  })"));
}

TEST(TestSetCarModification, TestPayTypeRemoval) {
  const Modifier modifier{nullptr,
                          {{"none", "undefined"}},
                          std::make_shared<DriverLocalizerMock>()};

  // provider is not Yandex
  ASSERT_EQ(modifier.Modify(formats::json::FromString(R"({
    "pay_type" : 0
  })"),
                            {RequestConfirmStatus::kUndefined}),
            formats::json::FromString(R"({
    "pay_type" : 0
  })"));

  // status is in the flags
  ASSERT_EQ(modifier.Modify(formats::json::FromString(R"({
    "provider": 2,
    "pay_type": 0
  })"),
                            {RequestConfirmStatus::kUndefined}),
            formats::json::FromString(R"({
    "provider": 2
  })"));

  // status is not in the flags
  ASSERT_EQ(modifier.Modify(formats::json::FromString(R"({
    "provider": 2,
    "pay_type": 0
  })"),
                            {RequestConfirmStatus::kDriving}),
            formats::json::FromString(R"({
    "provider": 2,
    "pay_type": 0,
    "status": 2
  })"));
}

TEST(TestSetCarModification, TestTypeNameSubstitution) {
  const Modifier modifier{nullptr, {}, std::make_shared<DriverLocalizerMock>()};

  // not a string
  ASSERT_EQ(modifier.Modify(formats::json::FromString(R"({
    "type_name" : []
  })"),
                            {}),
            formats::json::FromString(R"({
    "type_name" : []
  })"));

  // not a value to substitute
  ASSERT_EQ(modifier.Modify(formats::json::FromString(R"({
    "type_name" : "somevalue"
  })"),
                            {}),
            formats::json::FromString(R"({
    "type_name" : "somevalue"
  })"));

  // a value to substitute
  ASSERT_EQ(modifier.Modify(formats::json::FromString(R"({
    "type_name" : "Яндекс.Корпоративный"
  })"),
                            {}),
            formats::json::FromString(R"({
    "type_name" : "Яндекс.Безналичный"
  })"));
}

}  // namespace logic::setcar_processing
