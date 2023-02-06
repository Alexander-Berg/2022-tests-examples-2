#include <userver/utest/utest.hpp>

#include <authorizer/check_access.hpp>
#include <clients/eats-restapp-authorizer/client_gmock.hpp>

namespace eats_report_storage::authorizer {

inline bool operator==(const DataCheck& lhs, const DataCheck& rhs) noexcept {
  return lhs.place_ids == rhs.place_ids && lhs.permissions == rhs.permissions;
}

TEST(AuthorizerCheckAccess,
     function_should_return_empty_data_if_authorizar_returned_200) {
  clients::eats_restapp_authorizer::ClientGMock client;
  using AuthorizerResponse =
      clients::eats_restapp_authorizer::v1_user_access_check::post::Response200;
  AuthorizerResponse authorizer_result;
  EXPECT_CALL(client, V1UserAccessCheck)
      .WillOnce(::testing::Return(authorizer_result));
  ASSERT_EQ(CheckAccess(client, 1, {"permission1", "permission2"}),
            DataCheck());
}

TEST(
    AuthorizerCheckAccess,
    function_should_return_place_ids_and_permissions_that_returned_authorizer) {
  clients::eats_restapp_authorizer::ClientGMock client;
  using AuthorizerResponse =
      clients::eats_restapp_authorizer::v1_user_access_check::post::Response403;
  AuthorizerResponse authorizer_result;
  clients::eats_restapp_authorizer::ForbiddenAccess details;
  details.place_ids = {1};
  details.permissions = {"permission2"};
  authorizer_result.details = details;
  EXPECT_CALL(client, V1UserAccessCheck)
      .WillOnce(::testing::Throw(authorizer_result));
  ASSERT_EQ(CheckAccess(client, 1, {"permission1", "permission2"},
                        {types::PlaceId{1}, types::PlaceId{2}}),
            DataCheck({{1}, {"permission2"}}));
}

TEST(AuthorizerCheckAccess,
     function_should_return_exception_if_authorizer_return_403_and_empty_data) {
  clients::eats_restapp_authorizer::ClientGMock client;
  using AuthorizerResponse =
      clients::eats_restapp_authorizer::v1_user_access_check::post::Response403;
  AuthorizerResponse authorizer_result;
  EXPECT_CALL(client, V1UserAccessCheck)
      .WillOnce(::testing::Throw(authorizer_result));
  ASSERT_THROW(CheckAccess(client, 1, {"permission1", "permission2"},
                           {types::PlaceId{1}, types::PlaceId{2}}),
               std::exception);
}

TEST(AuthorizerCheckAccess,
     function_should_return_exception_if_authorizer_return_400) {
  clients::eats_restapp_authorizer::ClientGMock client;
  using AuthorizerResponse =
      clients::eats_restapp_authorizer::v1_user_access_check::post::Response400;
  AuthorizerResponse authorizer_result;
  EXPECT_CALL(client, V1UserAccessCheck)
      .WillOnce(::testing::Throw(authorizer_result));
  ASSERT_THROW(CheckAccess(client, 1, {"permission1", "permission2"},
                           {types::PlaceId{1}, types::PlaceId{2}}),
               std::exception);
}

}  // namespace eats_report_storage::authorizer
