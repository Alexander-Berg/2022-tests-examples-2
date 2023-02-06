#include <gtest/gtest.h>

#include <string>

#include <ml/common/embeddings.hpp>
#include <ml/common/filesystem.hpp>

#include "common/utils.hpp"

namespace {
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("common_embeddings");
}

TEST(CommonEmbeddings, simple_embedding) {
  using ml::common::LoadIdEmbeddingFromTxt;

  auto path = kTestDataDir + "/simple_embedding_wrong_path.txt";
  try {
    auto embedding = LoadIdEmbeddingFromTxt<std::string, double>(path);
    FAIL() << "Expected 'Can't open file' exception";
  } catch (std::runtime_error const& err) {
    EXPECT_EQ(err.what(), std::string("Can't open file: " + path));
  } catch (...) {
    FAIL() << "Expected 'Can't open file' exception";
  }

  path = kTestDataDir + "/simple_embedding_broken1.txt";
  try {
    auto embedding = LoadIdEmbeddingFromTxt<std::string, double>(path);
    FAIL() << "Expected 'End of stream is reached, but embedding is not read'";
  } catch (std::runtime_error const& err) {
    EXPECT_EQ(
        err.what(),
        std::string("End of stream is reached, but embedding is not read"));
  } catch (...) {
    FAIL() << "Expected 'End of stream is reached, but embedding is not read'";
  }

  path = kTestDataDir + "/simple_embedding_broken2.txt";
  try {
    auto embedding = LoadIdEmbeddingFromTxt<std::string, double>(path);
    FAIL() << "Expected 'Error while reading occurred'";
  } catch (std::runtime_error const& err) {
    EXPECT_EQ(err.what(), std::string("Error while reading occurred"));
  } catch (...) {
    FAIL() << "Expected 'Error while reading occurred'";
  }

  auto embedding = LoadIdEmbeddingFromTxt<std::string, double>(
      kTestDataDir + "/simple_embedding.txt");
  ASSERT_EQ(embedding.GetSize(), 5ul);
  ASSERT_EQ(embedding.Get("zero"), std::vector<double>({0, 0, 0, 0, 0}));
  ASSERT_EQ(embedding.Get("first"), std::vector<double>({1, 2, 3, 4, 5}));
  ASSERT_EQ(embedding.Get("second"), std::vector<double>({-1, -2, -3, -4, -5}));
  ASSERT_EQ(embedding.Get("third"), std::vector<double>({1, -1, 1, -1, 1}));
}
