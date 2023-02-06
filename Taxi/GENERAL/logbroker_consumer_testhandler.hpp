#pragma once

#include <memory>

#include <component_util/named_component.hpp>
#include <config/configfwd.hpp>
#include <handler_util/base.hpp>
#include <utils/statistics.hpp>

namespace logbroker {
class Chunk;
}

namespace handlers {

/** This class provides handler for testing interaction of your components that
 * are dependent from LogbrokerConsumerComponent
 *
 * Emulating source of logbroker data is hardly feasable, so instead an extra
 * handler is provided that allows you to write data to given
 * LogbrokerConsumerComponent 'outside' of normal connection. Handler accepts
 * request with following data: uri: www.site.x/handler/address/consumer:
 * consumer - name of the LogbrokerConsumerComponent. If component does not
 * exist, error is returned request body: 'chunks' -> array of { 'headers' : {},
 * data : string } -> array of Chunks to upload if 'headers' value does not
 * contain required information, it will be autofilled. At the moment, required
 * informatin is topic, partition, offset, wtime. If topic or partition are
 * passed, user is responsible for both topic, partition and correct offset
 */
class LogbrokerConsumerTestHandler
    : public Base,
      public components::NamedComponentMixIn<LogbrokerConsumerTestHandler> {
 public:
  static constexpr const char* name = "lb-consumer-test";

  using Base::Base;

  void onLoad() override;
  void onUnload() override;
  void HandleRequestThrow(fastcgi::Request& request,
                          BaseContext& context) override;

 private:
  /** This set of constants will be used as default values for omited headers*/
  static constexpr const char* const kDefaultPartitionName = "test-partition";
  static constexpr const char* const kDefaultTopicName = "test-topic/";
  static constexpr const char* const kHeadersKey = "headers";
  static constexpr const char* const kDataKey = "data";
  static constexpr const char* const kChunksKey = "chunks";
  struct ChunkArgs;
  struct ChunksArgs;

  void WriteChunksToConsumer(LogbrokerConsumerComponent* target_broker,
                             BaseContext& requestContext);
  bool IsChunkValid(const logbroker::Chunk& chunk, std::string& what) const;
  Json::Value ChunkToJSON(const logbroker::Chunk& chunk) const;
  /** Tests given chunk for validity. Throws LogicException if invalid*/
  void ValidateChunk(const logbroker::Chunk& chunk) const;

  std::string GetConsumerFromRequest(fastcgi::Request& request) const;

  /** Offset for our default topic and partition. Correct offset for
   * user-supplied topics/partitions are user's responsibility
   */
  long current_offset = 0;

  /** Commit data storage for test-partition/test-topic
   */
  logbroker::CommitDataStorage test_storage_;
};

}  // namespace handlers
