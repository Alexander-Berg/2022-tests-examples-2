#include <userver/utest/utest.hpp>

#include <utils/request_query.hpp>

namespace {
const auto kRequestDatetimeFormat = "%Y-%m-%dT%H:%M:%E6S%Ez";
}
UTEST(StaffRequestQuery, TestDatetimeCorrection) {
  const auto now = utils::datetime::Now();
  using Concat = utils::StaffRequestQuery::Concatenation;
  using Cond = utils::StaffRequestQuery::Condition;

  {
    utils::StaffRequestQuery query(Concat::kAnd);
    query.PushDatetime("keyname", now, Cond::kGT);
    const auto expected = fmt::format(
        "((keyname>=\"{}\"))",
        utils::datetime::Timestring(now + std::chrono::microseconds(1),
                                    utils::datetime::kDefaultTimezone,
                                    kRequestDatetimeFormat));
    ASSERT_EQ(fmt::format("{}", query), expected);
  }

  {
    utils::StaffRequestQuery query(Concat::kAnd);
    query.PushDatetime("keyname", now, Cond::kLT);
    const auto expected = fmt::format(
        "((keyname<=\"{}\"))",
        utils::datetime::Timestring(now - std::chrono::microseconds(1),
                                    utils::datetime::kDefaultTimezone,
                                    kRequestDatetimeFormat));
    ASSERT_EQ(fmt::format("{}", query), expected);
  }
}

UTEST(StaffRequestQuery, TestSplitIntoChunks) {
  using Concat = utils::StaffRequestQuery::Concatenation;
  using Cond = utils::StaffRequestQuery::Condition;

  {
    utils::StaffRequestQuery query(Concat::kOr);
    for (int n = 0; n < 4; n++) {
      query.PushString("id", std::to_string(n), Cond::kEQ);
    }
    auto chunks = query.SplitIntoChunks(2);
    ASSERT_EQ(chunks.size(), 2);
    ASSERT_EQ(fmt::format("{}", chunks[0]), "((id==\"0\")or(id==\"1\"))");
    ASSERT_EQ(fmt::format("{}", chunks[1]), "((id==\"2\")or(id==\"3\"))");
  }
  {
    utils::StaffRequestQuery query(Concat::kOr);
    for (int n = 0; n < 5; n++) {
      query.PushString("id", std::to_string(n), Cond::kEQ);
    }
    auto chunks = query.SplitIntoChunks(2);
    ASSERT_EQ(chunks.size(), 3);
    ASSERT_EQ(fmt::format("{}", chunks[0]), "((id==\"0\")or(id==\"1\"))");
    ASSERT_EQ(fmt::format("{}", chunks[1]), "((id==\"2\")or(id==\"3\"))");
    ASSERT_EQ(fmt::format("{}", chunks[2]), "((id==\"4\"))");
  }
  {
    utils::StaffRequestQuery query(Concat::kOr);
    query.PushString("id", std::to_string(10), Cond::kEQ);
    auto chunks = query.SplitIntoChunks(2);
    ASSERT_EQ(chunks.size(), 1);
    ASSERT_EQ(fmt::format("{}", chunks[0]), "((id==\"10\"))");
  }
  {
    utils::StaffRequestQuery query(Concat::kAnd);
    auto chunks = query.SplitIntoChunks(2);
    ASSERT_EQ(chunks.size(), 0);
  }
}
