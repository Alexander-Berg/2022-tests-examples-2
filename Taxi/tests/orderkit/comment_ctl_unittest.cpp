#include <gtest/gtest.h>
#include <common/test_config.hpp>
#include <config/config.hpp>
#include <controllers/card_operations.hpp>
#include <orderkit/comment_ctl.hpp>

namespace orderkit {

class NotFound : public std::runtime_error {
  using std::runtime_error::runtime_error;
};

struct CommentCtlTester {
  static const std::string& Find(CommentCtl& comment_ctl,
                                 const std::string& key) {
    const auto& it = comment_ctl.chunk_pairs.find(key);
    if (it == comment_ctl.chunk_pairs.cend()) {
      throw NotFound("unknown comment key: " + key);
    }
    return it->second;
  }
};

TEST(comment_ctl, simple) {
  config::DocsMap docs_map = config::DocsMapForTest();
  docs_map.Override("CRUTCH", true);
  config::Config config(docs_map);

  {
    CommentCtl comment_ctl(std::string(), config);
    EXPECT_TRUE(comment_ctl.Enabled());
  }

  {
    CommentCtl comment_ctl(
        "param1-value1, PAraM2-value2-Value3-value4  , param3, "
        "param4---//param5-value5",
        config);

    const auto& param1 = CommentCtlTester::Find(comment_ctl, "param1");
    const auto& param2 = CommentCtlTester::Find(comment_ctl, "param2");
    const auto& param4 = CommentCtlTester::Find(comment_ctl, "param4");

    const std::string excpect1 = "value1";
    const std::string excpect2 = "value2 value3 value4";
    const std::string excpect4 = "";

    EXPECT_EQ(param1, excpect1);
    EXPECT_EQ(param2, excpect2);
    ASSERT_THROW(CommentCtlTester::Find(comment_ctl, "param3"), NotFound);
    EXPECT_EQ(param4, excpect4);
    ASSERT_THROW(CommentCtlTester::Find(comment_ctl, "param5"), NotFound);
  }

  {
    CommentCtl comment_ctl0("failcard-0", config);
    ASSERT_THROW(comment_ctl0.RaiseInvalidCard(),
                 card_operations::InvalidCardError);

    CommentCtl comment_ctl1("failcard-1", config);
    ASSERT_NO_THROW(comment_ctl1.RaiseInvalidCard());
  }

  {
    docs_map.Override("CRUTCH", false);
    config::Config config_off(docs_map);

    CommentCtl comment_ctl("failcard-0", config_off);
    EXPECT_FALSE(comment_ctl.Enabled());

    ASSERT_NO_THROW(comment_ctl.RaiseInvalidCard());
  }
}

}  // namespace orderkit
