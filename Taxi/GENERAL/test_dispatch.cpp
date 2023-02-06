#include "test_dispatch.hpp"

#include <userver/formats/parse/common_containers.hpp>
#include <userver/formats/serialize/boost_uuid.hpp>
#include <userver/testsuite/testpoint.hpp>
#include <userver/utils/assert.hpp>
#include <userver/utils/datetime.hpp>

#include <models/exceptions.hpp>

namespace grocery_dispatch::controllers {

TestDispatch::TestDispatch(controllers::BaseDispatchContext ctx,
                           components::DispatchRepository& repo)
    : BaseDispatch(std::move(ctx)), repo_{repo} {}

models::DispatchState TestDispatch::Schedule() const {
  auto info = repo_.Get(ctx_.dispatch_id);
  info.wave = ctx_.wave;

  auto test_data = [&info, &order = ctx_.order_info]() {
    formats::json::ValueBuilder builder;
    builder["dispatch"] = info;
    builder["order"] = order;
    return builder.ExtractValue();
  }();
  TESTPOINT("test_dispatch_schedule", test_data);

  models::DispatchState ret;
  ret.status_meta = info.status_meta;
  ret.performer = info.performer;
  ret.eta_timestamp = info.eta_timestamp;
  ret.status = models::DispatchStatus::kScheduled;
  ret.wave = info.wave;
  ret.status_meta = info.status_meta;

  return ret;
}

models::StatusAndFailureReason TestDispatch::Accept() const {
  auto info = repo_.Get(ctx_.dispatch_id);

  TESTPOINT("test_dispatch_accept", [&info] {
    formats::json::ValueBuilder builder;
    builder["dispatch"] = info;
    return builder.ExtractValue();
  }());

  return models::StatusAndFailureReason{std::move(info.status),
                                        info.failure_reason_type};
}

models::DispatchState TestDispatch::NotifyOrderAssembled() const {
  auto info = repo_.Get(ctx_.dispatch_id);

  TESTPOINT("test_order_ready", [&info] {
    formats::json::ValueBuilder builder;
    builder["dispatch"] = info;
    return builder.ExtractValue();
  }());

  models::DispatchState ret;
  ret.eta_timestamp = info.eta_timestamp;
  ret.performer = info.performer;
  ret.status = info.status;
  ret.status_meta.cargo_dispatch = info.status_meta.cargo_dispatch;

  formats::json::ValueBuilder builder = info.status_meta.extra;
  builder["_test"]["status"] = "order_assembled";
  ret.status_meta.extra = builder.ExtractValue();
  ret.wave = info.wave;

  return ret;
}

models::StatusAndFailureReason TestDispatch::Cancel() const {
  auto info = repo_.Get(ctx_.dispatch_id);

  TESTPOINT("test_dispatch_cancel", [&info] {
    formats::json::ValueBuilder builder;
    builder["dispatch"] = info;
    return builder.ExtractValue();
  }());

  return models::StatusAndFailureReason{
      std::move(models::DispatchStatus::kCanceled), info.failure_reason_type};
}

models::DispatchState TestDispatch::Status() const {
  auto info = repo_.Get(ctx_.dispatch_id);

  models::DispatchState ret;
  ret.eta_timestamp = info.eta_timestamp;

  TESTPOINT_CALLBACK(
      "test_dispatch_status", ([&info] {
        formats::json::ValueBuilder builder;
        builder["dispatch"] = info;
        return builder.ExtractValue();
      }()),
      ([&ret](const ::formats::json::Value& doc) {
        const auto ts =
            doc["eta_timestamp"]
                .As<std::optional<std::chrono::system_clock::time_point>>();
        ret.eta_timestamp = ts.value_or(::utils::datetime::Now());
      }));

  ret.performer = info.performer;
  ret.status = info.status;

  formats::json::ValueBuilder builder{info.status_meta.extra};
  builder["_test"]["status"] = "order_assembled";
  ret.status_meta.extra = builder.ExtractValue();
  ret.wave = info.wave;
  ret.status_meta.cargo_dispatch = info.status_meta.cargo_dispatch;

  return ret;
}

std::optional<models::PerformerContact> TestDispatch::PerformerContact() const {
  UINVARIANT(false, "FIXME");
  return {};
}

void TestDispatch::UpdateRescheduleSpecificFields(
    models::OrderInfo& /*info*/) const {}

bool TestDispatch::NeedRescheduleForOrderReady() const { return false; }

}  // namespace grocery_dispatch::controllers
