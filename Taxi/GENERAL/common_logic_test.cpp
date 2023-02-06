#include "views/items/common_logic.hpp"

#include <gtest/gtest.h>

using namespace views::items::common_logic;

namespace {
struct RequestItemFields {
  std::optional<std::string> eats_item_id;
  std::optional<std::string> barcode;
  std::optional<std::string> vendor_code;
};
std::vector<handlers::ItemsToReplaceA> MakeRequestItems(
    std::vector<RequestItemFields>&& items_fields) {
  std::vector<handlers::ItemsToReplaceA> request_items;
  for (auto&& item_fields : items_fields) {
    handlers::ItemsToReplaceA request_item;
    request_item.eats_item_id = std::move(item_fields.eats_item_id);
    request_item.barcode = std::move(item_fields.barcode);
    request_item.vendor_code = std::move(item_fields.vendor_code);
    request_items.push_back(std::move(request_item));
  }
  return request_items;
}

struct ResponseItemFields {
  std::string item_id;
  std::vector<std::string> item_barcode_values;
  std::string item_vendor_code;
  std::optional<std::string> barcode;
  std::optional<std::string> sku;
};
utils::nomenclature_client::Response MakeResponseItems(
    std::vector<ResponseItemFields>&& items_fields) {
  std::vector<clients::eats_nomenclature::
                  BarcodeOrVendorCodeSearchResponseMatcheditemsA>
      response_items;
  for (auto&& item_fields : items_fields) {
    clients::eats_nomenclature::BarcodeOrVendorCodeSearchResponseMatcheditemsA
        response_item;
    response_item.item.origin_id = std::move(item_fields.item_id);
    response_item.item.barcode.values =
        std::move(item_fields.item_barcode_values);
    response_item.item.vendor_code = std::move(item_fields.item_vendor_code);
    response_item.barcode = std::move(item_fields.barcode);
    response_item.vendor_code = std::move(item_fields.sku);
    response_items.push_back(std::move(response_item));
  }
  utils::nomenclature_client::Response response;
  response.matched_items = std::move(response_items);
  return response;
}
}  // namespace

