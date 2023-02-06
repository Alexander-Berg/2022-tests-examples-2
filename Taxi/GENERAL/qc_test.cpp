#include <gtest/gtest.h>

#include <fstream>

#include <clients/qc.hpp>
#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/driver_protocol_config.hpp>

namespace {
const std::string kDirName = std::string(SOURCE_DIR) + "/tests/data/";

std::string ReadFile(const std::string& filename) {
  std::ifstream file(kDirName + filename);
  return std::string{std::istreambuf_iterator<char>(file),
                     std::istreambuf_iterator<char>()};
}

}  // namespace

TEST(TestDriverProtocolQcState, DkvuRealData) {
  const auto& response = ReadFile("qc/qc-state1.json");
  clients::qc::QcState state;

  ASSERT_NO_THROW(state = clients::qc::ParseQcState(response, {}));
  ASSERT_EQ(state.item_id, "3b1764bf0f6e4aa78ace02215f1c04c6");
  ASSERT_EQ(state.park_id, "c52e88b724674ef7917ee0f8fa4627de");

  ASSERT_EQ(state.exams.size(), 1u);
  ASSERT_EQ(state.exams.count("dkvu"), 1u);
  const auto& exam = state.exams["dkvu"];
  ASSERT_EQ(exam.code, "dkvu");
  ASSERT_TRUE(exam.present.is_initialized());

  ASSERT_EQ(exam.present->sanctions.size(), 1u);
  ASSERT_EQ(exam.present->sanctions.front(), "orders_off");

  ASSERT_TRUE(exam.present->pass.is_initialized());
  ASSERT_EQ(exam.present->pass->id, "5b543351d10eb2a81170c0e9");
}

TEST(TestDriverProtocolQcState, DkvuNoMediaLoaded) {
  const auto& response = ReadFile("qc/qc-no-loaded.json");
  clients::qc::QcState state;

  ASSERT_NO_THROW(state = clients::qc::ParseQcState(response, {}));
  ASSERT_EQ(state.exams.size(), 1u);
  ASSERT_EQ(state.exams.count("dkvu"), 1u);
  const auto& exam = state.exams["dkvu"];
  ASSERT_EQ(exam.code, "dkvu");
  ASSERT_TRUE(exam.present.is_initialized());

  ASSERT_TRUE(exam.present->pass.is_initialized());
  const auto& pass = *exam.present->pass;
  ASSERT_EQ(pass.id, "5b543351d10eb2a81170c0e9");

  ASSERT_EQ(pass.media.size(), 1u);
  const auto& media = pass.media.front();
  ASSERT_EQ(media.code, "front");
  ASSERT_EQ(media.type, "photo");
}

TEST(TestDriverProtocolQcState, EmptyState) {
  const auto& response = ReadFile("qc/qc-empty-state.json");
  clients::qc::QcState state;

  ASSERT_NO_THROW(state = clients::qc::ParseQcState(response, {}));
}
