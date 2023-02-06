#include "statistics.hpp"

#include <sstream>

#include <fastcgi2/request.h>
#include <fmt/format.h>
#include <components/logbroker_consumer_component.hpp>
#include <config/config.hpp>
#include <config/config_component.hpp>
#include <config/statistics_config.hpp>
#include <handler_util/errors.hpp>
#include <utils/helpers/json.hpp>
#include <utils/helpers/params.hpp>

#include "logbroker_consumer_testhandler.hpp"

namespace handlers {

/** Data for single logbroker Chunk
 */
struct LogbrokerConsumerTestHandler::ChunkArgs {
  /** Data for given chunk **/
  std::unordered_map<std::string, std::string> headers;
  std::string data;

  ChunkArgs(const Json::Value& body) {
    utils::helpers::FetchMember(data, body,
                                LogbrokerConsumerTestHandler::kDataKey);
    utils::helpers::FetchMember(headers, body,
                                LogbrokerConsumerTestHandler::kHeadersKey);
  }

  bool HasTopicOrPartition() const;
};

/** Store several chunks for given LogbrokerConsumerComponent
 */
struct LogbrokerConsumerTestHandler::ChunksArgs {
  /** Name of the target LogbrokerConsumerComponent */
  std::string consumer;
  /** Chunks */
  std::vector<ChunkArgs> chunks;

  ChunksArgs(const std::string& body) {
    utils::helpers::Params params(body);
    // load data

    // chunks
    auto json_chunks = utils::helpers::FetchArray(
        params.Get(), LogbrokerConsumerTestHandler::kChunksKey);
    for (auto json_chunk : json_chunks) {
      chunks.emplace_back(json_chunk);
    }
  }
};

bool LogbrokerConsumerTestHandler::ChunkArgs::HasTopicOrPartition() const {
  bool has_topic_or_partition = false;
  if (headers.find(logbroker::Chunk::kTopicKey) != headers.end()) {
    has_topic_or_partition = true;
  }
  if (!has_topic_or_partition &&
      headers.find(logbroker::Chunk::kPartitionKey) != headers.end()) {
    has_topic_or_partition = true;
  }

  return has_topic_or_partition;
}

void LogbrokerConsumerTestHandler::onLoad() {
  Base::onLoad();

  current_offset = 0;

  LOG_INFO() << "Log broker consumer test handler is loaded";
}

void LogbrokerConsumerTestHandler::onUnload() { Base::onUnload(); }

void LogbrokerConsumerTestHandler::WriteChunksToConsumer(
    LogbrokerConsumerComponent* target_broker, BaseContext& requestContext) {
  if (target_broker == 0) {
    LOG_DEBUG() << "nullptr as target LogbrokerConsumerComponent";
    return;
  }

  ChunksArgs source_chunks(requestContext.request_body);

  if (!source_chunks.chunks.empty()) {
    auto& target_queue = target_broker->GetChunksQueue();

    logbroker::ChunksPtr target_chunks = std::make_shared<logbroker::Chunks>();
    // This cycle will destroy(!) source_chunks data -> logbroker::Chunk
    // constructor takes rref (&&) as input
    for (auto& chunk_source_data : source_chunks.chunks) {
      auto& chunk_headers = chunk_source_data.headers;
      const bool is_test_partition = !chunk_source_data.HasTopicOrPartition();
      // Fill missing headers
      if (is_test_partition) {
        // Autofilling
        chunk_headers[logbroker::Chunk::kTopicKey] = kDefaultTopicName;
        chunk_headers[logbroker::Chunk::kPartitionKey] = kDefaultPartitionName;
        chunk_headers[logbroker::Chunk::kOffsetKey] =
            std::to_string(current_offset);
        current_offset++;
      }
      // Will not overwrite existing value
      chunk_headers.insert(make_pair(
          std::string(logbroker::Chunk::kWtimeKey),
          std::to_string(utils::datetime::Timestamp(utils::datetime::Now()))));

      auto& commit_data_storage = is_test_partition
                                      ? test_storage_
                                      : target_broker->GetCommitDataStorage();

      target_chunks->emplace_back(commit_data_storage,
                                  chunk_source_data.headers,
                                  std::move(chunk_source_data.data));

      // Test chunk
      ValidateChunk(target_chunks->back());
    }

    target_queue.Push(target_chunks);

    LOG_INFO() << source_chunks.chunks.size() << " were fed into consumer"
               << requestContext.log_extra;

    // source_chunks does not contain any data anyway
    source_chunks.chunks.clear();
  }
}

void LogbrokerConsumerTestHandler::ValidateChunk(
    const logbroker::Chunk& chunk) const {
  std::string error_description;
  if (!IsChunkValid(chunk, error_description)) {
    Json::Value chunkAsJSON = ChunkToJSON(chunk);
    throw LogicException(
        fmt::format("incorrect chunk: {}: {}", error_description,
                    utils::helpers::WriteStyledJson(chunkAsJSON)));
  }
}

std::string LogbrokerConsumerTestHandler::GetConsumerFromRequest(
    fastcgi::Request& request) const {
  std::string consumer;
  const std::string& path = request.getScriptName();
  const size_t pos = path.rfind("/");
  if (pos != std::string::npos) {
    consumer = path.substr(pos + 1, std::string::npos);
  }

  return consumer;
}

void LogbrokerConsumerTestHandler::HandleRequestThrow(
    fastcgi::Request& request, BaseContext& requestContext) {
  std::string consumer = GetConsumerFromRequest(request);

  if (consumer.empty()) {
    throw BadRequest("No consumer name");
  }

  // Find component by name.
  fastcgi::Component* target_component =
      context()->findComponent<fastcgi::Component>(consumer);
  if (target_component == nullptr) {
    throw BadRequest(fmt::format("No such component: {0}", consumer));
  }

  LogbrokerConsumerComponent* target_broker =
      dynamic_cast<LogbrokerConsumerComponent*>(target_component);
  if (target_broker == nullptr) {
    throw BadRequest(fmt::format(
        "Component {0} is not LogbrokerConsumerComponent", consumer));
  }

  WriteChunksToConsumer(target_broker, requestContext);

  Json::Value result;
  result["status"] = "ok";

  requestContext.response = utils::helpers::WriteStyledJson(result);
}

bool LogbrokerConsumerTestHandler::IsChunkValid(const logbroker::Chunk& chunk,
                                                std::string& what) const {
  try {
    chunk.GetOffset();
    chunk.GetWtime();
    if (chunk.GetPartition().empty()) {
      what = "empty partition";
      return false;
    }
    if (chunk.GetTopic().empty()) {
      what = "empty topic";
      return false;
    }
  } catch (std::exception& e) {
    what = e.what();
    return false;
  } catch (...) {
    what = "unknown exception when checking chunk";
    return false;
  }

  return true;
}

Json::Value LogbrokerConsumerTestHandler::ChunkToJSON(
    const logbroker::Chunk& chunk) const {
  Json::Value result;
  // This method MUST work with incorrect chunks - so no calling
  // GetTopic/GetPartition etc
  result = Json::Value();
  for (auto header : chunk.GetHeaders()) {
    result[LogbrokerConsumerTestHandler::kHeadersKey][header.first] =
        header.second;
  }

  result[LogbrokerConsumerTestHandler::kDataKey] = chunk.Data();

  return result;
}

}  // namespace handlers
