#include <views/logbroker/post-test/post/view.hpp>

#include <userver/engine/sleep.hpp>
#include <userver/logging/log.hpp>

namespace handlers::logbroker_post_test::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  std::vector<logbroker_producer::CommitFuture> commits;
  // auto seq_no = request.seq_no;
  for (ssize_t i = 0; i < request.count; i++) {
    auto message =
        std::make_unique<logbroker_producer::Message>(0, request.message);
    commits.push_back(
        dependencies.extra.positions->Publish(std::move(message)));
    engine::SleepFor(std::chrono::microseconds(request.delay_mcs));
  }

  for (auto& commit : commits) commit.Get();

  LOG_DEBUG() << "successfully published message to LogBroker";

  return Response200();
}

}  // namespace handlers::logbroker_post_test::post
