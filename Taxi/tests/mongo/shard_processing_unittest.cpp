#include <gtest/gtest.h>

#include <mongo/mongo.hpp>
#include <mongo/shard_processing.hpp>

struct TestData {
  bool enable;
  bool should_genreate_event;
  mongo::BSONObj query;
  bool multi;
};

class SignalingShardProcessor : public utils::mongo::ShardProcessor {
 public:
  SignalingShardProcessor(const mongo::BSONObj& expected_query,
                          bool expected_multi, bool enable)
      : check_search_called_(false),
        check_update_called_(false),
        enable_(enable),
        expected_query_(expected_query),
        expected_multi_(expected_multi) {}

  mutable bool check_search_called_;
  mutable bool check_update_called_;

 protected:
  bool enabled() const override final { return enable_; }
  ::mongo::BSONObj DoModifySearchQuery(
      const ::mongo::BSONObj& query) const override final {
    return query;
  }
  ::mongo::BSONObj DoModifyUpdateQuery(
      const ::mongo::BSONObj& query) const override final {
    return query;
  }

  virtual void CheckSearchQuery(
      const ::mongo::BSONObj& query) const override final {
    ASSERT_EQ(expected_query_, query);
    check_search_called_ = true;
  }
  virtual void CheckUpdateQuery(const ::mongo::BSONObj& query,
                                bool multi) const override final {
    ASSERT_EQ(expected_query_, query);
    ASSERT_EQ(expected_multi_, multi);
    check_update_called_ = true;
  }

 private:
  bool enable_;
  mongo::BSONObj expected_query_;
  bool expected_multi_;
};

class ShardProcessorTest : public ::testing::TestWithParam<TestData> {};

TEST_P(ShardProcessorTest, test_modify_query) {
  const auto& query = GetParam().query;
  SignalingShardProcessor processor(query, GetParam().multi, GetParam().enable);
  ASSERT_EQ(query, processor.ModifySearchQuery(GetParam().query));
  ASSERT_EQ(query,
            processor.ModifyUpdateQuery(GetParam().query, GetParam().multi));
  ASSERT_EQ(GetParam().should_genreate_event, processor.check_search_called_);
  ASSERT_EQ(GetParam().should_genreate_event, processor.check_update_called_);
}

TEST_P(ShardProcessorTest, test_modify_query_complex) {
  const auto& query = GetParam().query;
  SignalingShardProcessor processor(query, GetParam().multi, GetParam().enable);
  mongo::Query original_query = query;
  original_query.readPref(mongo::ReadPreference_SecondaryPreferred, {});
  original_query.sort("srt", utils::mongo::kDesc);
  original_query.hint(BSON("hnt" << 1));
  original_query.maxTimeMs(1001);

  const auto& result =
      processor.ModifyUpdateQuery(original_query, GetParam().multi);
  ASSERT_EQ(GetParam().should_genreate_event, processor.check_update_called_);
  ASSERT_EQ(query, result.getFilter());
  ASSERT_EQ(BSON("mode"
                 << "secondaryPreferred"),
            result.getReadPref());
  ASSERT_EQ(BSON("srt" << utils::mongo::kDesc), result.getSort());
  ASSERT_EQ(BSON("hnt" << 1), result.getHint().Obj());
  ASSERT_EQ(1001, result.getMaxTimeMs());
}

static const auto query = BSON("_id"
                               << "xxx");

INSTANTIATE_TEST_CASE_P(Common, ShardProcessorTest,
                        ::testing::Values(TestData{true, false, query, false},
                                          TestData{true, false, query, true},
                                          TestData{false, true, query, false},
                                          TestData{true, false, query,
                                                   false}), );
