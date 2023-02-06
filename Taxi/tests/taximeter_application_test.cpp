#include <gtest/gtest.h>

#include <optional>
#include <ua_parser/taximeter_application.hpp>

TEST(TaximeterApplicationVersionTest, To_From_String) {
  using namespace ua_parser;

  EXPECT_EQ("8.70 (1133)", TaximeterVersion("8.70 (1133)").ToString());

  EXPECT_THROW(TaximeterVersion("8 (1133)"), TaximeterApplicationError);

  EXPECT_THROW(TaximeterVersion("8.1 1133"), TaximeterApplicationError);

  EXPECT_THROW(TaximeterVersion("8.5 (1133.1)"), TaximeterApplicationError);

  // the tests bellow is a part of old TaximeterVersion
  EXPECT_THROW(TaximeterVersion(""), TaximeterApplicationError);

  EXPECT_THROW(TaximeterVersion("1"), TaximeterApplicationError);

  // sdc
  EXPECT_EQ("1.2", TaximeterVersion("1.2").ToString(false));
  EXPECT_EQ("1.02", TaximeterVersion("1.2").ToString(true));
  EXPECT_EQ("9.7", TaximeterVersion("9.7").ToString());

  // explicit ctor
  EXPECT_EQ(TaximeterVersion("1.2"), TaximeterVersion(1, 2));
  EXPECT_EQ(TaximeterVersion("1.2"), TaximeterVersion(1, 2, 0));
  EXPECT_EQ(TaximeterVersion("1.02"), TaximeterVersion(1, 2, 0));
  EXPECT_EQ(TaximeterVersion("1.02 (0)"), TaximeterVersion(1, 2, 0));
  EXPECT_EQ(TaximeterVersion("1.02 (1234)"), TaximeterVersion(1, 2, 1234));

  // // extended version format
  EXPECT_EQ("version:1.2", TaximeterVersion(1, 2).ToStringExtended());
  EXPECT_EQ("version:1.2", TaximeterVersion(1, 2, 0).ToStringExtended());
  EXPECT_EQ("version:1.02", TaximeterVersion(1, 2).ToStringExtended(true));
  EXPECT_EQ("version:1.2 build:1234",
            TaximeterVersion(1, 2, 1234).ToStringExtended());
  EXPECT_EQ("version:1.02 build:1234",
            TaximeterVersion(1, 2, 1234).ToStringExtended(true));
}

TEST(TaximeterApplicationTest, DefaultCtor) {
  using namespace ua_parser;
  TaximeterApp app;
  EXPECT_EQ("0.0", app.version.ToString());
  EXPECT_EQ(TaximeterVersionType::Default, app.version_type);
  EXPECT_EQ("yandex", app.GetBrand());
  EXPECT_EQ("", app.GetBuildType());
  EXPECT_EQ(std::nullopt, app.platform_version);
  EXPECT_FALSE(app.IsExtendedFormat());
}

