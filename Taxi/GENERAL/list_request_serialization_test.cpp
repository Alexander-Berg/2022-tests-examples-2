#include <gtest/gtest.h>

#include <utils/helpers/json.hpp>

#include <models/parks/cars/list_request_serialization.hpp>

namespace models::parks::cars {
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
  fields["car"] = MakeJsonArray({"id", "try"});
  return fields;
}

Json::Value MakeDefaultFields() {
  Json::Value fields{Json::objectValue};
  fields["car"] = MakeJsonArray({"id"});
  return fields;
}

Json::Value MakeQuery() {
  Json::Value query{Json::objectValue};

  query["park"]["id"] = "123";
  query["park"]["car"]["id"] = MakeJsonArray({"asd"});
  query["park"]["car"]["status"] = MakeJsonArray({"sid", "ssd"});
  query["park"]["car"]["amenities"] = MakeJsonArray({"pos", "ski", "rug"});
  query["park"]["car"]["categories"] = MakeJsonArray({"mkk"});
  query["park"]["car"]["categories_filter"] = MakeJsonArray({"mkk", "vip"});
  query["text"] = "qer";

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
  sort_order.append(make_field_sort("car.call_sign", "asc"));
  sort_order.append(make_field_sort("car.created_date", "asc"));
  sort_order.append(make_field_sort("car.normalized_number", "desc"));

  return sort_order;
}

Json::Value MakeRequest() {
  Json::Value request{Json::objectValue};

  request["offset"] = 1u;
  request["limit"] = 2u;
  request["query"] = MakeQuery();
  request["fields"] = MakeFields();
  request["sort_order"] = MakeSortOrder();

  return request;
}

}  // namespace

TEST(CarsListRequest, Serialization) {
  const auto jrequest = MakeRequest();
  const auto str_request = utils::helpers::WriteJson(jrequest);
  const auto parsed = ParseListRequest(str_request, kAllCarCategories);

  ASSERT_EQ(1u, parsed.offset);
  ASSERT_TRUE(static_cast<bool>(parsed.limit));
  ASSERT_EQ(2u, *parsed.limit);

  ASSERT_EQ(2u, parsed.fields.size());

  ASSERT_EQ("123", parsed.park_id);
  ASSERT_EQ(1u, parsed.car_id.size());
  ASSERT_EQ(2u, parsed.status.size());
  ASSERT_EQ(3u, parsed.amenities.size());
  ASSERT_EQ(1u, parsed.categories.size());
  ASSERT_EQ(2u, parsed.categories_filter.size());
  ASSERT_EQ("qer", parsed.text);

  ASSERT_EQ(3u, parsed.sort_order.size());

  const auto jdumped = DumpListRequest(parsed);
  ASSERT_EQ(jdumped, jrequest) << utils::helpers::WriteJson(jdumped)
                               << utils::helpers::WriteJson(jrequest);
}

TEST(CarsListRequest, SerializationNoOffsetLimit) {
  Json::Value jrequest{Json::objectValue};
  jrequest["query"] = MakeQuery();

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

}  // namespace models::parks::cars
