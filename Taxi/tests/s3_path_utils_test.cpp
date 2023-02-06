#include <utils/s3_path_utils.hpp>

#include <userver/utest/utest.hpp>

namespace eats_nomenclature_collector::utils::tests {

TEST(S3PathUtils, GetS3PathFromAbsoluteUrl) {
  const std::string test_url_1{
      "https:\\/\\/eda-integration.s3.mdst.yandex.net\\/integration\\/"
      "collector\\/nomenclature\\/test.json"};
  const std::string test_url_2{
      "http:\\/\\/eda-integration.s3.mdst.yandex.net\\/some_path\\/test.json"};
  const std::string test_url_3{
      "http://eda-integration.s3.mdst.yandex.net/some_other_path/test.json"};
  const std::string test_url_4{
      "https:\\/\\/s3.mds.yandex.net\\/eda-selfreg-menu\\/integration\\/"
      "menu\\/test.json"};

  const std::string expected_path_1{
      "integration/collector/nomenclature/test.json"};
  const std::string expected_path_2{"some_path/test.json"};
  const std::string expected_path_3{"some_other_path/test.json"};
  const std::string expected_path_4{
      "eda-selfreg-menu/integration/menu/test.json"};

  ASSERT_EQ(GetS3PathFromAbsoluteUrl(test_url_1), expected_path_1);
  ASSERT_EQ(GetS3PathFromAbsoluteUrl(test_url_2), expected_path_2);
  ASSERT_EQ(GetS3PathFromAbsoluteUrl(test_url_3), expected_path_3);
  ASSERT_EQ(GetS3PathFromAbsoluteUrl(test_url_4), expected_path_4);
}

}  // namespace eats_nomenclature_collector::utils::tests
