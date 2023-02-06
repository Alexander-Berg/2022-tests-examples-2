#include "ua_parser/application.hpp"

#include <fstream>

#include <gtest/gtest.h>
#include <testing/source_path.hpp>
#include <testing/taxi_config.hpp>

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/formats/json.hpp>

namespace {

using Map = std::map<std::string, std::string>;

dynamic_config::KeyValue GetTestAppDetector() {
  const auto json = formats::json::blocking::FromFile(
      utils::CurrentSourcePath("src/tests/static/appdetector.json"));

  const auto application_map_brand = dynamic_config::ValueDict<std::string>(
      "APPLICATION_MAP_BRAND", std::unordered_map<std::string, std::string>{
                                   {"android", "yataxi"},                    //
                                   {"iphone", "yataxi"},                     //
                                   {"yango_android", "yango"},               //
                                   {"yango_iphone", "yango"},                //
                                   {"uber_android", "yauber"},               //
                                   {"uber_iphone", "yauber"},                //
                                   {"uber_by_android", "yauber"},            //
                                   {"uber_by_iphone", "yauber"},             //
                                   {"uber_kz_android", "yauber"},            //
                                   {"uber_kz_iphone", "yauber"},             //
                                   {"uber_az_android", "yauber"},            //
                                   {"uber_az_iphone", "yauber"},             //
                                   {"win", "yataxi"},                        //
                                   {"mobileweb_android", "yataxi"},          //
                                   {"mobileweb_iphone", "yataxi"},           //
                                   {"mobileweb", "yataxi"},                  //
                                   {"mobileweb_yango", "yango"},             //
                                   {"mobileweb_uber", "yauber"},             //
                                   {"mobileweb_yango_android", "yango"},     //
                                   {"mobileweb_yango_iphone", "yango"},      //
                                   {"mobileweb_uber_android", "yauber"},     //
                                   {"mobileweb_uber_iphone", "yauber"},      //
                                   {"mobileweb_uber_by_android", "yauber"},  //
                                   {"mobileweb_uber_by_iphone", "yauber"},   //
                                   {"mobileweb_uber_kz_android", "yauber"},  //
                                   {"mobileweb_uber_kz_iphone", "yauber"},   //
                                   {"mobileweb_uber_az_android", "yauber"},  //
                                   {"mobileweb_uber_az_iphone", "yauber"},   //
                                   {"web_yango", "yango"},                   //
                                   {"web_uber", "yauber"},                   //
                                   {"web", "yataxi"},                        //
                               });
  return ua_parser::LoadAppDetectorFromJson(json, application_map_brand);
}

void DoTest(const std::string& user_agent, const std::string& x_taxi,
            const std::string& x_requested_uri, const Map& expected) {
  static dynamic_config::StorageMock config_storage{GetTestAppDetector()};
  auto appvars = ua_parser::DetectApplication(
      user_agent, x_taxi, x_requested_uri, config_storage.GetSnapshot());
  Map detected(appvars.begin(), appvars.end());
  EXPECT_EQ(detected, expected);
  EXPECT_FALSE(detected.at("app_name").empty());
}

void DoTest(const std::string& user_agent, const std::string& x_taxi,
            const std::string& x_requested_uri, const std::string& x_platform,
            const std::string& x_app_version, const Map& expected) {
  static dynamic_config::StorageMock config_storage{GetTestAppDetector()};

  ua_parser::DetectionParams dp;
  dp.SetUserAgent(user_agent);
  dp.SetXTaxi(x_taxi);
  dp.SetXRequestedUri(x_requested_uri);
  dp.SetXPlatform(x_platform);
  dp.SetXAppVersion(x_app_version);

  auto appvars = ua_parser::DetectApplication(dp, config_storage.GetSnapshot());
  Map detected(appvars.begin(), appvars.end());
  EXPECT_EQ(detected, expected);
  EXPECT_FALSE(detected.at("app_name").empty());
}

}  // namespace

