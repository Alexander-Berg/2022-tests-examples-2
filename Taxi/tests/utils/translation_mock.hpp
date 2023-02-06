#pragma once

#include <string>
#include <tuple>
#include <vector>
#include "utils/l10n.hpp"

namespace l10n {
std::string ConvertToTemplate(const std::string& str);
}

class MockTranslations : public l10n::MainTranslations {
  using locstrmap = std::unordered_map<std::string, ff::TextTemplate>;
  using klocmap = std::unordered_map<std::string, locstrmap>;
  using kskeymap = std::unordered_map<std::string, klocmap>;

  std::vector<std::tuple<std::string, std::string, std::string, std::string>>
      fixture = {
          std::make_tuple("geoareas", "inside_city", "en", "inside city"),
          std::make_tuple("geoareas", "inside_moscow", "en", "inside Moscow"),
          std::make_tuple("geoareas", "inside_suburb", "en", "in suburbs"),
          std::make_tuple("geoareas", "moscow", "en", "moscow"),
          std::make_tuple("geoareas", "to_ekb", "en", "To Yekaterinburg"),
          std::make_tuple("geoareas", "to_moscow", "en", "to Moscow"),
          std::make_tuple("geoareas", "zelenograd", "en", "Zelenograd"),
          std::make_tuple("geoareas", "mytishchi", "en", "Mytishchi"),
          std::make_tuple("geoareas", "inside_mytishchi", "en",
                          "Through Mytishchi"),
          std::make_tuple("geoareas", "inside_fryazino", "en",
                          "Through Fryazino"),
          std::make_tuple("tariff", "currency.rub", "en", "rub"),
          std::make_tuple("tariff", "currency.byn", "en", "byn"),
          std::make_tuple("tariff", "additional_info_prepaid", "en",
                          "(included %(included)s)"),
          std::make_tuple("tariff", "currency.uah", "en", "uah"),
          std::make_tuple("tariff", "currency_with_sign.default", "en",
                          "$SIGN$$VALUE$$CURRENCY$"),
          std::make_tuple("tariff", "currency_with_sign.byn", "en",
                          "$VALUE$ $SIGN$$CURRENCY$"),
          std::make_tuple("tariff", "detailed.hours", "en", "%(value).0f h"),
          std::make_tuple("tariff", "detailed.kilometer", "en", "km"),
          std::make_tuple("tariff", "detailed.kilometers", "en",
                          "%(value).0f km"),
          std::make_tuple("tariff", "detailed.kilometers_meters", "en",
                          "%(value).3f km"),
          std::make_tuple("tariff", "detailed.kilometers_per_hour", "en",
                          "%(value)s km/h"),
          std::make_tuple("tariff", "detailed.minute", "en", "min"),
          std::make_tuple("tariff", "detailed.hour", "en", "h"),
          std::make_tuple("tariff", "detailed.minutes", "en",
                          "%(value).0f min"),
          std::make_tuple("tariff", "detailed.seconds", "en", "%(value).0f s"),
          std::make_tuple("tariff", "group_name.free_route_with_city_name",
                          "en", "City (%(city)s)"),
          std::make_tuple("tariff", "details_tariff.dispatch", "en", "pickup"),
          std::make_tuple("tariff", "details_tariff.time_prepaid", "en",
                          "%(time)s min included"),
          std::make_tuple("tariff", "details_tariff.distance_prepaid", "en",
                          "%(distance)s km included"),
          std::make_tuple("tariff", "details_tariff.time_paid", "en",
                          "thereafter %(price_with_currency)s/min"),
          std::make_tuple("tariff", "details_tariff.distance_paid", "en",
                          "thereafter %(price_with_currency)s/km"),
          std::make_tuple("tariff", "details_tariff.distance_and_time_paid",
                          "en",
                          "thereafter %(distance_price_with_currency)s/km and "
                          "%(time_price_with_currency)s/min"),
          std::make_tuple("tariff",
                          "details_tariff.transfer_price_range_with_currency",
                          "en", "from at %(min_price_with_currency)s"),
          std::make_tuple("tariff",
                          "details_tariff.transfer_icon_range_with_currency",
                          "en", "from %(min_price_with_currency)s"),
          std::make_tuple("tariff", "details_tariff.to_pattern", "en",
                          "ride %(to_city)s"),
          std::make_tuple("tariff", "interval.day", "en", "Day"),
          std::make_tuple("tariff", "interval_description", "en",
                          "%(minimal_price)s"),
          std::make_tuple("tariff", "name.comfort", "en", "Comfort"),
          std::make_tuple("tariff", "name.econom", "en", "Econom"),
          std::make_tuple("tariff", "routestats.description.calculated", "en",
                          "%(price_with_currency)s"),
          std::make_tuple("tariff", "routestats.description.included_nothing",
                          "en", "from %(price_with_currency)s"),
          std::make_tuple("tariff", "routestats.description.included_N_min_km",
                          "en",
                          "%(price_with_currency)s for the first "
                          "%(included_min)d min and %(included_km)d km"),
          std::make_tuple("tariff", "routestats.description.included_1_min",
                          "en", "%(price_with_currency)s for the first minute"),
          std::make_tuple(
              "tariff", "routestats.description.included_N_min", "en",
              "%(price_with_currency)s for the first %(included_min)d min"),
          std::make_tuple("tariff", "routestats.description.included_1_km",
                          "en", "%(price_with_currency)s for the first km"),
          std::make_tuple(
              "tariff", "routestats.description.included_N_km", "en",
              "%(price_with_currency)s for the first %(included_km)d km"),
          std::make_tuple("tariff",
                          "routestats.description.transfer_to_pattern", "en",
                          "%(to_city)s — from %(price_with_currency)s"),
          std::make_tuple("tariff", "service_name.animaltransport", "en",
                          "animaltransport"),
          std::make_tuple("tariff", "service_name.bicycle", "en", "bicycle"),
          std::make_tuple("tariff", "service_name.childchair", "en",
                          "childchair"),
          std::make_tuple("tariff", "service_name.childchair.booster", "en",
                          "booster"),
          std::make_tuple("tariff", "service_name.conditioner", "en",
                          "conditioner"),
          std::make_tuple("tariff", "service_name.free_waiting", "en",
                          "free waiting"),
          std::make_tuple("tariff", "service_name.luggage", "en", "luggage"),
          std::make_tuple("tariff", "service_name.meeting_arriving", "en",
                          "meeting arriving"),
          std::make_tuple("tariff", "service_name.no_smoking", "en",
                          "no smoking"),
          std::make_tuple("tariff", "service_name.paid_dispatch.meter", "en",
                          "Suburban pickup fee"),
          std::make_tuple("tariff", "service_name.paid_waiting", "en",
                          "Paid waiting (not included in minimum fare!)"),
          std::make_tuple("tariff", "service_name.paid_waiting_as_ride", "en",
                          "further wait time is metered according to the "
                          "selected service class"),
          std::make_tuple("tariff", "service_name.ski", "en", "ski"),
          std::make_tuple("tariff", "service_name.taximeter.meter", "en",
                          "Fare"),
          std::make_tuple("tariff", "service_name.taximeter.meter_inside_area",
                          "en", "Fare %(area)s"),
          std::make_tuple("tariff",
                          "service_name.taximeter.meter_inside_area_additional",
                          "en", "Fare %(area)s (extra)"),
          std::make_tuple("tariff", "service_name.taximeter.meter_next_after_n",
                          "en", "Then (above %(included)s)"),
          std::make_tuple("tariff",
                          "service_name.taximeter.meter_next_inside_area", "en",
                          "Thereafter %(area)s"),
          std::make_tuple("tariff", "service_name.taximeter.min_price", "en",
                          "Minimum cost of ride"),
          std::make_tuple("tariff", "service_name.taximeter.min_price_included",
                          "en", "Starting fare (%(included)s included)"),
          std::make_tuple("tariff", "service_name.taximeter.once_price", "en",
                          "Getting into taxi"),
          std::make_tuple("tariff", "service_name.waiting_in_transit", "en",
                          "waiting in transit"),
          std::make_tuple("tariff", "service_name.universal", "en",
                          "universal"),
          std::make_tuple("tariff", "transfer_from_to", "en",
                          "%(from)s - %(to)s"),
          std::make_tuple("tariff", "workday_interval_description", "en",
                          "workdays from %(from)s to %(to)s"),
          std::make_tuple("tariff", "interval.dayoff", "en", "Weekend pricing"),
          std::make_tuple("tariff", "dayoff_interval_description", "en",
                          "weekends from %(from)s to %(to)s"),
          std::make_tuple("tariff", "service_name.childchair_moscow", "en",
                          "Child safety seat"),
          std::make_tuple("tariff", "service_name.compact_transfer", "en",
                          "Pickup %(once)s, then %(distance)s and %(time)s"),
          std::make_tuple(
              "tariff",
              "service_name.taximeter.min_price_included_distance_and_time",
              "en", "Starting fare (%(time)s and %(distance)s included)"),
          std::make_tuple(
              "tariff",
              "service_name.taximeter.meter_next_inside_area_additional", "en",
              "Thereafter %(area)s (additional)"),
          std::make_tuple(
              "tariff", "service_name.taximeter.meter_next_after_n_inside_area",
              "en", "Thereafter (after %(included)s %(area)s)"),
          std::make_tuple("tariff", "service_name.childchair_moscow.booster",
                          "en", "Booster seat"),
          std::make_tuple("tariff", "interval.night", "en",
                          "Nighttime pricing"),
          std::make_tuple("tariff", "name.business", "en", "business"),
          std::make_tuple("tariff", "name.minivan", "en", "Minivan"),
          std::make_tuple("tariff", "name.comfortplus", "en", "Comfort+"),
          std::make_tuple("tariff", "comment.default", "en",
                          "A taxi company may charge additional fees. Please "
                          "contact the taxi company for details"),
          std::make_tuple("tariff", "currency_sign.rub", "en", "\u20BD"),
          std::make_tuple("tariff", "round.minute", "en", "%(value).0f min"),
          std::make_tuple("tariff", "round.tens_minutes", "en",
                          "%(value).0f min"),
          std::make_tuple("tariff", "round.almost_hour", "en",
                          "%(value).0f min"),
          std::make_tuple("tariff", "round.hours", "en", "%(value).0f h"),
          std::make_tuple("tariff", "round.hours_mintes", "en",
                          "%(hours).0f h %(minutes).0f min"),
          std::make_tuple("tariff", "round.days", "en", "%(value).0f d"),
          std::make_tuple("tariff", "round.days_hours", "en",
                          "%(days).0f d %(hours).0f h"),
          std::make_tuple("tariff", "round.few_meters", "en", "10 m"),
          std::make_tuple("tariff", "round.tens_meters", "en", "%(value).0f m"),
          std::make_tuple("tariff", "round.hundreds_meters", "en",
                          "%(value).0f m"),
          std::make_tuple("tariff", "round.kilometers", "en", "%(value).0f km"),
          std::make_tuple("tariff", "round.detailed.kilometer", "en", "km"),

          std::make_tuple("geoareas", "svo", "en", "Sheremetyevo Airport"),
          std::make_tuple("geoareas", "ekb", "en", "Ekb"),
          std::make_tuple("geoareas", "city", "en", "City"),
          std::make_tuple("geoareas", "dme", "en", "Domodedovo Airport"),
          std::make_tuple("geoareas", "vko", "en", "Vnukovo Airport"),
          std::make_tuple("geoareas", "suburb", "en", "Suburbs"),
          std::make_tuple("geoareas", "from_airport", "en", "From airport"),
          std::make_tuple("geoareas", "to_airport", "en", "To airport"),
          std::make_tuple("geoareas", "airport", "en", "Airport"),

          std::make_tuple(
              "client_messages", "mainscreen.description_econom", "en",
              "Hyundai Solaris, Kia Rio, Ford Focus, Renault Fluence"),
          std::make_tuple(
              "client_messages", "mainscreen.description_business", "en",
              "Škoda Rapid, Hyundai Solaris, Peugeot 408, Chevrolet Cruze"),

          std::make_tuple(
              "client_messages", "taxiontheway.paid_waiting_cost_message", "en",
              "%(final_cost_with_currency)s for the trip and %(waiting_cost)s "
              "for %(waiting_time)s min. waiting"),

          std::make_tuple(
              "taximeter_backend_driver_messages", "alert_warning_wait", "en",
              "You need to be at least %s meters closer to the pickup point "
              "before you can change your status"),

          std::make_tuple("taximeter_driver_messages", "full_work_index", "en",
                          "%s of %s"),
      };

