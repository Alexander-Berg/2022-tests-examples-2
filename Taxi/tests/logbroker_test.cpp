#include <gtest/gtest.h>

#include <logbroker/base.hpp>
#include <logbroker/best_dc_read_strategy_policy.hpp>
#include <logbroker/request.hpp>
#include <threads/async.hpp>

static logbroker::Consumer& GetConsumer() {
  static utils::Async async(1, "xx", false);
  logbroker::ConsumerArgs args;
  args.base_url = "localhost";
  args.client_id = "clientid";
  args.log_type = "log_type";
  args.ident = "ident";
  static logbroker::Consumer cs(args, async.GetIoService(), async, LogExtra());
  return cs;
}

TEST(LogbrokerConsumer, ListResponse) {
  using namespace logbroker;
  auto& cs = GetConsumer();

  EXPECT_EQ(ListResponse(cs, "").GetTopics(), std::vector<std::string>());

  auto body1 =
      "rt3.sas--redir--redir-log\r\n"
      "rt3.iva--redir--redir-log\r\n"
      "rt3.fol--redir--redir-log\r\n";
  auto parts1 = std::vector<std::string>({"rt3.sas--redir--redir-log",
                                          "rt3.iva--redir--redir-log",
                                          "rt3.fol--redir--redir-log"});
  EXPECT_EQ(ListResponse(cs, body1).GetTopics(), parts1);

  auto body2 =
      "rt3.sas--redir--redir-log\n"
      "rt3.iva--redir--redir-log\n"
      "rt3.fol--redir--redir-log\n";
  EXPECT_EQ(ListResponse(cs, body2).GetTopics(), parts1);
}

TEST(LogbrokerConsumer, SuggestResponse) {
  using namespace logbroker;
  auto& cs = GetConsumer();

  auto body1 = "\r\n";
  EXPECT_EQ(SuggestResponse(cs, body1).GetPartitions(),
            std::vector<Partition>());

  auto body2 =
      "lb-sas-011.stat.yandex.net:8999\trt3.iva--yandex--access-log:8\r\n"
      "lb-sas-052.stat.yandex.net:8999\trt3.iva--yandex--access-log:\r\n";
  auto part2 =
      std::vector<Partition>({Partition("lb-sas-011.stat.yandex.net:8999",
                                        "rt3.iva--yandex--access-log:8"),
                              Partition("lb-sas-052.stat.yandex.net:8999",
                                        "rt3.iva--yandex--access-log:")});
  EXPECT_EQ(SuggestResponse(cs, body2).GetPartitions(), part2);
}

TEST(LogbrokerConsumer, OffsetsResponse) {
  using namespace logbroker;
  auto& cs = GetConsumer();

  EXPECT_EQ(OffsetsResponse(cs, "\r\n").GetPartitionsInfo(),
            std::vector<PartitionInfo>());

  auto body2 =
      "rt3.iva--yandex--access-log:0\t-"
      "1\t1064572522\t1066369385\t1796863\tnone\r\n"
      "rt3.iva--yandex--access-log:4\t-"
      "1\t1067069382\t1069129138\t2059756\tnone\r\n"
      "rt3.iva--yandex--access-log:6\t-"
      "1\t1089669402\t1091077276\t1407874\tnone\r\n"
      "rt3.iva--yandex--access-log:3\t-"
      "1\t1041536728\t1043742404\t2205676\tnone\r\n"
      "rt3.iva--yandex--access-log:9\t-"
      "1\t1100902968\t1103323131\t2420163\tnone\r\n"
      "rt3.iva--yandex--access-log:8\t-"
      "1\t1062421777\t1064259392\t1837615\tnone\r\n"
      "rt3.iva--yandex--access-log:5\t-"
      "1\t1074580284\t1077100164\t2519880\tnone\r\n";
  auto part2 = std::vector<PartitionInfo>(
      {PartitionInfo("rt3.iva--yandex--access-log:0", -1, 1064572522,
                     1066369385, 1796863, boost::none),
       PartitionInfo("rt3.iva--yandex--access-log:4", -1, 1067069382,
                     1069129138, 2059756, boost::none),
       PartitionInfo("rt3.iva--yandex--access-log:6", -1, 1089669402,
                     1091077276, 1407874, boost::none),
       PartitionInfo("rt3.iva--yandex--access-log:3", -1, 1041536728,
                     1043742404, 2205676, boost::none),
       PartitionInfo("rt3.iva--yandex--access-log:9", -1, 1100902968,
                     1103323131, 2420163, boost::none),
       PartitionInfo("rt3.iva--yandex--access-log:8", -1, 1062421777,
                     1064259392, 1837615, boost::none),
       PartitionInfo("rt3.iva--yandex--access-log:5", -1, 1074580284,
                     1077100164, 2519880, boost::none)});
  EXPECT_EQ(OffsetsResponse(cs, body2).GetPartitionsInfo(), part2);
}

