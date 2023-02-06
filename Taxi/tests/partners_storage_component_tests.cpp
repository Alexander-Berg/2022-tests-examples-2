#include <gmock/gmock-actions.h>
#include <gmock/gmock-more-actions.h>
#include <gmock/gmock-spec-builders.h>
#include <userver/utest/utest.hpp>

#include <clients/eats-restapp-authorizer/client_gmock.hpp>
#include <clients/eats-vendor/client_gmock.hpp>
#include <clients/personal/client_gmock.hpp>
#include <components/partners_storage.hpp>
#include <utils/convert.hpp>
#include "access_control_mock.hpp"
#include "partners_storage_mock.hpp"
#include "roles_storage_mock.hpp"

namespace testing {

using ::eats_partners::models::partners_storage::Storage;
using AuthorizerClient = ::eats_partners::models::authorizer::Client;
using VendorClient = ::eats_partners::models::vendor::Client;
using PersonalClient = ::eats_partners::models::personal::Client;

namespace vendor_update =
    ::clients::eats_vendor::api_v1_server_users_partnerid::post;
namespace vendor_create = ::clients::eats_vendor::api_v1_server_users::post;
namespace vendor_delete =
    ::clients::eats_vendor::api_v1_server_users_partnerid::del;

struct PartnerStorageComponentTest : public Test {
  std::shared_ptr<StrictMock<PartnersStorageMock>> storage_mock;
  std::shared_ptr<StrictMock<clients::eats_restapp_authorizer::ClientGMock>>
      authorizer_gmock;
  std::shared_ptr<StrictMock<clients::eats_vendor::ClientGMock>> vendor_gmock;
  std::shared_ptr<AccessControlMock> access_control_mock;
  std::shared_ptr<StrictMock<RolesStoragePgMock>> roles_storage_mock;
  std::shared_ptr<StrictMock<clients::personal::ClientGMock>> personal_gmock;
  eats_partners::components::partners_storage::ComponentImpl component_impl;

  PartnerStorageComponentTest()
      : storage_mock(std::make_shared<StrictMock<PartnersStorageMock>>()),
        authorizer_gmock(
            std::make_shared<
                StrictMock<clients::eats_restapp_authorizer::ClientGMock>>()),
        vendor_gmock(
            std::make_shared<StrictMock<clients::eats_vendor::ClientGMock>>()),
        access_control_mock(std::make_shared<StrictMock<AccessControlMock>>()),
        roles_storage_mock(std::make_shared<StrictMock<RolesStoragePgMock>>()),
        personal_gmock(
            std::make_shared<StrictMock<clients::personal::ClientGMock>>()),
        component_impl(
            std::make_shared<Storage>(storage_mock),
            std::make_shared<AuthorizerClient>(*authorizer_gmock),
            std::make_shared<VendorClient>(*vendor_gmock), access_control_mock,
            std::make_shared<::eats_partners::models::roles::Storage>(
                roles_storage_mock),
            std::make_shared<PersonalClient>(*personal_gmock)) {}

  static partner::Info MakePartnerInfo() {
    partner::Info info;
    info.id = partner::Id{1};
    info.email = partner::Email{"aaa@aaa.com"};
    info.personal_email_id =
        eats_partners::types::email::PersonalEmailId{"aaa"};
    info.places = {11, 12, 13};
    info.timezone = "msk";
    info.is_fast_food = true;
    info.roles = {{1, "ROLE_OPERATOR", "operator role"}};
    info.country_code = "RU";
    info.partner_uuid = "2ed43ecd-815b-4ad9-add0-fb44a5de0ddd";
    return info;
  }

  static partner::InfoStorage MakePartnerInfoStorage() {
    partner::InfoStorage info;
    info.id = partner::Id{1};
    info.personal_email_id =
        eats_partners::types::email::PersonalEmailId{"aaa"};
    info.places = {11, 12, 13};
    info.timezone = "msk";
    info.is_fast_food = true;
    info.roles = {{1, "ROLE_OPERATOR", "operator role"}};
    info.country_code = "RU";
    info.partner_uuid = "2ed43ecd-815b-4ad9-add0-fb44a5de0ddd";
    return info;
  }

  static partner::UpdatePartnerInfo MakeUpdateInfo() {
    const auto info = MakePartnerInfo();
    partner::UpdatePartnerInfo update_info;
    update_info.id = info.id;
    update_info.email = info.email;
    update_info.places = info.places;
    update_info.timezone = info.timezone;
    update_info.is_fast_food = info.is_fast_food;
    update_info.roles = ::eats_partners::utils::convert::GetIds(info.roles);
    update_info.country_code = info.country_code;
    update_info.personal_email_id = info.personal_email_id;
    return update_info;
  }

  static partner::CreatePartnerInfo MakeCreateInfo() {
    const auto info = MakePartnerInfo();
    partner::CreatePartnerInfo create_info;
    create_info.id = info.id;
    create_info.email = info.email.value();
    create_info.places = info.places;
    create_info.timezone = info.timezone;
    create_info.is_fast_food = info.is_fast_food;
    create_info.roles = ::eats_partners::utils::convert::GetIds(info.roles);
    create_info.country_code = info.country_code;
    create_info.partner_uuid = info.partner_uuid;
    return create_info;
  }

  static vendor_update::Request MakeVendorUpdateRequest() {
    const auto update_info = MakeUpdateInfo();
    vendor_update::Request request;

    request.partnerid = update_info.id.GetUnderlying();
    if (update_info.email.has_value()) {
      request.body.email = update_info.email->GetUnderlying();
      request.body.name = update_info.email->GetUnderlying();
    }
    request.body.isfastfood = update_info.is_fast_food;
    request.body.countrycode = update_info.country_code;
    request.body.timezone = update_info.timezone;
    request.body.roles = update_info.roles;
    request.body.restaurants = update_info.places;
    return request;
  }

