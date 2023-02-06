#include <clients/eats-restapp-authorizer/client_gmock.hpp>
#include <components/theme_blocks.hpp>
#include <userver/utest/utest.hpp>

namespace clients::eats_restapp_authorizer::v1_user_access_check::post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.body.partner_id, lhs.body.place_ids,
                  lhs.body.permissions) == std::tie(rhs.body.partner_id,
                                                    rhs.body.place_ids,
                                                    rhs.body.permissions);
}
}  // namespace clients::eats_restapp_authorizer::v1_user_access_check::post

namespace eats_report_storage::components::detail {
using namespace ::testing;

struct ThemeBlocksAuthTest : public Test {
  StrictMock<clients::eats_restapp_authorizer::ClientGMock>
      eats_restapp_authorizer;
  ThemeBlocksAuth theme_blocks_auth;

  const int64_t partner_id = 1;
  const types::PlaceIds place_ids =
      types::PlaceIds{types::PlaceId{10}, types::PlaceId{20}};
  AuthCheckInfo auth_check_info;

  static decltype(auto) MakeAuthorizerResponseOK() {
    return clients::eats_restapp_authorizer::v1_user_access_check::post::
        Response{};
  }

  static decltype(auto) MakeAuthorizerResponse403(
      const std::vector<int64_t> place_ids,
      const std::vector<std::string>& permissions) {
    clients::eats_restapp_authorizer::ForbiddenAccess reason;
    reason.place_ids = place_ids;
    reason.permissions = permissions;
    clients::eats_restapp_authorizer::v1_user_access_check::post::Response403
        response;
    response.details = std::move(reason);
    return response;
  }

  decltype(auto) MakeAuthorizerRequest() {
    clients::eats_restapp_authorizer::v1_user_access_check::post::Request
        request;
    request.body.partner_id = partner_id;
    std::transform(place_ids.begin(), place_ids.end(),
                   std::back_inserter(request.body.place_ids),
                   [](const auto& p) { return p.GetUnderlying(); });
    request.body.permissions = auth_check_info.GetAll();
    return request;
  }

