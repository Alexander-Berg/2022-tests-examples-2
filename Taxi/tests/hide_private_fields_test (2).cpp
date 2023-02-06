#include <gtest/gtest.h>

#include <unordered_map>

#include "messages_data.hpp"
#include "utils/utils.hpp"

namespace callcenter_stats::unit_tests {

class PrivateFieldsData : public MessagesData {
 protected:
  std::unordered_map<std::string, std::string> log_string{
      {"ENTERQUEUE",
       "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\",\"DATE\":"
       "1500000000,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1500000000.0000\","
       "\"QUEUENAME\":\"disp_cc\",\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
       "\"DATA1\":\"\",\"DATA2\":\"***\",\"DATA3\":\"1\",\"DATA4\":"
       "null,\"DATA5\":null,\"DATA6\":null,\"DATA7\":null,\"DATA8\":null,"
       "\"OTHER\":null}"},
      {"BLINDTRANSFER",
       "{\"NODE\":\"TAXI-MYT-QAPP1\",\"PARTITION\":\"TAXIMYT1\",\"DATE\":"
       "1500000002,\"CALLID\":\"taxi-myt-qapp1.yndx.net-1500000000.0000\","
       "\"QUEUENAME\":\"disp_cc\",\"AGENT\":\"Local/1000001287@CC_AGENTS/n\","
       "\"ACTION\":\"BLINDTRANSFER\",\"DATA1\":\"***\",\"DATA2\":"
       "\"CC_TXFR\",\"DATA3\":\"1\",\"DATA4\":\"1\",\"DATA5\":\"1\","
       "\"DATA6\":null,"
       "\"DATA7\":null,\"DATA8\":null,\"OTHER\":null}"},
  };

  std::unordered_map<std::string, std::string> phone_samples{
      {"7",
       "{\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
       "\"DATA1\":\"\",\"DATA2\":\"79872676410\","
       "\"DATA3\":\"1\",\"DATA4\":null,\"DATA5\":null}"},
      {"+7",
       "{\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
       "\"DATA1\":\"\",\"DATA2\":\"+79872676410\","
       "\"DATA3\":\"1\",\"DATA4\":null,\"DATA5\":null}"},
      {"D7",
       "{\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
       "\"DATA1\":\"\",\"DATA2\":\"D79872676410\","
       "\"DATA3\":\"1\",\"DATA4\":null,\"DATA5\":null}"},
      {"8",
       "{\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
       "\"DATA1\":\"\",\"DATA2\":\"89872676410\","
       "\"DATA3\":\"1\",\"DATA4\":null,\"DATA5\":null}"},
      {"8181",
       "{\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
       "\"DATA1\":\"\",\"DATA2\":\"8181\","
       "\"DATA3\":\"1\",\"DATA4\":null,\"DATA5\":null}"},
  };
  std::unordered_map<std::string, std::string> phone_hides{
      {"7",
       "{\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
       "\"DATA1\":\"\",\"DATA2\":\"***\","
       "\"DATA3\":\"1\",\"DATA4\":null,\"DATA5\":null}"},
      {"+7",
       "{\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
       "\"DATA1\":\"\",\"DATA2\":\"***\","
       "\"DATA3\":\"1\",\"DATA4\":null,\"DATA5\":null}"},
      {"D7",
       "{\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
       "\"DATA1\":\"\",\"DATA2\":\"***\","
       "\"DATA3\":\"1\",\"DATA4\":null,\"DATA5\":null}"},
      {"8",
       "{\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
       "\"DATA1\":\"\",\"DATA2\":\"***\","
       "\"DATA3\":\"1\",\"DATA4\":null,\"DATA5\":null}"},
      {"8181",
       "{\"AGENT\":null,\"ACTION\":\"ENTERQUEUE\","
       "\"DATA1\":\"\",\"DATA2\":\"***\","
       "\"DATA3\":\"1\",\"DATA4\":null,\"DATA5\":null}"},
  };
};

TEST_F(PrivateFieldsData, TestEnterQueue) {
  EXPECT_EQ(utils::HidePrivateFields(qapp_event["ENTERQUEUE"]),
            log_string["ENTERQUEUE"]);
}

TEST_F(PrivateFieldsData, TestBlindTransfer) {
  EXPECT_EQ(utils::HidePrivateFields(qapp_event["BLINDTRANSFER"]),
            log_string["BLINDTRANSFER"]);
}

TEST_F(PrivateFieldsData, TestLogAllString) {
  EXPECT_EQ(utils::HidePrivateFields(qapp_event["CONNECT"]),
            qapp_event["CONNECT"]);
}

TEST_F(PrivateFieldsData, TestHidePhone7) {
  EXPECT_EQ(utils::HidePrivateFields(phone_samples["7"]), phone_hides["7"]);
}
TEST_F(PrivateFieldsData, TestHidePhonePlus7) {
  EXPECT_EQ(utils::HidePrivateFields(phone_samples["+7"]), phone_hides["+7"]);
}
TEST_F(PrivateFieldsData, TestHidePhoneD7) {
  EXPECT_EQ(utils::HidePrivateFields(phone_samples["D7"]), phone_hides["D7"]);
}
TEST_F(PrivateFieldsData, TestHidePhone8) {
  EXPECT_EQ(utils::HidePrivateFields(phone_samples["8"]), phone_hides["8"]);
}
TEST_F(PrivateFieldsData, TestHidePhone8181) {
  EXPECT_EQ(utils::HidePrivateFields(phone_samples["8181"]),
            phone_hides["8181"]);
}

}  // namespace callcenter_stats::unit_tests
