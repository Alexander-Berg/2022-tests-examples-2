#include <userver/utest/utest.hpp>

#include <utils/callcenter_fetcher_filter.hpp>

namespace {

using EmployeeFilters = utils::CallcenterFetcherFilter::EmployeeFilters;

const model::Employee kDefaultEmployee = {
    "yandex_uid",  // std::string yandex_uid{};
    "login",       // std::string login{};
    {},            // std::vector<model::Department> departments{};
    {},            // std::vector<model::Department> head_of_departments{};
    "full_name",   // std::string full_name{};
    handlers::EmploymentStatus::kInStaff,  // handlers::EmploymentStatus
                                           // employment_status{};
    "domain",                              // model::Domain domain{};
    {},            // std::optional<Supervisor> supervisor{};
    {},            // std::optional<std::string> mentor_login{};
    {},            // std::optional<std::string> phone_pd_id{};
    {},            // std::optional<std::string> email_pd_id{};
    {},            // std::optional<std::string> telegram_login_pd_id{};
    {"position"},  // std::vector<std::string> positions{};
    {},            // std::optional<std::string> timezone{};
    {},            // std::optional<std::string> staff_login{};
    {},            // std::optional<std::chrono::system_clock::time_point>
                   // employment_datetime{};
    {},            // std::optional<std::string> comment{};
    {},            // std::optional<std::vector<std::string>> tags{};
    {},            // std::optional<std::string> organization{};
    {},            // std::optional<std::string> timezone_source{};
    {},            // std::optional<std::string> hr_ticket{};
};

const EmployeeFilters kDefaultFilters = {
    {{"yandex_uid", {std::vector<std::string>{"yandex_uid"}, {}}}}};

}  // namespace

UTEST(MappersSuite, TestFilterOut_1) {
  std::vector<model::Employee> to_filter{kDefaultEmployee};

  auto res = utils::CallcenterFetcherFilter::FilterEmployees(to_filter,
                                                             kDefaultFilters);

  ASSERT_TRUE(res.empty());
}

UTEST(MappersSuite, TestAllow_1) {
  std::vector<model::Employee> to_filter{kDefaultEmployee};

  const EmployeeFilters filters = {
      {{"yandex_uid", {{}, std::vector<std::string>{"yandex_uid"}}}}};

  auto res =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters);

  ASSERT_TRUE(res[0] == kDefaultEmployee);
}

UTEST(MappersSuite, TestFilterOutDepartment) {
  std::vector<model::Employee> to_filter;
  auto employee = kDefaultEmployee;
  employee.departments = {{1, "dep_id_1", "dep_name_1"},
                          {2, "dep_id_2", "dep_name_2"}};
  to_filter.emplace_back(employee);

  EmployeeFilters filters_1 = {
      {{"department_id",
        {std::vector<std::string>{"dep_id_1", "another"}, {}}}}};

  EmployeeFilters filters_2 = {
      {{"department_id",
        {std::vector<std::string>{"dep_id_2", "another"}, {}}}}};

  auto res_1 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_1);
  auto res_2 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_2);

  ASSERT_TRUE(res_1.empty());
  ASSERT_TRUE(res_2.empty());
}

UTEST(MappersSuite, TestFilterOutWithAllowDepartment) {
  std::vector<model::Employee> to_filter;
  auto employee = kDefaultEmployee;
  employee.departments = {{1, "dep_id_1", "dep_name_1"},
                          {2, "dep_id_2", "dep_name_2"}};
  to_filter.emplace_back(employee);

  EmployeeFilters filters_1 = {
      {{"department_id",
        {{}, std::vector<std::string>{"dep_id_5", "another"}}}}};

  EmployeeFilters filters_2 = {
      {{"department_id",
        {{}, std::vector<std::string>{"dep_id_6", "another"}}}}};

  auto res_1 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_1);
  auto res_2 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_2);

  ASSERT_TRUE(res_1.empty());
  ASSERT_TRUE(res_2.empty());
}

UTEST(MappersSuite, TestOkDepartment) {
  std::vector<model::Employee> to_filter;
  auto employee = kDefaultEmployee;
  employee.departments = {{1, "dep_id_1", "dep_name_1"},
                          {2, "dep_id_2", "dep_name_2"}};
  to_filter.emplace_back(employee);

  EmployeeFilters filters_1 = {
      {{"department_id",
        {std::vector<std::string>{"dep_id_3", "another"}, {}}}}};

  EmployeeFilters filters_2 = {
      {{"department_id",
        {std::vector<std::string>{"dep_id_4", "another"}, {}}}}};

  auto res_1 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_1);
  auto res_2 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_2);

  ASSERT_TRUE(res_1[0] == employee);
  ASSERT_TRUE(res_2[0] == employee);
}