  static vendor_update::Response200 MakeVendorUpdateResponse() {
    const auto info = MakePartnerInfo();
    vendor_update::Response200 response200;

    response200.issuccess = true;
    response200.payload.id = info.id.GetUnderlying();
    response200.payload.email = info.email->GetUnderlying();
    response200.payload.name = info.email->GetUnderlying();
    response200.payload.restaurants = {info.places.begin(), info.places.end()};
    response200.payload.timezone = info.timezone;
    response200.payload.isfastfood = info.is_fast_food;
    response200.payload.countrycode = info.country_code;
    response200.payload.roles = {
        {info.roles[0].id, info.roles[0].title,
         clients::eats_vendor::Parse(
             info.roles[0].slug,
             formats::parse::To<clients::eats_vendor::RoleRole>())}};
    return response200;
  }

  static vendor_create::Request MakeVendorCreateRequest() {
    const auto create_info = MakeCreateInfo();
    vendor_create::Request request;

    request.body.name = create_info.email.GetUnderlying();
    request.body.email = create_info.email.GetUnderlying();
    request.body.isfastfood = create_info.is_fast_food;
    request.body.countrycode = create_info.country_code;
    request.body.timezone = create_info.timezone;
    request.body.roles = create_info.roles;
    request.body.restaurants = create_info.places;
    request.body.partneruuid = create_info.partner_uuid;
    return request;
  }

  static vendor_create::Response200 MakeVendorCreateResponse() {
    const auto info = MakePartnerInfo();
    vendor_create::Response200 response200;

    response200.issuccess = true;
    response200.payload.id = info.id.GetUnderlying();
    return response200;
  }

  static vendor_delete::Request MakeVendorDeleteRequest() {
    const auto info = MakePartnerInfo();
    vendor_delete::Request request;
    request.partnerid = info.id.GetUnderlying();
    return request;
  }

  static vendor_delete::Response200 MakeVendorDeleteResponse() {
    vendor_delete::Response200 response200;
    response200.issuccess = true;
    return response200;
  }

  static vendor_delete::Response400 MakeVendorDeleteError() {
    return vendor_delete::Response400{};
  }

