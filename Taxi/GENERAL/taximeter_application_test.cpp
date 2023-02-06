#include "taximeter_application.hpp"

#include <gtest/gtest.h>

TEST(TaximeterApplicationVersionTest, To_From_String) {
  EXPECT_TRUE(models::TaximeterVersion{}.IsEmpty());
  EXPECT_EQ("", models::TaximeterVersion{}.ToString());

  EXPECT_EQ("8.70 (1133)", models::TaximeterVersion("8.70 (1133)").ToString());

  EXPECT_THROW(models::TaximeterVersion("8 (1133)"),
               models::TaximeterApplicationError);

  EXPECT_THROW(models::TaximeterVersion("8.1 1133"),
               models::TaximeterApplicationError);

  EXPECT_THROW(models::TaximeterVersion("8.5 (1133.1)"),
               models::TaximeterApplicationError);

  // the tests bellow is a part of old TaximeterVersion
  EXPECT_THROW(models::TaximeterVersion(""), models::TaximeterApplicationError);

  EXPECT_THROW(models::TaximeterVersion("1"),
               models::TaximeterApplicationError);

  // sdc
  EXPECT_EQ("1.2", models::TaximeterVersion("1.2").ToString(false));
  EXPECT_EQ("1.02", models::TaximeterVersion("1.2").ToString(true));
  EXPECT_EQ("9.7", models::TaximeterVersion("9.7").ToString());

  // explicit ctor
  EXPECT_EQ(models::TaximeterVersion("1.2"), models::TaximeterVersion(1, 2));
  EXPECT_EQ(models::TaximeterVersion("1.2"), models::TaximeterVersion(1, 2, 0));
  EXPECT_EQ(models::TaximeterVersion("1.02"),
            models::TaximeterVersion(1, 2, 0));
  EXPECT_EQ(models::TaximeterVersion("1.02 (0)"),
            models::TaximeterVersion(1, 2, 0));
  EXPECT_EQ(models::TaximeterVersion("1.02 (1234)"),
            models::TaximeterVersion(1, 2, 1234));
  EXPECT_EQ(models::TaximeterVersion("1.02", "1234"),
            models::TaximeterVersion(1, 2, 1234));

  // // extended version format
  EXPECT_EQ("version:0.0", models::TaximeterVersion{}.ToStringExtended());
  EXPECT_EQ("version:1.2", models::TaximeterVersion(1, 2).ToStringExtended());
  EXPECT_EQ("version:1.2",
            models::TaximeterVersion(1, 2, 0).ToStringExtended());
  EXPECT_EQ("version:1.02",
            models::TaximeterVersion(1, 2).ToStringExtended(true));
  EXPECT_EQ("version:1.2 build:1234",
            models::TaximeterVersion(1, 2, 1234).ToStringExtended());
  EXPECT_EQ("version:1.02 build:1234",
            models::TaximeterVersion(1, 2, 1234).ToStringExtended(true));
}

TEST(TaximeterApplicationTest, DefaultCtor) {
  using namespace models;
  TaximeterApp app{};
  EXPECT_EQ("", app.version.ToString());
  EXPECT_EQ(TaximeterVersionType::Default, app.version_type);
  EXPECT_EQ("yandex", app.GetBrand());
  EXPECT_EQ("", app.GetBuildType());
  EXPECT_EQ(std::nullopt, app.platform_version);
  EXPECT_FALSE(app.IsExtendedFormat());
}

