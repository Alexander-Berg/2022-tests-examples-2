#pragma once

#include <stq/client.hpp>

#include <stq_clients/test.hpp>

namespace stq {

template <typename ArgsStructType, typename ArgsType>
TaskArguments<ArgsType> Serialize(ArgsStructType&&);

using TestClient = QueueClient<stq_clients::test::Args, formats::json::Value>;

struct StqQueues {
  StqQueues(const clients::stq_agent::deprecated::Client& stq_agent_client_old,
            const clients::stq_agent::Client& stq_agent_client)
      : test({stq_agent_client_old, stq_agent_client, "test"}),
        queue1(stq_agent_client_old, stq_agent_client, "queue1"),
        queue2(stq_agent_client_old, stq_agent_client, "queue2"),
        queue3(stq_agent_client_old, stq_agent_client, "queue3")
  {}

  TestClient test;
  BaseQueueClient queue1;
  BaseQueueClient queue2;
  BaseQueueClient queue3;
};

using StqQueuesPtr = std::shared_ptr<StqQueues>;

}  // namespace stq
