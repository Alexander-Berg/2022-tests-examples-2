#include <gtest/gtest.h>
#include <optional>
#include <userver/utest/utest.hpp>

#include <models/processing_events/events/restore-helper.hpp>

namespace std {
template <typename T>
static ostream& operator<<(ostream& os, const vector<T>& in) {
  os << "{";
  for (size_t i(0); i < in.size(); ++i) {
    if (i) os << " ";
    os << in[i];
  }
  return os << "}";
}

template <typename T>
static ostream& operator<<(ostream& os, const optional<T>& in) {
  if (in)
    os << *in;
  else
    os << "std::nullopt";
  return os;
}

}  // namespace std

namespace processing::models::processing_events {
static std::ostream& operator<<(std::ostream& os, const EventFromYt& in) {
  return os << in.event_id << "/" << in.order_key << "/"
            << in.handling_order_key << "/" << in.idempotency_token;
}
}  // namespace processing::models::processing_events

namespace processing::models {
static std::ostream& operator<<(std::ostream& os, const QueueEvent& in) {
  return os << in.event_id_ << "/" << in.order_key_ << "/"
            << in.handling_order_key_;
}
}  // namespace processing::models

namespace processing::models::processing_events::events::tests {

struct Param {
  const std::vector<EventFromYt> in_yt;
  const std::vector<QueueEvent> in_pg;
  const std::vector<EventFromYt> expected;
  const QueueEventPred is_create_event = [](const auto&) { return false; };
};

static std::ostream& operator<<(std::ostream& os, const Param& in) {
  return os << in.in_yt << " + " << in.in_pg << " => " << in.expected;
}

namespace {
QueueEvent MakePg(std::string event_id, int order_key,
                  std::optional<int32_t> handling_order_key = std::nullopt) {
  std::string idempotency_token = event_id;
  return QueueEvent{
      event_id,            // event_id
      order_key,           // order_key
      {},                  // created
      {},                  // payload
      idempotency_token,   // idempotency_token
      false,               // need_handle
      {},                  // updated
      {},                  // due
      false,               // is_malformed
      {},                  // extra_order_key
      handling_order_key,  // handling_order_key
      false,               // is_duplicate
      {}                   // handling_counters
  };
}

EventFromYt MakeYt(std::string event_id, int order_key,
                   std::optional<int32_t> handling_order_key = std::nullopt) {
  std::string idempotency_token = event_id;
  return EventFromYt{{},                  // scope
                     {},                  // queue
                     {},                  // item_id
                     event_id,            // event_id
                     order_key,           // order_key
                     {},                  // created
                     {},                  // payload
                     idempotency_token,   // idempotency_token
                     false,               // need_handle
                     {},                  // updated
                     false,               // is_archivable
                     {},                  // due
                     {},                  // extra_order_key
                     handling_order_key,  // handling_order_key
                     false};              // is_duplicate
}

}  // namespace

class PrepareEventsForRestoreTest : public testing::TestWithParam<Param> {};

TEST_P(PrepareEventsForRestoreTest, Test) {
  const Param& param = GetParam();
  std::vector<EventFromYt> yt(param.in_yt);
  PrepareEventsForRestore(param.is_create_event, param.in_pg, yt);
  EXPECT_EQ(yt, param.expected);
}

INSTANTIATE_TEST_SUITE_P(
    ProcaasEvents, PrepareEventsForRestoreTest,
    ::testing::Values(
        // with handling_order_key and order_key
        Param{{MakeYt("a", 0, 0)}, {}, {MakeYt("a", -1, 0)}},
        Param{{MakeYt("a", 0, 0)}, {MakePg("b", 0)}, {MakeYt("a", -1, 0)}},
        Param{{MakeYt("a", 0, 0)}, {MakePg("b", 0, 0)}, {MakeYt("a", -1, -1)}},
        Param{{MakeYt("a", 0, 0), MakeYt("b", 1, 1)},
              {MakePg("c", 0, 0)},
              {MakeYt("a", -2, -2), MakeYt("b", -1, -1)}},
        Param{{MakeYt("b", 1, 1)}, {MakePg("c", 0, 0)}, {MakeYt("b", -1, -1)}},
        Param{
            {MakeYt("b", -1, -1)}, {MakePg("c", 0, 0)}, {MakeYt("b", -1, -1)}},
        Param{{MakeYt("a", -2, -1), MakeYt("b", -1, -2), MakeYt("c", 0, 0)},
              {MakePg("d", 0, 0), MakePg("e", 1, 1)},
              {MakeYt("b", -2, -3), MakeYt("a", -3, -2), MakeYt("c", -1, -1)}},
        Param{{MakeYt("a", -10, -10)},
              {MakePg("b", 0, 0)},
              {MakeYt("a", -1, -1)}},
        // only with order_key
        Param{{MakeYt("a", 0)}, {}, {MakeYt("a", -1, -1)}},
        Param{{MakeYt("a", 4)}, {MakePg("a", 0)}, {}},
        Param{{MakeYt("b", 0)}, {MakePg("a", 0)}, {MakeYt("b", -1, -1)}},
        Param{{MakeYt("a", 0)}, {MakePg("a", 0), MakePg("b", 1)}, {}},
        Param{{MakeYt("a", 0)},
              {MakePg("b", 0), MakePg("c", 1)},
              {MakeYt("a", -1, -1)}},
        Param{{MakeYt("a", 0), MakeYt("b", 1)},
              {MakePg("b", 0), MakePg("c", 1)},
              {MakeYt("a", -1, -1)}},
        Param{{MakeYt("a", 0), MakeYt("b", 0)},
              {MakePg("b", 0), MakePg("c", 1)},
              {MakeYt("a", -1, -1)}},
        Param{{MakeYt("a", 0), MakeYt("b", 1), MakeYt("c", 2)},
              {MakePg("d", 0), MakePg("e", 1)},
              {MakeYt("a", -3, -3), MakeYt("b", -2, -2), MakeYt("c", -1, -1)}},
        Param{{MakeYt("a", -3), MakeYt("b", -2), MakeYt("c", -1)},
              {MakePg("d", 0), MakePg("e", 1)},
              {MakeYt("a", -3, -3), MakeYt("b", -2, -2), MakeYt("c", -1, -1)}},
        Param{{MakeYt("a", -3), MakeYt("b", -2), MakeYt("c", -1)},
              {MakePg("d", 5), MakePg("e", 6)},
              {MakeYt("a", 2, 2), MakeYt("b", 3, 3), MakeYt("c", 4, 4)}},
        Param{{MakeYt("a", 0), MakeYt("b", 1), MakeYt("c", 2)},
              {MakePg("c", 0), MakePg("d", 1)},
              {MakeYt("a", -2, -2), MakeYt("b", -1, -1)}},
        Param{{MakeYt("a", 0), MakeYt("b", 1), MakeYt("c", 2)},
              {MakePg("b", 0), MakePg("c", 1), MakePg("d", 2)},
              {MakeYt("a", -1, -1)}},
        Param{{MakeYt("a", -1), MakeYt("b", 0), MakeYt("c", 1), MakeYt("d", 2)},
              {MakePg("c", 0), MakePg("d", 1), MakePg("e", 2)},
              {MakeYt("a", -2, -2), MakeYt("b", -1, -1)}},
        // special cases
        Param{{MakeYt("restart0", 0, 0), MakeYt("restart1", 1, 1),
               MakeYt("transporting", 2, 2), MakeYt("complete", 3, 3),
               MakeYt("payment_events", 4, 4)},
              {MakePg("payorder", 0, 0)},
              {MakeYt("restart0", -5, -5), MakeYt("restart1", -4, -4),
               MakeYt("transporting", -3, -3), MakeYt("complete", -2, -2),
               MakeYt("payment_events", -1, -1)},
              [](const QueueEvent& e) { return e.event_id_ == "create"; }},
        // empty one
        Param()));

}  // namespace processing::models::processing_events::events::tests
