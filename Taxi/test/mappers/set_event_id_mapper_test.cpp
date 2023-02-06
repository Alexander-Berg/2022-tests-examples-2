#include <userver/utest/utest.hpp>

#include <string>
#include <vector>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <eventus/mappers/set_event_id_mapper.hpp>
#include <eventus/order_event.hpp>

using eventus::common::OperationArgs;

TEST(Mappers, SetEventIdMapperTest) {
  auto event_id_mapper = eventus::mappers::SetEventIdMapper({});

  // good case
  {
    formats::json::ValueBuilder builder;
    builder[eventus::order_event::keys::kEventType] = "order";
    builder[eventus::order_event::keys::kOrderId] = "order_hash_here";
    builder[eventus::order_event::keys::kEventIndex] = 1;
    builder[eventus::order_event::keys::kEventKey] = "handle_key";

    eventus::mappers::Event event(builder.ExtractValue());

    event_id_mapper.Map(event);
    auto event_id =
        event.Get<std::string>(eventus::order_event::keys::kEventId);
    ASSERT_EQ(event_id, std::string("order/order_hash_here/1/handle_key"));
  }

  // bad case
  {
    eventus::mappers::Event event({});
    EXPECT_THROW(event_id_mapper.Map(event), std::exception);
  }
}
