#include <gtest/gtest.h>

#include <functional>
#include <memory>

#include <userver/engine/run_in_coro.hpp>

#include <access-control-info/exceptions.hpp>
#include <access-control-info/models/user_access_info.hpp>

namespace {

using AccessCache = access_control_info::models::UserAccessCache::Cache;
namespace models = access_control_info::models;

std::shared_ptr<AccessCache> CreateCachePtr() {
  return std::make_shared<AccessCache>(1, 1);
}

std::function<access_control_info::models::UserAccessInfo(
    access_control_info::models::AccessControlUser)>
UpdateValue(access_control_info::models::UserAccessInfo value) {
  return [value_ = std::move(value)](
             access_control_info::models::AccessControlUser) { return value_; };
}

access_control_info::models::HandlerAccessInfo MakeAccessInfo() {
  models::HandlerPermission permission_rule{
      models::PermissionType::kPermissionRule,
      models::PermissionName{"permission_rule_test"}};
  models::PermissionsGroup permission_rule_group{};
  permission_rule_group.all_of_permissions.push_back(permission_rule);

  models::HandlerPermission permission{
      models::PermissionType::kPermission,
      models::PermissionName{"permission_test"}};
  models::PermissionsGroup permission_group{};
  permission_group.all_of_permissions.push_back(permission);

  models::Permissions permissions{};
  permissions.any_of_permission_groups.push_back(permission_rule_group);
  permissions.any_of_permission_groups.push_back(permission_group);

  return models::HandlerAccessInfo{permissions};
}

void TestCheckAccess(models::UserAccessInfo& user_info, bool is_bad = false) {
  models::UserAccessCache user_access_cache{CreateCachePtr(),
                                            UpdateValue(user_info)};
  models::UserAccessChecker checker{user_access_cache};

  models::AccessControlUser test_user{
      models::AccessControlProviderUserId{"yandex:test-id"}};
  models::HttpRequest request;
  request.method = models::HttpMethod::kPost;
  request.path_query = "/path";
  request.body = "{\"field\": \"field_value\", \"number\": 3}";

  auto access_info = MakeAccessInfo();

  RunInCoro([&checker, &test_user, &request, &access_info, &is_bad] {
    if (is_bad) {
      EXPECT_THROW(checker.CheckAccess(test_user, request, access_info),
                   access_control_info::AccessDenied);
    } else {
      EXPECT_NO_THROW(checker.CheckAccess(test_user, request, access_info));
    }
  });
}

void TestCheckAccessRestappUser(models::UserAccessInfo& user_info,
                                bool is_bad = false) {
  models::UserAccessCache user_access_cache{CreateCachePtr(),
                                            UpdateValue(user_info)};
  models::UserAccessChecker checker{user_access_cache};

  models::AccessControlUser test_user{
      models::AccessControlProviderUserId{"restapp:test-id"}};
  models::HttpRequest request;
  request.method = models::HttpMethod::kPost;
  request.path_query = "/path";
  request.body = "{\"field\": \"field_value\", \"number\": 3}";

  auto access_info = MakeAccessInfo();

  RunInCoro([&checker, &test_user, &request, &access_info, &is_bad] {
    if (is_bad) {
      EXPECT_THROW(checker.CheckAccess(test_user, request, access_info),
                   access_control_info::AccessDenied);
    } else {
      EXPECT_NO_THROW(checker.CheckAccess(test_user, request, access_info));
    }
  });
}

}  // namespace

