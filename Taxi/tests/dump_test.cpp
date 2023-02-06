#include <gtest/gtest.h>

#include <api_base/cache_dumper.hpp>
#include <api_base/model.hpp>
#include <api_base/utils.hpp>

#include <functional>
#include <set>

#include <userver/cache/statistics_mock.hpp>

namespace {
struct TestInnerStruct {
  std::string str_field;

  std::size_t Save(std::ostream& out) const {
    std::size_t length = 0;
    length += api_over_db::utils::SaveToDump(out, str_field);
    return length;
  }

  void Load(std::istream& in) {
    api_over_db::utils::LoadFromDump(in, str_field);
  }

  bool IsDeleted() const { return false; }

  bool operator==(const TestInnerStruct& other) const {
    return str_field == other.str_field;
  }
};

struct TestModel final {
  std::string required_str_field1;
  std::string required_str_field2;
  std::optional<std::string> optional_str_field1;
  std::optional<std::string> optional_str_field2;
  std::optional<std::string> optional_str_field3;
  std::optional<std::string> optional_str_field4;
  std::optional<std::string> optional_str_field5;
  std::vector<TestInnerStruct> struct_vector_field1;
  std::vector<TestInnerStruct> struct_vector_field2;
  formats::bson::Timestamp mongo_timestamp;
  bool is_deleted{false};

  std::string GetId() const {
    return required_str_field1 + "_" + required_str_field2;
  }

  std::size_t Save(std::ostream& out) const {
    std::size_t length = 0;
    length += api_over_db::utils::SaveToDump(out, required_str_field1);
    length += api_over_db::utils::SaveToDump(out, required_str_field2);
    length += api_over_db::utils::SaveToDump(out, optional_str_field1);
    length += api_over_db::utils::SaveToDump(out, optional_str_field2);
    length += api_over_db::utils::SaveToDump(out, optional_str_field3);
    length += api_over_db::utils::SaveToDump(out, optional_str_field4);
    length += api_over_db::utils::SaveToDump(out, optional_str_field5);
    length += api_over_db::utils::SaveToDump(out, struct_vector_field1);
    length += api_over_db::utils::SaveToDump(out, struct_vector_field2);
    length += api_over_db::utils::SaveToDump(out, is_deleted);
    length += api_over_db::utils::SaveToDump(out, mongo_timestamp);
    return length;
  }

  void Load(std::istream& in) {
    api_over_db::utils::LoadFromDump(in, required_str_field1);
    api_over_db::utils::LoadFromDump(in, required_str_field2);
    api_over_db::utils::LoadFromDump(in, optional_str_field1);
    api_over_db::utils::LoadFromDump(in, optional_str_field2);
    api_over_db::utils::LoadFromDump(in, optional_str_field3);
    api_over_db::utils::LoadFromDump(in, optional_str_field4);
    api_over_db::utils::LoadFromDump(in, optional_str_field5);
    api_over_db::utils::LoadFromDump(in, struct_vector_field1);
    api_over_db::utils::LoadFromDump(in, struct_vector_field2);
    api_over_db::utils::LoadFromDump(in, is_deleted);
    api_over_db::utils::LoadFromDump(in, mongo_timestamp);
  }

  bool operator==(const TestModel& other) const {
    return required_str_field1 == other.required_str_field1 &&
           required_str_field2 == other.required_str_field2 &&
           optional_str_field1 == other.optional_str_field1 &&
           optional_str_field2 == other.optional_str_field2 &&
           optional_str_field3 == other.optional_str_field3 &&
           optional_str_field4 == other.optional_str_field4 &&
           optional_str_field5 == other.optional_str_field5 &&
           struct_vector_field1 == other.struct_vector_field1 &&
           struct_vector_field2 == other.struct_vector_field2 &&
           is_deleted == other.is_deleted &&
           mongo_timestamp == other.mongo_timestamp;
  }

  bool IsDeleted() const { return is_deleted; }
  virtual formats::bson::Timestamp GetTimestamp() const {
    return mongo_timestamp;
  }
};

struct TestCacheDumpModelTraits {
  static constexpr const char* kLogPrefix = "test-cache : ";
  using ItemType = TestModel;
  using Timestamp = formats::bson::Timestamp;
  enum class IndicesEnum { kCount };
  static const std::vector<
      std::function<std::set<std::optional<std::string>>(const ItemType& item)>>
      kKeysByIndex;
  static constexpr bool kEraseDeleted = false;
};

const std::vector<std::function<std::set<std::optional<std::string>>(
    const TestCacheDumpModelTraits::ItemType& item)>>
    TestCacheDumpModelTraits::kKeysByIndex{};

using TestCacheDumpModel = api_over_db::CacheModel<TestCacheDumpModelTraits>;

static const std::string reference_dump =
    R"=({"cursor":"0_3_3","lagging_cursor":"0_0_0","size":1}
8 park_id310 driver_id310 first	name11 middle
name4 last-1 -1 0 2 3 6543 3210 3 2 )=";

std::string GetStringFromFile(const std::string& file_name) {
  std::ifstream ifs(file_name);
  return std::string((std::istreambuf_iterator<char>(ifs)),
                     (std::istreambuf_iterator<char>()));
}
}  // namespace

