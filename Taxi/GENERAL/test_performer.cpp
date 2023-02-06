#include "test_performer.hpp"

#include <userver/formats/parse/common_containers.hpp>
#include <userver/logging/log.hpp>

#include "utils/helpers.hpp"

namespace routehistory::processes {
using utils::ForType;

template <typename U>
static void FieldMapping(ForType<TestData> item, U& map) {
  map(item->counter, "counter");
  map(item->from, "from");
  map(item->to, "to");
}

void TestPerformer::Run(RunContext& ctx) {
  if (!ctx.data.counter) {
    ctx.data.counter = ctx.data.from;
  }
  ++*ctx.data.counter;
  LOG_INFO() << "TestPerformer (" << ctx.process_id
             << "): counter=" << *ctx.data.counter;
  if (*ctx.data.counter > ctx.data.to) {
    throw ProcessFailed("Bad counter value");
  }
  ctx.done = (*ctx.data.counter == ctx.data.to);
}

TestData Parse(const formats::json::Value& data,
               ::formats::parse::To<TestData> to) {
  return utils::ParseImpl(data, to);
}

::formats::json::Value Serialize(
    const TestData& data, ::formats::serialize::To<formats::json::Value> to) {
  return utils::SerializeImpl(data, to);
}

}  // namespace routehistory::processes