UTEST(MappersSuite, TestOkWithAllowDepartment) {
  std::vector<model::Employee> to_filter;
  auto employee = kDefaultEmployee;
  employee.departments = {{1, "dep_id_1", "dep_name_1"},
                          {2, "dep_id_2", "dep_name_2"}};
  to_filter.emplace_back(employee);

  EmployeeFilters filters_1 = {
      {{"department_id",
        {{}, std::vector<std::string>{"dep_id_1", "another"}}}}};

  EmployeeFilters filters_2 = {
      {{"department_id",
        {{}, std::vector<std::string>{"dep_id_2", "another"}}}}};

  auto res_1 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_1);
  auto res_2 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_2);

  ASSERT_TRUE(res_1[0] == employee);
  ASSERT_TRUE(res_2[0] == employee);
}

UTEST(MappersSuite, TestAllowAndOptField) {
  std::vector<model::Employee> to_filter{kDefaultEmployee};
  EmployeeFilters filters = {
      {{"phone_pd_id", {{}, std::vector<std::string>{"some_value"}}}}};

  auto res =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters);

  ASSERT_TRUE(res.empty());
}

UTEST(MappersSuite, TestFilterOutAndOptField) {
  std::vector<model::Employee> to_filter{kDefaultEmployee};
  EmployeeFilters filters = {
      {{"phone_pd_id", {std::vector<std::string>{"some_value"}, {}}}}};

  auto res =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters);

  ASSERT_TRUE(res[0] == kDefaultEmployee);
}

UTEST(MappersSuite, TestFilterOutTags) {
  std::vector<model::Employee> to_filter;
  auto employee = kDefaultEmployee;
  employee.tags = {"tag_1", "tag_2", "tag_3"};
  to_filter.emplace_back(employee);

  EmployeeFilters filters_1 = {
      {{"tags", {std::vector<std::string>{"tag_1", "another"}, {}}}}};

  EmployeeFilters filters_2 = {
      {{"tags", {std::vector<std::string>{"tag_3", "another"}, {}}}}};

  auto res_1 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_1);
  auto res_2 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_2);

  ASSERT_TRUE(res_1.empty());
  ASSERT_TRUE(res_2.empty());
}

UTEST(MappersSuite, TestOkTags) {
  std::vector<model::Employee> to_filter;
  auto employee = kDefaultEmployee;
  employee.tags = {"tag_1", "tag_2", "tag_3"};
  to_filter.emplace_back(employee);

  EmployeeFilters filters_1 = {
      {{"tags", {std::vector<std::string>{"tag_5", "another"}, {}}}}};

  EmployeeFilters filters_2 = {
      {{"tags", {std::vector<std::string>{"tag_4", "another"}, {}}}}};

  auto res_1 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_1);
  auto res_2 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_2);

  ASSERT_TRUE(res_1[0] == employee);
  ASSERT_TRUE(res_2[0] == employee);
}

UTEST(MappersSuite, TestFilterOutWithAllowTags) {
  std::vector<model::Employee> to_filter;
  auto employee = kDefaultEmployee;
  employee.tags = {"tag_1", "tag_2", "tag_3"};
  to_filter.emplace_back(employee);

  EmployeeFilters filters_1 = {
      {{"tags", {{}, std::vector<std::string>{"tag_5", "another"}}}}};

  EmployeeFilters filters_2 = {
      {{"tags", {{}, std::vector<std::string>{"tag_6", "another"}}}}};

  auto res_1 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_1);
  auto res_2 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_2);

  ASSERT_TRUE(res_1.empty());
  ASSERT_TRUE(res_2.empty());
}

UTEST(MappersSuite, TestOkWithAllowTags) {
  std::vector<model::Employee> to_filter;
  auto employee = kDefaultEmployee;
  employee.tags = {"tag_1", "tag_2", "tag_3"};
  to_filter.emplace_back(employee);

  EmployeeFilters filters_1 = {
      {{"tags", {{}, std::vector<std::string>{"tag_1", "another"}}}}};

  EmployeeFilters filters_2 = {
      {{"tags", {{}, std::vector<std::string>{"tag_3", "another"}}}}};

  auto res_1 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_1);
  auto res_2 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_2);

  ASSERT_TRUE(res_1[0] == employee);
  ASSERT_TRUE(res_2[0] == employee);
}