  static std::exception MakeVendorDeleteInternalError() {
    return std::exception{};
  }
};

TEST_F(PartnerStorageComponentTest, check_call_personal_in_GetPartnerInfo) {
  const auto info = MakePartnerInfoStorage();
  EXPECT_CALL(*storage_mock, GetPartnerInfo(info.id, true))
      .WillOnce(Return(info));

  auto request_personal =
      clients::personal::v1_data_type_retrieve::post::Request{
          clients::personal::DataType::kEmails, {"aaa"}};
  auto personal_response =
      clients::personal::v1_data_type_retrieve::post::Response200{
          {"aaa", "aaa@aaa.com"}};

  EXPECT_CALL(*personal_gmock, V1DataTypeRetrieve(request_personal, _))
      .WillOnce(Return(personal_response));

  const auto result = component_impl.GetPartnerInfo(
      info.id, partner::GetInfoOptions{true, true});
  ASSERT_EQ("aaa@aaa.com", result->email);
}

TEST_F(PartnerStorageComponentTest,
       check_call_personal_in_GetPartnerInfo_without_personal_data) {
  const auto info = MakePartnerInfoStorage();
  EXPECT_CALL(*storage_mock, GetPartnerInfo(info.id, true))
      .WillOnce(Return(info));

  EXPECT_CALL(*personal_gmock, V1DataTypeRetrieve(_, _)).Times(0);

  const auto result = component_impl.GetPartnerInfo(
      info.id, partner::GetInfoOptions{true, false});
  ASSERT_EQ(1, result->id);
  ASSERT_EQ("", result->email);
}

TEST_F(PartnerStorageComponentTest,
       check_call_personal_in_false_GetPartnerInfo) {
  const auto info = MakePartnerInfoStorage();
  EXPECT_CALL(*storage_mock, GetPartnerInfo(info.id, true))
      .WillOnce(Return(info));

  auto request_personal =
      clients::personal::v1_data_type_retrieve::post::Request{
          clients::personal::DataType::kEmails, {"aaa"}};
  auto personal_response =
      clients::personal::v1_data_type_retrieve::post::Response200{
          {"aaa", "aaa@aaa.com"}};

  EXPECT_CALL(*personal_gmock, V1DataTypeRetrieve(request_personal, _))
      .WillOnce(Return(personal_response));

  const auto result = component_impl.GetPartnerInfo(
      info.id, partner::GetInfoOptions{true, true});
  ASSERT_EQ("aaa@aaa.com", result->email);
}

TEST_F(PartnerStorageComponentTest,
       check_call_personal_in_GetPartnerByInfo_with_off_email) {
  const auto info = MakePartnerInfoStorage();
  EXPECT_CALL(*storage_mock, GetPartnerInfo(info.id, true))
      .WillOnce(Return(info));

  auto request_personal =
      clients::personal::v1_data_type_retrieve::post::Request{
          clients::personal::DataType::kEmails, {"aaa"}};
  auto personal_response =
      clients::personal::v1_data_type_retrieve::post::Response200{
          {"aaa", "aaa@aaa.com"}};

  EXPECT_CALL(*personal_gmock, V1DataTypeRetrieve(request_personal, _))
      .WillOnce(Return(personal_response));

  const auto result = component_impl.GetPartnerInfo(
      info.id, partner::GetInfoOptions{true, true});
  ASSERT_EQ("aaa@aaa.com", result->email);
}

TEST_F(PartnerStorageComponentTest,
       check_call_personal_in_GetPartnerInfo_with_diff_email) {
  const auto info = MakePartnerInfoStorage();
  EXPECT_CALL(*storage_mock, GetPartnerInfo(info.id, true))
      .WillOnce(Return(info));

  auto request_personal =
      clients::personal::v1_data_type_retrieve::post::Request{
          clients::personal::DataType::kEmails, {"aaa"}};
  auto personal_response =
      clients::personal::v1_data_type_retrieve::post::Response200{
          {"aaa", "bbb@bbb.com"}};

  EXPECT_CALL(*personal_gmock, V1DataTypeRetrieve(request_personal, _))
      .WillOnce(Return(personal_response));

  const auto result = component_impl.GetPartnerInfo(
      info.id, partner::GetInfoOptions{true, true});
  ASSERT_EQ(result->email, "bbb@bbb.com");
}

TEST_F(PartnerStorageComponentTest,
       check_call_personal_in_GetPartnerInfo_no_email) {
  auto info = MakePartnerInfoStorage();
  EXPECT_CALL(*storage_mock, GetPartnerInfo(info.id, true))
      .WillOnce(Return(info));

  auto request_personal =
      clients::personal::v1_data_type_retrieve::post::Request{
          clients::personal::DataType::kEmails, {"aaa"}};
  auto personal_response =
      clients::personal::v1_data_type_retrieve::post::Response404{
          {"404", "Email not found"}};

  EXPECT_CALL(*personal_gmock, V1DataTypeRetrieve(request_personal, _))
      .WillOnce(Throw(personal_response));

  const auto result = component_impl.GetPartnerInfo(
      info.id, partner::GetInfoOptions{true, true});
  ASSERT_FALSE(result->email.has_value());
}

TEST_F(PartnerStorageComponentTest, logout_success) {
  clients::eats_restapp_authorizer::v1_session_unset::post::Request request;
  request.body.token = "000";

  clients::eats_restapp_authorizer::v1_session_unset::post::Response200
      response200;

  const clients::eats_restapp_authorizer::CommandControl control{};

  EXPECT_CALL(*authorizer_gmock, V1SessionUnset(request, control))
      .WillOnce(Return(response200));

  ASSERT_TRUE(component_impl.Logout(partner::Token{"000"}));
}

TEST_F(PartnerStorageComponentTest, logout_false) {
  clients::eats_restapp_authorizer::v1_session_unset::post::Request request;
  request.body.token = "111";

  clients::eats_restapp_authorizer::v1_session_unset::post::Response404
      response404;

  const clients::eats_restapp_authorizer::CommandControl control{};

  EXPECT_CALL(*authorizer_gmock, V1SessionUnset(request, control))
      .WillOnce(Throw(response404));

  ASSERT_FALSE(component_impl.Logout(partner::Token{"111"}));
}

using ::eats_partners::types::action_tokens::ActionToken;

TEST_F(PartnerStorageComponentTest,
       PasswordRequestReset_should_not_generate_link_if_not_found_in_db) {
  partner::Email email{"aaa@aaa.com"};
  {
    // GetPartnerByLogin return nullopt
    namespace client =
        clients::eats_restapp_authorizer::internal_partner_search::post;
    EXPECT_CALL(*authorizer_gmock, InternalPartnerSearch(_, _))
        .WillOnce(Return(client::Response200()));
  }
  {
    // Not find in personal
    namespace client = clients::personal::v1_data_type_find::post;
    EXPECT_CALL(*personal_gmock, V1DataTypeFind(_, _))
        .WillOnce(Throw(client::Response404()));
  }
  auto link = component_impl.PasswordRequestReset(
      email, {"link", "token", "email"}, false);
  ASSERT_FALSE(link.has_value());
}

TEST_F(PartnerStorageComponentTest,
       PasswordRequestReset_should_generate_link_if_found_in_db) {
  partner::Info info;
  partner::InfoStorage info_s;
  info.id = partner::Id{1};
  info_s.id = partner::Id{1};
  info.email = partner::Email{"aaa@aaa.com"};
  {
    InSequence seq;
    {
      // GetPartnerByLogin return id
      namespace client =
          clients::eats_restapp_authorizer::internal_partner_search::post;
      client::Response200 response;
      response.partners.push_back(clients::eats_restapp_authorizer::CredsPair{
          info.id.GetUnderlying(), info.email.value().GetUnderlying()});
      EXPECT_CALL(*authorizer_gmock, InternalPartnerSearch(_, _))
          .WillOnce(Return(response));
    }
    EXPECT_CALL(*storage_mock, GetPartnerInfo(info.id, true))
        .WillOnce(Return(info_s));
    {
      // Not find in personal
      namespace client = clients::personal::v1_data_type_retrieve::post;
      client::Response200 response{};
      response.id = "aaa@aaa.com_id";
      response.value = "aaa@aaa.com";
      EXPECT_CALL(*personal_gmock, V1DataTypeRetrieve(_, _))
          .WillOnce(Return(response));
    }
    EXPECT_CALL(*storage_mock, GenerateToken(info.id))
        .WillOnce(Return(ActionToken{info.id, "tttoken"}));
  }

  auto link = component_impl.PasswordRequestReset(
      info.email.value(), {"link", "token", "email"}, true);
  ASSERT_TRUE(link.has_value());
  ASSERT_EQ(link.value(), "link?token=tttoken&email=aaa%40aaa.com");
}

TEST_F(
    PartnerStorageComponentTest,
    PasswordRequestReset_should_not_generate_link_if_not_found_in_db_and_not_found_in_vendor) {
  partner::Info info;
  info.id = partner::Id{1};
  info.email = partner::Email{"aaa@aaa.com"};
  {
    InSequence seq;
    namespace client = clients::eats_vendor::api_v1_server_users_search::post;
    client::Response200 response200;
    response200.issuccess = true;

    {
      // GetPartnerByLogin return nullopt
      namespace client =
          clients::eats_restapp_authorizer::internal_partner_search::post;
      EXPECT_CALL(*authorizer_gmock, InternalPartnerSearch(_, _))
          .WillOnce(Return(client::Response200()));
    }
    {
      // Not find in personal
      namespace client = clients::personal::v1_data_type_find::post;
      EXPECT_CALL(*personal_gmock, V1DataTypeFind(_, _))
          .WillOnce(Throw(client::Response404()));
    }

    EXPECT_CALL(*vendor_gmock, ApiV1ServerUsersSearch(_, _))
        .WillOnce(Return(response200));
  }

  auto link = component_impl.PasswordRequestReset(
      info.email.value(), {"link", "token", "email"}, true);
  ASSERT_FALSE(link.has_value());
}

TEST_F(
    PartnerStorageComponentTest,
    PasswordRequestReset_should_generate_link_and_create_partner_if_not_found_in_db_but_found_in_vendor) {
  partner::Info info;
  partner::InfoStorage info_s;
  info.id = partner::Id{1};
  info_s.id = partner::Id{1};
  info.email = partner::Email{"aaa@aaa.com"};
  InSequence seq;

  {
    // GetPartnerByLogin return nullopt
    namespace client =
        clients::eats_restapp_authorizer::internal_partner_search::post;
    client::Response200 response{};
    response.partners =
        std::vector<clients::eats_restapp_authorizer::CredsPair>{};
    EXPECT_CALL(*authorizer_gmock, InternalPartnerSearch(_, _))
        .WillOnce(Return(response));
  }
  {
    // Not find in personal
    namespace client = clients::personal::v1_data_type_find::post;
    EXPECT_CALL(*personal_gmock, V1DataTypeFind(_, _))
        .WillOnce(Throw(client::Response404()));
  }
  //  partner = CreatePartnerFromVendorInfo(vendor_->GetPartner(email));
  {
    namespace client = clients::eats_vendor::api_v1_server_users_search::post;
    client::Response200 response200;
    response200.issuccess = true;
    clients::eats_vendor::StoredUser stored;
    stored.id = info.id.GetUnderlying();
    stored.email = info.email->GetUnderlying();
    response200.payload.emplace_back(std::move(stored));

    EXPECT_CALL(*vendor_gmock, ApiV1ServerUsersSearch(_, _))
        .WillOnce(Return(response200));
  }
  {
    auto personal_id =
        eats_partners::types::email::PersonalEmailId{"aaa@aaa.com_id"};
    namespace client = clients::personal::v1_data_type_store::post;
    client::Response200 response;
    response.id = personal_id.GetUnderlying();
    response.value = info.email->GetUnderlying();
    EXPECT_CALL(*personal_gmock, V1DataTypeStore(_, _))
        .Times(2)
        .WillRepeatedly(Return(response));
    info.personal_email_id = personal_id;
    info_s.personal_email_id = personal_id;
  }
  {
    // GetPartnerByLogin return nullopt
    namespace client =
        clients::eats_restapp_authorizer::internal_partner_search::post;
    client::Response200 response{};
    response.partners =
        std::vector<clients::eats_restapp_authorizer::CredsPair>{};
    EXPECT_CALL(*authorizer_gmock, InternalPartnerSearch(_, _))
        .WillOnce(Return(response));
  }
  EXPECT_CALL(*storage_mock, CreatePartner(_)).WillOnce(Return(info.id));
  std::vector<::eats_partners::types::role::Role> roles{};
  std::vector<::eats_partners::types::role_template::RoleTemplate>
      roles_templates{};
  EXPECT_CALL(*roles_storage_mock, GetRoleByIds(_)).WillOnce(Return(roles));
  EXPECT_CALL(*roles_storage_mock, GetRolesTemplatesBySlugs(_))
      .WillOnce(Return(roles_templates));
  EXPECT_CALL(*access_control_mock, CreateUser(_, _));
  EXPECT_CALL(*storage_mock, GetPartnerInfo(info.id, true))
      .WillOnce(Return(info_s));
  {
    auto personal_id =
        eats_partners::types::email::PersonalEmailId{"aaa@aaa.com_id"};
    namespace client = clients::personal::v1_data_type_retrieve::post;
    client::Response200 response;
    response.id = personal_id.GetUnderlying();
    response.value = info.email->GetUnderlying();
    EXPECT_CALL(*personal_gmock, V1DataTypeRetrieve(_, _))
        .WillOnce(Return(response));
  }
  EXPECT_CALL(*storage_mock, GenerateToken(info.id))
      .WillOnce(Return(ActionToken{info.id, "tttoken"}));

  auto link = component_impl.PasswordRequestReset(
      info.email.value(), {"link", "token", "email"}, true);
  ASSERT_TRUE(link.has_value());
  ASSERT_EQ(link.value(), "link?token=tttoken&email=aaa%40aaa.com");
}

TEST_F(PartnerStorageComponentTest, true_PasswordReset) {
  auto partner_id = partner::Id{1};
  auto token = partner::Token{"000"};
  auto email = partner::Email{"aaa@aaa.com"};
  size_t cost = 12;
  size_t length_password = 6;

  partner::Info info = MakePartnerInfo();
  partner::InfoStorage info_s = MakePartnerInfoStorage();
  info.email = email;

  using std::chrono_literals::operator""s;
  const auto expired_date = utils::datetime::Now() - 604800s;

  {
    namespace client =
        clients::eats_restapp_authorizer::internal_partner_search::post;
    client::Response200 response{};
    response.partners.push_back(
        {partner_id.GetUnderlying(), email.GetUnderlying()});
    EXPECT_CALL(*authorizer_gmock, InternalPartnerSearch(_, _))
        .WillOnce(Return(response));
    EXPECT_CALL(*authorizer_gmock, InternalPartnerSetCredentials(_, _))
        .WillOnce(
            Return(clients::eats_restapp_authorizer::
                       internal_partner_set_credentials::post::Response204{}));
  }

  EXPECT_CALL(*storage_mock, GetPartnerInfo(partner_id, true))
      .WillOnce(Return(info_s));
  {
    namespace client = clients::personal::v1_data_type_retrieve::post;
    client::Response200 response;
    response.id = info.personal_email_id->GetUnderlying();
    response.value = info.email->GetUnderlying();
    EXPECT_CALL(*personal_gmock, V1DataTypeRetrieve(_, _))
        .WillOnce(Return(response));
  }

  EXPECT_CALL(*storage_mock, IsTokenForResetPasswordValid(
                                 partner_id, token,
                                 storages::postgres::TimePointTz{expired_date}))
      .WillOnce(Return(true));

  clients::eats_restapp_authorizer::v1_session_unset_by_partner::post::Request
      request;
  request.body.partner_id = partner_id.GetUnderlying();

  clients::eats_restapp_authorizer::v1_session_unset_by_partner::post::
      Response200 response200;

  const clients::eats_restapp_authorizer::CommandControl control{};

  EXPECT_CALL(*authorizer_gmock, V1SessionUnsetByPartner(request, control))
      .WillOnce(Return(response200));

  auto password = component_impl.PasswordReset(
      email, token, cost, length_password, expired_date, false);

  ASSERT_TRUE(password.has_value());
  ASSERT_EQ(password->size(), length_password);
}

TEST_F(PartnerStorageComponentTest, false_PasswordReset_not_info) {
  auto partner_id = partner::Id{1};
  auto token = partner::Token{"000"};
  auto email = partner::Email{"aaa@aaa.com"};
  size_t cost = 12;
  size_t length_password = 6;

  std::optional<partner::Info> info;
  std::optional<partner::InfoStorage> info_s;

  using std::chrono_literals::operator""s;
  const auto expired_date = utils::datetime::Now() - 604800s;

  {
    namespace client =
        clients::eats_restapp_authorizer::internal_partner_search::post;
    client::Response200 response{};
    response.partners.push_back(
        {partner_id.GetUnderlying(), email.GetUnderlying()});
    EXPECT_CALL(*authorizer_gmock, InternalPartnerSearch(_, _))
        .WillOnce(Return(response));
  }

  EXPECT_CALL(*storage_mock, GetPartnerInfo(partner_id, true))
      .WillOnce(Return(info_s));

  EXPECT_CALL(*storage_mock, IsTokenForResetPasswordValid(
                                 partner_id, token,
                                 storages::postgres::TimePointTz{expired_date}))
      .Times(0);
  auto password = component_impl.PasswordReset(
      email, token, cost, length_password, expired_date, false);

  ASSERT_FALSE(password.has_value());
}

TEST_F(PartnerStorageComponentTest, false_PasswordReset_token_invalid) {
  auto partner_id = partner::Id{1};
  auto token = partner::Token{"000"};
  auto email = partner::Email{"aaa@aaa.com"};
  size_t cost = 12;
  size_t length_password = 6;

  InSequence inSequence;
  {
    namespace client =
        clients::eats_restapp_authorizer::internal_partner_search::post;
    client::Response200 response{};
    response.partners.push_back(
        {partner_id.GetUnderlying(), email.GetUnderlying()});
    EXPECT_CALL(*authorizer_gmock, InternalPartnerSearch(_, _))
        .WillOnce(Return(response));
  }

  using std::chrono_literals::operator""s;
  const auto expired_date = utils::datetime::Now() - 604800s;

  partner::Info info = MakePartnerInfo();
  partner::InfoStorage info_s = MakePartnerInfoStorage();

  EXPECT_CALL(*storage_mock, GetPartnerInfo(info.id, true))
      .WillOnce(Return(info_s));
  {
    namespace client = clients::personal::v1_data_type_retrieve::post;
    client::Response200 response;
    response.id = info.personal_email_id->GetUnderlying();
    response.value = info.email->GetUnderlying();
    EXPECT_CALL(*personal_gmock, V1DataTypeRetrieve(_, _))
        .WillOnce(Return(response));
  }
  EXPECT_CALL(*storage_mock, IsTokenForResetPasswordValid(
                                 partner_id, token,
                                 storages::postgres::TimePointTz{expired_date}))
      .WillOnce(Return(false));
  EXPECT_CALL(*authorizer_gmock, V1SessionUnsetByPartner(_, _)).Times(0);

  auto password = component_impl.PasswordReset(
      email, token, cost, length_password, expired_date, false);

  ASSERT_FALSE(password.has_value());
}

TEST_F(PartnerStorageComponentTest, true_PasswordReset_with_update_vendor) {
  auto token = partner::Token{"000"};
  auto email = partner::Email{"aaa@aaa.com"};
  size_t cost = 12;
  size_t length_password = 6;

  using std::chrono_literals::operator""s;
  const auto expired_date = utils::datetime::Now() - 604800s;

  partner::Info info = MakePartnerInfo();
  partner::InfoStorage info_s = MakePartnerInfoStorage();
  info.country_code = "KZ";
  info_s.country_code = "KZ";
  info_s.personal_email_id =
      eats_partners::types::email::PersonalEmailId{"aaa"};
  InSequence inSequence;
  {
    namespace client =
        clients::eats_restapp_authorizer::internal_partner_search::post;
    client::Response200 response{};
    response.partners.push_back(
        {info.id.GetUnderlying(), info.email->GetUnderlying()});
    EXPECT_CALL(*authorizer_gmock, InternalPartnerSearch(_, _))
        .WillOnce(Return(response));
  }
  EXPECT_CALL(*storage_mock, GetPartnerInfo(info.id, true))
      .WillOnce(Return(info_s));
  {
    namespace client = clients::personal::v1_data_type_retrieve::post;
    client::Response200 response;
    response.id = info.personal_email_id->GetUnderlying();
    response.value = info.email->GetUnderlying();
    EXPECT_CALL(*personal_gmock, V1DataTypeRetrieve(_, _))
        .WillOnce(Return(response));
  }
  EXPECT_CALL(*storage_mock, IsTokenForResetPasswordValid(
                                 info.id, token,
                                 storages::postgres::TimePointTz{expired_date}))
      .WillOnce(Return(true));
  {
    namespace client =
        clients::eats_restapp_authorizer::v1_session_unset_by_partner::post;
    client::Response200 response200{};
    EXPECT_CALL(*authorizer_gmock, V1SessionUnsetByPartner(_, _))
        .WillOnce(Return(response200));
  }

  {
    namespace client =
        clients::eats_vendor::api_v1_server_users_partnerid::post;
    client::Response200 response200;
    response200.issuccess = true;
    EXPECT_CALL(*vendor_gmock, ApiV1ServerUsersPartneridPost(_, _))
        .WillOnce(Return(response200));
  }
  EXPECT_CALL(*authorizer_gmock, InternalPartnerSetCredentials(_, _))
      .WillOnce(
          Return(clients::eats_restapp_authorizer::
                     internal_partner_set_credentials::post::Response204{}));
  auto password = component_impl.PasswordReset(
      email, token, cost, length_password, expired_date, true);

  ASSERT_TRUE(password.has_value());
  ASSERT_EQ(password->size(), length_password);
}

TEST_F(PartnerStorageComponentTest,
       UpdatePartner_on_nonexisting_user_without_vendor_update) {
  const auto update_info = MakeUpdateInfo();

  auto res = component_impl.UpdatePartner(update_info, std::nullopt, 10, false);
  ASSERT_FALSE(res.has_value());
}

TEST_F(PartnerStorageComponentTest,
       UpdatePartner_on_existing_user_without_vendor_update) {
  const auto info = MakePartnerInfo();
  const auto info_s = MakePartnerInfoStorage();
  const auto update_info = MakeUpdateInfo();
  {
    namespace client = clients::personal::v1_data_type_store::post;
    client::Response200 response;
    response.id = info.personal_email_id.value().GetUnderlying();
    response.value = info.email->GetUnderlying();
    EXPECT_CALL(*personal_gmock, V1DataTypeStore(_, _))
        .WillOnce(Return(response));
  }
  std::optional<eats_partners::types::partner::PasswordHash> password{};
  EXPECT_CALL(*storage_mock, UpdatePartner(update_info))
      .WillOnce(Return(info_s));
  std::vector<::eats_partners::types::role_template::RoleTemplate>
      roles_templates{};
  EXPECT_CALL(*roles_storage_mock, GetRolesTemplatesBySlugs(_))
      .WillOnce(Return(roles_templates));
  EXPECT_CALL(*access_control_mock, UpdateUser(_, _));
  EXPECT_CALL(*authorizer_gmock, PlaceAccessReset(_, _)).Times(1);

  auto res = component_impl.UpdatePartner(update_info, info, 10, false);
  ASSERT_TRUE(res.has_value());
  ASSERT_EQ(*res, info);
}

TEST_F(PartnerStorageComponentTest,
       UpdatePartner_on_nonexisting_user_with_vendor_update) {
  const auto info = MakePartnerInfo();
  const auto info_s = MakePartnerInfoStorage();
  const auto update_info = MakeUpdateInfo();
  {
    InSequence seq;
    auto request = MakeVendorUpdateRequest();
    const auto response200 = MakeVendorUpdateResponse();
    const auto create_info = MakeCreateInfo();

    {
      EXPECT_CALL(*vendor_gmock, ApiV1ServerUsersPartneridPost(request, _))
          .WillOnce(Return(response200));
    }

    {
      namespace client = clients::personal::v1_data_type_store::post;
      client::Response200 response;
      response.id = info.personal_email_id->GetUnderlying();
      response.value = info.email->GetUnderlying();
      EXPECT_CALL(*personal_gmock, V1DataTypeStore(_, _))
          .Times(2)
          .WillRepeatedly(Return(response));
    }
    {
      // GetPartnerByLogin return nullopt
      namespace client =
          clients::eats_restapp_authorizer::internal_partner_search::post;
      client::Response200 response{};
      response.partners =
          std::vector<clients::eats_restapp_authorizer::CredsPair>{};
      EXPECT_CALL(*authorizer_gmock, InternalPartnerSearch(_, _))
          .WillOnce(Return(response));
    }
    EXPECT_CALL(*storage_mock, CreatePartner(_)).WillOnce(Return(info.id));
    std::vector<::eats_partners::types::role::Role> roles{};
    std::vector<::eats_partners::types::role_template::RoleTemplate>
        roles_templates{};
    EXPECT_CALL(*roles_storage_mock, GetRoleByIds(_)).WillOnce(Return(roles));
    EXPECT_CALL(*roles_storage_mock, GetRolesTemplatesBySlugs(_))
        .WillOnce(Return(roles_templates));
    EXPECT_CALL(*access_control_mock, CreateUser(_, _));
    EXPECT_CALL(*storage_mock, GetPartnerInfo(info.id, true))
        .WillOnce(Return(info_s));
    {
      namespace client = clients::personal::v1_data_type_retrieve::post;
      client::Response200 response;
      response.id = info.personal_email_id->GetUnderlying();
      response.value = info.email->GetUnderlying();
      EXPECT_CALL(*personal_gmock, V1DataTypeRetrieve(_, _))
          .WillOnce(Return(response));
    }
  }

  auto res = component_impl.UpdatePartner(update_info, std::nullopt, 10, true);
  ASSERT_TRUE(res.has_value());
  ASSERT_EQ(*res, info);
}

TEST_F(PartnerStorageComponentTest,
       UpdatePartner_on_existing_user_with_vendor_update) {
  const auto info = MakePartnerInfo();
  const auto info_s = MakePartnerInfoStorage();
  const auto update_info = MakeUpdateInfo();
  {
    namespace client = clients::personal::v1_data_type_store::post;
    client::Response200 response;
    response.id = info.personal_email_id->GetUnderlying();
    response.value = info.email->GetUnderlying();
    EXPECT_CALL(*personal_gmock, V1DataTypeStore(_, _))
        .WillOnce(Return(response));
  }
  {
    InSequence seq;
    auto request = MakeVendorUpdateRequest();
    const auto response200 = MakeVendorUpdateResponse();
    EXPECT_CALL(*vendor_gmock, ApiV1ServerUsersPartneridPost(request, _))
        .WillOnce(Return(response200));
    EXPECT_CALL(*storage_mock, UpdatePartner(update_info))
        .WillOnce(Return(info_s));
    std::vector<::eats_partners::types::role_template::RoleTemplate>
        roles_templates{};
    EXPECT_CALL(*roles_storage_mock, GetRolesTemplatesBySlugs(_))
        .WillOnce(Return(roles_templates));
    EXPECT_CALL(*access_control_mock, UpdateUser(_, _));
    EXPECT_CALL(*authorizer_gmock, PlaceAccessReset(_, _)).Times(1);
  }

  auto res = component_impl.UpdatePartner(update_info, info, 10, true);
  ASSERT_TRUE(res.has_value());
  ASSERT_EQ(*res, info);
}

TEST_F(PartnerStorageComponentTest,
       CreatePartner_on_nonexisting_user_without_vendor_update) {
  const auto info = MakePartnerInfo();
  const auto info_s = MakePartnerInfoStorage();
  const auto create_info = MakeCreateInfo();
  InSequence seq;
  {
    namespace client = clients::personal::v1_data_type_store::post;
    client::Response200 response;
    response.id = info.personal_email_id->GetUnderlying();
    response.value = info.email->GetUnderlying();
    EXPECT_CALL(*personal_gmock, V1DataTypeStore(_, _))
        .WillOnce(Return(response));
  }
  {
    // GetPartnerByLogin return nullopt
    namespace client =
        clients::eats_restapp_authorizer::internal_partner_search::post;
    client::Response200 response{};
    response.partners =
        std::vector<clients::eats_restapp_authorizer::CredsPair>{};
    EXPECT_CALL(*authorizer_gmock, InternalPartnerSearch(_, _))
        .WillOnce(Return(response));
  }
  {
    EXPECT_CALL(*storage_mock, CreatePartner(_)).WillOnce(Return(info.id));
    std::vector<::eats_partners::types::role::Role> roles{};
    std::vector<::eats_partners::types::role_template::RoleTemplate>
        roles_templates{};
    EXPECT_CALL(*roles_storage_mock, GetRoleByIds(_)).WillOnce(Return(roles));
    EXPECT_CALL(*roles_storage_mock, GetRolesTemplatesBySlugs(_))
        .WillOnce(Return(roles_templates));
    EXPECT_CALL(*access_control_mock, CreateUser(_, _));
  }

  auto res = component_impl.CreatePartner(create_info, 10, false);
  ASSERT_TRUE(res.has_value());
  ASSERT_EQ(*res, info.id);
}

TEST_F(PartnerStorageComponentTest,
       CreatePartner_on_existing_user_without_vendor_update) {
  const auto info = MakePartnerInfo();
  const auto info_s = MakePartnerInfoStorage();
  const auto create_info = MakeCreateInfo();
  const auto update_info = MakeUpdateInfo();
  InSequence seq;
  {
    namespace client = clients::personal::v1_data_type_store::post;
    client::Response200 response;
    response.id = info.personal_email_id->GetUnderlying();
    response.value = info.email->GetUnderlying();
    EXPECT_CALL(*personal_gmock, V1DataTypeStore(_, _))
        .WillOnce(Return(response));
  }
  {
    // GetPartnerByLogin return find
    namespace client =
        clients::eats_restapp_authorizer::internal_partner_search::post;
    client::Response200 response{};
    response.partners =
        std::vector<clients::eats_restapp_authorizer::CredsPair>{};
    response.partners.push_back(clients::eats_restapp_authorizer::CredsPair{
        info.id.GetUnderlying(), info.email.value().GetUnderlying()});
    EXPECT_CALL(*authorizer_gmock, InternalPartnerSearch(_, _))
        .WillOnce(Return(response));
  }
  {
    EXPECT_CALL(*storage_mock, GetPartnerInfo(info.id, true))
        .WillOnce(Return(info_s));
  }
  {
    namespace client = clients::personal::v1_data_type_retrieve::post;
    client::Response200 response;
    response.id = info.personal_email_id->GetUnderlying();
    response.value = info.email->GetUnderlying();
    EXPECT_CALL(*personal_gmock, V1DataTypeRetrieve(_, _))
        .WillOnce(Return(response));
  }
  EXPECT_CALL(*storage_mock, UnblockPartner(info.id)).Times(1);
  EXPECT_CALL(*storage_mock, UpdatePartner(_)).WillOnce(Return(info_s));
  std::vector<::eats_partners::types::role_template::RoleTemplate>
      roles_templates{};
  EXPECT_CALL(*roles_storage_mock, GetRolesTemplatesBySlugs(_))
      .WillOnce(Return(roles_templates));
  EXPECT_CALL(*access_control_mock, UpdateUser(_, _));
  EXPECT_CALL(*authorizer_gmock, PlaceAccessReset(_, _)).Times(1);

  auto res = component_impl.CreatePartner(create_info, 10, false);
  ASSERT_TRUE(res.has_value());
  ASSERT_EQ(*res, info.id);
}

TEST_F(PartnerStorageComponentTest, CreatePartner_with_vendor_update) {
  const auto info = MakePartnerInfo();
  const auto create_info = MakeCreateInfo();
  InSequence seq;
  {
    namespace client = clients::personal::v1_data_type_store::post;
    client::Response200 response;
    response.id = info.personal_email_id->GetUnderlying();
    response.value = info.email->GetUnderlying();
    EXPECT_CALL(*personal_gmock, V1DataTypeStore(_, _))
        .WillOnce(Return(response));
  }
  {
    const auto request = MakeVendorCreateRequest();
    const auto response200 = MakeVendorCreateResponse();
    EXPECT_CALL(*vendor_gmock, ApiV1ServerUsers(request, _))
        .WillOnce(Return(response200));
  }
  {
    // GetPartnerByLogin return nullopt
    namespace client =
        clients::eats_restapp_authorizer::internal_partner_search::post;
    client::Response200 response{};
    EXPECT_CALL(*authorizer_gmock, InternalPartnerSearch(_, _))
        .WillOnce(Return(response));
  }
  EXPECT_CALL(*storage_mock, CreatePartner(_)).WillOnce(Return(info.id));

  std::vector<::eats_partners::types::role::Role> roles{};
  std::vector<::eats_partners::types::role_template::RoleTemplate>
      roles_templates{};
  EXPECT_CALL(*roles_storage_mock, GetRoleByIds(_)).WillOnce(Return(roles));
  EXPECT_CALL(*roles_storage_mock, GetRolesTemplatesBySlugs(_))
      .WillOnce(Return(roles_templates));
  EXPECT_CALL(*access_control_mock, CreateUser(_, _));

  auto res = component_impl.CreatePartner(create_info, 10, true);
  ASSERT_TRUE(res.has_value());
  ASSERT_EQ(*res, info.id);
}

TEST_F(PartnerStorageComponentTest, BlockPartner_without_vendor_delete) {
  const auto info = MakePartnerInfo();

  EXPECT_CALL(*storage_mock, BlockPartner(info.id)).WillOnce(Return(true));

  auto res = component_impl.BlockPartner(info.id, false);
  ASSERT_TRUE(res);
}

TEST_F(PartnerStorageComponentTest, BlockPartner_with_vendor_delete) {
  const auto info = MakePartnerInfo();
  {
    InSequence seq;
    const auto request = MakeVendorDeleteRequest();
    const auto response200 = MakeVendorDeleteResponse();

    EXPECT_CALL(*vendor_gmock, ApiV1ServerUsersPartneridDelete(request, _))
        .WillOnce(Return(response200));
    EXPECT_CALL(*storage_mock, BlockPartner(info.id)).WillOnce(Return(true));
  }

  auto res = component_impl.BlockPartner(info.id, true);
  ASSERT_TRUE(res);
}

TEST_F(PartnerStorageComponentTest, BlockPartner_with_vendor_delete_error) {
  const auto info = MakePartnerInfo();
  const auto request = MakeVendorDeleteRequest();
  const auto error = MakeVendorDeleteError();

  EXPECT_CALL(*vendor_gmock, ApiV1ServerUsersPartneridDelete(request, _))
      .WillOnce(Throw(error));

  ASSERT_THROW(component_impl.BlockPartner(info.id, true),
               ::eats_partners::models::vendor::ClientError400);
}

TEST_F(PartnerStorageComponentTest,
       BlockPartner_with_vendor_delete_internal_error) {
  const auto info = MakePartnerInfo();
  const auto request = MakeVendorDeleteRequest();
  const auto error = MakeVendorDeleteInternalError();

  EXPECT_CALL(*vendor_gmock, ApiV1ServerUsersPartneridDelete(request, _))
      .WillOnce(Throw(error));

  ASSERT_THROW(component_impl.BlockPartner(info.id, true),
               ::eats_partners::models::vendor::ClientError500);
}

}  // namespace testing