TEST(AppDetector, Android1) {
  Map expected = {
      {"app_brand", "yataxi"},   //
      {"app_name", "android"},   //
      {"app_build", "release"},  //
      {"platform_ver1", "8"},    //
      {"platform_ver2", "1"},    //
      {"platform_ver3", "0"},    //
      {"app_ver1", "3"},         //
      {"app_ver2", "96"},        //
      {"app_ver3", "0"},         //
  };
  DoTest("yandex-taxi/3.96.0.61338 Android/8.1.0 (Xiaomi; MI 8 Lite)", "", "",
         expected);
}

TEST(AppDetector, Android2) {
  Map expected = {
      {"app_brand", "yataxi"},   //
      {"app_name", "android"},   //
      {"app_build", "release"},  //
      {"platform_ver1", "9"},    //
  };
  DoTest("yandex-taxi/293 Android/9 (Xiaomi; MI 8 Lite)", "", "", expected);
}

TEST(AppDetector, Iphone1) {
  Map expected = {
      {"app_brand", "yataxi"},   //
      {"app_name", "iphone"},    //
      {"app_build", "release"},  //
      {"platform_ver1", "12"},   //
      {"platform_ver2", "2"},    //
      {"app_ver1", "4"},         //
      {"app_ver2", "81"},        //
      {"app_ver3", "30920"},     //
  };
  DoTest("ru.yandex.ytaxi/4.81.30920 (iPhone; iPhone6,2; iOS 12.2; Darwin)", "",
         "", expected);
}

TEST(AppDetector, YangoAndroid1) {
  Map expected = {
      {"app_brand", "yango"},         //
      {"app_name", "yango_android"},  //
      {"app_build", "release"},       //
      {"platform_ver1", "6"},         //
      {"platform_ver2", "0"},         //
      {"platform_ver3", "1"},         //
      {"app_ver1", "3"},              //
      {"app_ver2", "93"},             //
      {"app_ver3", "0"},              //
  };
  DoTest("yango/3.93.0.54106 Android/6.0.1 (Xiaomi; Redmi Note 3)", "", "",
         expected);
}

TEST(AppDetector, YangoIphone1) {
  Map expected = {
      {"app_brand", "yango"},        //
      {"app_name", "yango_iphone"},  //
      {"app_build", "release"},      //
      {"platform_ver1", "12"},       //
      {"platform_ver2", "1"},        //
      {"platform_ver3", "2"},        //
      {"app_ver1", "4"},             //
      {"app_ver2", "84"},            //
      {"app_ver3", "31436"},         //
  };
  DoTest("ru.yandex.yango/4.84.31436 (iPhone; iPhone9,3; iOS 12.1.2; Darwin)",
         "", "", expected);
}

TEST(AppDetector, UberAndroid1) {
  Map expected = {
      {"app_brand", "yauber"},       //
      {"app_name", "uber_android"},  //
      {"app_build", "release"},      //
      {"platform_ver1", "8"},        //
      {"platform_ver2", "0"},        //
      {"platform_ver3", "0"},        //
      {"app_ver1", "3"},             //
      {"app_ver2", "84"},            //
      {"app_ver3", "0"},             //
  };
  DoTest("yandex-uber/3.84.0.67190 Android/8.0.0 (samsung; SM-A730F)", "", "",
         expected);
}

TEST(AppDetector, UberIphone1) {
  Map expected = {
      {"app_brand", "yauber"},      //
      {"app_name", "uber_iphone"},  //
      {"app_build", "release"},     //
      {"platform_ver1", "12"},      //
      {"platform_ver2", "2"},       //
      {"app_ver1", "4"},            //
      {"app_ver2", "30"},           //
      {"app_ver3", "22266"},        //
  };
  DoTest("ru.yandex.uber/4.30.22266 (iPhone; iPhone11,6; iOS 12.2; Darwin)", "",
         "", expected);
}

