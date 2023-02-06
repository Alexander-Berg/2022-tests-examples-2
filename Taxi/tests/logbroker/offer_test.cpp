#include <userver/utest/utest.hpp>

#include <testing/source_path.hpp>
#include <userver/formats/bson/binary.hpp>
#include <userver/formats/bson/inline.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/fs/blocking/read.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <json-diff/json_diff.hpp>

#include <db/offers.hpp>
#include <logbroker/offers.hpp>

namespace order_offers::logbroker {

namespace {

std::string ReadStatic(const std::string& name) {
  return fs::blocking::ReadFileContents(
      utils::CurrentSourcePath("src/tests/static/logbroker/" + name));
}

void CompareMessages(const OfferMessage& lhs, const OfferMessage& rhs) {
  EXPECT_EQ(lhs.timestamp, rhs.timestamp);
  EXPECT_EQ(lhs.id, rhs.id);
  EXPECT_EQ(lhs.created, rhs.created);
  // Detailed diff for non-matching json docs.
  EXPECT_PRED_FORMAT2(json_diff::AreValuesEqual,
                      formats::json::FromString(lhs.doc),
                      formats::json::FromString(rhs.doc));
}

class MockNowTest : public testing::Test {
 protected:
  void SetUp() override {
    static const auto mocked_time = utils::datetime::GuessStringtime(
        "2021-10-25T10:47:56.724376+03:00", "Europe/Moscow");
    utils::datetime::MockNowSet(mocked_time);
  }

  void TearDown() override { utils::datetime::MockNowUnset(); }
};

}  // namespace

class YtUploadsBuildOfferMessage : public MockNowTest {};

TEST_F(YtUploadsBuildOfferMessage, MissingOfferId) {
  const auto offer_doc = formats::bson::MakeDoc();
  EXPECT_THROW(BuildOfferMessage(offer_doc), BuildOfferMessageException);
}

TEST_F(YtUploadsBuildOfferMessage, MissingCreated) {
  const auto offer_doc =
      formats::bson::MakeDoc("_id", "18d3a1133568d1c0fa5436123afbc370");
  EXPECT_THROW(BuildOfferMessage(offer_doc), BuildOfferMessageException);
}

TEST_F(YtUploadsBuildOfferMessage, MinimalOffer) {
  const auto created_time = utils::datetime::GuessStringtime(
      "2021-10-25T10:47:55.724376343+03:00", "Europe/Moscow");
  const auto offer_doc =
      formats::bson::MakeDoc("_id", "18d3a1133568d1c0fa5436123afbc370",  //
                             "created", created_time);

  // Note that 'created' field is truncated to three decimal digits since it
  // gets parsed from Mongo Date type which stores only milliseconds.
  const auto expected_message = OfferMessage{
      "2021-10-25T07:47:56.724376+0000",   // timestamp
      "18d3a1133568d1c0fa5436123afbc370",  // id
      "2021-10-25T07:47:55.724+0000",      // created
      R"-({
        "_id": "18d3a1133568d1c0fa5436123afbc370",
        "created": "2021-10-25T07:47:55.724+0000"
      })-",                                // doc
  };

  CompareMessages(BuildOfferMessage(offer_doc), expected_message);
}

TEST_F(YtUploadsBuildOfferMessage, FullOffer) {
  const auto offer_bson =
      formats::bson::FromBinaryString(ReadStatic("offer.bson"));

  const auto expected_message = OfferMessage{
      "2021-10-25T07:47:56.724376+0000",   // timestamp
      "18d3a1133568d1c0fa5436123afbc370",  // id
      "2021-10-20T08:23:07+0000",          // created
      ReadStatic("offer.json"),            // doc
  };

  CompareMessages(BuildOfferMessage(offer_bson), expected_message);
}

}  // namespace order_offers::logbroker