TEST(TaximeterApplicationTest, BadUserAgent) {
  using namespace models;

  EXPECT_THROW(TaximeterApp::FromUserAgent("SDC Taximeter 8.65"),
               TaximeterApplicationError);
  EXPECT_THROW(TaximeterApp::FromUserAgent("taximeter-yango\t9.09 (1719)"),
               TaximeterApplicationError);
  EXPECT_THROW(TaximeterApp::FromUserAgent("Taximeter-ajaj 8.70 (1133)"),
               TaximeterApplicationError);
  EXPECT_THROW(TaximeterApp::FromUserAgent("trympyrym 8.70 (1133)"),
               TaximeterApplicationError);
  EXPECT_THROW(TaximeterApp::FromUserAgent("TaXiMeteR-x  9.09    (1719) "),
               TaximeterApplicationError);
  EXPECT_THROW(TaximeterApp::FromUserAgent("Taximeter-1234 8.70 (1133)"),
               TaximeterApplicationError);
  EXPECT_THROW(TaximeterApp::FromUserAgent("taximetre 9.09 (1719)"),
               TaximeterApplicationError);
  EXPECT_THROW(TaximeterApp::FromUserAgent("  taximeter-DEV  9.09    (1719)"),
               TaximeterApplicationError);
  EXPECT_THROW(TaximeterApp::FromUserAgent("Taximeter   8.70 (1133)"),
               TaximeterApplicationError);
  EXPECT_THROW(TaximeterApp::FromUserAgent("Taximeter- 8.70 (1133)"),
               TaximeterApplicationError);
  EXPECT_THROW(TaximeterApp::FromUserAgent("Taximeter- aaa 8.70 (1133)"),
               TaximeterApplicationError);
  EXPECT_THROW(TaximeterApp::FromUserAgent("Taximeter-aaa 8.70 1133"),
               TaximeterApplicationError);
  EXPECT_THROW(TaximeterApp::FromUserAgent("Taximeter-aaa 8.70 (1133"),
               TaximeterApplicationError);
  EXPECT_THROW(
      TaximeterApp::FromUserAgent(
          "app:pro brand:bad_brand version:10.12 build_type:bad_build_type "
          "build:23455 "
          "platform:bad_platform platform_version:15.0.1"),
      TaximeterApplicationError);
  EXPECT_THROW(
      TaximeterApp::FromUserAgent("version:10.12 build_type:x build:23455 "
                                  "platform:ios platform_version:15.0.1"),
      TaximeterApplicationError);
  EXPECT_THROW(TaximeterApp::FromUserAgent(
                   "app:pro brant:yango version:10.12 platform:ios"),
               TaximeterApplicationError);
  EXPECT_THROW(
      TaximeterApp::FromUserAgent(
          "app:taximetre version:11.12 platform:android platform_version:12.0"),
      TaximeterApplicationError);
  EXPECT_THROW(TaximeterApp::FromUserAgent(
                   "app:taximetrer version:11.12 platform:ondroid "
                   "platform_version:12.0"),
               TaximeterApplicationError);
  EXPECT_THROW(
      TaximeterApp::FromUserAgent(
          "app:pro brand:yandex version:10.12 platform_version:15.0.1"),
      TaximeterApplicationError);

  EXPECT_THROW(
      TaximeterApp::FromUserAgent(
          "app:pro version:10.12 platform:ios platform_version:15.0.1"),
      TaximeterApplicationError);
}

TEST(TaximeterApplicationTestType, ComparisonUnequal) {
  for (const auto& item : std::vector<std::pair<std::string, std::string>>{
           {"8.64", "8.65 (123)"},
           {"8.65", "8.65 (123)"},
           {"8.65", "8.66"},
           {"8.65 (8765)", "8.66"},
           {"8.65 (1234)", "8.65 (1235)"},
       }) {
    models::TaximeterVersion first{item.first};
    models::TaximeterVersion second{item.second};

    EXPECT_TRUE(first < second);
    EXPECT_TRUE(second > first);

    EXPECT_FALSE(first >= second);
    EXPECT_FALSE(second <= first);

    EXPECT_FALSE(first == second);
    EXPECT_FALSE(second == first);

    EXPECT_TRUE(first != second);
    EXPECT_TRUE(second != first);
  }
}

TEST(TaximeterApplicationTestType, ComparisonEqual) {
  for (const auto& item : std::vector<std::pair<std::string, std::string>>{
           {"8.65", "8.65"},
           {"9.1", "9.01"},
           {"9.0 (123)", "9.00 (123)"},
       }) {
    models::TaximeterVersion first{item.first};
    models::TaximeterVersion second{item.second};

    EXPECT_TRUE(first == second);
    EXPECT_TRUE(second == first);

    EXPECT_TRUE(first <= second);
    EXPECT_TRUE(second <= first);

    EXPECT_TRUE(first >= second);
    EXPECT_TRUE(second >= first);

    EXPECT_FALSE(first < second);
    EXPECT_FALSE(second < first);

    EXPECT_FALSE(first > second);
    EXPECT_FALSE(second > first);

    EXPECT_FALSE(first != second);
    EXPECT_FALSE(second != first);
  }
}

