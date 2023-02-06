#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

#include <clients/eats-catalog-storage/client_gmock.hpp>
#include <clients/eats-core/client_gmock.hpp>
#include <clients/eats-partners/client_gmock.hpp>
#include <clients/eats-place-subscriptions/client_gmock.hpp>
#include <clients/personal/client_gmock.hpp>
#include <components/resolve_recipient_data.hpp>

namespace testing {
using eats_restapp_communications::components::resolve_recipient_data::
    ComponentImpl;
using LocaleSettings =
    eats_restapp_communications::types::locale::LocaleSettings;
using ConfigLocaleSettings =
    ::taxi_config::eats_restapp_communications_locale_settings::
        EatsRestappCommunicationsLocaleSettings;
using SpecificRecipientsSettings = eats_restapp_communications::types::
    specific_recipient::SpecificRecipientsSettings;
using ConfigSpecificRecipientsSettings =
    ::taxi_config::eats_restapp_communications_specific_recipients_settings::
        EatsRestappCommunicationsSpecificRecipientsSettings;
using PartnerId = eats_restapp_communications::types::partner::Id;
using PartnerishToken =
    eats_restapp_communications::types::partnerish::UuidToken;
using ResolvingError =
    eats_restapp_communications::components::resolve_recipient_data::Error;
using eats_restapp_communications::types::email::Email;
using PartnerAccessType =
    eats_restapp_communications::types::partner_access::PartnerAccess;
using StoredUser = clients::eats_partners::StoredUser;
using StoredLoginIdsByPlace =
    eats_restapp_communications::types::telegram::StoredLoginIdsByPlace;
using TelegramRecipients =
    eats_restapp_communications::types::telegram::Recipients;
using TelegramLogin = eats_restapp_communications::types::telegram::Login;

struct ResolveDataComponentTest : public Test {
  std::shared_ptr<StrictMock<clients::eats_partners::ClientGMock>>
      partners_mock =
          std::make_shared<StrictMock<clients::eats_partners::ClientGMock>>();
  std::shared_ptr<StrictMock<clients::eats_core::ClientGMock>> core_mock =
      std::make_shared<StrictMock<clients::eats_core::ClientGMock>>();
  std::shared_ptr<StrictMock<clients::personal::ClientGMock>> personal_mock =
      std::make_shared<StrictMock<clients::personal::ClientGMock>>();
  std::shared_ptr<StrictMock<clients::eats_place_subscriptions::ClientGMock>>
      subscriptions_mock = std::make_shared<
          StrictMock<clients::eats_place_subscriptions::ClientGMock>>();
  std::shared_ptr<StrictMock<clients::eats_catalog_storage::ClientGMock>>
      catalog_mock = std::make_shared<
          StrictMock<clients::eats_catalog_storage::ClientGMock>>();
  struct AccessPartnerFilterMock {
    std::vector<PartnerAccessType> Filter(
        const std::vector<int64_t>& /* partner_ids*/,
        const std::vector<int64_t>& /* place_ids*/,
        const std::vector<std::string>& /* permissions*/) const {
      return {};
    }
  };
  AccessPartnerFilterMock access_partner_filter_mock;

  ComponentImpl<AccessPartnerFilterMock> component;
  ResolveDataComponentTest()
      : component(*partners_mock, *core_mock, *personal_mock,
                  *subscriptions_mock, *catalog_mock,
                  access_partner_filter_mock) {}

