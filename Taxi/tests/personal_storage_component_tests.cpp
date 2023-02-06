#include <userver/utest/utest.hpp>

#include <boost/range/algorithm/transform.hpp>
#include <clients/personal/client_gmock.hpp>
#include <components/personal_storage.hpp>

namespace retrieve_email = ::clients::personal::v1_data_type_retrieve::post;
namespace bulk_retrieve_email =
    ::clients::personal::v1_data_type_bulk_retrieve::post;

namespace clients::personal::v1_data_type_retrieve::post {
inline bool operator==(const Request& l, const Request& r) {
  return std::tie(l.data_type, l.body.id, l.body.primary_replica) ==
         std::tie(r.data_type, r.body.id, r.body.primary_replica);
}
}  // namespace clients::personal::v1_data_type_retrieve::post

namespace clients::personal::v1_data_type_bulk_retrieve::post {
inline bool operator==(const Request& l, const Request& r) {
  return std::tie(l.data_type, l.body.items, l.body.primary_replica) ==
         std::tie(r.data_type, r.body.items, r.body.primary_replica);
}
}  // namespace clients::personal::v1_data_type_bulk_retrieve::post

namespace clients::codegen {
inline bool operator==(const CommandControl& l, const CommandControl& r) {
  return std::tie(l.retries, l.timeout) == std::tie(r.retries, r.timeout);
}
}  // namespace clients::codegen

namespace testing {

using PersonalClient = eats_partners::models::personal::Client;
using Email = eats_partners::types::email::Email;

static const auto storage_data = std::unordered_map<std::string, std::string>{
    std::make_pair("111", "partner1@partner.com"),
    std::make_pair("222", "partner2@partner.com"),
    std::make_pair("333", "partner3@partner.com"),
    std::make_pair("444", "partner4@partner.com")};

struct PersonalStorageComponentTest : public Test {
  std::shared_ptr<StrictMock<clients::personal::ClientGMock>> personal_gmock;
  eats_partners::components::personal_storage::ComponentImpl component_impl;

