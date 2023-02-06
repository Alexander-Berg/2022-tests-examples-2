#include <eventus/pipeline/test_helpers.hpp>

#include <eventus/pipeline/pipeline.hpp>

namespace eventus::pipeline {

namespace impl {

const std::vector<SeqNum>& TestStateManager::Commited() const {
  return commited;
}

void TestStateManager::Commit(SeqNum seq_num) { commited.push_back(seq_num); }

void TestStateManager::CommitBulk(const std::vector<SeqNum>& seq_nums) {
  commited.insert(commited.end(), seq_nums.begin(), seq_nums.end());
}

void TestStateManager::Reset() { commited.clear(); }

}  // namespace impl

PipelineTestHelper::PipelineTestHelper(
    eventus::pipeline::PipelinePtr pipeline_ptr)
    : pipeline_ptr_{std::move(pipeline_ptr)} {}

PipelineTestHelper::~PipelineTestHelper() = default;

void PipelineTestHelper::ProcessItem(eventus::pipeline::PipelineItem&& item) {
  pipeline_ptr_->ProcessItem(std::make_unique<PipelineItem>(std::move(item)));
}

const std::vector<SeqNum>& TestContext::Commited() const {
  return state_manager.Commited();
}

PipelineStateManager& TestContext::GetPipelineStateManager() {
  return state_manager;
}

PipelineItem TestContext::MakeItem(SeqNum no) {
  return PipelineItem{no, Event(formats::json::Value{})};
}

void TestContext::Reset() { state_manager.Reset(); }

const std::vector<PipelineItem>& DebugSink::GetMessages() const {
  return data_;
}

void DebugSink::Reset() { data_.clear(); }

void DebugSink::Process(PipelineItem& msg) {
  data_.push_back(msg);
  GetContext().GetPipelineStateManager().Commit(msg.seq_num);
}

eventus::pipeline::ErrorHandler MakeTestErrorHandler() {
  static const eventus::pipeline::ErrorHandlingPolicy
      test_error_handling_policy{
          1,
          std::chrono::milliseconds{0},
          std::chrono::milliseconds{0},
          1,
          config::ActionAfterErroneousExecution::kPropagate,
          config::ErroneousStatisticsLevel::kError};
  return eventus::pipeline::ErrorHandler{test_error_handling_policy};
}

}  // namespace eventus::pipeline
