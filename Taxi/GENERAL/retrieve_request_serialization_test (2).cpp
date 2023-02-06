#include <gtest/gtest.h>

#include <utils/helpers/json.hpp>

#include <models/parks/driver_profiles/retrieve_request_serialization.hpp>

namespace models::parks::driver_profiles {
namespace {

Json::Value GetJsonArray(const std::initializer_list<std::string> list) {
  Json::Value result{Json::arrayValue};

  for (const auto& item : list) {
    result.append(item);
  }

  return result;
}

Json::Value MakeFields() {
  Json::Value fields{Json::objectValue};
  fields["account"] = GetJsonArray({"id", "uio", "balance"});
  fields["car"] = GetJsonArray({"number"});
  fields["driver_profile"] = GetJsonArray({"id", "qwe"});
  fields["current_status"] = GetJsonArray({"sts", "ewqr"});
  fields["rating"] = GetJsonArray({"123", "456"});
  fields["driver_categories"] = GetJsonArray({"driver_restriction"});
  return fields;
}

Json::Value MakeQuery() {
  Json::Value query{Json::objectValue};
  query["park"]["id"] = "xyz";
  query["park"]["driver_profile"]["id"] = "abcd";
  return query;
}

Json::Value MakeRequest() {
  Json::Value request{Json::objectValue};
  request["query"] = MakeQuery();
  request["fields"] = MakeFields();
  return request;
}

}  // namespace

TEST(DriverProfilesRetrieveRequest, Serialization) {
  const auto& request_json = MakeRequest();
  const auto& request_body = utils::helpers::WriteJson(request_json);
  const auto& request_model = ParseRetrieveRequest(request_body, {});

  ASSERT_EQ(3u, request_model.account_fields.size());
  ASSERT_EQ(1u, request_model.car_fields.size());
  ASSERT_EQ(2u, request_model.driver_profile_fields.size());
  ASSERT_EQ(2u, request_model.current_status_fields.size());
  ASSERT_EQ(2u, request_model.ratings_fields.size());
  ASSERT_EQ(1u, request_model.driver_categories_fields.size());

  ASSERT_EQ("xyz", request_model.park_id);
  ASSERT_EQ("abcd", request_model.driver_profile_id);

  const auto dumped_request_json = DumpRetrieveRequest(request_model);
  ASSERT_EQ(dumped_request_json, request_json)
      << utils::helpers::WriteJson(dumped_request_json)
      << utils::helpers::WriteJson(request_json);
}

}  // namespace models::parks::driver_profiles