UTEST(MappersSuite, TestEmploymentStatus) {
  std::vector<model::Employee> to_filter_in_staff;
  std::vector<model::Employee> to_filter_fired;
  auto employee_in_staff = kDefaultEmployee;
  auto employee_fired = kDefaultEmployee;
  employee_fired.employment_status = handlers::EmploymentStatus::kFired;
  to_filter_in_staff.emplace_back(employee_in_staff);
  to_filter_fired.emplace_back(employee_fired);

  EmployeeFilters filters_allow_in_staff = {
      {{"employment_status", {{}, std::vector<std::string>{"in_staff"}}}}};

  EmployeeFilters filters_filter_in_staff = {
      {{"employment_status", {std::vector<std::string>{"in_staff"}, {}}}}};

  EmployeeFilters filters_allow_fired = {
      {{"employment_status", {{}, std::vector<std::string>{"fired"}}}}};

  EmployeeFilters filters_filter_fired = {
      {{"employment_status", {std::vector<std::string>{"fired"}, {}}}}};

  auto res_allow_in_staff = utils::CallcenterFetcherFilter::FilterEmployees(
      to_filter_in_staff, filters_allow_in_staff);
  auto res_filter_in_staff = utils::CallcenterFetcherFilter::FilterEmployees(
      to_filter_in_staff, filters_filter_in_staff);
  auto res_allow_fired = utils::CallcenterFetcherFilter::FilterEmployees(
      to_filter_fired, filters_allow_fired);
  auto res_filter_fired = utils::CallcenterFetcherFilter::FilterEmployees(
      to_filter_fired, filters_filter_fired);

  ASSERT_TRUE(res_allow_in_staff[0] == employee_in_staff);
  ASSERT_TRUE(res_filter_in_staff.empty());
  ASSERT_TRUE(res_allow_fired[0] == employee_fired);
  ASSERT_TRUE(res_filter_fired.empty());
}

UTEST(MappersSuite, TestAllowWithAllFields) {
  std::vector<model::Employee> to_filter;
  auto employee = kDefaultEmployee;

  employee.yandex_uid = "yandex_uid";
  employee.login = "login";
  employee.departments = {{1, "dep1", "a"}, {1, "dep2", "d"}, {1, "dep3", "e"}};
  employee.full_name = "full_name";
  employee.employment_status = handlers::EmploymentStatus::kInStaff;
  employee.domain = "domain";
  employee.mentor_login = "mentor_login";
  employee.phone_pd_id = "phone_pd_id";
  employee.email_pd_id = "email_pd_id";
  employee.telegram_login_pd_id = "telegram_login_pd_id";
  employee.positions = {"pos1", "pos2"};
  employee.timezone = "timezone";
  employee.staff_login = "staff_login";
  employee.comment = "comment";
  employee.tags = {"tag_1", "tag_2"};

  to_filter.emplace_back(employee);

  EmployeeFilters filters = {{

      {"yandex_uid", {{}, std::vector<std::string>{"yandex_uid", "another"}}},
      {"login", {{}, std::vector<std::string>{"login", "another"}}},
      {"department_id", {{}, std::vector<std::string>{"dep1", "dep2", "dep6"}}},
      {"full_name", {{}, std::vector<std::string>{"full_name", "another"}}},
      {"employment_status",
       {{}, std::vector<std::string>{"in_staff", "another"}}},
      {"domain", {{}, std::vector<std::string>{"domain", "another"}}},
      {"mentor_login",
       {{}, std::vector<std::string>{"mentor_login", "another"}}},
      {"phone_pd_id", {{}, std::vector<std::string>{"phone_pd_id", "another"}}},
      {"email_pd_id", {{}, std::vector<std::string>{"email_pd_id", "another"}}},
      {"telegram_login_pd_id",
       {{}, std::vector<std::string>{"telegram_login_pd_id", "another"}}},
      {"positions", {{}, std::vector<std::string>{"pos1", "another"}}},
      {"timezone", {{}, std::vector<std::string>{"timezone", "another"}}},
      {"staff_login", {{}, std::vector<std::string>{"staff_login", "another"}}},
      {"comment", {{}, std::vector<std::string>{"comment", "another"}}},
      {"tags", {{}, std::vector<std::string>{"tag_1", "another"}}},
  }};

  auto res =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters);

  ASSERT_TRUE(res[0] == employee);
}

