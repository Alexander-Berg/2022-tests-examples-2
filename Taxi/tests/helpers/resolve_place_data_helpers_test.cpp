#include "helpers/resolve_place_data_helpers.hpp"
#include <userver/utest/utest.hpp>

namespace testing {
using eats_restapp_communications::helpers::GetRecipientsFromPlacesInfo;
using eats_restapp_communications::helpers::
    GetRecipientsFromPlacesInfoAndPartners;

using LocaleSettings =
    eats_restapp_communications::types::locale::LocaleSettings;
using ConfigLocaleSettings =
    ::taxi_config::eats_restapp_communications_locale_settings::
        EatsRestappCommunicationsLocaleSettings;

using eats_restapp_communications::types::email::Email;
using eats_restapp_communications::types::partner_access::PartnerAccess;
using eats_restapp_communications::types::partner_access::PartnerId;

struct ResolvePlaceDataTest : public Test {
  static clients::eats_core::Place GetPlace(std::string email, std::string name,
                                            std::int64_t place_id,
                                            std::string address,
                                            std::string country_code) {
    clients::eats_core::Place place;
    place.country_code = country_code;
    place.emails = {{"email_type1", "e1@mail.ru"},
                    {"email_type2", "e2@mail.ru"},
                    {"email_we_need", email}};
    place.id = place_id;
    place.address = {"", "", "", "", address};
    place.name = name;
    return place;
  }
  static clients::eats_partners::StoredUser GetPartner(
      std::int64_t id, std::vector<std::int64_t> places) {
    clients::eats_partners::StoredUser partner;
    partner.id = id;
    partner.name = "name" + std::to_string(id);
    partner.email = "email" + std::to_string(id);
    partner.places = places;
    partner.country_code = "ru";
    return partner;
  }

