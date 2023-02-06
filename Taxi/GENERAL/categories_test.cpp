#include "categories.hpp"
#include <userver/utest/utest.hpp>

void TestCategories(const models::Classes& park_categories,
                    const models::Classes& car_categories,
                    const models::Classes& driver_restrictions,
                    const models::Classes& expected_classes) {
  const auto& actual = models::Categories::MakeAvailableClasses(
      park_categories, car_categories, driver_restrictions);
  ASSERT_EQ(expected_classes, actual);
}

UTEST(MakeAvailableClasses, Simple) {
  TestCategories(models::Classes{"econom"},
                 models::Classes{{"econom", "comfort"}},
                 models::Classes{"econom"}, models::Classes{"comfort"});
}

UTEST(MakeAvailableClasses, RealDriver1) {
  TestCategories(
      models::Classes({"standart", "start", "vip"}),
      models::Classes{{"business", "business2", "comfortplus", "econom",
                       "standart", "start", "vip"}},
      models::Classes{{"standart", "start", "vip"}},
      models::Classes{{"econom", "business", "business2", "comfortplus"}});
}

UTEST(MakeAvailableClasses, RealDriver2) {
  TestCategories(
      models::Classes(
          {"express", "minivan", "standart", "start", "universal", "vip"}),
      models::Classes{{"business", "business2", "comfortplus", "econom",
                       "express", "start"}},
      models::Classes{
          {"express", "minivan", "standart", "start", "universal", "vip"}},
      models::Classes{{"business2", "business", "comfortplus", "econom"}});
}

UTEST(MakeAvailableClasses, RealDriver2NoCommonSettings) {
  TestCategories(models::Classes{"express"},
                 models::Classes{{"business", "business2", "comfortplus",
                                  "econom", "express", "start"}},
                 models::Classes{{"express", "minivan", "standart", "start",
                                  "universal", "vip"}},
                 models::Classes{{"business2", "business", "comfortplus",
                                  "econom", "start"}});
}

UTEST(MakeAvailableClasses, RealDriver3) {
  TestCategories(
      models::Classes{},
      models::Classes{{"business", "econom", "express", "minivan", "standart",
                       "start", "business2", "comfortplus", "universal",
                       "vip"}},
      models::Classes{{"business2", "comfortplus", "universal", "vip"}},
      models::Classes{{"business", "econom", "express", "minivan", "standart",
                       "start", "business2", "comfortplus", "universal",
                       "vip"}});
}

UTEST(MakeAvailableClasses, RealDriver3NoCommonSettings) {
  TestCategories(
      models::Classes{"express", "vip"},
      models::Classes{
          {"business", "econom", "express", "minivan", "standart", "start"}},
      models::Classes{{"business2", "comfortplus", "universal", "vip"}},
      models::Classes{
          {"econom", "start", "minivan", "business", "express", "standart"}});
}