  void Load() {
    for (const auto& i : fixture) {
      data_[std::get<0>(i)][std::get<1>(i)].emplace(
          std::get<2>(i), l10n::ConvertToTemplate(std::get<3>(i)));
    }
  }

  kskeymap data_;

 public:
  MockTranslations(bool with_preloaded_values = true)
      : l10n::MainTranslations{{}} {
    if (with_preloaded_values) Load();
  }

  void LoadFromJSON(const std::string& name, const Json::Value& val) {
    for (const auto el : val) {
      const auto id = el["_id"];
      const auto& cond = el["values"];
      for (const auto& v : cond) {
        if (v.isMember("conditions")) {
          const auto& z = v["conditions"];
          if (z.isMember("locale")) {
            const auto& l = z["locale"];
            if (l.isMember("language")) {
              const auto& lang = l["language"];
              if (lang.asString() == "en") {
                data_[name][id.asString()].emplace(
                    lang.asString(),
                    l10n::ConvertToTemplate(v["value"].asString()));
              }
            }
          }
        }
      }
    }
  };

  const ff::TextTemplate& getTemplate(
      const std::string& keyset, const std::string& key,
      const std::string& locale, const int /*count*/ = 1,
      const std::string& /*fallback_locale*/ = "RU") const override {
    try {
      return data_.at(keyset).at(key).at(locale);
    } catch (const std::out_of_range& ex) {
      printf("not found %s: %s: %s\n", keyset.c_str(), key.c_str(),
             locale.c_str());
      throw l10n::NotFound(ex.what());
    }
  }

  std::string get(
      const std::string& keyset, const std::string& key,
      const std::string& locale, const int count = 1,
      const std::string& /*fallback_locale*/ = "RU") const override {
    return getTemplate(keyset, key, locale, count).Original();
  }

  ~MockTranslations() {}
};
