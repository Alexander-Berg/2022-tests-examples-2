#pragma once

#include <unordered_map>

#include "utils/utils.hpp"

namespace callcenter_stats::unit_tests {

const auto kMockTime = std::chrono::system_clock::from_time_t(1500000004);

class MessagesData : public ::testing::Test {
 protected:
  std::string kCallId = "taxi-myt-qapp1.yndx.net-1500000000.0000";

  std::unordered_map<std::string, std::string> pd_id_mapping{
      {"+79872676410", "+79872676410"}};

  std::unordered_map<std::string, std::string> qapp_event{
      // call started
      {"META",
       "{\"NODE\":\"YTC-TAXI-M9-QPROC1\",\"PARTITION\":\"TAXI1\",\"DATE\":"
       "1500000000,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1500000000.0000\","
       "\"QUEUENAME\":\"disp_cc\",\"AGENT\":null,\"ACTION\":\"META\",\"DATA1\":"
       "\"0\","
       "\"DATA2\":\"0002040101-0000065536-1582274287-0000030555\","
       "\"DATA3\":\"X-CC-OriginalDN\",\"DATA4\":\"+74832220220\","
       "\"DATA5\":null,\"DATA6\":null,"
       "\"DATA7\":null,\"DATA8\":null,\"OTHER\":null}"},
      {"ENTERQUEUE",
       "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\",\"DATE\":"
       "1500000000,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1500000000.0000\","
       "\"QUEUENAME\":\"disp_cc\",\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
       "\"DATA1\":\"\",\"DATA2\":\"+79872676410\",\"DATA3\":\"1\",\"DATA4\":"
       "null,\"DATA5\":null,\"DATA6\":null,\"DATA7\":null,\"DATA8\":null,"
       "\"OTHER\":null}"},
      // internal cancels
      {"RINGNOANSWER",
       "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\",\"DATE\":"
       "1500000001,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1500000000.0000\","
       "\"AGENT\":\"Local/1000001287@CC_AGENTS/n\","
       "\"QUEUENAME\":\"disp_cc\",\"ACTION\":\"RINGNOANSWER\",\"DATA1\":\"0\","
       "\"DATA2\":null,\"DATA3\":null,\"DATA4\":null,\"DATA5\":null,\"DATA6\":"
       "null,\"DATA7\":null,\"DATA8\":null,\"OTHER\":null}"},
      {"RINGCANCELED",
       "{\"NODE\":\"YTC-TAXI-MYT-QPROC1\",\"PARTITION\":\"TAXI1\",\"DATE\":"
       "1500000001,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1500000000.0000\","
       "\"QUEUENAME\":\"disp_cc\",\"AGENT\":\"Local/1000001287@CC_AGENTS/n\","
       "\"ACTION\":\"RINGCANCELED\",\"DATA1\":\"1\",\"DATA2\":null,\"DATA3\":"
       "null,"
       "\"DATA4\":null,\"DATA5\":null,\"DATA6\":null,\"DATA7\":null,\"DATA8\":"
       "null,"
       "\"OTHER\":null}"},
      // abandon
      {"ABANDON",
       "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\",\"DATE\":"
       "1500000001,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1500000000.0000\","
       "\"QUEUENAME\":\"disp_cc\",\"AGENT\":null,\"ACTION\":\"ABANDON\","
       "\"DATA1\":\"1\",\"DATA2\":\"1\",\"DATA3\":\"1\",\"DATA4\":null,"
       "\"DATA5\":null,\"DATA6\":null,\"DATA7\":null,\"DATA8\":null,\"OTHER\":"
       "null}"},
      // agent connect
      {"CONNECT",
       "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\",\"DATE\":"
       "1500000001,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1500000000.0000\","
       "\"QUEUENAME\":\"disp_cc\",\"AGENT\":\"Local/1000001287@CC_AGENTS/n\","
       "\"ACTION\":\"CONNECT\",\"DATA1\":\"1\",\"DATA2\":\"taxi-"
       "taxi-myt-qapp1.yndx.net-1500000000.0000\",\"DATA3\":\"9\",\"DATA4\":"
       "null,"
       "\"DATA5\":null,\"DATA6\":null,\"DATA7\":null,\"DATA8\":null,\"OTHER\":"
       "null}"},
      // completions
      {"COMPLETECALLER",
       "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\",\"DATE\":"
       "1500000002,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1500000000.0000\","
       "\"QUEUENAME\":\"disp_cc\",\"AGENT\":\"Local/1000001287@CC_AGENTS/n\","
       "\"ACTION\":\"COMPLETECALLER\",\"DATA1\":\"1\",\"DATA2\":"
       "\"1\",\"DATA3\":\"1\",\"DATA4\":null,\"DATA5\":null,\"DATA6\":null,"
       "\"DATA7\":null,\"DATA8\":null,\"OTHER\":null}"},
      {"COMPLETEAGENT",
       "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\",\"DATE\":"
       "1500000002,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1500000000.0000\","
       "\"QUEUENAME\":\"disp_cc\",\"AGENT\":\"Local/1000001287@CC_AGENTS/n\","
       "\"ACTION\":\"COMPLETEAGENT\",\"DATA1\":\"1\",\"DATA2\":"
       "\"1\",\"DATA3\":\"1\",\"DATA4\":null,\"DATA5\":null,\"DATA6\":null,"
       "\"DATA7\":null,\"DATA8\":null,\"OTHER\":null}"},
      {"BLINDTRANSFER",
       "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\",\"DATE\":"
       "1500000002,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1500000000.0000\","
       "\"QUEUENAME\":\"disp_cc\",\"AGENT\":\"Local/1000001287@CC_AGENTS/n\","
       "\"ACTION\":\"BLINDTRANSFER\",\"DATA1\":\"8002\",\"DATA2\":"
       "\"CC_TXFR\",\"DATA3\":\"1\",\"DATA4\":\"1\",\"DATA5\":\"1\","
       "\"DATA6\":null,"
       "\"DATA7\":null,\"DATA8\":null,\"OTHER\":null}"},
      {"ATTENDEDTRANSFER",
       "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\",\"DATE\":"
       "1500000002,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1500000000.0000\","
       "\"QUEUENAME\":\"disp_cc\",\"AGENT\":\"Local/1000001287@CC_AGENTS/n\","
       "\"ACTION\":\"ATTENDEDTRANSFER\",\"DATA1\":\"BRIDGE\","
       "\"DATA2\":"
       "\"4c388da1-f671-4644-9d08-83773983e9b8\",\"DATA3\":\"1\",\"DATA4\":"
       "\"1\",\"DATA5\":\"1\","
       "\"DATA6\":null,"
       "\"DATA7\":null,\"DATA8\":null,\"OTHER\":null}"},
      // unnecessary agent events
      {"ADDMEMBER",
       "{\"NODE\":\"YTC-TAXI-MYT-QPROC1\",\"PARTITION\":\"TAXI1\",\"DATE\":"
       "1500000000,\"CALLID\":\"REALTIME\",\"QUEUENAME\":\"disp_cc\","
       "\"AGENT\":\"Local/1000001287@CC_AGENTS/n\",\"ACTION\":\"ADDMEMBER\","
       "\"DATA1\":\"\",\"DATA2\":null,\"DATA3\":null,\"DATA4\":null,"
       "\"DATA5\":null,\"DATA6\":null,\"DATA7\":null,\"DATA8\":null,"
       "\"OTHER\":null}"},
      {"REMOVEMEMBER",
       "{\"NODE\":\"YTC-TAXI-MYT-QPROC11\",\"PARTITION\":\"TAXI11\",\"DATE\":"
       "1500000001,\"CALLID\":\"REALTIME\",\"QUEUENAME\":\"disp_cc\","
       "\"AGENT\":\"Local/1000001287@CC_AGENTS/n\",\"ACTION\":\"REMOVEMEMBER\","
       "\"DATA1\":\"\",\"DATA2\":null,\"DATA3\":null,\"DATA4\":null,\"DATA5\":"
       "null,"
       "\"DATA6\":null,\"DATA7\":null,\"DATA8\":null,\"OTHER\":null}"},
  };
};

}  // namespace callcenter_stats::unit_tests