TEST(AppDetector, UberByAndroid1) {
  Map expected = {
      {"app_brand", "yauber"},          //
      {"app_name", "uber_by_android"},  //
      {"app_build", "release"},         //
      {"platform_ver1", "8"},           //
      {"platform_ver2", "0"},           //
      {"platform_ver3", "0"},           //
      {"app_ver1", "3"},                //
      {"app_ver2", "85"},               //
      {"app_ver3", "1"},                //
  };
  DoTest("yandex-uber-by/3.85.1.72960 Android/8.0.0 (HUAWEI; RNE-L21)", "", "",
         expected);
}

TEST(AppDetector, UberByIphone1) {
  Map expected = {
      {"app_brand", "yauber"},         //
      {"app_name", "uber_by_iphone"},  //
      {"app_build", "release"},        //
      {"platform_ver1", "12"},         //
      {"platform_ver2", "3"},          //
      {"platform_ver3", "1"},          //
      {"app_ver1", "4"},               //
      {"app_ver2", "80"},              //
      {"app_ver3", "30925"},           //
  };
  DoTest(
      "ru.yandex.uber-by/4.80.30925 (iPhone; iPhone11,8; iOS 12.3.1; Darwin)",
      "", "", expected);
}

TEST(AppDetector, UberKzAndroid1) {
  Map expected = {
      {"app_brand", "yauber"},          //
      {"app_name", "uber_kz_android"},  //
      {"app_build", "release"},         //
      {"platform_ver1", "7"},           //
      {"platform_ver2", "1"},           //
      {"platform_ver3", "1"},           //
      {"app_ver1", "3"},                //
      {"app_ver2", "85"},               //
      {"app_ver3", "1"},                //
  };
  DoTest("yandex-uber-kz/3.85.1.72959 Android/7.1.1 (samsung; SM-J510FN)", "",
         "", expected);
}

TEST(AppDetector, UberKzIphone1) {
  Map expected = {
      {"app_brand", "yauber"},         //
      {"app_name", "uber_kz_iphone"},  //
      {"app_build", "release"},        //
      {"platform_ver1", "10"},         //
      {"platform_ver2", "3"},          //
      {"platform_ver3", "3"},          //
      {"app_ver1", "4"},               //
      {"app_ver2", "80"},              //
      {"app_ver3", "30923"},           //
  };
  DoTest("ru.yandex.uber-kz/4.80.30923 (iPhone; iPhone5,2; iOS 10.3.3; Darwin)",
         "", "", expected);
}

TEST(AppDetector, UberAzAndroid1) {
  Map expected = {
      {"app_brand", "yauber"},          //
      {"app_name", "uber_az_android"},  //
      {"app_build", "release"},         //
      {"platform_ver1", "8"},           //
      {"platform_ver2", "1"},           //
      {"platform_ver3", "0"},           //
      {"app_ver1", "3"},                //
      {"app_ver2", "85"},               //
      {"app_ver3", "1"},                //
  };
  DoTest(
      "yandex-uber-az/3.85.1.72957 Android/8.1.0 (INFINIX MOBILITY LIMITED; "
      "Infinix X5515F)",
      "", "", expected);
}

TEST(AppDetector, UberAzIphone1) {
  Map expected = {
      {"app_brand", "yauber"},         //
      {"app_name", "uber_az_iphone"},  //
      {"app_build", "release"},        //
      {"platform_ver1", "12"},         //
      {"platform_ver2", "3"},          //
      {"platform_ver3", "1"},          //
      {"app_ver1", "4"},               //
      {"app_ver2", "80"},              //
      {"app_ver3", "30928"},           //
  };
  DoTest("com.mlubv.uber-az/4.80.30928 (iPhone; iPhone9,3; iOS 12.3.1; Darwin)",
         "", "", expected);
}

TEST(AppDetector, Win1) {
  Map expected = {
      {"app_brand", "yataxi"},  //
      {"app_name", "win"},      //
      {"app_ver1", "1"},        //
      {"app_ver2", "11"},       //
      {"app_ver3", "5392"},     //
  };
  DoTest(
      "yandex-taxi/1.11.5392.423 WindowsPhone/8.10.15148.0 (Microsoft; "
      "RM-1075_1017)",
      "", "", expected);
}

