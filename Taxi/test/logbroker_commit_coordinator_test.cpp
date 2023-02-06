#include <eventus/sources/logbroker_source/logbroker_commit_coordinator.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

#include <eventus/pipeline/test_helpers.hpp>

namespace eventus::pipeline {

std::vector<SeqNum> GetCommitOrder(size_t commit_number_for_one_seq_num,
                                   size_t seq_num_per_msg) {
  std::vector<SeqNum> seq_num_commit_order;

  eventus::pipeline::impl::TestSource source("test_source");
  sources::logbroker_source::LogbrokerCommitCoordinator lbcc{source};

  std::vector<engine::Task> commit_tasks;

  for (size_t i = 0; i < 20; i++) {
    for (size_t j = 0; j < 50; j++) {
      SeqNum seq_num_start = (i * 50 + j) * seq_num_per_msg;

      std::unordered_set<SeqNum> related_seq_nums;
      for (SeqNum sn = seq_num_start; sn < seq_num_start + seq_num_per_msg;
           sn++) {
        related_seq_nums.insert(sn);
      }

      lbcc.PushMessage(logbroker_consumer::MessagePtr(), related_seq_nums,
                       [&seq_num_commit_order,
                        related_seq_nums](logbroker_consumer::MessagePtr&&) {
                         std::vector<SeqNum> vals;
                         vals.insert(vals.end(), related_seq_nums.begin(),
                                     related_seq_nums.end());
                         std::sort(vals.begin(), vals.end());
                         seq_num_commit_order.insert(seq_num_commit_order.end(),
                                                     vals.begin(), vals.end());
                       });
    }

    for (int j = 50; j >= 0; j--) {
      SeqNum seq_num_start = (i * 50 + j) * seq_num_per_msg;

      for (SeqNum sn = seq_num_start; sn < seq_num_start + seq_num_per_msg;
           sn++) {
        for (size_t k = 0; k < commit_number_for_one_seq_num; k++) {
          commit_tasks.push_back(
              ::utils::Async("commit_task_" + std::to_string(sn),
                             [&lbcc, sn]() { lbcc.Commit(sn); }));
        }
      }
    }
  }

  for (auto& ct : commit_tasks) {
    ct.Wait();
  }

  return seq_num_commit_order;
}

void MakeTest(size_t commit_number_for_one_seq_num, size_t seq_num_per_msg) {
  std::vector<SeqNum> seq_num_commit_order =
      GetCommitOrder(commit_number_for_one_seq_num, seq_num_per_msg);

  if (commit_number_for_one_seq_num == 0) {
    EXPECT_TRUE(seq_num_commit_order.empty());
  } else {
    EXPECT_TRUE(seq_num_commit_order.size() == 1000 * seq_num_per_msg);
    for (size_t i = 0; i < 1000 * seq_num_per_msg; i++) {
      EXPECT_TRUE(seq_num_commit_order[i] == i);
    }
  }
}

UTEST(LogbrokerCommitCoordinator, test_commit_once) {
  std::vector<size_t> seq_num_per_msg_vec{1, 2, 10};
  std::vector<size_t> commit_number_for_one_seq_num_vec{1, 2, 0};

  for (auto commit_number_for_one_seq_num : commit_number_for_one_seq_num_vec) {
    for (auto seq_num_per_msg : seq_num_per_msg_vec) {
      MakeTest(commit_number_for_one_seq_num, seq_num_per_msg);
    }
  }
}

}  // namespace eventus::pipeline
