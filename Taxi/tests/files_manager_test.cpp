#include <atomic>

#include <clients/taxi-exp-uservices/client_gmock.hpp>
#include <testing/source_path.hpp>
#include <testing/taxi_config.hpp>
#include <tvm2/utest/mock_client_context.hpp>
#include <userver/crypto/hash.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/dynamic_config/test_helpers.hpp>
#include <userver/engine/task/task.hpp>
#include <userver/formats/json.hpp>
#include <userver/fs/blocking/read.hpp>
#include <userver/fs/blocking/temp_directory.hpp>
#include <userver/fs/blocking/write.hpp>
#include <userver/utest/http_client.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

#include <experiments3/models/files_manager.hpp>

UTEST(FilesManager, LocalFileWithMatchingHash) {
  clients::taxi_exp_uservices::ClientGMock mock_client;
  experiments3::models::FilesManagerImpl files_manager{
      utils::CurrentSourcePath("/src/tests/static/files_manager_tests"),
      mock_client, engine::current_task::GetTaskProcessor(),
      dynamic_config::GetDefaultSource(), std::nullopt};
  EXPECT_CALL(mock_client, V1Files).Times(0);
  auto result = files_manager.FetchFile("existing_file", "string");
  ASSERT_TRUE(result->Hashes().size() == 1);
}

UTEST(FilesManager, LocalFileWithNonMatchingHash) {
  clients::taxi_exp_uservices::ClientGMock mock_client;
  const auto dir_path = fs::blocking::TempDirectory::Create().GetPath();
  const auto files_dir = dir_path + "/___files/";
  boost::filesystem::create_directories(files_dir);
  fs::blocking::RewriteFileContents(files_dir + "broken_file.string", "");
  fs::blocking::RewriteFileContents(
      files_dir + "broken_file.string.sha256",
      "844850bcb588c97d1b9510d8e69d34c8dff0b4ee8ecb37f1c032fe5665b7f3b0");
  experiments3::models::FilesManagerImpl files_manager{
      dir_path, mock_client, engine::current_task::GetTaskProcessor(),
      dynamic_config::GetDefaultSource(), std::nullopt};
  EXPECT_CALL(mock_client, V1Files).Times(1);
  files_manager.FetchFile("broken_file", "string");
}

UTEST(FilesManager, DownloadedFileWithMatchingHash) {
  clients::taxi_exp_uservices::ClientGMock mock_client;
  const auto dir_path = fs::blocking::TempDirectory::Create().GetPath();
  experiments3::models::FilesManagerImpl files_manager{
      dir_path, mock_client, engine::current_task::GetTaskProcessor(),
      dynamic_config::GetDefaultSource(), std::nullopt};
  using Response = clients::taxi_exp_uservices::v1_files::get::Response;
  Response response;
  response.x_content_hash =
      "105359a0d91d5ef9674f35ecf29e75145d3c0e14e9db302ceb2be8c72f192d4d";
  response.body = "5e9044ba7984b5db62dcc971\n5e9044ba7984b5db62dcc971\n";
  EXPECT_CALL(mock_client, V1Files)
      .Times(1)
      .WillOnce(::testing::Return(response));
  auto result = files_manager.FetchFile("non_existing_file", "string");
  ASSERT_NE(result, nullptr);
  ASSERT_TRUE(result->Hashes().size() == 1);
  auto file_path = dir_path +
                   "/___files/non_existing_file"
                   ".string";
  auto hash_file_path = file_path + ".sha256";
  EXPECT_TRUE(boost::filesystem::exists(hash_file_path));
  EXPECT_TRUE(boost::filesystem::exists(file_path));
  ASSERT_TRUE(crypto::hash::Sha256(fs::blocking::ReadFileContents(file_path)) ==
              fs::blocking::ReadFileContents(hash_file_path));
}

