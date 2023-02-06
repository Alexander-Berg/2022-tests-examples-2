#include <gtest/gtest.h>

#include <utils/helpers/json.hpp>

#include <models/parks/driver_profiles/list_request_serialization.hpp>

namespace models::parks::driver_profiles {
namespace {

const models::driver_categories::CarCategories kAllCarCategories{"mkk", "vip"};

Json::Value MakeJsonArray(const std::initializer_list<std::string> list) {
  Json::Value result{Json::arrayValue};

  for (const auto& item : list) {
    result.append(item);
  }

  return result;
}

Json::Value MakeFields() {
  Json::Value fields{Json::objectValue};

  fields["park"] = MakeJsonArray({"id", "asd"});
  fields["driver_profile"] = MakeJsonArray({"id", "qwe"});
  fields["car"] = MakeJsonArray({"id", "try"});
  fields["account"] = MakeJsonArray({"id", "uio"});
  fields["current_status"] = MakeJsonArray({"status", "status_updated_at"});

  Json::Value aggregate_fields{Json::objectValue};
  aggregate_fields["account"] = MakeJsonArray({"positive_balance_sum", "oh"});
  fields["aggregate"] = std::move(aggregate_fields);

  return fields;
}

Json::Value MakeDefaultFields() {
  Json::Value fields{Json::objectValue};

  fields["park"] = MakeJsonArray({"id"});
  fields["driver_profile"] = MakeJsonArray({"id"});

  return fields;
}

Json::Value MakeQuery() {
  Json::Value query{Json::objectValue};
  query["park"]["id"] = "123";
  query["text"] = "qer";
  query["park"]["driver_profile"]["id"] = MakeJsonArray({"id", "asd"});
  query["park"]["driver_profile"]["work_rule_id"] = MakeJsonArray({"asd"});
  query["park"]["driver_profile"]["work_status"] = MakeJsonArray({"id", "asd"});
  query["park"]["car"]["id"] = MakeJsonArray({"asd", "qwe"});
  query["park"]["car"]["amenities"] = MakeJsonArray({"wifi", "ski", "rug"});
  query["park"]["car"]["categories"] = MakeJsonArray({"vip"});
  query["park"]["car"]["categories_filter"] = MakeJsonArray({"mkk", "vip"});
  query["park"]["current_status"]["status"] = MakeJsonArray({"free", "busy"});

  return query;
}

Json::Value MakeSortOrder() {
  const auto make_field_sort = [](std::string field, std::string direction) {
    Json::Value field_sort{Json::objectValue};
    field_sort["field"] = field;
    field_sort["direction"] = direction;
    return field_sort;
  };

  Json::Value sort_order{Json::arrayValue};
  sort_order.append(make_field_sort("driver_profile.last_name", "asc"));
  sort_order.append(make_field_sort("driver_profile.middle_name", "asc"));
  sort_order.append(make_field_sort("driver_profile.first_name", "desc"));
  sort_order.append(make_field_sort("driver_profile.created_date", "desc"));
  sort_order.append(make_field_sort("account.current.balance", "desc"));

  return sort_order;
}

Json::Value MakeRequest() {
  Json::Value request{Json::objectValue};
  request["offset"] = 1u;
  request["limit"] = 2u;
  request["query"] = MakeQuery();
  request["fields"] = MakeFields();
  request["required"] = MakeJsonArray({"car"});
  request["sort_order"] = MakeSortOrder();

  return request;
}

Json::Value MakeRequestForRemovedDriver() {
  auto request = MakeRequest();
  request["removed_drivers_mode"] = "hide_all_fields";
  return request;
}

}  // namespace

TEST(DriverProfilesListRequest, DefaultRemovedMode) {
  const auto jrequest = MakeRequest();
  const auto str_request = utils::helpers::WriteJson(jrequest);
  const auto parsed = ParseListRequest(str_request, kAllCarCategories);

  ASSERT_EQ(models::parks::driver_profiles::RemovedDriversMode::AsNormalDriver,
            parsed.removed_drivers_mode);
}

TEST(DriverProfilesListRequest, Serialization) {
  const auto jrequest = MakeRequestForRemovedDriver();
  const auto str_request = utils::helpers::WriteJson(jrequest);
  const auto parsed = ParseListRequest(str_request, kAllCarCategories);

  ASSERT_EQ(1u, parsed.offset);
  ASSERT_TRUE(static_cast<bool>(parsed.limit));
  ASSERT_EQ(2u, *parsed.limit);

  ASSERT_EQ(2u, parsed.fields.account.size());
  ASSERT_EQ(2u, parsed.fields.park.size());
  ASSERT_EQ(2u, parsed.fields.car.size());
  ASSERT_EQ(2u, parsed.fields.driver_profile.size());
  ASSERT_EQ(2u, parsed.fields.current_status.size());

  ASSERT_EQ("123", parsed.park_id);
  ASSERT_EQ(2u, parsed.driver_profile_id.size());
  ASSERT_EQ(2u, parsed.work_status.size());
  ASSERT_EQ(1u, parsed.work_rule_id.size());
  ASSERT_EQ(2u, parsed.car_id.size());
  ASSERT_EQ(3u, parsed.car_amenities.size());
  ASSERT_EQ(1u, parsed.car_categories.size());
  ASSERT_EQ(2u, parsed.car_categories_filter.size());
  ASSERT_EQ(2u, parsed.current_status.size());
  ASSERT_EQ("qer", parsed.text);

  ASSERT_TRUE(parsed.car_required);

  ASSERT_EQ(5u, parsed.sort_order.size());

  const auto jdumped = DumpListRequest(parsed);
  ASSERT_EQ(jdumped, jrequest) << utils::helpers::WriteJson(jdumped)
                               << utils::helpers::WriteJson(jrequest);
}

TEST(DriverProfilesListRequest, SerializationNoOffsetLimit) {
  Json::Value jrequest{Json::objectValue};
  jrequest["query"] = MakeQuery();
  jrequest["removed_drivers_mode"] = "hide_all_fields";

  const auto str_request = utils::helpers::WriteJson(jrequest);
  const auto parsed = ParseListRequest(str_request, kAllCarCategories);

  ASSERT_EQ(parsed.offset, 0u);
  ASSERT_FALSE(static_cast<bool>(parsed.limit));

  const auto jdumped = DumpListRequest(parsed);

  // extend expected with default values
  jrequest["fields"] = MakeDefaultFields();
  ASSERT_EQ(jdumped, jrequest) << utils::helpers::WriteJson(jdumped)
                               << utils::helpers::WriteJson(jrequest);
}

}  // namespace models::parks::driver_profiles
