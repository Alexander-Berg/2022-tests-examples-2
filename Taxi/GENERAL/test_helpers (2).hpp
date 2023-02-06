#pragma once

#include <eventus/pipeline/error_handler.hpp>
#include <eventus/pipeline/node.hpp>
#include <eventus/pipeline/pipeline_state_manager.hpp>
#include <eventus/pipeline/sink.hpp>
#include <eventus/pipeline/source.hpp>
#include <eventus/statistics/pipeline_statistics.hpp>

namespace eventus::pipeline {

class Pipeline;

namespace impl {

struct TestStateManager final : public PipelineStateManager {
 public:
  std::vector<SeqNum> commited;
  const std::vector<SeqNum>& Commited() const;
  virtual void Commit(SeqNum seq_num) override;
  virtual void CommitBulk(const std::vector<SeqNum>& seq_nums) override;

  void Reset();
};

}  // namespace impl

struct TestContext : public PipelineContext {
 public:
  TestContext() {}

  impl::TestStateManager state_manager;

  const std::vector<SeqNum>& Commited() const;

  PipelineStateManager& GetPipelineStateManager() override;

  PipelineItem MakeItem(SeqNum no);

  void Reset();
};

// hack: friend of Pipeline, can call private functions
class PipelineTestHelper {
 public:
  PipelineTestHelper(std::shared_ptr<eventus::pipeline::Pipeline> pipeline_ptr);

  ~PipelineTestHelper();

  void ProcessItem(eventus::pipeline::PipelineItem&& item);

 private:
  std::shared_ptr<Pipeline> pipeline_ptr_;
};

namespace impl {

class TestSource final : public pipeline::Source {
 public:
  struct Stats {
    int pop_noblock_called_times{0};
    int pop_called_times{0};
    int commit_called_times{0};
  };

  std::shared_ptr<Stats> stats;

  TestSource(const std::string& name)
      : Source(name), stats{std::make_shared<Stats>()} {}

  virtual bool PopNoBlock(std::vector<PipelineItem>& /*msg*/,
                          size_t /*max_bulk*/) override {
    stats->pop_noblock_called_times++;
    return false;
  }
  virtual bool Pop(std::vector<PipelineItem>& /*msg*/,
                   engine::Deadline /*deadline*/ = {}) override {
    stats->pop_called_times++;
    return false;
  }
  /// message has been processed and can be committed to a source
  virtual void Commit(SeqNum /*msg*/) override {
    stats->commit_called_times++;
  };

  // Used for testsuite purposes only
  virtual void TestsuiteInvalidate() override{};
};

}  // namespace impl

class DebugSink : public Sink {
 private:
  std::vector<PipelineItem> data_;

 public:
  DebugSink(std::string name) : Sink(name) {}
  virtual ~DebugSink(){};
  const std::vector<PipelineItem>& GetMessages() const;
  void Reset();

  void Process(PipelineItem& msg) override;
};

eventus::pipeline::ErrorHandler MakeTestErrorHandler();

}  // namespace eventus::pipeline