namespace clients::eats_restapp_authorizer::v1_session_create::post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.body.email, rhs.body.partner_id) ==
         std::tie(rhs.body.email, rhs.body.partner_id);
}
}  // namespace clients::eats_restapp_authorizer::v1_session_create::post

namespace clients::eats_restapp_authorizer::v1_session_unset::post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return lhs.body.token == rhs.body.token;
}
}  // namespace clients::eats_restapp_authorizer::v1_session_unset::post

namespace clients::eats_restapp_authorizer::v1_session_unset_by_partner::post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return lhs.body.partner_id == rhs.body.partner_id;
}
// clang-format off
}  // namespace clients::eats_restapp_authorizer::v1_session_unset_by_partner::post
// clang-format on

namespace clients::codegen {
inline bool operator==(const CommandControl& lhs, const CommandControl& rhs) {
  return std::tie(lhs.retries, lhs.timeout) ==
         std::tie(rhs.retries, rhs.timeout);
}
}  // namespace clients::codegen

namespace clients::eats_vendor::api_v1_server_users::post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.body.email, lhs.body.name, lhs.body.partneruuid,
                  lhs.body.isfastfood, lhs.body.countrycode, lhs.body.timezone,
                  lhs.body.password, lhs.body.restaurants, lhs.body.roles) ==
         std::tie(rhs.body.email, rhs.body.name, rhs.body.partneruuid,
                  rhs.body.isfastfood, rhs.body.countrycode, rhs.body.timezone,
                  rhs.body.password, rhs.body.restaurants, rhs.body.roles);
}
}  // namespace clients::eats_vendor::api_v1_server_users::post

