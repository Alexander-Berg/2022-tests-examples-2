#include <gtest/gtest.h>

#include <storages/postgres/tests/test_buffers.hpp>
#include <storages/postgres/tests/util_pgtest.hpp>

#include <fmt/format.h>

#include <userver/storages/postgres/io/chrono.hpp>
#include <userver/storages/postgres/io/time_of_day.hpp>
#include <userver/storages/postgres/io/user_types.hpp>

USERVER_NAMESPACE_BEGIN

namespace utils::datetime {

template <typename Duration>
void PrintTo(const TimeOfDay<Duration>& val, std::ostream* os) {
  *os << fmt::format("{}", val);
}

}  // namespace utils::datetime

namespace {

namespace pg = storages::postgres;
namespace io = pg::io;

UTEST_F(PostgreConnection, TimeOfDayRoundtrip) {
  using Micros = utils::datetime::TimeOfDay<std::chrono::microseconds>;
  using Minutes = utils::datetime::TimeOfDay<std::chrono::minutes>;

  CheckConnection(conn);
  pg::ResultSet res{nullptr};
  EXPECT_NO_THROW(res = conn->Execute("select '06:30'::time"));
  Micros tod;
  EXPECT_NO_THROW(res[0][0].To(tod));
  EXPECT_EQ(Micros{"06:30"}, tod);

  EXPECT_NO_THROW(res = conn->Execute("select $1", tod));
  EXPECT_NO_THROW(res[0][0].To(tod));
  EXPECT_EQ(Micros{"06:30"}, tod);

  EXPECT_NO_THROW(res = conn->Execute("select $1", Minutes{"23:30"}));
  EXPECT_EQ(Minutes{"23:30"}, res[0][0].As<Minutes>());
}

}  // namespace

USERVER_NAMESPACE_END