  static LocaleSettings MakeLocaleSettings() {
    return LocaleSettings(ConfigLocaleSettings{"ru", {}});
  };
};

TEST_F(ResolvePlaceDataTest, test_data) {
  auto place1 = GetPlace("email1", "name1", 1, "address1", "ru");
  auto result = GetRecipientsFromPlacesInfo(
      {place1}, {std::string("email_we_need")}, MakeLocaleSettings(), {});
  ASSERT_EQ(result.size(), 1);
  ASSERT_FALSE(result.begin()->name.has_value());
  ASSERT_EQ(result.begin()->email.GetUnderlying(), "email1");
  ASSERT_EQ(result.begin()->locale.value(), "ru");

  ASSERT_EQ(result.begin()->place_ids.size(), 1);
  ASSERT_EQ(*result.begin()->place_ids.begin(), 1);

  ASSERT_EQ(result.begin()->places.size(), 1);
  ASSERT_EQ(*result.begin()->places.begin(), "name1 (address1)");
}

TEST_F(ResolvePlaceDataTest, test_grouping_by_email) {
  auto place1 = GetPlace("equal_email", "name1", 1, "address1", "ru");
  auto place2 = GetPlace("equal_email", "name2", 2, "address2", "ru");
  auto place3 = GetPlace("not_equal_email", "name3", 3, "address3", "ru");

  auto result = GetRecipientsFromPlacesInfo({place1, place2, place3},
                                            {std::string("email_we_need")},
                                            MakeLocaleSettings(), {});
  ASSERT_EQ(result.size(), 2);
  bool is_contains_equal = false, is_contains_not_equal = false;
  for (auto& email : result) {
    if (email.email.GetUnderlying() == "equal_email") {
      is_contains_equal = true;
      ASSERT_FALSE(email.name.has_value());
      ASSERT_EQ(email.locale.value(), "ru");

      ASSERT_EQ(email.place_ids.size(), 2);
      ASSERT_TRUE(email.place_ids.count(1) == 1);
      ASSERT_TRUE(email.place_ids.count(2) == 1);

      ASSERT_EQ(email.places.size(), 2);
      ASSERT_TRUE(email.places.count("name1 (address1)") == 1);
      ASSERT_TRUE(email.places.count("name2 (address2)") == 1);
    }
    if (email.email.GetUnderlying() == "not_equal_email") {
      is_contains_not_equal = true;
      ASSERT_FALSE(email.name.has_value());
      ASSERT_EQ(email.locale.value(), "ru");

      ASSERT_EQ(email.place_ids.size(), 1);
      ASSERT_TRUE(email.place_ids.count(3) == 1);

      ASSERT_EQ(email.places.size(), 1);
      ASSERT_TRUE(email.places.count("name3 (address3)") == 1);
    }
  }
  ASSERT_TRUE(is_contains_equal);
  ASSERT_TRUE(is_contains_not_equal);
}

TEST_F(ResolvePlaceDataTest,
       test_data_get_recipients_from_places_info_and_partners) {
  auto place1 = GetPlace("email", "name", 1, "address", "en");
  auto partenr1 = GetPartner(1, {1, 2});
  auto result = GetRecipientsFromPlacesInfoAndPartners(
      {place1}, {partenr1},
      {PartnerAccess{PartnerId(1), {1, 2}, {"permission1", "permission2"}}},
      {"permission1"}, MakeLocaleSettings(), {});
  ASSERT_EQ(result.size(), 1);
  ASSERT_EQ(result.begin()->name.value(), "name1");
  ASSERT_EQ(result.begin()->email.GetUnderlying(), "email1");
  ASSERT_EQ(result.begin()->locale.value(), "ru");

  ASSERT_EQ(result.begin()->place_ids.size(), 1);
  ASSERT_EQ(*result.begin()->place_ids.begin(), 1);

  ASSERT_EQ(result.begin()->places.size(), 1);
  ASSERT_EQ(*result.begin()->places.begin(), "name (address)");
}

TEST_F(
    ResolvePlaceDataTest,
    test_data_get_recipients_from_places_info_and_partners_grouping_by_email) {
  auto place1 = GetPlace("equal_email", "place_name1", 1, "address1", "ru");
  auto place2 = GetPlace("equal_email", "place_name2", 2, "address2", "en");
  auto place3 = GetPlace("not_equal_email", "place_name3", 3, "address3", "en");
  auto place5 = GetPlace("not_equal_email", "place_name5", 5, "address5", "en");
  auto partenr1 = GetPartner(1, {1, 2});
  auto partenr2 = GetPartner(2, {1, 3});
  auto partenr3 = GetPartner(3, {1, 2, 3});
  auto partenr4 = GetPartner(3, {1, 2, 3});
  std::vector<PartnerAccess> partner_access = {
      {PartnerId(1), {1, 2}, {"permission1", "permission2"}},
      {PartnerId(2), {3}, {"permission1", "permission2"}},
      {PartnerId(3), {1, 2, 3, 4}, {"permission1", "permission2"}},
      {PartnerId(4), {1, 2, 3, 4}, {"permission1"}}};

  auto result = GetRecipientsFromPlacesInfoAndPartners(
      {place1, place2, place3, place5},
      {partenr1, partenr2, partenr3, partenr4}, partner_access,
      {"permission1", "permission2"}, MakeLocaleSettings(), {});
  ASSERT_EQ(result.size(), 3);
  for (auto& email : result) {
    if (email.email.GetUnderlying() == "email1") {
      ASSERT_EQ(email.name.value(), "name1");
      ASSERT_EQ(email.locale.value(), "ru");

      ASSERT_EQ(email.place_ids.size(), 2);
      ASSERT_TRUE(email.place_ids.count(1) == 1);
      ASSERT_TRUE(email.place_ids.count(2) == 1);

      ASSERT_EQ(email.places.size(), 2);
      ASSERT_TRUE(email.places.count("place_name1 (address1)") == 1);
      ASSERT_TRUE(email.places.count("place_name2 (address2)") == 1);
    }
    if (email.email.GetUnderlying() == "email2") {
      ASSERT_EQ(email.name.value(), "name2");
      ASSERT_EQ(email.locale.value(), "ru");

      ASSERT_EQ(email.place_ids.size(), 1);
      ASSERT_TRUE(email.place_ids.count(3) == 1);

      ASSERT_EQ(email.places.size(), 1);
      ASSERT_TRUE(email.places.count("place_name3 (address3)") == 1);
    }
    if (email.email.GetUnderlying() == "email3") {
      ASSERT_EQ(email.name.value(), "name3");
      ASSERT_EQ(email.locale.value(), "ru");

      ASSERT_EQ(email.place_ids.size(), 3);
      ASSERT_TRUE(email.place_ids.count(1) == 1);
      ASSERT_TRUE(email.place_ids.count(2) == 1);
      ASSERT_TRUE(email.place_ids.count(3) == 1);

      ASSERT_EQ(email.places.size(), 3);
      ASSERT_TRUE(email.places.count("place_name1 (address1)") == 1);
      ASSERT_TRUE(email.places.count("place_name2 (address2)") == 1);
      ASSERT_TRUE(email.places.count("place_name3 (address3)") == 1);
    }
    ASSERT_FALSE(email.email.GetUnderlying() == "email4");
  }
}

}  // namespace testing
