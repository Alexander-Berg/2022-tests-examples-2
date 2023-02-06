#include <userver/utest/utest.hpp>

#include <userver/formats/json/serialize.hpp>

#include <features/protocol_proxy/feature.hpp>

namespace routestats::features {

using ProtocolResponse = ProtocolResponseExtraProxy::ProtocolResponse;

using ServiceLevel = clients::protocol_routestats::ServiceLevel;

ServiceLevel BuildServiceLevel(const std::string& class_name,
                               const std::string& extra_source) {
  ServiceLevel result;

  result.class_ = class_name;
  result.extra = formats::json::FromString(extra_source);

  return result;
}

TEST(ProtocolResponseExtraProxy, RootExtraFields) {
  ProtocolResponse response;
  response.extra = formats::json::FromString(R"({"a": "b", "c": 1})");

  ProtocolResponseExtraProxy feature;
  feature.StoreResponseExtra(response);

  ASSERT_EQ(feature.GetRootExtra(), response.extra);
}

TEST(ProtocolResponseExtraProxy, ServiceLevelsExtraFields) {
  ProtocolResponse response;
  response.service_levels = {
      BuildServiceLevel("econom", R"({"__name__": "econom"})"),
      BuildServiceLevel("comfort", R"({"__name__": "comfort"})"),
  };

  ProtocolResponseExtraProxy feature;
  feature.StoreResponseExtra(response);

  ASSERT_EQ(feature.GetServiceLevelExtra("econom"),
            formats::json::FromString(R"({"__name__": "econom"})"));
  ASSERT_EQ(feature.GetServiceLevelExtra("comfort"),
            formats::json::FromString(R"({"__name__": "comfort"})"));
  ASSERT_EQ(feature.GetServiceLevelExtra("yet_another_level"),
            formats::json::Value{});
}

TEST(ProtocolResponseExtraProxy, ServiceLevelsDuplicates) {
  ProtocolResponse response;
  response.service_levels = {
      BuildServiceLevel("econom", R"({"__name__": "econom"})"),
      BuildServiceLevel("comfort", R"({"__name__": "comfort"})"),
      BuildServiceLevel("econom", R"({"__name__": "yet_another_econom"})"),
  };

  ProtocolResponseExtraProxy feature;
  feature.StoreResponseExtra(response);

  ASSERT_EQ(feature.GetServiceLevelExtra("econom"),
            formats::json::FromString(R"({"__name__": "econom"})"));
  ASSERT_EQ(feature.GetServiceLevelExtra("comfort"),
            formats::json::FromString(R"({"__name__": "comfort"})"));
}

}  // namespace routestats::features
