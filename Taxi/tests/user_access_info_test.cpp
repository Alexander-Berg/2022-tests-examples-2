#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>

#include "clients/access-control/definitions.hpp"

#include "access-control-info/models/user_access_info.hpp"

namespace {
clients::access_control::UserAccessInfo BuildResponse() {
  clients::access_control::UserAccessInfo response{};
  response.permissions.push_back("perm1");
  response.permissions.push_back("perm2");
  response.permissions.push_back("perm3");
  response.permissions.push_back("perm4");
  response.permissions.push_back("perm5");

  response.evaluated_permissions.push_back(
      {"rule_name_1",
       clients::access_control::EvaluatedPermissionRulestorage::kBody, "path_1",
       "value_1"});
  response.evaluated_permissions.push_back(
      {"rule_name_2",
       clients::access_control::EvaluatedPermissionRulestorage::kQuery,
       "path_2", "value_2"});

  std::string_view predicate_mock{
      "{\"init\":{\"predicates\":[]}, \"type\": \"all_of\"}"};
  clients::access_control::RestrictionV1 restriction_1{
      "/path/test/1", clients::access_control::HandlerMethod::kPost};
  restriction_1.restriction.extra = formats::json::FromString(predicate_mock);
  clients::access_control::RestrictionV1 restriction_2{
      "/path/test/1", clients::access_control::HandlerMethod::kPost};
  restriction_2.restriction.extra = formats::json::FromString(predicate_mock);
  response.restrictions.push_back(restriction_1);
  response.restrictions.push_back(restriction_2);

  clients::access_control::UserAccessInfoRole role1{};
  role1.role = "role1";
  role1.restrictions.push_back(response.restrictions[0]);
  role1.permissions.push_back(response.permissions[0]);

  clients::access_control::UserAccessInfoRole role2{};
  role2.role = "role2";
  role2.permissions.push_back(response.permissions[1]);
  role2.permissions.push_back(response.permissions[2]);
  role2.permissions.push_back(response.permissions[3]);
  role2.evaluated_permissions.push_back(response.evaluated_permissions[0]);
  role2.evaluated_permissions.push_back(response.evaluated_permissions[1]);

  clients::access_control::UserAccessInfoRole role3{};
  role3.role = "role3";
  role3.permissions.push_back(response.permissions[4]);
  role3.restrictions.push_back(response.restrictions[1]);

  response.roles.push_back(role1);
  response.roles.push_back(role2);
  response.roles.push_back(role3);
  return response;
}

access_control_info::models::UserAccessInfo BuildExpectedUserInfo() {
  namespace models = access_control_info::models;
  models::UserAccessInfo user_info{};
  models::UserAccessRole role_first{};
  role_first.role = models::RoleSlug{"role1"};
  role_first.permissions.push_back(models::PermissionName{"perm1"});
  role_first.restrictions.push_back(
      models::Restriction{"/path/test/1", models::HttpMethod::kPost,
                          std::make_shared<::experiments3::models::AllOf>()});
  user_info.roles.push_back(role_first);

  models::UserAccessRole role_second{};
  role_second.role = models::RoleSlug{"role2"};
  role_second.permissions.push_back(models::PermissionName{"perm2"});
  role_second.permissions.push_back(models::PermissionName{"perm3"});
  role_second.permissions.push_back(models::PermissionName{"perm4"});
  role_second.evaluated_permissions.push_back(
      {models::RuleName{"rule_name_1"}, models::PermissionRuleStorage::kBody,
       models::RulePath{"path_1"}, models::RuleValue{"value_1"}});
  role_second.evaluated_permissions.push_back(
      {models::RuleName{"rule_name_2"}, models::PermissionRuleStorage::kQuery,
       models::RulePath{"path_2"}, models::RuleValue{"value_2"}});
  user_info.roles.push_back(role_second);

  models::UserAccessRole role_third{};
  role_third.role = models::RoleSlug{"role3"};
  role_third.permissions.push_back(models::PermissionName{"perm5"});
  role_third.restrictions.push_back(
      models::Restriction{"/path/test/1", models::HttpMethod::kPost,
                          std::make_shared<::experiments3::models::AllOf>()});
  user_info.roles.push_back(role_third);
  return user_info;
}
}  // namespace

namespace access_control_info {

TEST(AccessControlInfoUserAccessInfo, ParseFromResponseTest) {
  const auto response = BuildResponse();
  const auto user_info = models::UserAccessInfo::ParseResponse(response);
  const auto expected_user_info = BuildExpectedUserInfo();

  EXPECT_EQ(user_info.roles.size(), expected_user_info.roles.size());

  for (size_t index = 0; index < expected_user_info.roles.size(); index++) {
    const auto& user_info_role = user_info.roles[index];
    const auto& expected_role = expected_user_info.roles[index];
    EXPECT_EQ(user_info_role.role, expected_role.role);
    EXPECT_EQ(user_info_role.permissions, expected_role.permissions);

    EXPECT_EQ(user_info_role.evaluated_permissions.size(),
              expected_role.evaluated_permissions.size());

    for (size_t ev_index = 0;
         ev_index < expected_role.evaluated_permissions.size(); ev_index++) {
      const auto& user_info_ev_permission =
          user_info_role.evaluated_permissions[ev_index];
      const auto& expected_ev_permission =
          expected_role.evaluated_permissions[ev_index];
      EXPECT_EQ(user_info_ev_permission.rule_name,
                expected_ev_permission.rule_name);
      EXPECT_EQ(user_info_ev_permission.rule_path,
                expected_ev_permission.rule_path);
      EXPECT_EQ(user_info_ev_permission.rule_storage,
                expected_ev_permission.rule_storage);
      EXPECT_EQ(user_info_ev_permission.rule_value,
                expected_ev_permission.rule_value);
    }

    EXPECT_EQ(user_info_role.restrictions.size(),
              expected_role.restrictions.size());

    for (size_t rest_index = 0; rest_index < expected_role.restrictions.size();
         rest_index++) {
      const auto& user_info_restriction =
          user_info_role.restrictions[rest_index];
      const auto& expected_restriction = expected_role.restrictions[rest_index];
      EXPECT_EQ(user_info_restriction.handler_path,
                expected_restriction.handler_path);
      EXPECT_EQ(user_info_restriction.handler_method,
                expected_restriction.handler_method);
    }
  }
}

}  // namespace access_control_info
