#include <experiments3/kwargs_builders/consumer.hpp>
#include <experiments3/models/cache_manager.hpp>
#include <experiments3/test_experiment.hpp>

#include <yt-logger/logger.hpp>
#include <yt-logger/messages/extra_info/message.hpp>

#include "view.hpp"

namespace handlers::experiments_try::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  Response200 response;

  yt_logger::messages::extra_info message;
  message.info = request.body;
  dependencies.yt_logger->Log(message);

  experiments3::kwargs_builders::Consumer builder;
  builder.UpdateUserId(request.body);

  auto greet_setting =
      dependencies.experiments3->GetValue<experiments3::Greet>(builder);

  response.value = greet_setting ? greet_setting->greeting : "hello";

  return response;
}

}  // namespace handlers::experiments_try::post
