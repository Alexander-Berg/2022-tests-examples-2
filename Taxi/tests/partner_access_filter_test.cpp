#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

#include <clients/eats-restapp-authorizer/client_gmock.hpp>
#include <components/partner_access_filter.hpp>

namespace testing {
using eats_restapp_communications::components::partner_access_filter::
    ComponentImpl;
using PartnerId = eats_restapp_communications::types::partner::Id;
using PartnerAccess =
    eats_restapp_communications::types::partner_access::PartnerAccess;

struct PartnerAccessFilterTest : public Test {
  std::shared_ptr<StrictMock<clients::eats_restapp_authorizer::ClientGMock>>
      authorizer_mock = std::make_shared<
          StrictMock<clients::eats_restapp_authorizer::ClientGMock>>();

  ComponentImpl component;
  PartnerAccessFilterTest() : component(*authorizer_mock) {}
};

TEST_F(PartnerAccessFilterTest, empty_input_data) {
  std::vector<int64_t> places{};
  std::vector<int64_t> partners{};
  std::vector<std::string> permissions{};
  {
    namespace client =
        clients::eats_restapp_authorizer::v1_user_access_check_bulk::post;
    client::Request request;
    request.body.partner_ids = partners;
    request.body.place_ids = places;
    request.body.permissions = permissions;
    client::Response200 response200;

    EXPECT_CALL(*authorizer_mock, V1UserAccessCheckBulk(request, _))
        .WillOnce(Return(response200));
  }

  auto res = component.Filter(partners, places, permissions);
  ASSERT_EQ(0, res.size());
}

TEST_F(PartnerAccessFilterTest, access_to_all_places) {
  std::vector<int64_t> places{1, 2, 3, 4, 5};
  std::vector<int64_t> partners{1, 2, 3};
  std::vector<std::string> permissions{"permission1", "permission2",
                                       "permission3"};
  {
    namespace client =
        clients::eats_restapp_authorizer::v1_user_access_check_bulk::post;
    client::Request request;
    request.body.partner_ids = partners;
    request.body.place_ids = places;
    request.body.permissions = permissions;
    client::Response200 response200;

    EXPECT_CALL(*authorizer_mock, V1UserAccessCheckBulk(request, _))
        .WillOnce(Return(response200));
  }

  auto result = component.Filter(partners, places, permissions);
  std::vector<PartnerAccess> expected = {
      {PartnerId{1},
       {1, 2, 3, 4, 5},
       {"permission1", "permission2", "permission3"}},
      {PartnerId{2},
       {1, 2, 3, 4, 5},
       {"permission1", "permission2", "permission3"}},
      {PartnerId{3},
       {1, 2, 3, 4, 5},
       {"permission1", "permission2", "permission3"}}};
  ASSERT_THAT(result, UnorderedElementsAreArray(expected));
}

TEST_F(PartnerAccessFilterTest, access_denied_to_all_places) {
  std::vector<int64_t> places{1, 2, 3, 4, 5};
  std::vector<int64_t> partners{1, 2, 3};
  std::vector<std::string> permissions{"permission1", "permission2",
                                       "permission3"};
  {
    namespace client =
        clients::eats_restapp_authorizer::v1_user_access_check_bulk::post;
    client::Request request;
    request.body.partner_ids = partners;
    request.body.place_ids = places;
    request.body.permissions = permissions;
    client::Response403 response403;
    clients::eats_restapp_authorizer::ForbiddenAccess forbidden_access{
        {}, {1, 2, 3, 4, 5}};
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_one_error;
    partner_one_error.partner_id = 1;
    partner_one_error.details = forbidden_access;
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_two_error;
    partner_two_error.partner_id = 2;
    partner_two_error.details = forbidden_access;
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_three_error;
    partner_three_error.partner_id = 3;
    partner_three_error.details = forbidden_access;

    response403.partners = {partner_one_error, partner_two_error,
                            partner_three_error};

    EXPECT_CALL(*authorizer_mock, V1UserAccessCheckBulk(request, _))
        .WillOnce(Throw(response403));
  }

  auto result = component.Filter(partners, places, permissions);
  std::vector<PartnerAccess> expected = {
      {PartnerId{1}, {}, {"permission1", "permission2", "permission3"}},
      {PartnerId{2}, {}, {"permission1", "permission2", "permission3"}},
      {PartnerId{3}, {}, {"permission1", "permission2", "permission3"}}};
  ASSERT_THAT(result, UnorderedElementsAreArray(expected));
}

TEST_F(PartnerAccessFilterTest, access_denied_for_all_except_one_partner) {
  std::vector<int64_t> places{1, 2, 3, 4, 5};
  std::vector<int64_t> partners{1, 2, 3};
  std::vector<std::string> permissions{"permission1", "permission2",
                                       "permission3"};
  {
    namespace client =
        clients::eats_restapp_authorizer::v1_user_access_check_bulk::post;
    client::Request request;
    request.body.partner_ids = partners;
    request.body.place_ids = places;
    request.body.permissions = permissions;
    client::Response403 response403;
    clients::eats_restapp_authorizer::ForbiddenAccess forbidden_access{
        {}, {1, 2, 3, 4, 5}};
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_one_error;
    partner_one_error.partner_id = 1;
    partner_one_error.details = forbidden_access;
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_two_error;
    partner_two_error.partner_id = 2;
    partner_two_error.details = forbidden_access;

    response403.partners = {partner_one_error, partner_two_error};

    EXPECT_CALL(*authorizer_mock, V1UserAccessCheckBulk(request, _))
        .WillOnce(Throw(response403));
  }

  auto result = component.Filter(partners, places, permissions);
  std::vector<PartnerAccess> expected = {
      {PartnerId{1}, {}, {"permission1", "permission2", "permission3"}},
      {PartnerId{2}, {}, {"permission1", "permission2", "permission3"}},
      {PartnerId{3},
       {1, 2, 3, 4, 5},
       {"permission1", "permission2", "permission3"}},
  };
  ASSERT_THAT(result, UnorderedElementsAreArray(expected));
}

TEST_F(PartnerAccessFilterTest,
       access_denied_for_all_except_one_partner_for_several_places) {
  std::vector<int64_t> places{1, 2, 3, 4, 5};
  std::vector<int64_t> partners{1, 2, 3};
  std::vector<std::string> permissions{"permission1", "permission2",
                                       "permission3"};
  {
    namespace client =
        clients::eats_restapp_authorizer::v1_user_access_check_bulk::post;
    client::Request request;
    request.body.partner_ids = partners;
    request.body.place_ids = places;
    request.body.permissions = permissions;
    client::Response403 response403;
    clients::eats_restapp_authorizer::ForbiddenAccess forbidden_access{
        {}, {1, 2, 3, 4, 5}};
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_one_error;
    partner_one_error.partner_id = 1;
    partner_one_error.details = forbidden_access;
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_two_error;
    partner_two_error.partner_id = 2;
    partner_two_error.details = forbidden_access;
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_three_error;
    partner_three_error.partner_id = 3;
    partner_three_error.details =
        clients::eats_restapp_authorizer::ForbiddenAccess{{}, {1, 3, 5}};

    response403.partners = {partner_one_error, partner_two_error,
                            partner_three_error};

    EXPECT_CALL(*authorizer_mock, V1UserAccessCheckBulk(request, _))
        .WillOnce(Throw(response403));
  }

  auto result = component.Filter(partners, places, permissions);
  std::vector<PartnerAccess> expected = {
      {PartnerId{1}, {}, {"permission1", "permission2", "permission3"}},
      {PartnerId{2}, {}, {"permission1", "permission2", "permission3"}},
      {PartnerId{3}, {2, 4}, {"permission1", "permission2", "permission3"}},
  };
  ASSERT_THAT(result, UnorderedElementsAreArray(expected));
}

TEST_F(PartnerAccessFilterTest,
       access_denied_for_all_partners_for_several_places) {
  std::vector<int64_t> places{1, 2, 3, 4, 5};
  std::vector<int64_t> partners{1, 2, 3};
  std::vector<std::string> permissions{"permission1", "permission2",
                                       "permission3"};
  {
    namespace client =
        clients::eats_restapp_authorizer::v1_user_access_check_bulk::post;
    client::Request request;
    request.body.partner_ids = partners;
    request.body.place_ids = places;
    request.body.permissions = permissions;
    client::Response403 response403;
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_one_error;
    partner_one_error.partner_id = 1;
    partner_one_error.details =
        clients::eats_restapp_authorizer::ForbiddenAccess{{}, {1, 2, 4}};
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_two_error;
    partner_two_error.partner_id = 2;
    partner_two_error.details =
        clients::eats_restapp_authorizer::ForbiddenAccess{{}, {2, 5}};
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_three_error;
    partner_three_error.partner_id = 3;
    partner_three_error.details =
        clients::eats_restapp_authorizer::ForbiddenAccess{{}, {1, 3, 5}};

    response403.partners = {partner_one_error, partner_two_error,
                            partner_three_error};

    EXPECT_CALL(*authorizer_mock, V1UserAccessCheckBulk(request, _))
        .WillOnce(Throw(response403));
  }

  auto result = component.Filter(partners, places, permissions);
  std::vector<PartnerAccess> expected = {
      {PartnerId{1}, {3, 5}, {"permission1", "permission2", "permission3"}},
      {PartnerId{2}, {1, 3, 4}, {"permission1", "permission2", "permission3"}},
      {PartnerId{3}, {2, 4}, {"permission1", "permission2", "permission3"}},
  };
  ASSERT_THAT(result, UnorderedElementsAreArray(expected));
}

TEST_F(PartnerAccessFilterTest, access_denied_for_one_partner) {
  std::vector<int64_t> places{1, 2, 3, 4, 5};
  std::vector<int64_t> partners{1, 2, 3};
  std::vector<std::string> permissions{"permission1", "permission2",
                                       "permission3"};
  {
    namespace client =
        clients::eats_restapp_authorizer::v1_user_access_check_bulk::post;
    client::Request request;
    request.body.partner_ids = partners;
    request.body.place_ids = places;
    request.body.permissions = permissions;
    client::Response403 response403;
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_one_error;
    partner_one_error.partner_id = 1;
    partner_one_error.details =
        clients::eats_restapp_authorizer::ForbiddenAccess{{}, {1, 2, 4}};

    response403.partners = {partner_one_error};

    EXPECT_CALL(*authorizer_mock, V1UserAccessCheckBulk(request, _))
        .WillOnce(Throw(response403));
  }

  auto result = component.Filter(partners, places, permissions);
  std::vector<PartnerAccess> expected = {
      {PartnerId{1}, {3, 5}, {"permission1", "permission2", "permission3"}},
      {PartnerId{2},
       {1, 2, 3, 4, 5},
       {"permission1", "permission2", "permission3"}},
      {PartnerId{3},
       {1, 2, 3, 4, 5},
       {"permission1", "permission2", "permission3"}},
  };
  ASSERT_THAT(result, UnorderedElementsAreArray(expected));
}

TEST_F(PartnerAccessFilterTest, access_denied_for_wrong_partner) {
  std::vector<int64_t> places{1, 2, 3, 4, 5};
  std::vector<int64_t> partners{1, 2, 3};
  std::vector<std::string> permissions{"permission1", "permission2",
                                       "permission3"};
  {
    namespace client =
        clients::eats_restapp_authorizer::v1_user_access_check_bulk::post;
    client::Request request;
    request.body.partner_ids = partners;
    request.body.place_ids = places;
    request.body.permissions = permissions;
    client::Response403 response403;
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_one_error;
    partner_one_error.partner_id = 4;
    partner_one_error.details =
        clients::eats_restapp_authorizer::ForbiddenAccess{{}, {1, 2, 4}};

    response403.partners = {partner_one_error};

    EXPECT_CALL(*authorizer_mock, V1UserAccessCheckBulk(request, _))
        .WillOnce(Throw(response403));
  }

  auto result = component.Filter(partners, places, permissions);
  std::vector<PartnerAccess> expected = {
      {PartnerId{1},
       {1, 2, 3, 4, 5},
       {"permission1", "permission2", "permission3"}},
      {PartnerId{2},
       {1, 2, 3, 4, 5},
       {"permission1", "permission2", "permission3"}},
      {PartnerId{3},
       {1, 2, 3, 4, 5},
       {"permission1", "permission2", "permission3"}}};
  ASSERT_THAT(result, UnorderedElementsAreArray(expected));
}

TEST_F(PartnerAccessFilterTest, access_denied_by_all_permissions) {
  std::vector<int64_t> places{1, 2, 3, 4, 5};
  std::vector<int64_t> partners{1, 2, 3};
  std::vector<std::string> permissions{"permission1", "permission2",
                                       "permission3"};
  {
    namespace client =
        clients::eats_restapp_authorizer::v1_user_access_check_bulk::post;
    client::Request request;
    request.body.partner_ids = partners;
    request.body.place_ids = places;
    request.body.permissions = permissions;
    client::Response403 response403;
    clients::eats_restapp_authorizer::ForbiddenAccess forbidden_access{
        {"permission1", "permission2", "permission3"}, {}};
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_one_error;
    partner_one_error.partner_id = 1;
    partner_one_error.details = forbidden_access;
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_two_error;
    partner_two_error.partner_id = 2;
    partner_two_error.details = forbidden_access;
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_three_error;
    partner_three_error.partner_id = 3;
    partner_three_error.details = forbidden_access;

    response403.partners = {partner_one_error, partner_two_error,
                            partner_three_error};

    EXPECT_CALL(*authorizer_mock, V1UserAccessCheckBulk(request, _))
        .WillOnce(Throw(response403));
  }

  auto result = component.Filter(partners, places, permissions);
  std::vector<PartnerAccess> expected = {{PartnerId{1}, {1, 2, 3, 4, 5}, {}},
                                         {PartnerId{2}, {1, 2, 3, 4, 5}, {}},
                                         {PartnerId{3}, {1, 2, 3, 4, 5}, {}}};
  ASSERT_THAT(result, UnorderedElementsAreArray(expected));
}

TEST_F(PartnerAccessFilterTest, access_denied_by_permissions_and_restaurants) {
  std::vector<int64_t> places{1, 2, 3, 4, 5};
  std::vector<int64_t> partners{1, 2, 3};
  std::vector<std::string> permissions{"permission1", "permission2",
                                       "permission3"};
  {
    namespace client =
        clients::eats_restapp_authorizer::v1_user_access_check_bulk::post;
    client::Request request;
    request.body.partner_ids = partners;
    request.body.place_ids = places;
    request.body.permissions = permissions;
    client::Response403 response403;
    clients::eats_restapp_authorizer::ForbiddenAccess forbidden_access{
        {"permission1", "permission2", "permission3"}, {}};
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_one_error;
    partner_one_error.partner_id = 1;
    partner_one_error.details = forbidden_access;
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_two_error;
    partner_two_error.partner_id = 2;
    partner_two_error.details = forbidden_access;
    clients::eats_restapp_authorizer::ForbiddenUsersAccessResponseA1PartnersA
        partner_three_error;
    partner_three_error.partner_id = 3;
    partner_three_error.details =
        clients::eats_restapp_authorizer::ForbiddenAccess{
            {"permission1", "permission2"}, {1, 3}};

    response403.partners = {partner_one_error, partner_two_error,
                            partner_three_error};

    EXPECT_CALL(*authorizer_mock, V1UserAccessCheckBulk(request, _))
        .WillOnce(Throw(response403));
  }

  auto result = component.Filter(partners, places, permissions);
  std::vector<PartnerAccess> expected = {
      {PartnerId{1}, {1, 2, 3, 4, 5}, {}},
      {PartnerId{2}, {1, 2, 3, 4, 5}, {}},
      {PartnerId{3}, {2, 4, 5}, {"permission3"}}};
  ASSERT_THAT(result, UnorderedElementsAreArray(expected));
}

TEST_F(PartnerAccessFilterTest, throw_error) {
  std::vector<int64_t> places{1, 2, 3, 4, 5};
  std::vector<int64_t> partners{1, 2, 3};
  std::vector<std::string> permissions{};

  {
    namespace client =
        clients::eats_restapp_authorizer::v1_user_access_check_bulk::post;

    client::Request request;
    request.body.partner_ids = partners;
    request.body.place_ids = places;
    request.body.permissions = permissions;
    client::Response400 response400;

    EXPECT_CALL(*authorizer_mock, V1UserAccessCheckBulk(request, _))
        .WillOnce(Throw(response400));
  }

  ASSERT_THROW(component.Filter(partners, places, permissions),
               clients::eats_restapp_authorizer::v1_user_access_check_bulk::
                   post::Response400);
}

}  // namespace testing

namespace clients::eats_restapp_authorizer {
namespace v1_user_access_check_bulk::post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return lhs.body.place_ids.size() == rhs.body.place_ids.size() &&
         lhs.body.partner_ids.size() == rhs.body.partner_ids.size() &&
         lhs.body.permissions.size() == rhs.body.permissions.size();
}
}  // namespace v1_user_access_check_bulk::post
}  // namespace clients::eats_restapp_authorizer

namespace eats_restapp_communications::types::partner_access {
inline bool operator==(const PartnerAccess& lhs, const PartnerAccess& rhs) {
  return std::tie(lhs.partner_id, lhs.place_ids, lhs.permissions) ==
         std::tie(rhs.partner_id, rhs.place_ids, rhs.permissions);
}
}  // namespace eats_restapp_communications::types::partner_access
