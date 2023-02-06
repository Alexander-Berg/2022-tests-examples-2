#include <gtest/gtest.h>

#include <utils/helpers/json.hpp>

#include <models/parks/cars/retrieve_request_serialization.hpp>

namespace models::parks::cars {
namespace {

Json::Value MakeJsonArray(const std::initializer_list<std::string> list) {
  Json::Value result{Json::arrayValue};

  for (const auto& item : list) {
    result.append(item);
  }

  return result;
}

Json::Value MakeFields() {
  Json::Value fields{Json::objectValue};
  fields["car"] = MakeJsonArray({"number", "normalized_number"});
  return fields;
}

Json::Value MakeQuery() {
  Json::Value query{Json::objectValue};
  query["park"]["id"] = "xyz";
  query["park"]["car"]["id"] = "abcd";
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

  ASSERT_EQ(2u, request_model.fields.size());

  ASSERT_EQ("xyz", request_model.park_id);
  ASSERT_EQ("abcd", request_model.car_id);

  const auto dumped_request_json = DumpRetrieveRequest(request_model);
  ASSERT_EQ(dumped_request_json, request_json)
      << utils::helpers::WriteJson(dumped_request_json)
      << utils::helpers::WriteJson(request_json);
}

}  // namespace models::parks::cars