// Parametrized test to check how each TaximeterApp component
// is parsed from old User-Agent
// 1. User-Agent,
// 2. Expect Version
// 3. Expect Version Type,
// 4. Expect Platform,
// 5. Expect Brand,
// 6. Expect Build Type
// 7. Expect exp3 app
TEST(TaximeterApplicationTestType, ParseFromOldUserAgent) {
  using namespace models;
  using Type = TaximeterVersionType;
  using Platform = TaximeterPlatform;

  using TestCase = std::tuple<std::string, std::string, Type, Platform,
                              std::string, std::string, std::string>;

  const TestCase kTestCases[] = {
      {"Taximeter 8.65 (123)", "8.65 (123)", Type::Production,
       Platform::kAndroid, "yandex", "", "taximeter"},
      {"tAxImEtEr 1.74 (123) ios", "1.74 (123)", Type::Production,
       Platform::kIos, "yandex", "", "taximeter-ios"},
      {"Taximeter-beta 8.65 (1234)", "8.65 (1234)", Type::Beta,
       Platform::kAndroid, "yandex", "beta", "taximeter"},
      {"Taximeter-X 8.65 (1234)", "8.65 (1234)", Type::Experimental,
       Platform::kAndroid, "yandex", "x", "taximeter"},
      {"Taximeter-SDC 8.65 (1234)", "8.65 (1234)", Type::Sdc,
       Platform::kAndroid, "yandex", "sdc", "taximeter"},
      {"TaXiMeTer-DeV 8.02 (1234)", "8.02 (1234)", Type::Developer,
       Platform::kAndroid, "yandex", "dev", "taximeter"},
      {"taximeter-yango 9.10 (1234)", "9.10 (1234)", Type::Yango,
       Platform::kAndroid, "yango", "", "taximeter"},
      {"Taximeter-Uber 99.01 (12345)", "99.01 (12345)", Type::Uber,
       Platform::kAndroid, "uber", "", "uberdriver"},
      {"Taximeter-Yango 1.74 (123) ios", "1.74 (123)", Type::Yango,
       Platform::kIos, "yango", "", "taximeter-ios"},
      {"Taximeter-AZ 1.74 (123) ios", "1.74 (123)", Type::Azerbaijan,
       Platform::kIos, "az", "", "taximeter-ios"},
      {"Taximeter-Vezet 1.74 (123)", "1.74 (123)", Type::Vezet,
       Platform::kAndroid, "vezet", "", "taximeter"},
      {"Taximeter-Embedded 1.74 (123)", "1.74 (123)", Type::Embedded,
       Platform::kAndroid, "yandex", "", "taximeter"},
      {"Taximeter-Rida 1.74 (123)", "1.74 (123)", Type::Rida,
       Platform::kAndroid, "rida", "", "taximeter"},
      {"Taximeter-Turla 1.74 (123)", "1.74 (123)", Type::Turla,
       Platform::kAndroid, "turla", "", "taximeter"},
  };

  for (const auto& testCase : kTestCases) {
    const auto [user_agent, version, version_type, platform, brand, build_type,
                exp3_app] = testCase;
    const auto app = TaximeterApp::FromUserAgent(user_agent);
    EXPECT_EQ(version, app.version.ToString(true));
    EXPECT_EQ(version_type, app.version_type);
    EXPECT_EQ(platform, app.platform);
    EXPECT_EQ(brand, app.GetBrand());
    EXPECT_EQ(build_type, app.GetBuildType());
    EXPECT_EQ(std::nullopt, app.platform_version);
    EXPECT_FALSE(app.IsExtendedFormat());
    EXPECT_EQ(exp3_app, app.GetExp3Application());
  }
}

