#include <userver/utest/utest.hpp>
#include <userver/utils/assert.hpp>

#include <eventus/pipeline/impl/state_manager.hpp>

namespace {

using eventus::pipeline::PipelineItem;
using eventus::pipeline::SeqNum;

class TestSource final : public eventus::pipeline::Source {
 public:
  std::unordered_map<SeqNum, size_t> commits_come;

  TestSource() : eventus::pipeline::Source("utest-source") {}

  virtual bool PopNoBlock([[maybe_unused]] std::vector<PipelineItem>& msg,
                          [[maybe_unused]] size_t max_bulk) override {
    UASSERT(false);
    return false;
  }
  virtual bool Pop([[maybe_unused]] std::vector<PipelineItem>& msg,
                   [[maybe_unused]] engine::Deadline deadline = {}) override {
    UASSERT(false);
    return false;
  }
  /// message has been processed and can be committed to a source
  virtual void Commit(SeqNum msg) override { commits_come[msg]++; }

  // Used for testsuite purposes only
  virtual void TestsuiteInvalidate() override{};
};

}  // namespace

UTEST(PipelineSuite, StateManagerTest) {
  eventus::pipeline::impl::StateManager state_mgr;
  TestSource source;
  state_mgr.SetSource(source);
  state_mgr.SetSinksCount(2);

  const eventus::pipeline::SeqNum msg = 0;
  state_mgr.StoreSeqNum(msg);
  state_mgr.Commit(msg);
  ASSERT_TRUE(source.commits_come.find(msg) == source.commits_come.end());
  state_mgr.Commit(msg);
  ASSERT_TRUE(source.commits_come.find(msg) != source.commits_come.end());
  ASSERT_EQ(source.commits_come[msg], 1);
  state_mgr.Commit(msg);
  ASSERT_EQ(source.commits_come[msg], 1);
}

UTEST(PipelineSuite, StateManagerBulkTest) {
  eventus::pipeline::impl::StateManager state_mgr;
  TestSource source;
  state_mgr.SetSource(source);
  state_mgr.SetSinksCount(2);

  const eventus::pipeline::SeqNum msg = 0;
  state_mgr.StoreSeqNum(msg);
  state_mgr.CommitBulk({msg});
  ASSERT_TRUE(source.commits_come.find(msg) == source.commits_come.end());
  state_mgr.CommitBulk({msg});
  ASSERT_TRUE(source.commits_come.find(msg) != source.commits_come.end());
  ASSERT_EQ(source.commits_come[msg], 1);
  state_mgr.CommitBulk({msg});
  ASSERT_EQ(source.commits_come[msg], 1);
}