UTEST(MappersSuite, TestFilterOutAllFields) {
  std::vector<model::Employee> to_filter;
  auto employee = kDefaultEmployee;

  employee.yandex_uid = "yandex_uid";
  employee.login = "login";
  employee.departments = {{1, "dep1", "a"}, {2, "dep2", "d"}, {3, "dep3", "e"}};
  employee.full_name = "full_name";
  employee.employment_status = handlers::EmploymentStatus::kInStaff;
  employee.domain = "domain";
  employee.mentor_login = "mentor_login";
  employee.phone_pd_id = "phone_pd_id";
  employee.email_pd_id = "email_pd_id";
  employee.telegram_login_pd_id = "telegram_login_pd_id";
  employee.positions = {"pos1", "pos2"};
  employee.timezone = "timezone";
  employee.staff_login = "staff_login";
  employee.comment = "comment";
  employee.tags = {"tag_1", "tag_2"};

  to_filter.emplace_back(employee);

  std::vector<std::pair<
      std::string,
      ::taxi_config::effrat_employees_callcenter_fetcher_filters::Filter>>
      filter_values = {

          {"yandex_uid",
           {std::vector<std::string>{"yandex_uid", "another"}, {}}},
          {"login", {std::vector<std::string>{"login", "another"}, {}}},
          {"department_id",
           {std::vector<std::string>{"dep1", "dep2", "dep6"}, {}}},
          {"full_name", {std::vector<std::string>{"full_name", "another"}, {}}},
          {"employment_status",
           {std::vector<std::string>{"in_staff", "another"}, {}}},
          {"domain", {std::vector<std::string>{"domain", "another"}, {}}},
          {"mentor_login",
           {std::vector<std::string>{"mentor_login", "another"}, {}}},
          {"phone_pd_id",
           {std::vector<std::string>{"phone_pd_id", "another"}, {}}},
          {"email_pd_id",
           {std::vector<std::string>{"email_pd_id", "another"}, {}}},
          {"telegram_login_pd_id",
           {std::vector<std::string>{"telegram_login_pd_id", "another"}, {}}},
          {"positions", {std::vector<std::string>{"pos1", "another"}, {}}},
          {"timezone", {std::vector<std::string>{"timezone", "another"}, {}}},
          {"staff_login",
           {std::vector<std::string>{"staff_login", "another"}, {}}},
          {"comment", {std::vector<std::string>{"comment", "another"}, {}}},
          {"tags", {std::vector<std::string>{"tag_1", "another"}, {}}},
      };

  for (const auto& fv : filter_values) {
    EmployeeFilters filters = {{fv}};

    auto res =
        utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters);

    ASSERT_TRUE(res.empty());
  }
}

UTEST(MappersSuite, TestUnknownFilter) {
  std::vector<model::Employee> to_filter{kDefaultEmployee};

  EmployeeFilters filters_1 = {
      {{"unknown", {{}, std::vector<std::string>{"some_val"}}}}};

  auto res_1 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_1);

  EmployeeFilters filters_2 = {
      {{"unknown", {std::vector<std::string>{"some_val"}, {}}}}};

  auto res_2 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_2);

  ASSERT_TRUE(res_1[0] == kDefaultEmployee);
  ASSERT_TRUE(res_2[0] == kDefaultEmployee);
}

UTEST(MappersSuite, TestWrongFilterType) {
  std::vector<model::Employee> to_filter{kDefaultEmployee};

  EmployeeFilters filters_1 = {{{"yandex_uid", {{}, std::vector<int>{10}}}}};
  EmployeeFilters filters_2 = {{{"yandex_uid", {std::vector<int>{10}, {}}}}};

  auto res_1 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_1);
  auto res_2 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_2);

  ASSERT_TRUE(res_1[0] == kDefaultEmployee);
  ASSERT_TRUE(res_2[0] == kDefaultEmployee);
}

UTEST(MappersSuite, TestWrongFilterTypeForVector) {
  std::vector<model::Employee> to_filter;
  auto employee = kDefaultEmployee;
  employee.tags = {"tag_1", "tag_2", "tag_3"};
  to_filter.emplace_back(employee);

  EmployeeFilters filters_1 = {{{"tags", {{}, std::vector<int>{10}}}}};

  auto res_1 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_1);

  EmployeeFilters filters_2 = {{{"tags", {std::vector<int>{10}, {}}}}};

  auto res_2 =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters_2);

  ASSERT_TRUE(res_1[0] == employee);
  ASSERT_TRUE(res_2[0] == employee);
}

UTEST(MappersSuite, TestNonEmptyFilterIntersection) {
  std::vector<model::Employee> to_filter{kDefaultEmployee};

  EmployeeFilters filters = {{{"yandex_uid",
                               {std::vector<std::string>{"yandex_uid"},
                                std::vector<std::string>{"yandex_uid"}}}}};

  auto res =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters);

  ASSERT_TRUE(res[0] == kDefaultEmployee);
}

UTEST(MappersSuite, TestDifferentFilterTypes) {
  std::vector<model::Employee> to_filter{kDefaultEmployee};

  EmployeeFilters filters = {
      {{"yandex_uid",
        {std::vector<std::string>{"yandex_uid"}, std::vector<int>{10}}}}};

  auto res =
      utils::CallcenterFetcherFilter::FilterEmployees(to_filter, filters);

  ASSERT_TRUE(res[0] == kDefaultEmployee);
}
