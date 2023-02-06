#include <gtest/gtest.h>

#include <unordered_map>

#include "utils/utils.hpp"

namespace {
std::string valid_string =
    "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\",\"DATE\":"
    "1566395449,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444.1632\","
    "\"QUEUENAME\":\"disp_cc\",\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
    "\"DATA1\":\"\",\"DATA2\":\"79872676410\",\"DATA3\":\"1\",\"DATA4\":"
    "null,\"DATA5\":null,\"DATA6\":null,\"DATA7\":null,\"DATA8\":null,"
    "\"OTHER\":null}\n";
std::string valid_long_string =
    "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\",\"DATE\":"
    "1566395449,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444.1632\","
    "\"QUEUENAME\":\"disp_cc\",\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
    "\"DATA1\":\"\",\"DATA2\":\"79872676410\",\"DATA3\":\"1\",\"DATA4\":"
    "null,\"DATA5\":null,\"DATA6\":null,\"DATA7\":null,\"DATA8\":null,"
    "\"OTHER\":null}\n"
    "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\",\"DATE\":"
    "1566395449,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444.1632\","
    "\"QUEUENAME\":\"disp_cc\",\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
    "\"DATA1\":\"\",\"DATA2\":\"79872676410\",\"DATA3\":\"1\",\"DATA4\":"
    "null,\"DATA5\":null,\"DATA6\":null,\"DATA7\":null,\"DATA8\":null,"
    "\"OTHER\":null}\n";
std::string not_valid_ending_string =
    "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\",\"DATE\":"
    "1566395449,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444.1632\","
    "\"QUEUENAME\":\"disp_cc\",\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
    "\"DATA1\":\"\",\"DATA2\":\"79872676410\",\"DATA3\":\"1\",\"DATA4\":"
    "null,\"DATA5\":null,\"DATA6\":null,\"DATA7\":null,\"DATA8\":null,"
    "\"OTHER\":null}\n"
    "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\","
    "\"DATE\":1566395449,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444."
    "1632\","
    "\"QUEUENAME\":\"disp_cc\",\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
    "\"DATA1\":\"\",\"DATA2\":\"79872676410\",\"DATA3\":\"1\",\"DATA4\":"
    "null,\"DATA5\":null,\"DATA6\":null,\"DATA7\":null,\"DATA8\":null,"
    "\"OTHER\":null}";

std::string valid_long_long_string =
    "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\",\"DATE\":"
    "1566467280,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566467144.1696\","
    "\"QUEUENAME\":\"disp_cc\",\"AGENT\":\"Agent/"
    "8278078728\",\"ACTION\":\"BLINDTRANSFER\",\"DATA1\":\"+79153456754\","
    "\"DATA2\":\"\",\"DATA3\":\"\",\"DATA4\":null,\"DATA5\":null,\"DATA6\":"
    "null,"
    "\"DATA7\":null,\"DATA8\":null,\"OTHER\":null}\n"
    "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\","
    "\"DATE\":1566395449,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444."
    "1632\","
    "\"QUEUENAME\":\"disp_cc\",\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
    "\"DATA1\":\"\",\"DATA2\":\"79872676410\",\"DATA3\":\"1\",\"DATA4\":"
    "null,\"DATA5\":null,\"DATA6\":null,\"DATA7\":null,\"DATA8\":null,"
    "\"OTHER\":null}\n"
    "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\","
    "\"DATE\":1566395449,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444."
    "1632\","
    "\"QUEUENAME\":\"disp_cc\",\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
    "\"DATA1\":\"\",\"DATA2\":\"79872676410\",\"DATA3\":\"1\",\"DATA4\":null,"
    "\"DATA5\":null,\"DATA6\":null,\"DATA7\":null,\"DATA8\":null,"
    "\"OTHER\":null}\n";

std::string with_delimiter = "1\n2\n3\n4\n5\n6\n7\n8\n9\n0\n";
std::string with_double_delimiters = "1\n\n2\n";

std::string wo_delimiter = "1234567890";

std::string wo_delimiter_n = "1234567890\n";

}  // namespace