// Parametrized test to check how TaximeterApp can be constructed
// (old way via version_type)
// Test case params:
// 1. VersionType
// 2. App Version
// 3. App Platform
// 4. Expect Serialized TaximeterApp (string)
// 5. Expect Brand
// 6. Expect Build Type
// 7. Expect exp3 application
TEST(TaximeterApplicationTestType, ConstructAppOldWay) {
  using namespace models;
  using Type = TaximeterVersionType;
  using Platform = TaximeterPlatform;

  using TestCase = std::tuple<Type, std::string, Platform, std::string,
                              std::string, std::string, std::string>;

  const TestCase kTestCases[] = {
      {TaximeterVersionType::Production, "1.2", TaximeterPlatform::kAndroid,
       "Taximeter 1.2", "yandex", "", "taximeter"},
      {TaximeterVersionType::Production, "1.2", TaximeterPlatform::kIos,
       "Taximeter 1.2 ios", "yandex", "", "taximeter-ios"},
      {TaximeterVersionType::Beta, "1.2", TaximeterPlatform::kAndroid,
       "Taximeter-beta 1.2", "yandex", "beta", "taximeter"},
      {TaximeterVersionType::Experimental, "1.2", TaximeterPlatform::kAndroid,
       "Taximeter-x 1.2", "yandex", "x", "taximeter"},
      {TaximeterVersionType::Developer, "1.2", TaximeterPlatform::kAndroid,
       "Taximeter-dev 1.2", "yandex", "dev", "taximeter"},
      {TaximeterVersionType::Sdc, "1.2", TaximeterPlatform::kAndroid,
       "Taximeter-sdc 1.2", "yandex", "sdc", "taximeter"},
      {TaximeterVersionType::Sdc, "1.2", TaximeterPlatform::kIos,
       "Taximeter-sdc 1.2 ios", "yandex", "sdc", "taximeter-ios"},
      {TaximeterVersionType::Yango, "1.2 (666)", TaximeterPlatform::kAndroid,
       "Taximeter-yango 1.2 (666)", "yango", "", "taximeter"},
      {TaximeterVersionType::Yango, "1.2 (666)", TaximeterPlatform::kIos,
       "Taximeter-yango 1.2 (666) ios", "yango", "", "taximeter-ios"},
      {TaximeterVersionType::Uber, "1.2 (666)", TaximeterPlatform::kAndroid,
       "Taximeter-uber 1.2 (666)", "uber", "", "uberdriver"},
      {TaximeterVersionType::Vezet, "1.2 (666)", TaximeterPlatform::kAndroid,
       "Taximeter-vezet 1.2 (666)", "vezet", "", "taximeter"},
      {TaximeterVersionType::Azerbaijan, "1.2 (666)",
       TaximeterPlatform::kAndroid, "Taximeter-az 1.2 (666)", "az", "",
       "taximeter"},
      {TaximeterVersionType::Embedded, "1.2 (666)", TaximeterPlatform::kAndroid,
       "Taximeter-embedded 1.2 (666)", "yandex", "", "taximeter"},
      {TaximeterVersionType::Rida, "1.2 (666)", TaximeterPlatform::kAndroid,
       "Taximeter-rida 1.2 (666)", "rida", "", "taximeter"},
      {TaximeterVersionType::Turla, "1.2 (666)", TaximeterPlatform::kAndroid,
       "Taximeter-turla 1.2 (666)", "turla", "", "taximeter"},
  };

  for (const auto& testCase : kTestCases) {
    const auto [version_type, app_version, platform, serialized_app, brand,
                build_type, exp3_app] = testCase;
    const TaximeterApp app{version_type, app_version, platform};
    EXPECT_EQ(serialized_app, app.ToString());
    EXPECT_EQ(version_type, app.version_type);
    EXPECT_EQ(platform, app.platform);
    EXPECT_EQ(models::TaximeterVersion{app_version}, app.version);
    EXPECT_EQ(brand, app.GetBrand());
    EXPECT_EQ(build_type, app.GetBuildType());
    EXPECT_EQ(std::nullopt, app.platform_version);
    EXPECT_EQ(exp3_app, app.GetExp3Application());
    EXPECT_FALSE(app.IsExtendedFormat());
  }
}