  static LocaleSettings MakeLocaleSettings() {
    return LocaleSettings(ConfigLocaleSettings{"ru", {}});
  }
  static SpecificRecipientsSettings MakeSpecificRecipientsSettings() {
    ConfigSpecificRecipientsSettings settings;
    settings.recipient_types = {
        {"special_recipient", "mail@mail.ru", "Recipient Name", "ru"}};
    return SpecificRecipientsSettings(settings);
  }
};

TEST_F(ResolveDataComponentTest, get_partner_info) {
  PartnerId partner_id{111111};
  {
    namespace client = clients::eats_partners::internal_partners_v1_info::get;
    client::Request request;
    request.partner_id = partner_id.GetUnderlying();
    request.with_blocked = false;
    client::Response200 response200;
    EXPECT_CALL(*partners_mock, InternalPartnersV1Info(request, _))
        .WillOnce(Return(response200));
  }
  component.GetData(partner_id, MakeLocaleSettings(), {});
}
TEST_F(ResolveDataComponentTest, get_partnerish_info) {
  PartnerishToken partnerish_token{"111111"};
  {
    namespace client = clients::eats_partners::
        ns_4_0_restapp_front_partners_v1_login_partnerish_info::post;
    client::Request request{partnerish_token.GetUnderlying()};
    client::Response200 response200;
    EXPECT_CALL(*partners_mock,
                Ns40RestappFrontPartnersV1LoginPartnerishInfo(request, _))
        .WillOnce(Return(response200));
  }
  component.GetData(partnerish_token, MakeLocaleSettings(), {});
}
TEST_F(ResolveDataComponentTest, get_info_by_email) {
  Email email("user@m.ru");
  {
    namespace client =
        clients::eats_partners::internal_partners_v1_search::post;
    client::Request request;
    request.limit = 1;
    request.body.email = email.GetUnderlying();

    EXPECT_CALL(*partners_mock, InternalPartnersV1Search(request, _)).Times(1);
  }
  component.GetData(email, MakeLocaleSettings(), {});
}
TEST_F(ResolveDataComponentTest, get_info_by_specific_user) {
  auto user = "special_recipient";
  auto result = component.GetData(user, MakeSpecificRecipientsSettings());
  ASSERT_EQ(result[0].email, "mail@mail.ru");
  ASSERT_EQ(result[0].name, "Recipient Name");
  ASSERT_EQ(result[0].locale, "ru");
}
TEST_F(ResolveDataComponentTest, get_info_by_place_ids) {
  std::vector<std::int64_t> place_ids{1};
  {
    namespace client_core = clients::eats_core::v1_places_info::post;
    client_core::Request request_core;
    request_core.body.place_ids = place_ids;
    EXPECT_CALL(*core_mock, V1PlacesInfo(request_core, _)).Times(1);
  }
  component.GetData(place_ids, {std::string("email_type")},
                    MakeLocaleSettings(), {});
}
TEST_F(ResolveDataComponentTest, get_info_by_place_ids_for_all_partners) {
  std::vector<std::int64_t> place_ids{1};
  std::vector<StoredUser> partners = {
      StoredUser{1, "name", "email", false, {}, {1}, false, "ru", {}, {}, {}}};
  std::vector<std::string> permissions = {"permission"};
  {
    namespace client_core = clients::eats_core::v1_places_info::post;
    client_core::Request request_core;
    request_core.body.place_ids = place_ids;
    EXPECT_CALL(*core_mock, V1PlacesInfo(request_core, _)).Times(1);

    namespace client_partner =
        clients::eats_partners::internal_partners_v1_search::post;
    client_partner::Request request;
    request.limit = 100;
    request.body.places = place_ids;

    EXPECT_CALL(*partners_mock, InternalPartnersV1Search(request, _)).Times(1);
  }
  component.GetData(place_ids, permissions, MakeLocaleSettings(), {}, {});
}

TEST_F(ResolveDataComponentTest, get_telegram_info_full_data_no_logins) {
  const std::vector<StoredLoginIdsByPlace> logins_by_places{
      StoredLoginIdsByPlace{1, {"id1"}},
      StoredLoginIdsByPlace{2, {"id2", "id1"}},
      StoredLoginIdsByPlace{3, {"id3"}}};
  const std::vector<int64_t> place_ids{1, 2, 3};
  {
    namespace personal = clients::personal::v1_data_type_bulk_retrieve::post;
    personal::Request request;
    request.data_type = clients::personal::DataType::kTelegramLogins;
    request.body.items.push_back(
        clients::personal::BulkRetrieveRequestItem{"id1"});
    request.body.items.push_back(
        clients::personal::BulkRetrieveRequestItem{"id2"});
    request.body.items.push_back(
        clients::personal::BulkRetrieveRequestItem{"id3"});
    personal::Response200 response200;
    EXPECT_CALL(*personal_mock, V1DataTypeBulkRetrieve(request, _))
        .WillOnce(Return(response200));
  }
  const auto result = component.GetTelegramData(logins_by_places, true);
  ASSERT_TRUE(result.empty());
}

TEST_F(ResolveDataComponentTest, get_telegram_info_full_data_no_info) {
  const std::vector<StoredLoginIdsByPlace> logins_by_places{
      StoredLoginIdsByPlace{1, {"id1"}},
      StoredLoginIdsByPlace{2, {"id2", "id1"}},
      StoredLoginIdsByPlace{3, {"id3"}}};
  const std::vector<int64_t> place_ids{1, 2, 3};
  {
    namespace personal = clients::personal::v1_data_type_bulk_retrieve::post;
    personal::Request request;
    request.data_type = clients::personal::DataType::kTelegramLogins;
    request.body.items.push_back(
        clients::personal::BulkRetrieveRequestItem{"id1"});
    request.body.items.push_back(
        clients::personal::BulkRetrieveRequestItem{"id2"});
    request.body.items.push_back(
        clients::personal::BulkRetrieveRequestItem{"id3"});
    personal::Response200 response200;
    response200.items.push_back(
        clients::personal::BulkRetrieveResponseItem{"id2", "@login2"});
    EXPECT_CALL(*personal_mock, V1DataTypeBulkRetrieve(request, _))
        .WillOnce(Return(response200));
  }
  {
    namespace catalog = clients::eats_catalog_storage::
        internal_eats_catalog_storage_v1_places_retrieve_by_ids::post;
    catalog::Request request;
    request.body.place_ids = place_ids;
    request.body.projection.emplace(
        clients::eats_catalog_storage::PlacesProjection::kName);
    request.body.projection.emplace(
        clients::eats_catalog_storage::PlacesProjection::kAddress);
    request.body.projection.emplace(
        clients::eats_catalog_storage::PlacesProjection::kType);
    request.body.projection.emplace(
        clients::eats_catalog_storage::PlacesProjection::kRegion);
    catalog::Response200 response200;
    EXPECT_CALL(*catalog_mock,
                InternalEatsCatalogStorageV1PlacesRetrieveByIds(request, _))
        .WillOnce(Return(response200));
  }
  const auto result = component.GetTelegramData(logins_by_places, true);
  ASSERT_TRUE(result.empty());
}

TEST_F(ResolveDataComponentTest, get_telegram_info_full_data) {
  const std::vector<StoredLoginIdsByPlace> logins_by_places{
      StoredLoginIdsByPlace{1, {"id1"}},
      StoredLoginIdsByPlace{2, {"id2", "id1"}},
      StoredLoginIdsByPlace{3, {"id3"}}};
  const std::vector<int64_t> place_ids{1, 2, 3};
  const std::vector<TelegramRecipients> expected{
      TelegramRecipients{2,
                         "Name2",
                         "Address2",
                         "marketplace",
                         "Asia/Dushanbe",
                         {TelegramLogin{"login2"}},
                         {"id2", "id1"}}};
  {
    namespace personal = clients::personal::v1_data_type_bulk_retrieve::post;
    personal::Request request;
    request.data_type = clients::personal::DataType::kTelegramLogins;
    request.body.items.push_back(
        clients::personal::BulkRetrieveRequestItem{"id1"});
    request.body.items.push_back(
        clients::personal::BulkRetrieveRequestItem{"id2"});
    request.body.items.push_back(
        clients::personal::BulkRetrieveRequestItem{"id3"});
    personal::Response200 response200;
    response200.items.push_back(
        clients::personal::BulkRetrieveResponseItem{"id2", "@login2"});
    EXPECT_CALL(*personal_mock, V1DataTypeBulkRetrieve(request, _))
        .WillOnce(Return(response200));
  }
  {
    namespace catalog = clients::eats_catalog_storage::
        internal_eats_catalog_storage_v1_places_retrieve_by_ids::post;
    catalog::Request request;
    request.body.place_ids = place_ids;
    request.body.projection.emplace(
        clients::eats_catalog_storage::PlacesProjection::kName);
    request.body.projection.emplace(
        clients::eats_catalog_storage::PlacesProjection::kAddress);
    request.body.projection.emplace(
        clients::eats_catalog_storage::PlacesProjection::kType);
    request.body.projection.emplace(
        clients::eats_catalog_storage::PlacesProjection::kRegion);
    catalog::Response200 response200;
    clients::eats_catalog_storage::Address address;
    clients::eats_catalog_storage::Region region;
    clients::eats_catalog_storage::PlacesItem place;
    place.id = 1;
    place.name = "Name1";
    address.short_ = "Address1";
    place.address = address;
    region.time_zone = "Europe/Moscow";
    place.region = region;
    place.type = clients::eats_catalog_storage::PlaceType::kNative;
    response200.places.push_back(place);
    place.id = 2;
    place.name = "Name2";
    address.short_ = "Address2";
    place.address = address;
    region.time_zone = "Asia/Dushanbe";
    place.region = region;
    place.type = clients::eats_catalog_storage::PlaceType::kMarketplace;
    response200.places.push_back(place);
    EXPECT_CALL(*catalog_mock,
                InternalEatsCatalogStorageV1PlacesRetrieveByIds(request, _))
        .WillOnce(Return(response200));
  }
  const auto result = component.GetTelegramData(logins_by_places, true);
  ASSERT_EQ(result, expected);
}

TEST_F(ResolveDataComponentTest, get_telegram_info_not_full_data_no_logins) {
  const std::vector<StoredLoginIdsByPlace> logins_by_places{
      StoredLoginIdsByPlace{1, {"id1"}},
      StoredLoginIdsByPlace{2, {"id2", "id1"}},
      StoredLoginIdsByPlace{3, {"id3"}}};
  const std::vector<int64_t> place_ids{1, 2, 3};
  {
    namespace personal = clients::personal::v1_data_type_bulk_retrieve::post;
    personal::Request request;
    request.data_type = clients::personal::DataType::kTelegramLogins;
    request.body.items.push_back(
        clients::personal::BulkRetrieveRequestItem{"id1"});
    request.body.items.push_back(
        clients::personal::BulkRetrieveRequestItem{"id2"});
    request.body.items.push_back(
        clients::personal::BulkRetrieveRequestItem{"id3"});
    personal::Response200 response200;
    EXPECT_CALL(*personal_mock, V1DataTypeBulkRetrieve(request, _))
        .WillOnce(Return(response200));
  }
  const auto result = component.GetTelegramData(logins_by_places, false);
  ASSERT_TRUE(result.empty());
}

TEST_F(ResolveDataComponentTest, get_telegram_info_not_full_data) {
  const std::vector<StoredLoginIdsByPlace> logins_by_places{
      StoredLoginIdsByPlace{1, {"id1"}},
      StoredLoginIdsByPlace{2, {"id2", "id1"}},
      StoredLoginIdsByPlace{3, {"id3"}}};
  const std::vector<int64_t> place_ids{1, 2, 3};
  const std::vector<TelegramRecipients> expected{
      TelegramRecipients{
          2, "", "", {}, {}, {TelegramLogin{"login2"}}, {"id2", "id1"}},
      TelegramRecipients{
          3, "", "", {}, {}, {TelegramLogin{"login3"}}, {"id3"}}};
  {
    namespace personal = clients::personal::v1_data_type_bulk_retrieve::post;
    personal::Request request;
    request.data_type = clients::personal::DataType::kTelegramLogins;
    request.body.items.push_back(
        clients::personal::BulkRetrieveRequestItem{"id1"});
    request.body.items.push_back(
        clients::personal::BulkRetrieveRequestItem{"id2"});
    request.body.items.push_back(
        clients::personal::BulkRetrieveRequestItem{"id3"});
    personal::Response200 response200;
    response200.items.push_back(
        clients::personal::BulkRetrieveResponseItem{"id2", "@login2"});
    response200.items.push_back(
        clients::personal::BulkRetrieveResponseItem{"id3", "login3@"});
    EXPECT_CALL(*personal_mock, V1DataTypeBulkRetrieve(request, _))
        .WillOnce(Return(response200));
  }
  const auto result = component.GetTelegramData(logins_by_places, false);
  ASSERT_EQ(result, expected);
}

}  // namespace testing