namespace {

TEST(MatchIntegrationItems, AddByBarcodeAndSku) {
  auto request_items = MakeRequestItems({{{}, "BARCODE", "VENDOR_CODE"}});
  const auto response_items =
      MakeResponseItems({{"", {}, "", "BARCODE", "VENDOR_CODE"}});
  const auto matched_items =
      MatchIntegrationItems(request_items, response_items);
  ASSERT_EQ(matched_items.size(), 1);

  const auto expected_match =
      std::make_pair(&request_items[0], &response_items.matched_items[0].item);
  ASSERT_EQ(matched_items[0], expected_match);
}

TEST(MatchIntegrationItems, AddByBarcodeAndVendorCode) {
  auto request_items = MakeRequestItems({{{}, "BARCODE", "VENDOR_CODE"}});
  const auto response_items =
      MakeResponseItems({{"", {}, "VENDOR_CODE", "BARCODE", {}}});
  const auto matched_items =
      MatchIntegrationItems(request_items, response_items);
  ASSERT_EQ(matched_items.size(), 1);

  const auto expected_match =
      std::make_pair(&request_items[0], &response_items.matched_items[0].item);
  ASSERT_EQ(matched_items[0], expected_match);
}

TEST(MatchIntegrationItems, AddByBarcodesAndSku) {
  auto request_items = MakeRequestItems({{{}, "BARCODE", "VENDOR_CODE"}});
  const auto response_items =
      MakeResponseItems({{"", {"BARCODE"}, "", {}, "VENDOR_CODE"}});
  const auto matched_items =
      MatchIntegrationItems(request_items, response_items);
  ASSERT_EQ(matched_items.size(), 1);

  const auto expected_match =
      std::make_pair(&request_items[0], &response_items.matched_items[0].item);
  ASSERT_EQ(matched_items[0], expected_match);
}

TEST(MatchIntegrationItems, AddByBarcodesAndVendorCode) {
  auto request_items = MakeRequestItems({{{}, "BARCODE", "VENDOR_CODE"}});
  const auto response_items =
      MakeResponseItems({{"", {"BARCODE"}, "VENDOR_CODE", {}, {}}});
  const auto matched_items =
      MatchIntegrationItems(request_items, response_items);
  ASSERT_EQ(matched_items.size(), 1);

  const auto expected_match =
      std::make_pair(&request_items[0], &response_items.matched_items[0].item);
  ASSERT_EQ(matched_items[0], expected_match);
}

TEST(MatchIntegrationItems, AddByEatsItemId) {
  auto request_items = MakeRequestItems({{"ID", {}, {}}});
  const auto response_items = MakeResponseItems({{"ID", {}, "", {}, {}}});
  const auto matched_items =
      MatchIntegrationItems(request_items, response_items);
  ASSERT_EQ(matched_items.size(), 1);

  const auto expected_match =
      std::make_pair(&request_items[0], &response_items.matched_items[0].item);
  ASSERT_EQ(matched_items[0], expected_match);
}

TEST(MatchIntegrationItems, AddBySku) {
  auto request_items = MakeRequestItems({{{}, {}, "VENDOR_CODE"}});
  const auto response_items =
      MakeResponseItems({{"", {}, "", {}, "VENDOR_CODE"}});
  const auto matched_items =
      MatchIntegrationItems(request_items, response_items);
  ASSERT_EQ(matched_items.size(), 1);

  const auto expected_match =
      std::make_pair(&request_items[0], &response_items.matched_items[0].item);
  ASSERT_EQ(matched_items[0], expected_match);
}

TEST(MatchIntegrationItems, AddByVendorCode) {
  auto request_items = MakeRequestItems({{{}, {}, "VENDOR_CODE"}});
  const auto response_items =
      MakeResponseItems({{"", {}, "VENDOR_CODE", {}, {}}});
  const auto matched_items =
      MatchIntegrationItems(request_items, response_items);
  ASSERT_EQ(matched_items.size(), 1);

  const auto expected_match =
      std::make_pair(&request_items[0], &response_items.matched_items[0].item);
  ASSERT_EQ(matched_items[0], expected_match);
}

TEST(MatchIntegrationItems, AddByItemBarcodes) {
  auto request_items = MakeRequestItems({{{}, "BARCODE", {}}});
  const auto response_items =
      MakeResponseItems({{"", {"BARCODE"}, "", {}, {}}});
  const auto matched_items =
      MatchIntegrationItems(request_items, response_items);
  ASSERT_EQ(matched_items.size(), 1);
  const auto expected_match =
      std::make_pair(&request_items[0], &response_items.matched_items[0].item);
  ASSERT_EQ(matched_items[0], expected_match);
}

TEST(MatchIntegrationItems, AddByBarcode) {
  auto request_items = MakeRequestItems({{{}, "BARCODE", {}}});
  const auto response_items = MakeResponseItems({{"", {}, "", "BARCODE", {}}});
  const auto matched_items =
      MatchIntegrationItems(request_items, response_items);
  ASSERT_EQ(matched_items.size(), 1);
  const auto expected_match =
      std::make_pair(&request_items[0], &response_items.matched_items[0].item);
  ASSERT_EQ(matched_items[0], expected_match);
}

TEST(MatchIntegrationItems, FailAddItemIdIsPresentButNotMatched) {
  auto request_items = MakeRequestItems({{"ID", "BARCODE", "VENDOR_CODE"}});
  const auto response_items = MakeResponseItems({
      {"ID1", {"BARCODE"}, "VENDOR_CODE", "BARCODE", "VENDOR_CODE"},
      {"ID2", {"BARCODE"}, "VENDOR_CODE", "BARCODE", "VENDOR_CODE"},
      {"ID3", {"BARCODE"}, "VENDOR_CODE", "BARCODE", "VENDOR_CODE"},
  });
  const auto matched_items =
      MatchIntegrationItems(request_items, response_items);
  ASSERT_EQ(matched_items.size(), 0);
}

TEST(MatchIntegrationItems, PriorityEatsItemId) {
  auto request_items = MakeRequestItems({{"ID2", "BARCODE", "VENDOR_CODE"}});
  const auto response_items = MakeResponseItems({
      {"ID1", {"BARCODE"}, "VENDOR_CODE", "BARCODE", "VENDOR_CODE"},
      {"ID2", {}, "", {}, {}},
  });
  const auto matched_items =
      MatchIntegrationItems(request_items, response_items);
  ASSERT_EQ(matched_items.size(), 1);

  const auto expected_match =
      std::make_pair(&request_items[0], &response_items.matched_items[1].item);
  ASSERT_EQ(matched_items[0], expected_match);
}

TEST(MatchIntegrationItems, PriorityVendorCode) {
  auto request_items = MakeRequestItems({{{}, "BARCODE", "VENDOR_CODE"}});
  const auto response_items = MakeResponseItems({
      {"ID1", {"BARCODE"}, "", "BARCODE", "VENDOR_CODE"},
      {"ID2", {"BARCODE"}, "VENDOR_CODE", "BARCODE", {}},
  });
  const auto matched_items =
      MatchIntegrationItems(request_items, response_items);
  ASSERT_EQ(matched_items.size(), 1);

  const auto expected_match =
      std::make_pair(&request_items[0], &response_items.matched_items[1].item);
  ASSERT_EQ(matched_items[0], expected_match);
}

TEST(MatchIntegrationItems, SkipMatchingBarcode) {
  auto request_items = MakeRequestItems({{{}, "BARCODE", "VENDOR_CODE"}});
  const auto response_items = MakeResponseItems({
      {"", {"BARCODE"}, "", "BARCODE", {}},
      {"", {"BARCODE"}, "", "BARCODE", {}},
      {"", {"BARCODE"}, "", "BARCODE", {}},
      {"", {"BARCODE"}, "VENDOR_CODE", "BARCODE", {}},
  });
  const auto matched_items =
      MatchIntegrationItems(request_items, response_items);
  ASSERT_EQ(matched_items.size(), 1);

  const auto expected_match =
      std::make_pair(&request_items[0], &response_items.matched_items[3].item);
  ASSERT_EQ(matched_items[0], expected_match);
}

}  // namespace
