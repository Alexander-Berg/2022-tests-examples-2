#include "wrappers.hpp"
#include "stats.hpp"

#include <gtest/gtest.h>

using Pool = utils::mongo::Pool;
using Client = utils::mongo::Client;
using ConnectionFailedError = utils::mongo::ConnectionFailedError;
using Storage = utils::mongo::stats::Storage;
using CollectionStorage = utils::mongo::stats::CollectionStorage;

namespace {
utils::mongo::stats::ResultsArray results{{}};
utils::mongo::stats::CollectionTimingsArray timings{{}};
CollectionStorage GetStatsStorage() {
  return CollectionStorage(std::make_shared<Storage>(), results, timings,
                           results, timings);
}
}  // namespace

TEST(MongoWrappers, NullCursorAndConnection) {
  utils::mongo::CursorWrapper cursor(
      Pool::Entry(nullptr, [](Client* c) { delete c; }), nullptr,
      GetStatsStorage(), true);

  EXPECT_THROW(cursor.more(), ConnectionFailedError);
  EXPECT_THROW(cursor.next(), ConnectionFailedError);
  EXPECT_THROW(cursor.nextSafe(), ConnectionFailedError);
  EXPECT_THROW(cursor.itcount(), ConnectionFailedError);
}

TEST(MongoWrappers, NullCursor) {
  Client* conn = new ::mongo::DBClientConnection();
  utils::mongo::CursorWrapper cursor(
      Pool::Entry(conn, [](Client* c) { delete c; }), nullptr,
      GetStatsStorage(), true);

  EXPECT_THROW(cursor.more(), ConnectionFailedError);
  EXPECT_THROW(cursor.next(), ConnectionFailedError);
  EXPECT_THROW(cursor.nextSafe(), ConnectionFailedError);
  EXPECT_THROW(cursor.itcount(), ConnectionFailedError);
}

TEST(MongoWrappers, NullConnection) {
  ::mongo::DBClientConnection client;  // for ::mongo cursor only
  auto cur = new ::mongo::DBClientCursor(&client, "ns", 1, 1, 0, 0);
  utils::mongo::CursorWrapper cursor(
      Pool::Entry(nullptr, [](Client* c) { delete c; }), cur, GetStatsStorage(),
      true);

  EXPECT_THROW(cursor.more(), ConnectionFailedError);
  EXPECT_THROW(cursor.next(), ConnectionFailedError);
  EXPECT_THROW(cursor.nextSafe(), ConnectionFailedError);
  EXPECT_THROW(cursor.itcount(), ConnectionFailedError);
}
