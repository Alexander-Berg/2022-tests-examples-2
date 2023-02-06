#include <utils/helpers/bson.hpp>
#include <utils/helpers/json.hpp>
#include <vgw/models/voice_gateways_zones.hpp>

#include <gtest/gtest.h>

static const char* kVoiceGatewaysZoneJson_Correct =
    "{"
    "  \"_id\": \"moscow\","
    "  \"voice_gateways\": {"
    "    \"mtt\":"
    "    {"
    "        \"city_id\": \"Sochi\","
    "        \"driver\": true,"
    "        \"passenger\": false"
    "    },"
    "    \"zingaya\":"
    "    {"
    "      \"city_id\": \"Сочи\","
    "      \"driver\": false,"
    "      \"passenger\": true"
    "     }"
    "  }"
    "}";

static const char* kVoiceGatewaysZoneJson_NoGateways =
    "{"
    "  \"_id\": \"moscow\","
    "  \"voice_gateways\": {"
    "  }"
    "}";

static const char* kVoiceGatewaysZoneJson_NoGatewaysObject =
    "{"
    "  \"_id\": \"moscow\""
    "}";

static const char* kVoiceGatewaysZoneJson_Incorrect =
    "{"
    "  \"_id\": \"moscow\","
    "  \"voice_gateways\": {"
    "    \"mtt\": {},"
    "    \"\":"
    "    {"
    "      \"city_id\": \"Sochi\","
    "      \"driver\": false,"
    "      \"passenger\": true"
    "    },"
    "    \"zingaya\":"
    "    {"
    "      \"city_id\": \"\","
    "      \"driver\": true"
    "    }"
    "  }"
    "}";

TEST(VoiceGatewaysZones, Deserialize) {
  {
    mongo::BSONObj doc = utils::helpers::Json2Bson(
        utils::helpers::ParseJson(kVoiceGatewaysZoneJson_Correct));
    vgw::models::VoiceGatewaysZone zone;
    ASSERT_NO_THROW(zone.Deserialize(doc));
    ASSERT_EQ(zone.id, "moscow");
    const auto& vgws = zone.voice_gateways;
    ASSERT_EQ(vgws.size(), 2ul);
    ASSERT_EQ(vgws[0].id, "mtt");
    ASSERT_EQ(vgws[0].city_id, "Sochi");
    ASSERT_EQ(vgws[0].driver_enabled, true);
    ASSERT_EQ(vgws[0].passenger_enabled, false);
    ASSERT_EQ(vgws[1].id, "zingaya");
    ASSERT_EQ(vgws[1].city_id, "Сочи");
    ASSERT_EQ(vgws[1].driver_enabled, false);
    ASSERT_EQ(vgws[1].passenger_enabled, true);
  }

  {
    mongo::BSONObj doc = utils::helpers::Json2Bson(
        utils::helpers::ParseJson(kVoiceGatewaysZoneJson_NoGateways));
    vgw::models::VoiceGatewaysZone zone;
    ASSERT_NO_THROW(zone.Deserialize(doc));
    const auto& vgws = zone.voice_gateways;
    ASSERT_EQ(vgws.size(), 0ul);
  }

  {
    mongo::BSONObj doc = utils::helpers::Json2Bson(
        utils::helpers::ParseJson(kVoiceGatewaysZoneJson_NoGatewaysObject));
    vgw::models::VoiceGatewaysZone zone;
    ASSERT_NO_THROW(zone.Deserialize(doc));
    const auto& vgws = zone.voice_gateways;
    ASSERT_EQ(vgws.size(), 0ul);
  }

  {
    mongo::BSONObj doc = utils::helpers::Json2Bson(
        utils::helpers::ParseJson(kVoiceGatewaysZoneJson_Incorrect));
    vgw::models::VoiceGatewaysZone zone;
    ASSERT_NO_THROW(zone.Deserialize(doc));
    const auto& vgws = zone.voice_gateways;
    ASSERT_EQ(vgws.size(), 0ul);
  }
}
