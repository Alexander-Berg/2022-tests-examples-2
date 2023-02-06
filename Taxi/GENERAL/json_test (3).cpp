#include <gtest/gtest.h>
#include <utils/json.hpp>

#include <userver/formats/json.hpp>

#include <string>

namespace signal_device_configs::utils {

const std::string kJson1 = R"(
  {
      "mqtt":false,
      "distraction":true
  }  
)";

const std::string kJson2 = R"(
  {
      "mqtt":true
  }  
)";

const std::string kJson3 = R"(
  {
      "mqtt": {
          "enabled" : true,
          "path" : "/aasd"
      }
  }  
)";

const std::string kJson4 = R"(
  {
      "mqtt": {
          "enabled" : false,
          "tests" : {
              "on" : "line"
          }
      },
      "voice" : "off"
  }  
)";

const std::string kExpected_1_2 = R"(
  {
      "mqtt":true,
      "distraction":true
  }  
)";

const std::string kExpected_2_1 = R"(
  {
      "mqtt":false,
      "distraction":true
  }  
)";

const std::string kExpected_1_3 = R"(
  {
      "mqtt": {
          "enabled" : true,
          "path" : "/aasd"
      },
      "distraction":true
  }  
)";

const std::string kExpected_3_1 = R"(
  {
      "mqtt":false,
      "distraction":true
  }  
)";

const std::string kExpected_3_4 = R"(
  {
      "mqtt": {
          "enabled" : false,
          "path" : "/aasd",
          "tests" : {
              "on" : "line"
          }
      },
      "voice" : "off"
  }  
)";

const std::string kExpected_4_3 = R"(
  {
      "mqtt": {
          "enabled" : true,
          "path" : "/aasd",
          "tests" : {
              "on" : "line"
          }
      },
      "voice" : "off"
  }  
)";

TEST(MergeJson, MergeJson_1_2) {
  EXPECT_EQ(MergeJson(formats::json::FromString(kJson1),
                      formats::json::FromString(kJson2)),
            formats::json::FromString(kExpected_1_2));
}

TEST(MergeJson, MergeJson_2_1) {
  EXPECT_EQ(MergeJson(formats::json::FromString(kJson2),
                      formats::json::FromString(kJson1)),
            formats::json::FromString(kExpected_2_1));
}

TEST(MergeJson, MergeJson_1_3) {
  EXPECT_EQ(MergeJson(formats::json::FromString(kJson1),
                      formats::json::FromString(kJson3)),
            formats::json::FromString(kExpected_1_3));
}

TEST(MergeJson, MergeJson_3_1) {
  EXPECT_EQ(MergeJson(formats::json::FromString(kJson3),
                      formats::json::FromString(kJson1)),
            formats::json::FromString(kExpected_3_1));
}

TEST(MergeJson, MergeJson_3_4) {
  EXPECT_EQ(MergeJson(formats::json::FromString(kJson3),
                      formats::json::FromString(kJson4)),
            formats::json::FromString(kExpected_3_4));
}

TEST(MergeJson, MergeJson_4_3) {
  EXPECT_EQ(MergeJson(formats::json::FromString(kJson4),
                      formats::json::FromString(kJson3)),
            formats::json::FromString(kExpected_4_3));
}

}  // namespace signal_device_configs::utils