TEST(AppDetector, MobileWebAndroid1) {
  Map expected = {
      {"app_brand", "yataxi"},            //
      {"app_name", "mobileweb_android"},  //
      {"app_build", "release"},           //
      {"platform_ver1", "7"},             //
      {"platform_ver2", "1"},             //
      {"platform_ver3", "2"},             //
      {"app_ver1", "3"},                  //
      {"app_ver2", "97"},                 //
      {"app_ver3", "2"},                  //
  };
  DoTest(
      "Mozilla/5.0 (Linux; Android 7.1.2; Redmi 5A Build/N2G47H; wv) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/73.0.3683.90 "
      "Mobile Safari/537.36 yandex-taxi/3.97.2.63189 Android/7.1.2 (Xiaomi; "
      "Redmi 5A)",
      "", "", expected);
}

TEST(AppDetector, MobileWebAndroid2) {
  Map expected = {
      {"app_brand", "yataxi"},            //
      {"app_name", "mobileweb_android"},  //
      {"app_build", "release"},           //
      {"platform_ver1", "7"},             //
      {"platform_ver2", "1"},             //
      {"platform_ver3", "2"},             //
      {"app_ver1", "3"},                  //
      {"app_ver2", "97"},                 //
      {"app_ver3", "2"},                  //
  };
  DoTest(
      "Mozilla/5.0 (Linux; Android 7.1.2; Redmi 5A Build/N2G47H; wv) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/73.0.3683.90 "
      "Mobile Safari/537.36 yandex-taxi/3.97.2.63189 Android/7.1.2 (Xiaomi; "
      "Redmi 5A)",
      "mobile", "", expected);
}

TEST(AppDetector, MobileWeb1) {
  Map expected = {
      {"app_brand", "yataxi"},    //
      {"app_name", "mobileweb"},  //
      {"app_ver1", "2"},          //
  };
  DoTest("Something Android/4.8.15.16.23.42", "mobile", "", expected);
}

TEST(AppDetector, MobileWebYango1) {
  Map expected = {
      {"app_brand", "yango"},           //
      {"app_name", "mobileweb_yango"},  //
      {"app_ver1", "2"},                //
  };
  DoTest("Something Android/4.8.15.16.23.42", "mobile",
         "string with yango in it", expected);
}

TEST(AppDetector, MobileWebUber1) {
  Map expected = {
      {"app_brand", "yauber"},         //
      {"app_name", "mobileweb_uber"},  //
      {"app_ver1", "2"},               //
  };
  DoTest(
      "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko)",
      "mobile", "string with UBER in it", expected);
}

TEST(AppDetector, MobileWebIphone1) {
  Map expected = {
      {"app_brand", "yataxi"},           //
      {"app_name", "mobileweb_iphone"},  //
      {"app_build", "release"},          //
      {"platform_ver1", "12"},           //
      {"platform_ver2", "3"},            //
      {"platform_ver3", "1"},            //
      {"app_ver1", "4"},                 //
      {"app_ver2", "81"},                //
      {"app_ver3", "30920"},             //
  };
  DoTest(
      "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) yandex-taxi/4.81.30920",
      "", "", expected);
}

TEST(AppDetector, MobileWebYangoAndroid1) {
  Map expected = {
      {"app_brand", "yango"},                   //
      {"app_name", "mobileweb_yango_android"},  //
      {"app_build", "release"},                 //
      {"platform_ver1", "5"},                   //
      {"platform_ver2", "1"},                   //
      {"platform_ver3", "1"},                   //
      {"app_ver1", "3"},                        //
      {"app_ver2", "106"},                      //
      {"app_ver3", "0"},                        //
  };
  DoTest(
      "Mozilla/5.0 (Linux; Android 5.1.1; SM-J500H Build/LMY48B; wv) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 "
      "Mobile Safari/537.36 yango/3.106.0.75248 Android/5.1.1 (samsung; "
      "SM-J500H)",
      "", "", expected);
}

