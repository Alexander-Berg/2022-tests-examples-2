#include "shared_buffer.hpp"

#include <userver/engine/task/task_with_result.hpp>
#include <userver/utest/utest.hpp>

#include <atomic>
#include <numeric>
#include <userver/engine/sleep.hpp>
#include <userver/utils/async.hpp>

namespace routehistory::processes {
namespace {
using namespace std::chrono_literals;
struct TestState {
  size_t begin;
  size_t end;
  auto Tie() const { return std::tie(begin, end); }
  bool operator==(const TestState& rhs) const { return Tie() == rhs.Tie(); }
  bool operator!=(const TestState& rhs) const { return Tie() != rhs.Tie(); }
};
struct TestData {
  size_t value;
};
using TestBuffer = SharedBuffer<TestState, TestData>;

struct Params {
  Params(const char* name) : name(name) {}
  std::string name;

  size_t thread_count = 10;

  bool wait_for_read = true;

  size_t writer_count = 30;
  size_t data_size = 600;
  size_t max_queue_size = 500;

  size_t initial_min_hint = 80;
  size_t initial_limit = 200;

  size_t min_hint = 100;
  size_t limit = 200;
};

std::vector<Params> MakeParams() {
  std::vector<Params> result;
  {
    auto& p = result.emplace_back("default");
    (void)p;
  }
  {
    auto& p = result.emplace_back("no_wait");
    p.wait_for_read = false;
  }
  {
    auto& p = result.emplace_back("default_single_thread");
    p.thread_count = 1;
  }
  {
    auto& p = result.emplace_back("no_wait_single_thread");
    p.wait_for_read = false;
    p.thread_count = 1;
  }
  {
    auto& p = result.emplace_back("small_data");
    p.data_size = 1;
    p.writer_count = 1;
  }
  {
    auto& p = result.emplace_back("small_data_single_thread");
    p.data_size = 1;
    p.writer_count = 1;
    p.thread_count = 1;
  }

  return result;
}

struct SharedBufferTest : testing::TestWithParam<Params> {
  static void Run();
};

void SharedBufferTest::Run() {
  auto start_time = std::chrono::steady_clock::now();
  auto buffer = TestBuffer::Create();
  struct WriterInfo {
    ::engine::TaskWithResult<void> task;
    std::optional<TestState> final_state;
  };
  std::vector<std::unique_ptr<WriterInfo>> tasks;
  std::atomic_size_t finished = 0;
  // Create writers
  for (size_t i = 0; i < GetParam().writer_count; ++i) {
    auto writer_info = std::make_unique<WriterInfo>();
    auto writer =
        std::make_shared<TestBuffer::WriteHandle>(buffer->CreateWriteHandle());
    writer_info->task = ::utils::Async(
        "write_task",
        [i, writer, &final_state = writer_info->final_state, &finished] {
          const auto start_value = i * GetParam().data_size;
          size_t start = 0;
          size_t chunk_size = 1;
          while (start != GetParam().data_size) {
            size_t end = std::min(GetParam().data_size, start + chunk_size);
            std::vector<TestData> chunk_data(end - start);
            for (size_t j = 0; j < end - start; ++j) {
              chunk_data[j].value = start_value + start + j;
            }
            bool result = writer->AddData({start_value, start_value + end},
                                          chunk_data, GetParam().max_queue_size,
                                          ::engine::Deadline());
            ASSERT_TRUE(result);
            ASSERT_TRUE(writer->IsActive());
            chunk_size *= 2;
            start = end;
          }
          ++finished;
          writer->SetActive(false);
          do {
            final_state = writer->GetLastProcessedState(
                final_state, ::engine::Deadline::FromDuration(10s));
          } while (GetParam().wait_for_read &&
                   (!final_state ||
                    final_state->end != start_value + GetParam().data_size));
        });
    tasks.push_back(std::move(writer_info));
  }
  // Create a reader
  auto reader = buffer->CreateReadHandle();
  std::vector<size_t> final;

  // Read but don't commit
  (void)reader.GetData(GetParam().initial_min_hint, GetParam().initial_limit,
                       ::engine::Deadline::FromDuration(5s), false);

  size_t read_iterations = 0;
  size_t buffer_size;
  size_t finished_;
  while (finished_ = finished, buffer_size = buffer->GetSize(),
         (finished_ < GetParam().writer_count || buffer_size > 0)) {
    bool has_active_writers = buffer->HasActiveWriters();
    auto read_result = reader.GetData(GetParam().min_hint, GetParam().limit,
                                      ::engine::Deadline::FromDuration(8s),
                                      has_active_writers || buffer_size > 0);
    for (const auto& result : read_result.GetRecords()) {
      final.push_back(result.value);
    }
    read_result.Finish();
    ++read_iterations;
  }
  std::cerr << GetParam().name << ": size= " << final.size()
            << ", reads=" << read_iterations << std::endl;
  // Verify the results
  std::sort(final.begin(), final.end());
  auto it = final.begin();
  ASSERT_EQ(std::adjacent_find(final.begin(), final.end()), final.end());
  if (GetParam().wait_for_read) {
    ASSERT_EQ(final.size(), GetParam().writer_count * GetParam().data_size);
  }
  for (size_t i = 0; i < GetParam().writer_count; ++i) {
    auto& task = tasks[i];
    task->task.Get();
    if (task->final_state) {
      auto value = task->final_state->begin;
      it = std::find(it, final.end(), value);
      while (value != task->final_state->end) {
        ASSERT_EQ(value++, *it++);
      }
    }
  }
  auto end_time = std::chrono::steady_clock::now();
  ASSERT_LE(end_time - start_time, 4s);
}

TEST_P(SharedBufferTest, SharedBuffer1) {
  RunInCoro(Run, GetParam().thread_count);
}

INSTANTIATE_TEST_SUITE_P(SharedBufferTests1, SharedBufferTest,
                         ::testing::ValuesIn(MakeParams()),
                         [](const auto& t) { return t.param.name; });

}  // namespace
}  // namespace routehistory::processes