TEST(TaximeterApplicationTest, FromUserAgent) {
  using namespace ua_parser;

  TaximeterApp app;
  app = TaximeterApp::FromUserAgent("Taximeter 8.70 (1133)");
  EXPECT_EQ(static_cast<std::size_t>(8), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(70), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(1133), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Production, app.version_type);
  EXPECT_EQ("yandex", app.GetBrand());
  EXPECT_EQ("", app.GetBuildType());
  EXPECT_EQ(std::nullopt, app.platform_version);
  EXPECT_FALSE(app.IsExtendedFormat());
  EXPECT_FALSE(app.IsUberdriver());
  EXPECT_FALSE(app.IsVezet());

  app = TaximeterApp::FromUserAgent("Taximeter-AZ 8.67 (1111)");
  EXPECT_EQ(static_cast<std::size_t>(8), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(67), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(1111), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Azerbaijan, app.version_type);
  EXPECT_EQ("az", app.GetBrand());
  EXPECT_EQ("", app.GetBuildType());
  EXPECT_EQ(std::nullopt, app.platform_version);
  EXPECT_FALSE(app.IsExtendedFormat());

  app = TaximeterApp::FromUserAgent("Taximeter-Beta 8.71 (1192)");
  EXPECT_EQ(static_cast<std::size_t>(8), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(71), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(1192), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Beta, app.version_type);
  EXPECT_EQ("yandex", app.GetBrand());
  EXPECT_EQ("beta", app.GetBuildType());
  EXPECT_EQ(std::nullopt, app.platform_version);
  EXPECT_FALSE(app.IsExtendedFormat());

  app = TaximeterApp::FromUserAgent("Taximeter-X 8.72 (1198)");
  EXPECT_EQ(static_cast<std::size_t>(8), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(72), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(1198), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Experimental, app.version_type);
  EXPECT_EQ("yandex", app.GetBrand());
  EXPECT_EQ("x", app.GetBuildType());
  EXPECT_EQ(std::nullopt, app.platform_version);
  EXPECT_FALSE(app.IsExtendedFormat());

  app = TaximeterApp::FromUserAgent("Taximeter-Sdc 8.65 (123)");
  EXPECT_EQ(static_cast<std::size_t>(8), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(65), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(123), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Sdc, app.version_type);
  EXPECT_EQ("yandex", app.GetBrand());
  EXPECT_EQ("sdc", app.GetBuildType());
  EXPECT_EQ(std::nullopt, app.platform_version);
  EXPECT_FALSE(app.IsExtendedFormat());

  app = TaximeterApp::FromUserAgent("Taximeter-Dev 8.65 (123)");
  EXPECT_EQ(static_cast<std::size_t>(8), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(65), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(123), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Developer, app.version_type);
  EXPECT_EQ("yandex", app.GetBrand());
  EXPECT_EQ("dev", app.GetBuildType());
  EXPECT_EQ(std::nullopt, app.platform_version);
  EXPECT_FALSE(app.IsExtendedFormat());

  app = TaximeterApp::FromUserAgent("Taximeter-Embedded 8.65 (123)");
  EXPECT_EQ(static_cast<std::size_t>(8), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(65), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(123), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Embedded, app.version_type);
  EXPECT_EQ("yandex", app.GetBrand());
  EXPECT_EQ("", app.GetBuildType());
  EXPECT_EQ(std::nullopt, app.platform_version);
  EXPECT_FALSE(app.IsExtendedFormat());

  app = TaximeterApp::FromUserAgent("Taximeter-uber 9.05 (1234)");
  EXPECT_EQ(static_cast<std::size_t>(9), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(5), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(1234), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Uber, app.version_type);
  EXPECT_EQ("uber", app.GetBrand());
  EXPECT_EQ("", app.GetBuildType());
  EXPECT_EQ(std::nullopt, app.platform_version);
  EXPECT_FALSE(app.IsExtendedFormat());
  EXPECT_TRUE(app.IsUberdriver());
  EXPECT_FALSE(app.IsVezet());

  app = TaximeterApp::FromUserAgent("taximeter-yango 9.10 (1234)");
  EXPECT_EQ(static_cast<std::size_t>(9), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(10), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(1234), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Yango, app.version_type);
  EXPECT_EQ("yango", app.GetBrand());
  EXPECT_EQ("", app.GetBuildType());
  EXPECT_EQ(std::nullopt, app.platform_version);
  EXPECT_FALSE(app.IsExtendedFormat());

  app = TaximeterApp::FromUserAgent("taximeter-vezet 9.10 (1234)");
  EXPECT_EQ(static_cast<std::size_t>(9), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(10), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(1234), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Vezet, app.version_type);
  EXPECT_EQ("vezet", app.GetBrand());
  EXPECT_EQ("", app.GetBuildType());
  EXPECT_EQ(std::nullopt, app.platform_version);
  EXPECT_FALSE(app.IsExtendedFormat());
  EXPECT_FALSE(app.IsUberdriver());
  EXPECT_TRUE(app.IsVezet());

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
  EXPECT_THROW(TaximeterApp::FromUserAgent("  taximeter-DEV  9.09    (1719) "),
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
}

// Parametrized test to check how each TaximeterApp component
// is parsed from old User-Agent
// 1. User-Agent,
// 2. Expect Version Type,
// 4. Expect Platform,
// 5. Expect Brand,
// 6. Expect Build Type
// 7. Expect exp3 app
TEST(TaximeterApplicationTestType, ParseFromOldUserAgent) {
  using namespace ua_parser;
  using Type = TaximeterVersionType;
  using Platform = TaximeterPlatform;

  using TestCase = std::tuple<std::string, Type, Platform, std::string,
                              std::string, std::string>;

  const TestCase kTestCases[] = {
      {"Taximeter 8.65 (123)", Type::Production, Platform::kAndroid, "yandex",
       "", "taximeter"},
      {"Taximeter 1.74 (123) ios", Type::Production, Platform::kIos, "yandex",
       "", "taximeter-ios"},
      {"Taximeter-beta 8.65 (1234)", Type::Beta, Platform::kAndroid, "yandex",
       "beta", "taximeter"},
      {"Taximeter-X 8.65 (1234)", Type::Experimental, Platform::kAndroid,
       "yandex", "x", "taximeter"},
      {"Taximeter-SDC 8.65 (1234)", Type::Sdc, Platform::kAndroid, "yandex",
       "sdc", "taximeter"},
      {"TaXiMeTer-DeV 8.02 (1234)", Type::Developer, Platform::kAndroid,
       "yandex", "dev", "taximeter"},
      {"taximeter-yango 9.10 (1234)", Type::Yango, Platform::kAndroid, "yango",
       "", "taximeter"},
      {"Taximeter-Uber 99.01 (12345)", Type::Uber, Platform::kAndroid, "uber",
       "", "uberdriver"},
      {"Taximeter-Yango 1.74 (123) ios", Type::Yango, Platform::kIos, "yango",
       "", "taximeter-ios"},
      {"Taximeter-AZ 1.74 (123) ios", Type::Azerbaijan, Platform::kIos, "az",
       "", "taximeter-ios"},
      {"Taximeter-Vezet 1.74 (123)", Type::Vezet, Platform::kAndroid, "vezet",
       "", "taximeter"},
      {"Taximeter-Embedded 1.74 (123)", Type::Embedded, Platform::kAndroid,
       "yandex", "", "taximeter"},
      {"Taximeter-Rida 1.74 (123)", Type::Rida, Platform::kAndroid, "rida", "",
       "taximeter"},
      {"Taximeter-Turla 1.74 (123)", Type::Turla, Platform::kAndroid, "turla",
       "", "taximeter"},
  };

  for (const auto& testCase : kTestCases) {
    const auto [user_agent, version_type, platform, brand, build_type,
                exp3_app] = testCase;
    const auto app = TaximeterApp::FromUserAgent(user_agent);
    EXPECT_EQ(version_type, app.version_type);
    EXPECT_EQ(platform, app.platform);
    EXPECT_EQ(brand, app.GetBrand());
    EXPECT_EQ(build_type, app.GetBuildType());
    EXPECT_EQ(std::nullopt, app.platform_version);
    EXPECT_FALSE(app.IsExtendedFormat());
    EXPECT_EQ(exp3_app, app.GetExp3Application());
  }
}

// Parametrized test to check how TaximeterApp is serialized to string,
// after parsing from old User-Agent.
// Test case params:
// 1. User-Agent
// 2. Expect Serialized App
// 3. Expect Version Type
// 4. Expect Brand
// 5. Expect Platform
// 6. Expect Build Type
// 7. Expect exp3 application
TEST(TaximeterApplicationTestType, ParseFromOldAndSerialize) {
  using namespace ua_parser;
  using TestCase =
      std::tuple<std::string, std::string, std::string, std::string,
                 std::string, std::string, std::string>;

  const TestCase kTestCases[] = {
      {"Taximeter 8.65 (123)", "Taximeter 8.65 (123)", "", "yandex", "android",
       "", "taximeter"},
      {"Taximeter 8.65", "Taximeter 8.65", "", "yandex", "android", "",
       "taximeter"},
      {"Taximeter 8.65 (123) ios", "Taximeter 8.65 (123) ios", "", "yandex",
       "ios", "", "taximeter-ios"},
      {"Taximeter 8.65 ios", "Taximeter 8.65 ios", "", "yandex", "ios", "",
       "taximeter-ios"},
      {"TaXiMeTer-Beta 8.02 (1234)", "Taximeter-beta 8.2 (1234)", "beta",
       "yandex", "android", "beta", "taximeter"},
      {"TaXiMeTer-Beta 8.02 (1234) ios", "Taximeter-beta 8.2 (1234) ios",
       "beta", "yandex", "ios", "beta", "taximeter-ios"},
      {"TaXiMeTer-DeV 8.02 (1234)", "Taximeter-dev 8.2 (1234)", "dev", "yandex",
       "android", "dev", "taximeter"},
      {"TaXiMeTer-SDC 8.02 (1234)", "Taximeter-sdc 8.2 (1234)", "sdc", "yandex",
       "android", "sdc", "taximeter"},
      {"TaXiMeTer-X 8.02 (1234)", "Taximeter-x 8.2 (1234)", "x", "yandex",
       "android", "x", "taximeter"},
      {"taximeter-Yango 9.10 (1234)", "Taximeter-yango 9.10 (1234)", "yango",
       "yango", "android", "", "taximeter"},
      {"taximeter-Yango 9.10 (1234) ios", "Taximeter-yango 9.10 (1234) ios",
       "yango", "yango", "ios", "", "taximeter-ios"},
      {"Taximeter 99.01 (12345)", "Taximeter 99.1 (12345)", "", "yandex",
       "android", "", "taximeter"},
      {"Taximeter-Vezet 99.02 (12345)", "Taximeter-vezet 99.2 (12345)", "vezet",
       "vezet", "android", "", "taximeter"},
      {"Taximeter-Uber 99.03 (12345)", "Taximeter-uber 99.3 (12345)", "uber",
       "uber", "android", "", "uberdriver"},
      {"Taximeter-AZ 99.03 (12345)", "Taximeter-az 99.3 (12345)", "az", "az",
       "android", "", "taximeter"},
      {"Taximeter-Embedded 99.03 (12345)", "Taximeter-embedded 99.3 (12345)",
       "embedded", "yandex", "android", "", "taximeter"},
  };

  for (const auto& testCase : kTestCases) {
    const auto [user_agent, serialized_app, version_type, brand, platform,
                build_type, exp3_app] = testCase;
    const auto app = TaximeterApp::FromUserAgent(user_agent);
    EXPECT_EQ(serialized_app, app.ToString());
    EXPECT_EQ(version_type, app.GetType());
    EXPECT_EQ(brand, app.GetBrand());
    EXPECT_EQ(platform, app.GetPlatform());
    EXPECT_EQ(build_type, app.GetBuildType());
    EXPECT_EQ(std::nullopt, app.platform_version);
    EXPECT_EQ(exp3_app, app.GetExp3Application());
    EXPECT_FALSE(app.IsExtendedFormat());
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
  using namespace ua_parser;
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
    EXPECT_EQ(TaximeterVersion{app_version}, app.version);
    EXPECT_EQ(brand, app.GetBrand());
    EXPECT_EQ(build_type, app.GetBuildType());
    EXPECT_EQ(std::nullopt, app.platform_version);
    EXPECT_EQ(exp3_app, app.GetExp3Application());
    EXPECT_FALSE(app.IsExtendedFormat());
  }
}

TEST(TaximeterApplicationTestType, ComparisonUnequal) {
  using namespace ua_parser;
  for (const auto& item : std::vector<std::pair<std::string, std::string>>{
           {"8.64", "8.65 (123)"},
           {"8.65", "8.65 (123)"},
           {"8.65", "8.66"},
           {"8.65 (8765)", "8.66"},
           {"8.65 (1234)", "8.65 (1235)"},
       }) {
    TaximeterVersion first{item.first};
    TaximeterVersion second{item.second};

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
  using namespace ua_parser;
  for (const auto& item : std::vector<std::pair<std::string, std::string>>{
           {"8.65", "8.65"},
           {"9.1", "9.01"},
           {"9.0 (123)", "9.00 (123)"},
       }) {
    TaximeterVersion first{item.first};
    TaximeterVersion second{item.second};

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

TEST(ProTempHeaderWorkaroundTest, FromUserAgent) {
  using namespace ua_parser;

  TaximeterApp app;
  app = TaximeterApp::FromUserAgent("Taximeter-Embedded 91.70 (1133)");
  EXPECT_EQ(static_cast<std::size_t>(91), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(70), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(1133), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Embedded, app.version_type);
  EXPECT_EQ("yandex", app.GetBrand());
  EXPECT_TRUE(app.IsMagistrali());
  EXPECT_FALSE(app.IsExtendedFormat());

  app = TaximeterApp::FromUserAgent("Taximeter-Embedded 90.70 (1133)");
  EXPECT_EQ(static_cast<std::size_t>(90), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(70), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(1133), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Embedded, app.version_type);
  EXPECT_EQ("yandex", app.GetBrand());
  EXPECT_TRUE(app.IsUslugi());
  EXPECT_FALSE(app.IsExtendedFormat());
}

TEST(TaximeterApplicationExtendedTest, FromUserAgent) {
  using namespace ua_parser;

  TaximeterApp app;
  app = TaximeterApp::FromUserAgent(
      "app:pro brand:yandex version:11.12 platform:android "
      "platform_version:12.0");
  EXPECT_EQ(static_cast<std::size_t>(11), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(12), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(0), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Production, app.version_type);
  EXPECT_EQ(TaximeterPlatform::kAndroid, app.platform);
  EXPECT_EQ("yandex", app.GetBrand());
  EXPECT_EQ("", app.GetBuildType());
  EXPECT_EQ(PlatformVersion(12, 0, 0), *app.platform_version);
  EXPECT_TRUE(app.IsExtendedFormat());
  EXPECT_FALSE(app.IsUberdriver());
  EXPECT_FALSE(app.IsVezet());

  app = TaximeterApp::FromUserAgent(
      "app:pro brand:yandex version:10.12 build_type:x build:23455 "
      "platform:ios "
      "platform_version:15.0.1");
  EXPECT_EQ(static_cast<std::size_t>(10), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(12), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(23455), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Experimental, app.version_type);
  EXPECT_EQ(TaximeterPlatform::kIos, app.platform);
  EXPECT_EQ("yandex", app.GetBrand());
  EXPECT_EQ("x", app.GetBuildType());
  EXPECT_EQ(PlatformVersion(15, 0, 1), *app.platform_version);
  EXPECT_TRUE(app.IsExtendedFormat());

  app = TaximeterApp::FromUserAgent(
      "app:pro brand:yandex version:10.12 platform_version:12.03.4 "
      "build_type:beta "
      "platform:ios");
  EXPECT_EQ(static_cast<std::size_t>(10), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(12), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(0), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Beta, app.version_type);
  EXPECT_EQ(TaximeterPlatform::kIos, app.platform);
  EXPECT_EQ("yandex", app.GetBrand());
  EXPECT_EQ("beta", app.GetBuildType());
  EXPECT_EQ(PlatformVersion(12, 3, 4), app.platform_version);
  EXPECT_TRUE(app.IsExtendedFormat());

  app = TaximeterApp::FromUserAgent(
      "app:pro brand:yandex version:11.12 build_type:dev platform:android "
      "platform_version:12.0");
  EXPECT_EQ(static_cast<std::size_t>(11), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(12), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(0), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Developer, app.version_type);
  EXPECT_EQ(TaximeterPlatform::kAndroid, app.platform);
  EXPECT_EQ("yandex", app.GetBrand());
  EXPECT_EQ("dev", app.GetBuildType());
  EXPECT_EQ(PlatformVersion(12, 0, 0), *app.platform_version);
  EXPECT_TRUE(app.IsExtendedFormat());

  app = TaximeterApp::FromUserAgent(
      "app:pro brand:az version:11.12 build_type:x "
      "platform:android platform_version:12");
  EXPECT_EQ(static_cast<std::size_t>(11), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(12), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(0), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Azerbaijan, app.version_type);
  EXPECT_EQ(TaximeterPlatform::kAndroid, app.platform);
  EXPECT_EQ("az", app.GetBrand());
  EXPECT_EQ("x", app.GetBuildType());
  EXPECT_EQ(PlatformVersion(12, 0, 0), *app.platform_version);
  EXPECT_TRUE(app.IsExtendedFormat());

  app = TaximeterApp::FromUserAgent(
      "app:pro brand:vezet version:11.12 "
      "platform:ios platform_version:12.0");
  EXPECT_EQ(static_cast<std::size_t>(11), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(12), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(0), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Vezet, app.version_type);
  EXPECT_EQ(TaximeterPlatform::kIos, app.platform);
  EXPECT_EQ("vezet", app.GetBrand());
  EXPECT_EQ("", app.GetBuildType());
  EXPECT_EQ(PlatformVersion(12, 0, 0), *app.platform_version);
  EXPECT_TRUE(app.IsExtendedFormat());
  EXPECT_FALSE(app.IsUberdriver());
  EXPECT_TRUE(app.IsVezet());

  app = TaximeterApp::FromUserAgent(
      "app:pro brand:uber version:11.12 build_type:beta "
      "platform:android platform_version:12.0");
  EXPECT_EQ(static_cast<std::size_t>(11), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(12), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(0), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Uber, app.version_type);
  EXPECT_EQ(TaximeterPlatform::kAndroid, app.platform);
  EXPECT_EQ("uber", app.GetBrand());
  EXPECT_EQ("beta", app.GetBuildType());
  EXPECT_EQ(PlatformVersion(12, 0, 0), *app.platform_version);
  EXPECT_TRUE(app.IsExtendedFormat());
  EXPECT_TRUE(app.IsUberdriver());
  EXPECT_FALSE(app.IsVezet());

  app = TaximeterApp::FromUserAgent(
      "app:pro brand:yango version:10.12 build_type:sdc build:23455 "
      "platform:ios platform_version:15.0.1");
  EXPECT_EQ(static_cast<std::size_t>(10), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(12), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(23455), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Yango, app.version_type);
  EXPECT_EQ(TaximeterPlatform::kIos, app.platform);
  EXPECT_EQ("yango", app.GetBrand());
  EXPECT_EQ("sdc", app.GetBuildType());
  EXPECT_EQ(PlatformVersion(15, 0, 1), *app.platform_version);
  EXPECT_TRUE(app.IsExtendedFormat());

  app = TaximeterApp::FromUserAgent(
      "app:pro brand:rida version:10.12 build_type:x build:23455 "
      "platform:ios platform_version:15.0.1");
  EXPECT_EQ(static_cast<std::size_t>(10), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(12), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(23455), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Rida, app.version_type);
  EXPECT_EQ(TaximeterPlatform::kIos, app.platform);
  EXPECT_EQ("rida", app.GetBrand());
  EXPECT_EQ("x", app.GetBuildType());
  EXPECT_EQ(PlatformVersion(15, 0, 1), *app.platform_version);
  EXPECT_TRUE(app.IsExtendedFormat());

  app = TaximeterApp::FromUserAgent(
      "app:pro brand:turla version:10.12 build_type:dev build:23455 "
      "platform:ios platform_version:15.0.1");
  EXPECT_EQ(static_cast<std::size_t>(10), app.version.Major());
  EXPECT_EQ(static_cast<std::size_t>(12), app.version.Minor());
  EXPECT_EQ(static_cast<std::size_t>(23455), app.version.Build());
  EXPECT_EQ(TaximeterVersionType::Turla, app.version_type);
  EXPECT_EQ(TaximeterPlatform::kIos, app.platform);
  EXPECT_EQ("turla", app.GetBrand());
  EXPECT_EQ("dev", app.GetBuildType());
  EXPECT_EQ(PlatformVersion(15, 0, 1), *app.platform_version);
  EXPECT_TRUE(app.IsExtendedFormat());

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

TEST(TaximeterApplicationExtendedTest, CheckExtraAppVars) {
  using namespace ua_parser;

  const auto app = TaximeterApp::FromUserAgent(
      "app:pro brand:yandex version:1.2 platform:ios platform_version:12.3.0 "
      "foo:bar");
  const auto& it = app.raw_vars.find("foo");
  EXPECT_NE(it, app.raw_vars.cend());
  EXPECT_EQ("bar", it->second);
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
  using namespace ua_parser;

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

// 1. version_type
// 2. expect_brand
TEST(TaximeterApplicationTest, BrandFromVersionType) {
  using namespace ua_parser;

  using TestCase = std::tuple<std::string, std::string>;
  const TestCase kTestCases[] = {
      {"", "yandex"},         {"yango", "yango"}, {"az", "az"},
      {"uber", "uber"},       {"vezet", "vezet"}, {"beta", "yandex"},
      {"x", "yandex"},        {"sdc", "yandex"},  {"dev", "yandex"},
      {"embedded", "yandex"}, {"rida", "rida"},   {"turla", "turla"},
  };

  for (const auto& testCase : kTestCases) {
    const auto [version_type, expect_brand] = testCase;
    EXPECT_EQ(BrandFromVersionType(version_type), expect_brand);
  }
}