TEST(AppDetector, MobileWebYangoIphone1) {
  Map expected = {
      {"app_brand", "yango"},                  //
      {"app_name", "mobileweb_yango_iphone"},  //
      {"app_build", "release"},                //
      {"platform_ver1", "12"},                 //
      {"platform_ver2", "1"},                  //
      {"app_ver1", "4"},                       //
      {"app_ver2", "78"},                      //
      {"app_ver3", "30300"},                   //
  };
  DoTest(
      "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) yango/4.78.30300",
      "", "", expected);
}

TEST(AppDetector, MobileWebUberAndroid1) {
  Map expected = {
      {"app_brand", "yauber"},                 //
      {"app_name", "mobileweb_uber_android"},  //
      {"app_build", "release"},                //
      {"platform_ver1", "9"},                  //
      {"app_ver1", "3"},                       //
      {"app_ver2", "85"},                      //
      {"app_ver3", "1"},                       //
  };
  DoTest(
      "Mozilla/5.0 (Linux; Android 9; Redmi Note 5 Build/PKQ1.180904.001; wv) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/75.0.3770.101 "
      "Mobile Safari/537.36 uber-ru/3.85.1.72958 Android/9 (Xiaomi; Redmi Note "
      "5)",
      "", "", expected);
}

TEST(AppDetector, MobileWebUberIphone1) {
  Map expected = {
      {"app_brand", "yauber"},                //
      {"app_name", "mobileweb_uber_iphone"},  //
      {"app_build", "release"},               //
      {"platform_ver1", "11"},                //
      {"platform_ver2", "4"},                 //
      {"app_ver1", "4"},                      //
      {"app_ver2", "30"},                     //
      {"app_ver3", "22266"},                  //
  };
  DoTest(
      "Mozilla/5.0 (iPhone; CPU iPhone OS 11_4 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) uber-ru/4.30.22266",
      "", "", expected);
}

TEST(AppDetector, MobileWebUberByAndroid1) {
  Map expected = {
      {"app_brand", "yauber"},                    //
      {"app_name", "mobileweb_uber_by_android"},  //
      {"app_build", "release"},                   //
      {"platform_ver1", "6"},                     //
      {"platform_ver2", "0"},                     //
      {"platform_ver3", "1"},                     //
      {"app_ver1", "3"},                          //
      {"app_ver2", "85"},                         //
      {"app_ver3", "1"},                          //
  };
  DoTest(
      "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5 Build/M4B30Z; wv) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/75.0.3770.101 "
      "Mobile Safari/537.36 uber-by/3.85.1.72960 Android/6.0.1 (LGE; Nexus 5)",
      "", "", expected);
}

TEST(AppDetector, MobileWebUberByIphone1) {
  Map expected = {
      {"app_brand", "yauber"},                   //
      {"app_name", "mobileweb_uber_by_iphone"},  //
      {"app_build", "release"},                  //
      {"platform_ver1", "12"},                   //
      {"platform_ver2", "2"},                    //
      {"app_ver1", "4"},                         //
      {"app_ver2", "80"},                        //
      {"app_ver3", "30925"},                     //
  };
  DoTest(
      "Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) uber-by/4.80.30925",
      "", "", expected);
}

TEST(AppDetector, MobileWebUberKzAndroid1) {
  Map expected = {
      {"app_brand", "yauber"},                    //
      {"app_name", "mobileweb_uber_kz_android"},  //
      {"app_build", "release"},                   //
      {"platform_ver1", "9"},                     //
      {"app_ver1", "3"},                          //
      {"app_ver2", "85"},                         //
      {"app_ver3", "1"},                          //
  };
  DoTest(
      "Mozilla/5.0 (Linux; Android 9; CLT-L29 Build/HUAWEICLT-L29; wv) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/73.0.3683.90 "
      "Mobile Safari/537.36 uber-kz/3.85.1.72959 Android/9 (HUAWEI; CLT-L29)",
      "", "", expected);
}

