#include <endpoints/full/plugins/brandings/common/brandings_serializable.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/serialize/common_containers.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::full::brandings {

service_level::TariffBranding MockBranding(
    const std::string& type, bool extra = false, bool tooltip = false,
    std::optional<std::string> icon = std::nullopt) {
  service_level::TariffBranding result;
  result.type = type;
  result.title = "title_key";
  result.subtitle = "subtitle_key";
  result.value = "30";
  result.action = "redirect";
  result.redirect_class = "econom";
  result.icon = std::move(icon);

  if (extra) {
    auto payment = service_level::BrandingExtraPayment{"wallet", "wallet_id"};
    result.extra =
        service_level::BrandingExtra{"coverage", payment, "banner_id"};
  }

  if (tooltip) {
    result.tooltip = service_level::ToolTip{"tooltip"};
  }

  return result;
}

TEST(BrandingsSerializable, Ok) {
  std::vector<service_level::TariffBranding> brandings{
      MockBranding("test_1"),
      MockBranding("test_2", true),
      MockBranding("test_3", false, true),
      MockBranding("test_4", true, true, "plus_promo_big_cashback"),
  };

  const auto& serializable = BrandingsSerializable(brandings);

  handlers::ServiceLevel sl_resp;
  plugins::common::ResultWrapper<handlers::ServiceLevel> wrapper(sl_resp);
  serializable.SerializeInPlace(wrapper);

  const auto& result = *sl_resp.brandings;
  ASSERT_EQ(brandings.size(), 4);

  using formats::json::FromString;
  using formats::json::ValueBuilder;
  ASSERT_EQ(ValueBuilder(result[0]).ExtractValue(), FromString(R"({
             "type": "test_1",
             "title": "title_key",
             "subtitle": "subtitle_key",
             "value": "30",
             "redirect_class": "econom",
             "action": "redirect"})"));

  ASSERT_EQ(ValueBuilder(result[1]).ExtractValue(), FromString(R"({
             "type": "test_2",
             "title": "title_key",
             "subtitle": "subtitle_key",
             "value": "30",
             "redirect_class": "econom",
             "action": "redirect",
             "extra": {
                 "payment": {
                     "type": "wallet",
                     "payment_method_id": "wallet_id"
                 },
                 "cost_coverage": "coverage",
                 "banner_id": "banner_id"
             }})"));

  ASSERT_EQ(ValueBuilder(result[2]).ExtractValue(), FromString(R"({
             "type": "test_3",
             "title": "title_key",
             "subtitle": "subtitle_key",
             "value": "30",
             "redirect_class": "econom",
             "action": "redirect",
             "tooltip": {
                 "text": "tooltip"
             }})"));

  ASSERT_EQ(ValueBuilder(result[3]).ExtractValue(), FromString(R"({
             "type": "test_4",
             "title": "title_key",
             "icon": "plus_promo_big_cashback",
             "subtitle": "subtitle_key",
             "value": "30",
             "redirect_class": "econom",
             "action": "redirect",
             "extra": {
                 "payment": {
                     "type": "wallet",
                     "payment_method_id": "wallet_id"
                 },
                 "cost_coverage": "coverage",
                 "banner_id": "banner_id"
             },
             "tooltip": {
                 "text": "tooltip"
             }})"));
}

}  // namespace routestats::full::brandings