TEST(ApiOverDbDumper, DumpCacheFormat) {
  TestCacheDumpModel cache_model;

  TestModel test_item;
  test_item.required_str_field1 = "park_id3";
  test_item.required_str_field2 = "driver_id3";
  test_item.optional_str_field1 = std::optional<std::string>("first\tname");
  test_item.optional_str_field2 = std::optional<std::string>("middle\nname");
  test_item.optional_str_field3 = std::optional<std::string>("last\0name");
  test_item.optional_str_field4 = std::nullopt;
  test_item.optional_str_field5 = std::nullopt;
  test_item.struct_vector_field1 = {};
  test_item.struct_vector_field2 = {{"654"}, {"321"}};
  test_item.is_deleted = false;
  test_item.mongo_timestamp = formats::bson::Timestamp{3, 2};
  cache_model.Upsert(std::make_shared<TestModel>(test_item));

  cache_model.SetCursor(formats::bson::Timestamp{3, 3});

  auto cache_model_ptr = std::make_shared<TestCacheDumpModel>(cache_model);

  api_over_db::DumpContext dump_context("test-dump", "1");

  api_over_db::DumpCacheInFile<TestCacheDumpModel>(
      cache_model_ptr, "./test-dump/", "", 1, -1, dump_context);

  auto file_list =
      api_over_db::GetMatchedFiles("./test-dump/", dump_context, true);
  ASSERT_EQ(1, file_list.size());

  std::string dump =
      GetStringFromFile("./test-dump/" + file_list.begin()->filename);
  EXPECT_EQ(reference_dump, dump);
}

template <class Map>
void test_equal_pointer_maps(const Map& m1, const Map& m2) {
  EXPECT_EQ(m1.size(), m2.size());
  for (const auto& [key, value] : m1) {
    EXPECT_EQ(1, m2.count(key));
    const auto& value2 = m2.at(key);
    EXPECT_EQ(*value, *value2);
  }
}

TEST(ApiOverDbDumper, DumpCacheSaveAndLoad) {
  // Too big to store on stack
  auto cache_model = std::make_shared<TestCacheDumpModel>();

  {
    TestModel test_item;
    test_item.required_str_field1 = "park_id1";
    test_item.required_str_field2 = "driver_id1";
    test_item.optional_str_field1 = std::optional<std::string>("first\tname");
    test_item.optional_str_field2 = std::optional<std::string>("middle\nname");
    test_item.optional_str_field3 = std::optional<std::string>("last\0name");
    test_item.optional_str_field4 = std::nullopt;
    test_item.optional_str_field5 = std::nullopt;
    test_item.struct_vector_field1 = {};
    test_item.struct_vector_field2 = {{"654"}, {"321"}};
    test_item.is_deleted = false;
    test_item.mongo_timestamp = formats::bson::Timestamp{1, 1};
    cache_model->Upsert(std::make_shared<TestModel>(test_item));
  }

  {
    TestModel test_item;
    test_item.required_str_field1 = "park_id2";
    test_item.required_str_field2 = "driver_id2";
    test_item.optional_str_field1 = std::nullopt;
    test_item.optional_str_field2 = std::optional<std::string>("middle name2");
    test_item.optional_str_field3 = std::optional<std::string>("last\0name");
    test_item.optional_str_field4 = "abcde";
    test_item.optional_str_field5 = "";
    test_item.struct_vector_field1 = {{"654"}};
    test_item.struct_vector_field2 = {};
    test_item.is_deleted = false;
    test_item.mongo_timestamp = formats::bson::Timestamp{1, 2};
    cache_model->Upsert(std::make_shared<TestModel>(test_item));
  }

  {
    TestModel test_item;
    test_item.required_str_field1 = "park_id3";
    test_item.required_str_field2 = "driver_id3";
    test_item.is_deleted = true;
    test_item.mongo_timestamp = formats::bson::Timestamp{3, 1};
    cache_model->Upsert(std::make_shared<TestModel>(test_item));
  }

  cache_model->SetCursor(formats::bson::Timestamp{3, 3});

  auto cache_model_ptr = std::make_shared<TestCacheDumpModel>(*cache_model);

  api_over_db::DumpContext dump_context("test-dump2", "1");

  api_over_db::DumpCacheInFile<TestCacheDumpModel>(
      cache_model_ptr, "./test-dump2/", "", 1, -1, dump_context);

  auto file_list =
      api_over_db::GetMatchedFiles("./test-dump2/", dump_context, true);
  ASSERT_EQ(1, file_list.size());

  std::string filename = "./test-dump2/" + file_list.begin()->filename;
  std::ifstream ifs(filename);

  ::cache::UpdateStatisticsScopeMock scope(::cache::UpdateType::kFull);

  auto loaded_cache_model = std::make_shared<TestCacheDumpModel>();
  loaded_cache_model->Read(ifs, scope.GetScope(), filename);

  test_equal_pointer_maps(cache_model->GetItemsById(),
                          loaded_cache_model->GetItemsById());
  test_equal_pointer_maps(cache_model->GetItemsByTimestamp(),
                          loaded_cache_model->GetItemsByTimestamp());
  EXPECT_EQ(cache_model->GetCursor(), loaded_cache_model->GetCursor());
}