// Parametrized test to check how TaximeterApp can be
// serialized after being parsed from UA
// (both new and old way)
// Test case params:
// 1. User-Agent
// 2. Serialized app
TEST(TaximeterApplicationExtendedTest, SerializeApp) {
  using namespace models;

  using TestCase = std::tuple<std::string, std::string>;
  const TestCase kTestCases[] = {
      {"TAXIMETER 8.65 (123)", "Taximeter 8.65 (123)"},
      {"taximeter-BETA 8.1", "Taximeter-beta 8.01"},
      {"Taximeter-Dev 8.1 (0) ios", "Taximeter-dev 8.01 ios"},
      {"Taximeter-X 8.1", "Taximeter-x 8.01"},
      {"Taximeter-TURLA 8.1 ios", "Taximeter-turla 8.01 ios"},
      {"platform_version:12.0 platform:android version:11.12 brand:yandex "
       "app:pro",
       "app:pro brand:yandex version:11.12 platform:android "
       "platform_version:12.0.0"},
      {"app:pro build_type:dev version:11.1 build:1234 platform_version:12 "
       "platform:android brand:rida",
       "app:pro brand:rida version:11.01 build:1234 platform:android "
       "platform_version:12.0.0 build_type:dev"}};

  for (const auto& testCase : kTestCases) {
    const auto [user_agent, serialized_app] = testCase;

    const auto app = TaximeterApp::FromUserAgent(user_agent);
    EXPECT_EQ(serialized_app, app.ToString(true));
  }
}

// Parametrized test to check how each TaximeterApp component
// is parsed from extended User-Agent
// 1. User-Agent (extended),
// 2. Expect Version
// 3. Expect Version Type,
// 4. Expect Platform,
// 5. Expect Brand,
// 6. Expect Build Type
// 7. Expect Platform Version
// 8. Expect exp3 app
TEST(TaximeterApplicationTestType, ParseFromExtendedUA) {
  using namespace models;
  using Type = TaximeterVersionType;
  using Platform = TaximeterPlatform;

  using TestCase =
      std::tuple<std::string, std::string, Type, Platform, std::string,
                 std::string, std::string, std::string>;

  const TestCase kTestCases[] = {
      {"app:pro brand:yandex version:11.12 platform:android "
       "platform_version:12.0",
       "11.12", Type::Production, Platform::kAndroid, "yandex", "", "12.0.0",
       "taximeter"},
      {"app:pro brand:yandex version:10.12 build_type:x build:23455 "
       "platform:ios "
       "platform_version:15.0.1",
       "10.12 (23455)", Type::Experimental, Platform::kIos, "yandex", "x",
       "15.0.1", "taximeter-ios"},
      {"app:pro brand:yandex version:10.12 platform_version:12.03.4 "
       "build_type:beta "
       "platform:ios",
       "10.12", Type::Beta, Platform::kIos, "yandex", "beta", "12.3.4",
       "taximeter-ios"},
      {"app:pro brand:yandex version:11.12 build_type:dev platform:android "
       "platform_version:12.0",
       "11.12", Type::Developer, Platform::kAndroid, "yandex", "dev", "12.0.0",
       "taximeter"},
      {"app:pro brand:az version:11.12 build_type:x "
       "platform:android platform_version:12",
       "11.12", Type::Azerbaijan, Platform::kAndroid, "az", "x", "12.0.0",
       "taximeter"},
      {"app:pro brand:vezet version:11.12 "
       "platform:ios platform_version:12.0",
       "11.12", Type::Vezet, Platform::kIos, "vezet", "", "12.0.0",
       "taximeter-ios"},
      {"app:pro brand:uber version:11.12 build_type:beta "
       "platform:android platform_version:12.0",
       "11.12", Type::Uber, Platform::kAndroid, "uber", "beta", "12.0.0",
       "uberdriver"},
      {"app:pro brand:yango version:10.12 build_type:sdc build:23455 "
       "platform:ios platform_version:15.0.1",
       "10.12 (23455)", Type::Yango, Platform::kIos, "yango", "sdc", "15.0.1",
       "taximeter-ios"},
      {"app:pro brand:rida version:10.12 build_type:x build:23455 "
       "platform:ios platform_version:15.0.1",
       "10.12 (23455)", Type::Rida, Platform::kIos, "rida", "x", "15.0.1",
       "taximeter-ios"},
      {"app:pro brand:turla version:10.12 build_type:dev build:23455 "
       "platform:ios platform_version:15.0.1",
       "10.12 (23455)", Type::Turla, Platform::kIos, "turla", "dev", "15.0.1",
       "taximeter-ios"},
  };

  for (const auto& testCase : kTestCases) {
    const auto [user_agent, version, version_type, platform, brand, build_type,
                platform_version, exp3_app] = testCase;
    const auto app = TaximeterApp::FromUserAgent(user_agent);
    EXPECT_EQ(version, app.version.ToString(true));
    EXPECT_EQ(version_type, app.version_type);
    EXPECT_EQ(platform, app.platform);
    EXPECT_EQ(brand, app.GetBrand());
    EXPECT_EQ(build_type, app.GetBuildType());
    EXPECT_TRUE(app.platform_version);
    EXPECT_EQ(platform_version, app.platform_version->ToString());
    EXPECT_TRUE(app.IsExtendedFormat());
    EXPECT_EQ(exp3_app, app.GetExp3Application());
  }
}