namespace access_control_info {

TEST(AccessControlInfoCheckAccess, CheckAccessTest) {
  models::UserAccessInfo user_info{};
  models::UserAccessRole role{};
  role.permissions.push_back(models::PermissionName{"permission_test"});
  role.evaluated_permissions.push_back(models::EvaluatedPermission{
      models::RuleName{"permission_rule_test"},
      models::PermissionRuleStorage::kBody,
      models::RulePath{"test.value"},
      models::RuleValue{"test_value"},
  });
  user_info.roles.push_back(role);

  TestCheckAccess(user_info);
  TestCheckAccessRestappUser(user_info);
}

TEST(AccessControlInfoCheckAccess, CheckAccessSeveralRolesTest) {
  models::UserAccessInfo user_info{};

  models::UserAccessRole role{};
  role.role = models::RoleSlug{"role1"};
  role.permissions.push_back(models::PermissionName{"permission_test_2"});
  user_info.roles.push_back(role);

  models::UserAccessRole second_role{};
  second_role.role = models::RoleSlug{"role2"};
  second_role.permissions.push_back(models::PermissionName{"permission_test"});
  user_info.roles.push_back(second_role);

  TestCheckAccess(user_info);
  TestCheckAccessRestappUser(user_info);
}

TEST(AccessControlInfoCheckAccess, CheckAccessBadSeveralRolesTest) {
  models::UserAccessInfo user_info{};

  models::UserAccessRole role{};
  role.role = models::RoleSlug{"role1"};
  role.permissions.push_back(models::PermissionName{"permission_test_2"});
  user_info.roles.push_back(role);

  models::UserAccessRole second_role{};
  second_role.role = models::RoleSlug{"role2"};
  second_role.permissions.push_back(
      models::PermissionName{"permission_test_3"});
  user_info.roles.push_back(second_role);

  TestCheckAccess(user_info, true);
  TestCheckAccessRestappUser(user_info, true);
}

TEST(AccessControlInfoCheckAccess, CheckAccessSeveralEvaluatedRolesTest) {
  models::UserAccessInfo user_info{};

  models::UserAccessRole role{};
  role.role = models::RoleSlug{"role1"};
  role.evaluated_permissions.push_back(models::EvaluatedPermission{
      models::RuleName{"permission_rule_test"},
      models::PermissionRuleStorage::kBody,
      models::RulePath{"field"},
      models::RuleValue{"field_value"},
  });
  user_info.roles.push_back(role);

  models::UserAccessRole second_role{};
  second_role.role = models::RoleSlug{"role2"};
  role.evaluated_permissions.push_back(models::EvaluatedPermission{
      models::RuleName{"permission_rule_test_2"},
      models::PermissionRuleStorage::kBody,
      models::RulePath{"test.value"},
      models::RuleValue{"test_value"},
  });
  user_info.roles.push_back(second_role);

  TestCheckAccess(user_info);
  TestCheckAccessRestappUser(user_info);
}

TEST(AccessControlInfoCheckAccess, CheckAccessSeveralBadEvaluatedRolesTest) {
  models::UserAccessInfo user_info{};

  models::UserAccessRole role{};
  role.role = models::RoleSlug{"role1"};
  role.permissions.push_back(models::PermissionName{"perm_failed"});
  user_info.roles.push_back(role);

  models::UserAccessRole second_role{};
  second_role.role = models::RoleSlug{"role2"};
  role.evaluated_permissions.push_back(models::EvaluatedPermission{
      models::RuleName{"permission_rule_test_2"},
      models::PermissionRuleStorage::kBody,
      models::RulePath{"test.value"},
      models::RuleValue{"test_value"},
  });
  user_info.roles.push_back(second_role);

  TestCheckAccess(user_info, true);
  TestCheckAccessRestappUser(user_info, true);
}

TEST(AccessControlInfoCheckAccess, CheckAccessIgnoreRoleTest) {
  models::UserAccessInfo user_info{};

  models::UserAccessRole role{};
  role.role = models::RoleSlug{"role1"};
  role.permissions.push_back(models::PermissionName{"permission_test"});
  user_info.roles.push_back(role);

  models::UserAccessRole second_role{};
  second_role.role = models::RoleSlug{"role2"};
  role.evaluated_permissions.push_back(models::EvaluatedPermission{
      models::RuleName{"permission_rule_test"},
      models::PermissionRuleStorage::kBody,
      models::RulePath{"field"},
      models::RuleValue{"field_value"},
  });
  auto predicate = std::make_shared<::experiments3::models::False>();
  second_role.restrictions.push_back(
      {"/path", models::HttpMethod::kPost, predicate});
  user_info.roles.push_back(second_role);

  TestCheckAccess(user_info);
  TestCheckAccessRestappUser(user_info);
}

TEST(AccessControlInfoCheckAccess, CheckAccessIgnoreRoleBadTest) {
  models::UserAccessInfo user_info{};

  models::UserAccessRole role{};
  role.role = models::RoleSlug{"role1"};
  role.permissions.push_back(models::PermissionName{"permission_test_2"});
  user_info.roles.push_back(role);

  models::UserAccessRole second_role{};
  second_role.role = models::RoleSlug{"role2"};
  role.evaluated_permissions.push_back(models::EvaluatedPermission{
      models::RuleName{"permission_rule_test"},
      models::PermissionRuleStorage::kBody,
      models::RulePath{"field"},
      models::RuleValue{"field_value"},
  });
  auto predicate = std::make_shared<::experiments3::models::False>();
  second_role.restrictions.push_back(
      {"/path", models::HttpMethod::kPost, predicate});
  user_info.roles.push_back(second_role);

  TestCheckAccess(user_info, true);
  TestCheckAccessRestappUser(user_info, true);
}

}  // namespace access_control_info