namespace callcenter_queues::unit_tests {

class RawMessageSeparation : public ::testing::Test {
 protected:
  std::unordered_map<std::string, std::vector<std::string>> data{
      {"VALID",
       {
           "{\"NODE\":\"TAXI-MYT-QAPP1\","
           "\"PARTITION\":\"TAXIMYT1\","
           "\"DATE\":1566395449,"
           "\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444.1632\","
           "\"QUEUENAME\":\"disp_cc\","
           "\"AGENT\":null,"
           "\"ACTION\":\"ENTERQUEUE\","
           "\"DATA1\":\"\","
           "\"DATA2\":\"79872676410\","
           "\"DATA3\":\"1\","
           "\"DATA4\":null,"
           "\"DATA5\":null,"
           "\"DATA6\":null,"
           "\"DATA7\":null,"
           "\"DATA8\":null,"
           "\"OTHER\":null}",
       }},
      {
          "VALID_LONG",
          {
              "{\"NODE\":\"TAXI-MYT-QAPP1\","
              "\"PARTITION\":\"TAXIMYT1\","
              "\"DATE\":1566395449,"
              "\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444.1632\","
              "\"QUEUENAME\":\"disp_cc\","
              "\"AGENT\":null,"
              "\"ACTION\":\"ENTERQUEUE\","
              "\"DATA1\":\"\","
              "\"DATA2\":\"79872676410\","
              "\"DATA3\":\"1\","
              "\"DATA4\":null,"
              "\"DATA5\":null,"
              "\"DATA6\":null,"
              "\"DATA7\":null,"
              "\"DATA8\":null,"
              "\"OTHER\":null}",

              "{\"NODE\":\"TAXI-MYT-QAPP1\","
              "\"PARTITION\":\"TAXIMYT1\","
              "\"DATE\":1566395449,"
              "\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444.1632\","
              "\"QUEUENAME\":\"disp_cc\","
              "\"AGENT\":null,"
              "\"ACTION\":\"ENTERQUEUE\","
              "\"DATA1\":\"\","
              "\"DATA2\":\"79872676410\","
              "\"DATA3\":\"1\","
              "\"DATA4\":null,"
              "\"DATA5\":null,"
              "\"DATA6\":null,"
              "\"DATA7\":null,"
              "\"DATA8\":null,"
              "\"OTHER\":null}",
          },
      },
      {"NOT_VALID_ENDING",
       {
           "{\"NODE\":\"TAXI-MYT-QAPP1\","
           "\"PARTITION\":\"TAXIMYT1\","
           "\"DATE\":1566395449,"
           "\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444.1632\","
           "\"QUEUENAME\":\"disp_cc\","
           "\"AGENT\":null,"
           "\"ACTION\":\"ENTERQUEUE\","
           "\"DATA1\":\"\","
           "\"DATA2\":\"79872676410\","
           "\"DATA3\":\"1\","
           "\"DATA4\":null,"
           "\"DATA5\":null,"
           "\"DATA6\":null,"
           "\"DATA7\":null,"
           "\"DATA8\":null,"
           "\"OTHER\":null}",

           "{\"NODE\":\"TAXI-MYT-QAPP1\","
           "\"PARTITION\":\"TAXIMYT1\","
           "\"DATE\":1566395449,"
           "\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444.1632\","
           "\"QUEUENAME\":\"disp_cc\","
           "\"AGENT\":null,"
           "\"ACTION\":\"ENTERQUEUE\","
           "\"DATA1\":\"\","
           "\"DATA2\":\"79872676410\","
           "\"DATA3\":\"1\","
           "\"DATA4\":null,"
           "\"DATA5\":null,"
           "\"DATA6\":null,"
           "\"DATA7\":null,"
           "\"DATA8\":null,"
           "\"OTHER\":null}",
       }},
      {"VALID_LONG_LONG",
       {
           "{\"NODE\":\"TAXI-MYT-QAPP1\","
           "\"PARTITION\":\"TAXIMYT1\","
           "\"DATE\":1566467280,"
           "\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566467144.1696\","
           "\"QUEUENAME\":\"disp_cc\","
           "\"AGENT\":\"Agent/8278078728\","
           "\"ACTION\":\"BLINDTRANSFER\","
           "\"DATA1\":\"+79153456754\","
           "\"DATA2\":\"\","
           "\"DATA3\":\"\","
           "\"DATA4\":null,"
           "\"DATA5\":null,"
           "\"DATA6\":null,"
           "\"DATA7\":null,"
           "\"DATA8\":null,"
           "\"OTHER\":null}",

           "{\"NODE\":\"TAXI-MYT-QAPP1\","
           "\"PARTITION\":\"TAXIMYT1\","
           "\"DATE\":1566395449,"
           "\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444.1632\","
           "\"QUEUENAME\":\"disp_cc\","
           "\"AGENT\":null,"
           "\"ACTION\":\"ENTERQUEUE\","
           "\"DATA1\":\"\","
           "\"DATA2\":\"79872676410\","
           "\"DATA3\":\"1\","
           "\"DATA4\":null,"
           "\"DATA5\":null,"
           "\"DATA6\":null,"
           "\"DATA7\":null,"
           "\"DATA8\":null,"
           "\"OTHER\":null}",

           "{\"NODE\":\"TAXI-MYT-QAPP1\","
           "\"PARTITION\":\"TAXIMYT1\","
           "\"DATE\":1566395449,"
           "\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444.1632\","
           "\"QUEUENAME\":\"disp_cc\","
           "\"AGENT\":null,"
           "\"ACTION\":\"ENTERQUEUE\","
           "\"DATA1\":\"\","
           "\"DATA2\":\"79872676410\","
           "\"DATA3\":\"1\","
           "\"DATA4\":null,"
           "\"DATA5\":null,"
           "\"DATA6\":null,"
           "\"DATA7\":null,"
           "\"DATA8\":null,"
           "\"OTHER\":null}",
       }},
      {"WITH_DELIMITER",
       {
           "1",
           "2",
           "3",
           "4",
           "5",
           "6",
           "7",
           "8",
           "9",
           "0",
       }},
      {"WITH_DOUBLE_DELIMITER", {"1", "2"}},
      {"WO_DELIMITER",
       {
           "1234567890",
       }},
      {"WO_DELIMITER_N",
       {
           "1234567890",
       }},
  };
};
TEST_F(RawMessageSeparation, TestValid) {
  EXPECT_EQ(utils::SplitEvents(valid_string), data["VALID"]);
}

TEST_F(RawMessageSeparation, TestValidLong) {
  EXPECT_EQ(utils::SplitEvents(valid_long_string), data["VALID_LONG"]);
}

TEST_F(RawMessageSeparation, TestNotValidEnding) {
  EXPECT_EQ(utils::SplitEvents(not_valid_ending_string),
            data["NOT_VALID_ENDING"]);
}

TEST_F(RawMessageSeparation, TestValidLongLong) {
  EXPECT_EQ(utils::SplitEvents(valid_long_long_string),
            data["VALID_LONG_LONG"]);
}
TEST_F(RawMessageSeparation, TestWithDelimiter) {
  EXPECT_EQ(utils::SplitEvents(with_delimiter), data["WITH_DELIMITER"]);
}
TEST_F(RawMessageSeparation, TestWithDoubleDelimiter) {
  EXPECT_EQ(utils::SplitEvents(with_double_delimiters),
            data["WITH_DOUBLE_DELIMITER"]);
}
TEST_F(RawMessageSeparation, TestWoDelimiter) {
  EXPECT_EQ(utils::SplitEvents(wo_delimiter), data["WO_DELIMITER"]);
}
TEST_F(RawMessageSeparation, TestWoDelimiter_n) {
  EXPECT_EQ(utils::SplitEvents(wo_delimiter_n), data["WO_DELIMITER_N"]);
}
}  // namespace callcenter_queues::unit_tests