// Parametrized test to check how TaximeterApp can be
// parsed from DAP headers
// (both new and old way)
// Test case params:
// 1. version
// 2. platform_str
// 3. version_type_str
// 4. brand_str
// 5. build_type_str
// 6. platform_version_str
// 7. expect extended format
// 8. expect platform
// 9. expect version_type
// 10. expect brand
// 11. expect build_type
TEST(TaximeterApplicationExtendedTest, FromTaximeterAppVars) {
  using namespace models;

  using TestCase =
      std::tuple<std::string, std::string, std::string, std::string,
                 std::string, std::string, bool, std::string, std::string,
                 std::string, std::string>;
  const TestCase kTestCases[] = {
      {"9.63", "android", "", "", "", "", false, "android", "", "yandex", ""},
      {"9.63", "", "", "", "", "", false, "android", "", "yandex", ""},
      {"9.63", "", "uber", "", "", "", false, "android", "uber", "uber", ""},
      {"9.63", "ios", "beta", "", "", "", false, "ios", "beta", "yandex",
       "beta"},
      {"9.63", "ios", "yango", "", "", "", false, "ios", "yango", "yango", ""},
      {"9.63", "android", "embedded", "", "", "", false, "android", "embedded",
       "yandex", ""},
      // parsing from version_type (not from brand and build_type),
      // because platform_version is empty
      {"9.63", "", "yango", "ignore_brand", "ignore_build", "", false,
       "android", "yango", "yango", ""},
      {"9.63", "", "", "yandex", "x", "15.0.1", true, "android", "x", "yandex",
       "x"},
      {"9.63", "", "", "uber", "", "15.0.1", true, "android", "uber", "uber",
       ""},
      {"9.63", "", "", "az", "beta", "15.0.1", true, "android", "az", "az",
       "beta"},
      {"9.63 (1234)", "", "", "az", "x", "15.0.1", true, "android", "az", "az",
       "x"},
      {"9.63 (1234)", "", "ignore_version_type", "az", "x", "15.0.1", true,
       "android", "az", "az", "x"},
      {"9.63", "", "", "rida", "x", "15.0.1", true, "android", "rida", "rida",
       "x"},
      {"9.63", "", "", "turla", "x", "15.0.1", true, "android", "turla",
       "turla", "x"},
  };

  for (const auto& testCase : kTestCases) {
    const auto [version_str, platform_str, version_type_str, brand_str,
                build_type_str, platform_version_str, expect_extended,
                expect_platform, expect_version_type, expect_brand,
                expect_build_type] = testCase;

    const auto app = TaximeterApp::FromTaximeterAppVars(
        version_str, platform_str, version_type_str, brand_str, build_type_str,
        platform_version_str);
    EXPECT_EQ(expect_extended, app.IsExtendedFormat());
    EXPECT_EQ(expect_platform, app.GetPlatform());
    EXPECT_EQ(expect_version_type, app.GetType());
    EXPECT_EQ(expect_brand, app.GetBrand());
    EXPECT_EQ(expect_build_type, app.GetBuildType());
  }

  EXPECT_THROW(TaximeterApp::FromTaximeterAppVars(
                   "9.63 (1234)", "unkown_platform", "", "bad_brand",
                   "bad_build_type", "15.0.1"),
               TaximeterApplicationError);
}
