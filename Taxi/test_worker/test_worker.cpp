#include "test_worker.hpp"

#include "utils/vad_config.hpp"
#include "workers/ivr/algorithm_workers/action_with_log_info.hpp"
#include "workers/ivr/algorithm_workers/states.hpp"

#include <defs/definitions.hpp>

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/logging/log.hpp>

namespace ivr_dispatcher::workers::ivr::test {
namespace base = ivr_dispatcher::workers::ivr;
namespace vad = ivr_dispatcher::utils::vad;

TestWorker::TestWorker(const components::ComponentConfig& config,
                       const components::ComponentContext& context)
    : BaseIvrAlgorithmWorker(config, context) {
  worker_name_ = kName;
  state_handlers = {
      {kInitiating, &BaseIvrAlgorithmWorker::ProcessInit},
      {kAnswering, &BaseIvrAlgorithmWorker::ProcessInit},
      {kPlaying, &BaseIvrAlgorithmWorker::ProcessInit},
      {kAsking, &BaseIvrAlgorithmWorker::ProcessAsk},
      {kHangup, &BaseIvrAlgorithmWorker::ProcessHangup}
      // ProcessHangup not initialized, return Hangup
  };
}

ivr_dispatcher::models::ActionForLogging TestWorker::ProcessInit(
    [[maybe_unused]] const handlers::ActionRequest& request,
    [[maybe_unused]] BaseContext& context) {
  context.state = ivr_dispatcher::workers::ivr::kAnswering;
  LOG_INFO() << "Hoooray!";
  IncStats("answering");
  auto builder = formats::json::ValueBuilder();
  builder["vad-threshold"] = 40;
  builder["vad-voice-ms"] = 20;
  builder["vad-silence-ms"] = 20;
  builder["no-input-timeout-ms"] = 10000;
  builder["speech-complete-timeout-ms"] = 2000;
  builder["speech-timeout-ms"] = 10000;
  auto vad_config =
      vad::Parse(builder.ExtractValue(), formats::parse::To<vad::VadConfig>());

  if (request.action.error_cause) {
    LOG_WARNING() << "Error:" << *request.action.error_cause;
    context.state = ivr_dispatcher::workers::ivr::kHangup;
    return Hangup();
  }
  if (request.action.type == handlers::ActionResultType::kInitial) {
    context.state = ivr_dispatcher::workers::ivr::kAnswering;
    return Answer(false);
  } else if (request.action.type == handlers::ActionResultType::kAnswer) {
    context.state = ivr_dispatcher::workers::ivr::kPlaying;
    return Play("oiw/check.wav");
  } else if (request.action.type == handlers::ActionResultType::kPlay) {
    context.state = ivr_dispatcher::workers::ivr::kAsking;

    return Ask("Тест диалога. Нажмите 1 или скажите проверка чтобы повторить.",
               {}, false, vad_config, false, "any");
  }
  return Hangup();
}

ivr_dispatcher::models::ActionForLogging TestWorker::ProcessAsk(
    [[maybe_unused]] const handlers::ActionRequest& request,
    [[maybe_unused]] BaseContext& context) {
  auto builder = formats::json::ValueBuilder();
  builder["vad-threshold"] = 40;
  builder["vad-voice-ms"] = 20;
  builder["vad-silence-ms"] = 20;
  builder["no-input-timeout-ms"] = 10000;
  builder["speech-complete-timeout-ms"] = 2000;
  builder["speech-timeout-ms"] = 10000;
  auto vad_config =
      vad::Parse(builder.ExtractValue(), formats::parse::To<vad::VadConfig>());

  if (request.action.error_cause) {
    LOG_WARNING() << "Error:" << *request.action.error_cause;
    context.state = ivr_dispatcher::workers::ivr::kHangup;
    return Hangup();
  }
  if (request.action.user_input) {
    LOG_INFO() << "Replied:" << *request.action.user_input;
    if (*request.action.user_input == "DIGIT: 1" or
        *request.action.user_input == "Проверка") {
      return Ask({}, "tw/check.wav", false, vad_config, false, "any");
    } else {
      context.state = ivr_dispatcher::workers::ivr::kHangup;
      return Hangup();
    }
  }
  context.state = ivr_dispatcher::workers::ivr::kHangup;
  return Hangup();
}

}  // namespace ivr_dispatcher::workers::ivr::test