namespace clients::eats_vendor::api_v1_server_users_partnerid::post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.partnerid, lhs.body.email, lhs.body.name,
                  lhs.body.isfastfood, lhs.body.countrycode, lhs.body.timezone,
                  lhs.body.password, lhs.body.restaurants, lhs.body.roles) ==
         std::tie(rhs.partnerid, rhs.body.email, rhs.body.name,
                  rhs.body.isfastfood, rhs.body.countrycode, rhs.body.timezone,
                  rhs.body.password, rhs.body.restaurants, rhs.body.roles);
}
}  // namespace clients::eats_vendor::api_v1_server_users_partnerid::post

namespace clients::eats_vendor::api_v1_server_users_partnerid::del {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return lhs.partnerid == rhs.partnerid;
}
}  // namespace clients::eats_vendor::api_v1_server_users_partnerid::del

namespace clients::personal::v1_data_type_retrieve::post {
inline bool operator==(const Request& l, const Request& r) {
  return std::tie(l.data_type, l.body.id, l.body.primary_replica) ==
         std::tie(r.data_type, r.body.id, r.body.primary_replica);
}
}  // namespace clients::personal::v1_data_type_retrieve::post

namespace clients::personal::v1_data_type_bulk_retrieve::post {
inline bool operator==(const Request& l, const Request& r) {
  return std::tie(l.data_type, l.body.items, l.body.primary_replica) ==
         std::tie(r.data_type, r.body.items, r.body.primary_replica);
}
}  // namespace clients::personal::v1_data_type_bulk_retrieve::post
