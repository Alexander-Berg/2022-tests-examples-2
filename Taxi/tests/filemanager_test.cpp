#include <utils/filemanager.hpp>

#include <boost/filesystem.hpp>
#include <testing/source_path.hpp>
#include <userver/engine/task/task.hpp>
#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

namespace taxi_tariffs {

std::string MakeFilepath(const std::string& filename) {
  return utils::CurrentSourcePath("tests/static/" + filename);
}

std::string MakeWritableFilepath(const std::string& filename) {
  return utils::CurrentWorkPath("tests/static/" + filename);
}

class WritableTest : public testing::Test {
 protected:
  virtual void SetUp() {}
  virtual void TearDown() {
    const auto& tmp_path = boost::filesystem::path(MakeFilepath("tmp"));
    boost::filesystem::remove_all(tmp_path);
  }
};

UTEST(TestFileManager, NoCache) {
  auto& task_processor = engine::current_task::GetTaskProcessor();
  CacheFileManager fm(MakeFilepath("tmp/wrong_file"), task_processor);
  ASSERT_THROW(fm.LoadCache(), CacheFileException);
}

UTEST(TestFileManager, WrongDir) {
  auto& task_processor = engine::current_task::GetTaskProcessor();
  CacheFileManager fm(MakeFilepath("tmp/inner/file.json"), task_processor);
  ASSERT_THROW(fm.LoadCache(), CacheFileException);
}

UTEST(TestFileManager, ReadOk) {
  auto& task_processor = engine::current_task::GetTaskProcessor();
  CacheFileManager fm(MakeFilepath("moscow.json"), task_processor);

  const auto& cache = fm.LoadCache();
  ASSERT_EQ(cache.size(), 1);

  const auto& [key, value] = *cache.begin();
  ASSERT_EQ(key, "moscow");
  ASSERT_EQ(*value.home_zone, "moscow");
}

UTEST(TestFileManager, ReadMalformed) {
  auto& task_processor = engine::current_task::GetTaskProcessor();
  CacheFileManager fm(MakeFilepath("malformed.json"), task_processor);
  ASSERT_THROW(fm.LoadCache(), CacheFileException);
}

UTEST_F(WritableTest, ReadWritten) {
  auto& task_processor = engine::current_task::GetTaskProcessor();
  CacheFileManager fm1(MakeFilepath("moscow.json"), task_processor);
  CacheFileManager fm2(MakeWritableFilepath("tmp/moscow_2.json"),
                       task_processor);
  fm2.StoreCache(fm1.LoadCache());

  const auto& val1 =
      formats::json::blocking::FromFile(MakeFilepath("moscow.json"));
  const auto& val2 = formats::json::blocking::FromFile(
      MakeWritableFilepath("tmp/moscow_2.json"));
  ASSERT_EQ(val1, val2);
}

UTEST_F(WritableTest, WriteEmpty) {
  auto& task_processor = engine::current_task::GetTaskProcessor();

  models::TariffSettingsMap cache;
  CacheFileManager fm(MakeWritableFilepath("tmp/moscow_2.json"),
                      task_processor);
  fm.StoreCache(cache);

  const auto& val2 = formats::json::blocking::FromFile(
      MakeWritableFilepath("tmp/moscow_2.json"));
  ASSERT_TRUE(val2.IsEmpty());
}

UTEST_F(WritableTest, WriteNew) {
  auto& task_processor = engine::current_task::GetTaskProcessor();

  std::string home_zone = "murmansk";
  models::TariffSettingsMap cache;
  cache[home_zone] = models::TariffSettings{home_zone, home_zone};

  CacheFileManager fm(MakeWritableFilepath("tmp/moscow_2.json"),
                      task_processor);
  fm.StoreCache(cache);

  const auto& val = formats::json::blocking::FromFile(
      MakeWritableFilepath("tmp/moscow_2.json"));
  const auto& expected = formats::json::FromString(
      R"([{"tariff_settings_id":"murmansk","home_zone":"murmansk"}])");
  ASSERT_EQ(val, expected);
}

UTEST_F(WritableTest, WriteAppend) {
  auto& task_processor = engine::current_task::GetTaskProcessor();
  CacheFileManager fm1(MakeFilepath("moscow.json"), task_processor);
  CacheFileManager fm2(MakeWritableFilepath("tmp/moscow_2.json"),
                       task_processor);
  const auto& original = fm1.LoadCache();
  fm2.StoreCache(original);

  models::TariffSettingsMap cache = fm2.LoadCache();
  std::string home_zone = "murmansk";
  cache[home_zone] = models::TariffSettings{home_zone, home_zone};
  fm2.StoreCache(cache);

  const auto& result = fm2.LoadCache();
  const auto& expected_murmansk =
      formats::json::FromString(
          R"({"tariff_settings_id":"murmansk","home_zone":"murmansk"})")
          .As<models::TariffSettings>();
  ASSERT_EQ(result.size(), 2);
  ASSERT_EQ(result.at("moscow"), original.at("moscow"));
  ASSERT_EQ(result.at(home_zone), expected_murmansk);
}

UTEST_F(WritableTest, WriteInnerDir) {
  auto& task_processor = engine::current_task::GetTaskProcessor();
  CacheFileManager fm(MakeWritableFilepath("tmp/inner/cache.json"),
                      task_processor);
  fm.StoreCache(models::TariffSettingsMap());
  const auto& cache = fm.LoadCache();
  ASSERT_EQ(cache.size(), 0);
}

}  // namespace taxi_tariffs
