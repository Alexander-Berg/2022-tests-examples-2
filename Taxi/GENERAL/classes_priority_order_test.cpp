#include <configs/classes_priority_order.hpp>

#include <optional>
#include <set>
#include <string>

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <gtest/gtest.h>

std::set<std::string> MakeEmptyClasses() { return {}; }

std::set<std::string> MakeSingleClass() { return {"Business"}; }

std::set<std::string> MakeSomeClasses() {
  return {"Business", "Business2", "ComfortPlus"};
}

std::set<std::string> MakeAllClasses() {
  return {"Business",       "Business2",  "Cargo",          "ChildTariff",
          "ComfortPlus",    "DemoStand",  "Econom",         "Express",
          "Kids",           "Maybach",    "Minivan",        "Mkk",
          "MkkAntifraud",   "Night",      "PersonalDriver", "Pool",
          "PoputkaPromo",   "PremiumSuv", "PremiumVan",     "Promo",
          "SelfDriving",    "Standart",   "Start",          "Suv",
          "UberBlack",      "UberKids",   "UberLux",        "UberSelect",
          "UberSelectPlus", "UberStart",  "UberVan",        "UberX",
          "Ubernight",      "Ultimate",   "Universal",      "Vip"};
}

class ConfigBase {
 public:
  ConfigBase(const std::set<std::string>& classes) {
    auto array_builder =
        formats::json::ValueBuilder(formats::json::Type::kArray);
    for (auto& cls : classes) {
      array_builder.PushBack(std::move(cls));
    }
    auto cfg = array_builder.ExtractValue();

    docs_map.Set("DISPATCH_CLASSES_ORDER", cfg);
  }

  const dynamic_config::DocsMap& GetDocsMap() const { return docs_map; }

 private:
  dynamic_config::DocsMap docs_map;
};

struct EmptyConfig : public ConfigBase {
 public:
  EmptyConfig() : ConfigBase(MakeEmptyClasses()) {}
};

struct SingleClassConfig : public ConfigBase {
 public:
  SingleClassConfig() : ConfigBase(MakeSingleClass()) {}
};

class SomeClassesConfig : public ConfigBase {
 public:
  SomeClassesConfig() : ConfigBase(MakeSomeClasses()) {}
};

struct AllClassesConfig : public ConfigBase {
 public:
  AllClassesConfig() : ConfigBase(MakeAllClasses()) {}
};

TEST(ClassesPriorityOrder, GetMaxOverlapping) {
  auto test = [](const ConfigBase& cfg, const std::string& max_class) {
    auto cpo = driver_scoring::configs::ClassesPriorityOrder(cfg.GetDocsMap());
    auto all_classes = MakeAllClasses();
    return cpo.GetMaxPriorityClass(all_classes) == max_class;
  };

  EXPECT_TRUE(test(SingleClassConfig(), "Business"));
  EXPECT_TRUE(test(SomeClassesConfig(), "ComfortPlus"));
  EXPECT_TRUE(test(AllClassesConfig(), "Vip"));
}

TEST(ClassesPriorityOrder, GetMaxNonOverlapping) {
  auto test = [](const std::set<std::string>& order,
                 const std::set<std::string>& classes) {
    auto cpo = driver_scoring::configs::ClassesPriorityOrder(
        ConfigBase(order).GetDocsMap());
    return cpo.GetMaxPriorityClass(classes) == std::nullopt;
  };

  EXPECT_TRUE(test({}, {"Business"}));

  EXPECT_TRUE(test({"Econom"}, {"Business"}));

  EXPECT_TRUE(test({"Business"}, {"Econom"}));

  EXPECT_TRUE(test({"Business", "ComfortPlus"}, {"Econom", "Vip"}));
}

TEST(ClassesPriorityOrder, GetMinOverlapping) {
  auto test = [](const ConfigBase& cfg, const std::string& min_class) {
    auto cpo = driver_scoring::configs::ClassesPriorityOrder(cfg.GetDocsMap());
    auto all_classes = MakeAllClasses();
    return cpo.GetMinPriorityClass(all_classes) == min_class;
  };

  EXPECT_TRUE(test(SingleClassConfig(), "Business"));
  EXPECT_TRUE(test(SomeClassesConfig(), "Business"));
  EXPECT_TRUE(test(AllClassesConfig(), "Business"));
}

TEST(ClassesPriorityOrder, GetMinNonOverlapping) {
  auto test = [](const std::set<std::string>& order,
                 const std::set<std::string>& classes) {
    auto cpo = driver_scoring::configs::ClassesPriorityOrder(
        ConfigBase(order).GetDocsMap());
    return cpo.GetMinPriorityClass(classes) == std::nullopt;
  };

  EXPECT_TRUE(test({}, {"Business"}));

  EXPECT_TRUE(test({"Econom"}, {"Business"}));

  EXPECT_TRUE(test({"Business"}, {"Econom"}));

  EXPECT_TRUE(test({"Business", "ComfortPlus"}, {"Econom", "Vip"}));
}