  PersonalStorageComponentTest()
      : personal_gmock(
            std::make_shared<StrictMock<clients::personal::ClientGMock>>()),
        component_impl(std::make_shared<PersonalClient>(*personal_gmock)) {}
};

TEST_F(PersonalStorageComponentTest, get_empty) {
  ASSERT_EQ(component_impl.GetEmailByPersonalId(std::nullopt), std::nullopt);
}

struct PersonalStorageComponentParamsTest
    : ::testing::TestWithParam<
          std::pair<std::string, std::optional<std::string>>> {
  std::shared_ptr<StrictMock<clients::personal::ClientGMock>> personal_gmock;
  eats_partners::components::personal_storage::ComponentImpl component_impl;

  PersonalStorageComponentParamsTest()
      : personal_gmock(
            std::make_shared<StrictMock<clients::personal::ClientGMock>>()),
        component_impl(std::make_shared<PersonalClient>(*personal_gmock)) {}
};

INSTANTIATE_TEST_SUITE_P(
    results, PersonalStorageComponentParamsTest,
    ::testing::Values(std::make_pair("111", "partner1@partner.com"),
                      std::make_pair("222", "partner2@partner.com"),
                      std::make_pair("333", "partner3@partner.com"),
                      std::make_pair("444", "partner4@partner.com"),
                      std::make_pair("555", std::nullopt),
                      std::make_pair("", std::nullopt)));

TEST_P(PersonalStorageComponentParamsTest, get_retrive_data) {
  const auto data = GetParam();
  std::optional<std::string> expected_eq{};

  auto [key, expected] = data;

  const auto request = retrieve_email::Request{
      clients::personal::DataType::kEmails, {key, false}};
  const auto control = clients::personal::CommandControl{};

  if (storage_data.count(key) > 0) {
    const auto response = retrieve_email::Response200{
        clients::personal::PersonalRetrieveResponse{key, storage_data.at(key)}};

    EXPECT_CALL(*personal_gmock, V1DataTypeRetrieve(request, control))
        .WillOnce(Return(response));
  } else {
    const auto error = clients::personal::Error{
        std::string("404"), std::string("Personal not found")};
    const auto response = retrieve_email::Response404();

    EXPECT_CALL(*personal_gmock, V1DataTypeRetrieve(request, control))
        .WillOnce(Throw(response));
  }
  const auto result = component_impl.GetEmailByPersonalId(key);
  if (result) {
    expected_eq = result->GetUnderlying();
  }
  ASSERT_EQ(expected, expected_eq);
}

struct PersonalStorageComponentParamsBulkTest
    : ::testing::TestWithParam<std::pair<
          std::vector<std::string>, std::unordered_map<std::string, Email>>> {
  std::shared_ptr<StrictMock<clients::personal::ClientGMock>> personal_gmock;
  eats_partners::components::personal_storage::ComponentImpl component_impl;

  PersonalStorageComponentParamsBulkTest()
      : personal_gmock(
            std::make_shared<StrictMock<clients::personal::ClientGMock>>()),
        component_impl(std::make_shared<PersonalClient>(*personal_gmock)) {}
};

INSTANTIATE_TEST_SUITE_P(
    results, PersonalStorageComponentParamsBulkTest,
    ::testing::Values(
        std::make_pair(std::vector<std::string>{},
                       std::unordered_map<std::string, Email>{}),
        std::make_pair(std::vector<std::string>{"qwertyu", "qaz", "wefsd"},
                       std::unordered_map<std::string, Email>{}),
        std::make_pair(std::vector<std::string>{"111"},
                       std::unordered_map<std::string, Email>{std::make_pair(
                           "111", Email{storage_data.at("111")})}),
        std::make_pair(std::vector<std::string>{"111", "222", "333"},
                       std::unordered_map<std::string, Email>{
                           std::make_pair("111", Email{storage_data.at("111")}),
                           std::make_pair("222", Email{storage_data.at("222")}),
                           std::make_pair("333", Email{storage_data.at("333")}),
                       }),
        std::make_pair(std::vector<std::string>{"222", "000", "333", "QAZ"},
                       std::unordered_map<std::string, Email>{
                           std::make_pair("222", Email{storage_data.at("222")}),
                           std::make_pair("333", Email{storage_data.at("333")}),
                       }),
        std::make_pair(std::vector<std::string>{"000", "QAZ", "444"},
                       std::unordered_map<std::string, Email>{
                           std::make_pair("444", Email{storage_data.at("444")}),
                       }),
        std::make_pair(std::vector<std::string>{"000", "QAZ", "444"},
                       std::unordered_map<std::string, Email>{
                           std::make_pair("444", Email{storage_data.at("444")}),
                       }),
        std::make_pair(std::vector<std::string>{"111", "222", "333", "444"},
                       std::unordered_map<std::string, Email>{
                           std::make_pair("111", Email{storage_data.at("111")}),
                           std::make_pair("222", Email{storage_data.at("222")}),
                           std::make_pair("333", Email{storage_data.at("333")}),
                           std::make_pair("444", Email{storage_data.at("444")}),
                       })));

TEST_P(PersonalStorageComponentParamsBulkTest, get_retrive_bulk_data) {
  const auto data = GetParam();
  std::optional<std::string> expected_eq{};

  auto [keys, expected] = data;

  std::vector<clients::personal::BulkRetrieveRequestItem> request_ids;
  request_ids.reserve(keys.size());

  boost::transform(keys, std::back_insert_iterator(request_ids), [](auto& id) {
    return clients::personal::BulkRetrieveRequestItem{{id}};
  });

  const auto request = bulk_retrieve_email::Request{
      clients::personal::DataType::kEmails, {request_ids, false}};
  const auto control = clients::personal::CommandControl{};

  if (request_ids.size() > 0) {
    ::std::vector<clients::personal::BulkRetrieveResponseItem> items{};
    for (const auto& key : keys) {
      if (storage_data.count(key) > 0) {
        items.push_back(clients::personal::BulkRetrieveResponseItem{
            key, storage_data.at(key)});
      }
    }
    const auto response =
        clients::personal::PersonalBulkRetrieveResponse{items};

    EXPECT_CALL(*personal_gmock, V1DataTypeBulkRetrieve(request, control))
        .WillOnce(Return(bulk_retrieve_email::Response200{response}));
  }
  const auto result = component_impl.GetEmailsByPersonalIds(keys);
  ASSERT_EQ(expected, result);
}

}  // namespace testing
