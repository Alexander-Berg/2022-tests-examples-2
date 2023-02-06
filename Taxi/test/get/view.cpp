#include <views/v1/client/test/get/view.hpp>

#include <clients/example-replica/client.hpp>

#include <userver/utils/assert.hpp>

namespace {
template <class Request, class Client, class RequestFunction>
void CheckRetrieveResponse(Client& client, RequestFunction request_function) {
  std::vector<std::string> ids{"example_1", "unknown_id"};
  Request proxy_retrieve_request{{ids, {}}, "test_client"};

  auto proxy_retrieve_response =
      (client.*request_function)(proxy_retrieve_request, {});

  auto resp_items = proxy_retrieve_response.examples;

  UASSERT(!resp_items.empty());

  UASSERT(resp_items.size() == 2);
  auto exampleItem = resp_items.at(0);
  UASSERT(exampleItem.example_id == "example_1");
  UASSERT(bool(exampleItem.data));
  UASSERT(*exampleItem.data->example_main_field == "example_1_main_field");
  UASSERT(*exampleItem.data->example_additional_field ==
          "example_1_additional_field");
  UASSERT(bool(exampleItem.data->example_object_type_field));
  UASSERT(*exampleItem.data->example_object_type_field->bool_field == true);

  auto emptyItem = resp_items.at(1);
  UASSERT(emptyItem.example_id == "unknown_id");
  UASSERT(!bool(emptyItem.data));

  std::vector<std::string> projection{"data.example_additional_field"};

  Request proxy_retrieve_request2{{ids, projection}, "test_client"};

  auto proxy_retrieve_response2 =
      (client.*request_function)(proxy_retrieve_request2, {});
  resp_items = proxy_retrieve_response2.examples;
  UASSERT(resp_items.size() == 2);
  exampleItem = resp_items.at(0);
  UASSERT(exampleItem.example_id == "example_1");
  UASSERT(bool(exampleItem.data));
  UASSERT(!bool(exampleItem.data->example_main_field));
  UASSERT(*exampleItem.data->example_additional_field ==
          "example_1_additional_field");
  UASSERT(!bool(exampleItem.data->example_object_type_field));

  emptyItem = resp_items.at(1);
  UASSERT(emptyItem.example_id == "unknown_id");
  UASSERT(!bool(emptyItem.data));
}
}  // namespace

namespace handlers::v1_client_test::get {

Response View::Handle(Request&& /*request*/, Dependencies&& dependencies) {
  CheckRetrieveResponse<
      clients::example_replica::v1_examples_proxy_retrieve::post::Request>(
      dependencies.example_replica_client,
      &clients::example_replica::Client::ExampleProxyRetrieve);

  CheckRetrieveResponse<
      clients::example_replica::v1_examples_retrieve::post::Request>(
      dependencies.example_replica_client,
      &clients::example_replica::Client::ExampleRetrieve);

  clients::example_replica::v1_examples_retrieve_by_main::post::Request
      retrieve_by_main_request;
  retrieve_by_main_request.consumer = "test_client";
  retrieve_by_main_request.body.main_field_in_set = {"example_1_main_field",
                                                     "unknown"};
  retrieve_by_main_request.body.projection = std::nullopt;
  auto resp = dependencies.example_replica_client.ExampleRetrieveByMain(
      retrieve_by_main_request, {});
  auto resp_items = resp.examples_by_main;
  UASSERT(resp_items.size() == 2);
  UASSERT(resp_items.at(0).main_field == "example_1_main_field");
  clients::example_replica::ExampleItem expected_item{
      "example_1", std::string{"0_1234567_1"},
      clients::example_replica::ExampleItemData{
          std::string{"example_1_main_field"},
          std::string{"example_1_additional_field"},
          clients::example_replica::ExampleItemDataExampleobjecttypefield{
              {true}}}};
  UASSERT(resp_items.at(0).examples.size() == 1);
  UASSERT(resp_items.at(0).examples.at(0) == expected_item);

  UASSERT(resp_items.at(1).main_field == "unknown");
  UASSERT(resp_items.at(1).examples.empty());

  return Response200{};
}

}  // namespace handlers::v1_client_test::get