namespace clients::eats_partners {
namespace internal_partners_v1_info::get {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return lhs.partner_id == rhs.partner_id;
}
}  // namespace internal_partners_v1_info::get
namespace ns_4_0_restapp_front_partners_v1_login_partnerish_info::post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return lhs.body.uuid == rhs.body.uuid;
}
}  // namespace ns_4_0_restapp_front_partners_v1_login_partnerish_info::post
namespace internal_partners_v1_search::post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return lhs.body == rhs.body;
}
}  // namespace internal_partners_v1_search::post
}  // namespace clients::eats_partners

namespace clients::eats_core {
namespace v1_places_info::post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return lhs.body.place_ids.size() == rhs.body.place_ids.size();
}
}  // namespace v1_places_info::post
}  // namespace clients::eats_core

namespace clients::personal {
namespace v1_data_type_bulk_retrieve::post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  if (lhs.data_type != rhs.data_type) {
    return false;
  }
  if (lhs.body.items.size() != rhs.body.items.size()) {
    return false;
  }
  std::unordered_set<std::string> lhs_items;
  for (const auto& li : lhs.body.items) {
    lhs_items.insert(li.id);
  }
  for (const auto& ri : rhs.body.items) {
    if (lhs_items.end() == lhs_items.find(ri.id)) {
      return false;
    }
  }
  return true;
}
}  // namespace v1_data_type_bulk_retrieve::post
}  // namespace clients::personal

namespace clients::eats_catalog_storage {
namespace internal_eats_catalog_storage_v1_places_retrieve_by_ids::post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.body.place_ids, lhs.body.projection) ==
         std::tie(rhs.body.place_ids, rhs.body.projection);
}
}  // namespace internal_eats_catalog_storage_v1_places_retrieve_by_ids::post
}  // namespace clients::eats_catalog_storage

namespace eats_restapp_communications::types::telegram {
inline bool operator==(const Recipients& lhs, const Recipients& rhs) {
  return std::tie(lhs.place_id, lhs.place_name, lhs.place_address,
                  lhs.delivery_type, lhs.timezone, lhs.logins, lhs.login_ids) ==
         std::tie(rhs.place_id, rhs.place_name, rhs.place_address,
                  rhs.delivery_type, rhs.timezone, rhs.logins, rhs.login_ids);
}
}  // namespace eats_restapp_communications::types::telegram