  ThemeBlocksAuthTest() : theme_blocks_auth(eats_restapp_authorizer) {}
};

TEST_F(ThemeBlocksAuthTest,
       CheckAccess_returns_block_false_if_places_not_allowed) {
  EXPECT_CALL(eats_restapp_authorizer,
              V1UserAccessCheck(MakeAuthorizerRequest(), _))
      .WillOnce(Throw(MakeAuthorizerResponse403({10}, {})));
  const auto result =
      theme_blocks_auth.CheckAccess(partner_id, place_ids, auth_check_info);
  ASSERT_FALSE(result.block);
}

TEST_F(ThemeBlocksAuthTest, CheckAccess_returns_all_true_on_empty_permissions) {
  EXPECT_CALL(eats_restapp_authorizer,
              V1UserAccessCheck(MakeAuthorizerRequest(), _))
      .WillOnce(Throw(MakeAuthorizerResponse403({}, {"block_permission"})));
  const auto result =
      theme_blocks_auth.CheckAccess(partner_id, place_ids, auth_check_info);
  ASSERT_TRUE(result.block);
  ASSERT_TRUE(result.insides);
  ASSERT_TRUE(result.benchmarks);
  ASSERT_TRUE(result.suggests);
  ASSERT_TRUE(result.links);
}

TEST_F(ThemeBlocksAuthTest,
       CheckAccess_returns_block_false_on_missing_permissions) {
  auth_check_info.block.insert("block_permission");
  EXPECT_CALL(eats_restapp_authorizer,
              V1UserAccessCheck(MakeAuthorizerRequest(), _))
      .WillOnce(Throw(MakeAuthorizerResponse403({}, {"block_permission"})));
  const auto result =
      theme_blocks_auth.CheckAccess(partner_id, place_ids, auth_check_info);
  ASSERT_FALSE(result.block);
}

TEST_F(ThemeBlocksAuthTest,
       CheckAccess_returns_block_true_insides_false_on_missing_permissions) {
  auth_check_info.block.insert("block_permission");
  auth_check_info.insides.insert("insides_permission");
  EXPECT_CALL(eats_restapp_authorizer,
              V1UserAccessCheck(MakeAuthorizerRequest(), _))
      .WillOnce(Throw(MakeAuthorizerResponse403({}, {"insides_permission"})));
  const auto result =
      theme_blocks_auth.CheckAccess(partner_id, place_ids, auth_check_info);
  ASSERT_TRUE(result.block);
  ASSERT_FALSE(result.insides);
}

TEST_F(
    ThemeBlocksAuthTest,
    CheckAccess_returns_block_true_insides_true_on_at_least_one_permissions) {
  auth_check_info.block.insert("block_permission");
  auth_check_info.insides.insert("insides_permission");
  auth_check_info.insides.insert("insides_permission_extra");
  EXPECT_CALL(eats_restapp_authorizer,
              V1UserAccessCheck(MakeAuthorizerRequest(), _))
      .WillOnce(Throw(MakeAuthorizerResponse403({}, {"insides_permission"})));
  const auto result =
      theme_blocks_auth.CheckAccess(partner_id, place_ids, auth_check_info);
  ASSERT_TRUE(result.block);
  ASSERT_TRUE(result.insides);
}

TEST_F(ThemeBlocksAuthTest,
       CheckAccess_returns_block_true_benchmarks_false_on_missing_permissions) {
  auth_check_info.block.insert("block_permission");
  auth_check_info.benchmarks.insert("benchmarks_permission");
  EXPECT_CALL(eats_restapp_authorizer,
              V1UserAccessCheck(MakeAuthorizerRequest(), _))
      .WillOnce(
          Throw(MakeAuthorizerResponse403({}, {"benchmarks_permission"})));
  const auto result =
      theme_blocks_auth.CheckAccess(partner_id, place_ids, auth_check_info);
  ASSERT_TRUE(result.block);
  ASSERT_FALSE(result.benchmarks);
}

TEST_F(
    ThemeBlocksAuthTest,
    CheckAccess_returns_block_true_benchmarks_true_on_at_least_one_permissions) {
  auth_check_info.block.insert("block_permission");
  auth_check_info.benchmarks.insert("benchmarks_permission");
  auth_check_info.benchmarks.insert("benchmarks_permission_extra");
  EXPECT_CALL(eats_restapp_authorizer,
              V1UserAccessCheck(MakeAuthorizerRequest(), _))
      .WillOnce(
          Throw(MakeAuthorizerResponse403({}, {"benchmarks_permission"})));
  const auto result =
      theme_blocks_auth.CheckAccess(partner_id, place_ids, auth_check_info);
  ASSERT_TRUE(result.block);
  ASSERT_TRUE(result.benchmarks);
}

TEST_F(ThemeBlocksAuthTest,
       CheckAccess_returns_block_true_suggests_false_on_missing_permissions) {
  auth_check_info.block.insert("block_permission");
  auth_check_info.suggests.insert("suggests_permission");
  EXPECT_CALL(eats_restapp_authorizer,
              V1UserAccessCheck(MakeAuthorizerRequest(), _))
      .WillOnce(Throw(MakeAuthorizerResponse403({}, {"suggests_permission"})));
  const auto result =
      theme_blocks_auth.CheckAccess(partner_id, place_ids, auth_check_info);
  ASSERT_TRUE(result.block);
  ASSERT_FALSE(result.suggests);
}

TEST_F(
    ThemeBlocksAuthTest,
    CheckAccess_returns_block_true_suggests_true_on_at_least_one_permissions) {
  auth_check_info.block.insert("block_permission");
  auth_check_info.suggests.insert("suggests_permission");
  auth_check_info.suggests.insert("suggests_permission_extra");
  EXPECT_CALL(eats_restapp_authorizer,
              V1UserAccessCheck(MakeAuthorizerRequest(), _))
      .WillOnce(Throw(MakeAuthorizerResponse403({}, {"suggests_permission"})));
  const auto result =
      theme_blocks_auth.CheckAccess(partner_id, place_ids, auth_check_info);
  ASSERT_TRUE(result.block);
  ASSERT_TRUE(result.suggests);
}

TEST_F(ThemeBlocksAuthTest,
       CheckAccess_returns_block_true_links_false_on_missing_permissions) {
  auth_check_info.block.insert("block_permission");
  auth_check_info.links.insert("links_permission");
  EXPECT_CALL(eats_restapp_authorizer,
              V1UserAccessCheck(MakeAuthorizerRequest(), _))
      .WillOnce(Throw(MakeAuthorizerResponse403({}, {"links_permission"})));
  const auto result =
      theme_blocks_auth.CheckAccess(partner_id, place_ids, auth_check_info);
  ASSERT_TRUE(result.block);
  ASSERT_FALSE(result.links);
}

TEST_F(ThemeBlocksAuthTest,
       CheckAccess_returns_block_true_links_true_on_at_least_one_permissions) {
  auth_check_info.block.insert("block_permission");
  auth_check_info.links.insert("links_permission");
  auth_check_info.links.insert("links_permission_extra");
  EXPECT_CALL(eats_restapp_authorizer,
              V1UserAccessCheck(MakeAuthorizerRequest(), _))
      .WillOnce(Throw(MakeAuthorizerResponse403({}, {"links_permission"})));
  const auto result =
      theme_blocks_auth.CheckAccess(partner_id, place_ids, auth_check_info);
  ASSERT_TRUE(result.block);
  ASSERT_TRUE(result.links);
}

TEST_F(ThemeBlocksAuthTest, CheckAccess_returns_all_true_on_authorizer_ok) {
  auth_check_info.block.insert("block_permission");
  auth_check_info.insides.insert("insides_permission");
  auth_check_info.benchmarks.insert("benchmarks_permission");
  auth_check_info.suggests.insert("suggests_permission");
  auth_check_info.links.insert("links_permission");
  EXPECT_CALL(eats_restapp_authorizer,
              V1UserAccessCheck(MakeAuthorizerRequest(), _))
      .WillOnce(Return(MakeAuthorizerResponseOK()));
  const auto result =
      theme_blocks_auth.CheckAccess(partner_id, place_ids, auth_check_info);
  ASSERT_TRUE(result.block);
  ASSERT_TRUE(result.insides);
  ASSERT_TRUE(result.benchmarks);
  ASSERT_TRUE(result.suggests);
  ASSERT_TRUE(result.links);
}

}  // namespace eats_report_storage::components::detail