#if 0
TEST(LogbrokerConsumer, ReadResponse) {
  using namespace logbroker;
  auto &cs = GetConsumer();

  auto body1 = "211\r\n"
"seqno=1148\tserver=unknown\tpath=unknown\tpartition=0\tident=other\toffset=9094202\tsourceid=base64:BG7hPYsbQze7eGLQkxDOjw\tcodec=lzop\ttopic=rt3.iva--other--statbox-synthetic-log\ttype=statbox-synthetic-log\r\n"
"[binary data]*";

  std::vector<Chunk> resp1 = { Chunk(cs, std::unordered_map<std::string, std::string>{{"seqno", "1148"}}, "data") };

  EXPECT_EQ(ReadResponse(cs, body1).GetChunks(), ChunksPtr(new Chunks(resp1)));

}
#endif

TEST(LogbrokerConsumer, BestDcReadStrategyPolicyEmpty) {
  using namespace logbroker;

  BestDcReadStrategyPolicy policy;
  EXPECT_EQ("", policy.GetBestDcForTopic("abba"));
  EXPECT_EQ("", policy.GetBestDcForTopic("eee"));
}

TEST(LogbrokerConsumer, BestDcReadStrategyPolicy1) {
  using namespace logbroker;

  BestDcReadStrategyPolicy policy;
  policy.FeedPartitionInfo(
      "dc1", {PartitionInfo("abba", -1, 2, 3, 1, std::string("owner"))});

  EXPECT_EQ("dc1", policy.GetBestDcForTopic("abba"));
  EXPECT_EQ("", policy.GetBestDcForTopic("eee"));
}

TEST(LogbrokerConsumer, BestDcReadStrategyPolicy2) {
  using namespace logbroker;

  BestDcReadStrategyPolicy policy;
  policy.FeedPartitionInfo(
      "dc1", {PartitionInfo("abba", -1, 1, 3, 1, std::string("owner")),
              PartitionInfo("eee", -1, 1, 3, 1, std::string("owner"))});
  policy.FeedPartitionInfo(
      "dc2", {PartitionInfo("abba", -1, 1, 4, 1, std::string("owner")),
              PartitionInfo("fff", -1, 1, 4, 1, std::string("owner"))});

  EXPECT_EQ("dc2", policy.GetBestDcForTopic("abba"));
  EXPECT_EQ("dc2", policy.GetBestDcForTopic("fff"));
  EXPECT_EQ("dc1", policy.GetBestDcForTopic("eee"));
  EXPECT_EQ("", policy.GetBestDcForTopic("wrong"));
}

TEST(LogbrokerConsumer, BestDcReadStrategyPolicyExisting1) {
  using namespace logbroker;

  BestDcReadStrategyPolicy policy;
  policy.FeedPartitionInfo(
      "dc1", {
                 PartitionInfo("abba", -1, 1, 3, 1, std::string("owner")),
             });
  policy.FeedPartitionInfo(
      "dc2", {
                 PartitionInfo("abba", -1, 1, 4, 1, std::string("owner")),
             });
  policy.FeedPartitionInfo(
      "dc3", {
                 PartitionInfo("abba", -1, 1, 5, 1, std::string("owner")),
             });
  policy.SetCurrentDc("abba", "dc2");
  policy.SetReplicationLagTolerance(3);

  EXPECT_EQ("dc2", policy.GetBestDcForTopic("abba"));
  EXPECT_EQ("", policy.GetBestDcForTopic("wrong"));
}

TEST(LogbrokerConsumer, BestDcReadStrategyPolicyExisting2) {
  using namespace logbroker;

  BestDcReadStrategyPolicy policy;
  policy.FeedPartitionInfo(
      "dc1", {
                 PartitionInfo("abba", -1, 1, 30, 1, std::string("owner")),
             });
  policy.FeedPartitionInfo(
      "dc2", {
                 PartitionInfo("abba", -1, 1, 40, 1, std::string("owner")),
             });
  policy.FeedPartitionInfo(
      "dc3", {
                 PartitionInfo("abba", -1, 1, 50, 1, std::string("owner")),
             });
  policy.SetCurrentDc("abba", "dc2");
  policy.SetReplicationLagTolerance(3);

  EXPECT_EQ("dc3", policy.GetBestDcForTopic("abba"));
  EXPECT_EQ("", policy.GetBestDcForTopic("wrong"));
}

TEST(LogbrokerConsumer, BestDcReadStrategyPolicyExisting3) {
  using namespace logbroker;

  BestDcReadStrategyPolicy policy;
  policy.FeedPartitionInfo(
      "dc1", {
                 PartitionInfo("abba", -1, 1, 30, 1, std::string("owner")),
             });
  policy.FeedPartitionInfo(
      "dc2", {
                 PartitionInfo("abba", -1, 1, 40, 1, std::string("owner")),
             });
  policy.FeedPartitionInfo(
      "dc3", {
                 PartitionInfo("abba", -1, 1, 50, 1, std::string("owner")),
             });
  policy.SetLocalDc("dc2");
  policy.SetReplicationLagTolerance(3);

  EXPECT_EQ("dc3", policy.GetBestDcForTopic("abba"));
  EXPECT_EQ("", policy.GetBestDcForTopic("wrong"));

  policy.SetReplicationLagTolerance(20);
  EXPECT_EQ("dc2", policy.GetBestDcForTopic("abba"));
}