TEST(AppDetector, MobileWebUberKzIphone1) {
  Map expected = {
      {"app_brand", "yauber"},                   //
      {"app_name", "mobileweb_uber_kz_iphone"},  //
      {"app_build", "release"},                  //
      {"platform_ver1", "12"},                   //
      {"platform_ver2", "3"},                    //
      {"platform_ver3", "1"},                    //
      {"app_ver1", "4"},                         //
      {"app_ver2", "80"},                        //
      {"app_ver3", "30923"},                     //
  };
  DoTest(
      "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) uber-kz/4.80.30923",
      "", "", expected);
}

TEST(AppDetector, MobileWebUberAzAndroid1) {
  Map expected = {
      {"app_brand", "yauber"},                    //
      {"app_name", "mobileweb_uber_az_android"},  //
      {"app_build", "release"},                   //
      {"platform_ver1", "9"},                     //
      {"app_ver1", "3"},                          //
      {"app_ver2", "85"},                         //
      {"app_ver3", "1"},                          //
  };
  DoTest(
      "Mozilla/5.0 (Linux; Android 9; Mi A2 Build/PKQ1.180904.001; wv) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/75.0.3770.101 "
      "Mobile Safari/537.36 uber-az/3.85.1.72957 Android/9 (Xiaomi; Mi A2)",
      "", "", expected);
}

TEST(AppDetector, MobileWebUberAzIphone1) {
  Map expected = {
      {"app_brand", "yauber"},                   //
      {"app_name", "mobileweb_uber_az_iphone"},  //
      {"app_build", "release"},                  //
      {"platform_ver1", "12"},                   //
      {"platform_ver2", "3"},                    //
      {"platform_ver3", "1"},                    //
      {"app_ver1", "4"},                         //
      {"app_ver2", "80"},                        //
      {"app_ver3", "30928"},                     //
  };
  DoTest(
      "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) uber-az/4.80.30928",
      "", "", expected);
}

TEST(AppDetector, WebYango) {
  Map expected = {
      {"app_brand", "yango"},     //
      {"app_name", "web_yango"},  //
      {"app_ver1", "2"},          //
  };
  DoTest("Something Android/4.8.15.16.23.42", "", "String with yango in it",
         expected);
}

TEST(AppDetector, WebUber) {
  Map expected = {
      {"app_brand", "yauber"},   //
      {"app_name", "web_uber"},  //
      {"app_ver1", "2"},         //
  };
  DoTest("Something Android/4.8.15.16.23.42", "anything",
         "String with uber in it", expected);
}

TEST(AppDetector, Web) {
  Map expected = {
      {"app_brand", "yataxi"},  //
      {"app_name", "web"},      //
      {"app_ver1", "2"},        //
  };
  DoTest("Something Android/4.8.15.16.23.42", "anything", "Some other string",
         expected);
}

TEST(AppDetector, Platform_1) {
  Map expected = {
      {"app_brand", "yataxi"},  //
      {"app_name", "iphone"},   //
      {"app_ver1", "1"},        //
      {"app_ver2", "2"},        //
      {"app_ver3", "3"},        //
  };
  DoTest("Something ios/4.8.15.16.23.42", "anything", "Some other string",
         "ios_app", "1.2.3", expected);
}

TEST(AppDetector, Platform_2) {
  Map expected = {
      {"app_brand", "yataxi"},  //
      {"app_name", "web"},      //
      {"app_ver1", "2"},        //
      {"app_ver2", "3"},        //
  };
  DoTest("Something desktop/4.8.15.16.23.42", "anything", "Some other string",
         "desktop_web", "2.3", expected);
}

TEST(AppDetector, Platform_3) {
  Map expected = {
      {"app_brand", "yataxi"},    //
      {"app_name", "super_web"},  //
  };
  DoTest("Something super app/4.8.15.16.23.42", "anything", "Some other string",
         "superapp_taxi_web", "", expected);
}

TEST(AppDetector, DefaultConfig) {
  [[maybe_unused]] const auto& config = dynamic_config::GetDefaultSnapshot();
}
