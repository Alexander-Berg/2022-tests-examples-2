#include <endpoints/full/plugins/brandings/common/brandings_serializable.hpp>
#include <endpoints/full/plugins/brandings/subplugins/brandings_proxy.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/parse/common_containers.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::full::brandings {

static const std::string kBrandingsJson = R"([
        {
          "action": "redirect",
          "redirect_class": "comfortplus",
          "title": "Сейчас «Комфорт+»  для вас чуть дороже, чем «Эконом»",
          "type": "tariff_upgrade_suggestion"
        },
        {
          "action": "redirect",
          "redirect_class": "courier",
          "title": "Новый тариф «Курьер»",
          "type": "tariff_promotion"
        },
        {
          "title": "Кэшбэк за поездку",
          "tooltip": {
            "text": "кэшбэк за поездку"
          },
          "type": "cashback",
          "value": "+93"
        },
        {
          "title": "Поездка может стоить на 47 $SIGN$$CURRENCY$ дешевле — с подпиской на Плюс",
          "type": "plus_promotion",
          "extra": {"payment": {"type": "wallet", "payment_method_id": "wallet_id"}, "cost_coverage": "full"}
        }
      ])";

ProtocolResponse MockProtocolResponse() {
  ProtocolResponse response;

  clients::protocol_routestats::ServiceLevel econom_sl;
  econom_sl.class_ = "econom";
  econom_sl.brandings =
      formats::json::FromString(kBrandingsJson)
          .As<std::vector<
              clients::protocol_routestats::ServiceLevelBranding>>();

  response.service_levels = {econom_sl};
  return response;
}

TEST(TestBrandingsProxyPlugin, Proxy) {
  BrandingsProxyPlugin plugin;
  plugin.OnGotProtocolResponse(MockProtocolResponse());

  auto brandings = plugin.GetBrandings("econom");
  ASSERT_EQ(brandings.size(), 4);

  auto vip_brandings = plugin.GetBrandings("vip");
  ASSERT_EQ(vip_brandings.size(), 0);

  auto serializable = BrandingsSerializable(brandings);

  handlers::ServiceLevel sl_resp;
  plugins::common::ResultWrapper<handlers::ServiceLevel> wrapper(sl_resp);
  serializable.SerializeInPlace(wrapper);

  const auto& result_json = formats::json::ValueBuilder(sl_resp).ExtractValue();
  ASSERT_EQ(result_json["brandings"],
            formats::json::FromString(kBrandingsJson));
}

}  // namespace routestats::full::brandings