UTEST(FilesManager, DownloadedFileWithNonMatchingHash) {
  clients::taxi_exp_uservices::ClientGMock mock_client;
  const auto dir_path = fs::blocking::TempDirectory::Create().GetPath();
  experiments3::models::FilesManagerImpl files_manager{
      dir_path, mock_client, engine::current_task::GetTaskProcessor(),
      dynamic_config::GetDefaultSource(), std::nullopt};
  using Response = clients::taxi_exp_uservices::v1_files::get::Response;
  Response response;
  response.x_content_hash =
      "3aaf519ed8466851266299bb024d81491eb072dbb43a60ae36960701f92bf3a";
  response.body = "5e9044ba7984b5db62dcc971\n";
  EXPECT_CALL(mock_client, V1Files)
      .Times(2)
      .WillOnce(::testing::Return(response))
      .WillOnce(::testing::Return(response));
  auto result = files_manager.FetchFile("non_existing_broken_file", "string");
  ASSERT_EQ(result, nullptr);
  EXPECT_FALSE(boost::filesystem::exists(dir_path +
                                         "/___files/non_existing_file"
                                         ".string.sha256"));
  EXPECT_FALSE(boost::filesystem::exists(dir_path +
                                         "/___files/non_existing_file"
                                         ".string"));
}

UTEST(FilesManager, LocalFileWithNoHash) {
  clients::taxi_exp_uservices::ClientGMock mock_client;
  experiments3::models::FilesManagerImpl files_manager{
      utils::CurrentSourcePath("/src/tests/static/files_manager_tests"),
      mock_client, engine::current_task::GetTaskProcessor(),
      dynamic_config::GetDefaultSource(), std::nullopt};
  EXPECT_CALL(mock_client, V1Files).Times(0);
  auto result = files_manager.FetchFile("existing_file_no_hash", "string");
  ASSERT_NE(result, nullptr);
  ASSERT_TRUE(result->Hashes().size() == 1);
}

UTEST(FilesManager, DownloadedFileWithNoHash) {
  clients::taxi_exp_uservices::ClientGMock mock_client;
  const auto dir_path = fs::blocking::TempDirectory::Create().GetPath();
  experiments3::models::FilesManagerImpl files_manager{
      dir_path, mock_client, engine::current_task::GetTaskProcessor(),
      dynamic_config::GetDefaultSource(), std::nullopt};
  using Response = clients::taxi_exp_uservices::v1_files::get::Response;
  Response response;
  response.body = "5e9044ba7984b5db62dcc971\n";
  EXPECT_CALL(mock_client, V1Files)
      .Times(1)
      .WillOnce(::testing::Return(response));
  auto result = files_manager.FetchFile("non_existing_file_no_hash", "string");
  ASSERT_NE(result, nullptr);
  ASSERT_TRUE(result->Hashes().size() == 1);
  EXPECT_TRUE(boost::filesystem::exists(dir_path +
                                        "/___files/non_existing_file_no_hash"
                                        ".string"));
  EXPECT_FALSE(boost::filesystem::exists(dir_path +
                                         "/___files/non_existing_file_no_hash"
                                         ".string.sha256"));
}

UTEST(FilesManager, DoNotRemoveHash) {
  clients::taxi_exp_uservices::ClientGMock mock_client;
  const auto dir_path = fs::blocking::TempDirectory::Create().GetPath();
  experiments3::models::FilesManagerImpl files_manager{
      dir_path, mock_client, engine::current_task::GetTaskProcessor(),
      dynamic_config::GetDefaultSource(), std::nullopt};

  using Response = clients::taxi_exp_uservices::v1_files::get::Response;
  Response response;
  response.x_content_hash =
      "3aaf519ed8466851266299bb024d81491eb072dbb43a60ae36960701f92bf3a9";
  response.body = "5e9044ba7984b5db62dcc971\n";
  EXPECT_CALL(mock_client, V1Files)
      .Times(1)
      .WillOnce(::testing::Return(response));
  auto result = files_manager.FetchFile("non_existing_file", "string");
  ASSERT_NE(result, nullptr);
  ASSERT_TRUE(result->Hashes().size() == 1);
  files_manager.RemoveUnusedFilesFromDisk();
  EXPECT_TRUE(boost::filesystem::exists(dir_path + "/___files/non_existing_file"
                                                   ".string"));
  EXPECT_TRUE(boost::filesystem::exists(dir_path + "/___files/non_existing_file"
                                                   ".string.sha256"));
}
