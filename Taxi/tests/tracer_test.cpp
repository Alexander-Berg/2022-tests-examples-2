#include <algorithm>
#include <deque>
#include <locale>
#include <string>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/tracing_config.hpp>

#include <gtest/gtest.h>

#include <logging/log_extra.hpp>
#include <utils/mock_now.hpp>

#include <fastcgi2/request.h>

#include <tracing/baggage.hpp>
#include <tracing/helpers.hpp>
#include <tracing/tracer.hpp>
#include <tracing/tracer_component.hpp>

#include <tracing/reporter.hpp>

TEST(TestTracer, ContextStack) {
  EXPECT_FALSE(bool(tracing::Tracer::ActiveContext()));

  auto span_context1 = std::make_shared<const tracing::SpanContext>(
      tracing::SpanContext{"sp_id1", "tr_id1", {}, {}});
  tracing::Tracer::ActivateContext(span_context1);
  ASSERT_TRUE(bool(tracing::Tracer::ActiveContext()));
  EXPECT_EQ(tracing::Tracer::ActiveContext()->span_id, "sp_id1");
  EXPECT_EQ(tracing::Tracer::ActiveContext()->trace_id, "tr_id1");

  auto span_context2 = std::make_shared<const tracing::SpanContext>(
      tracing::SpanContext{"sp_id2", "tr_id2", {}, {}});
  tracing::Tracer::ActivateContext(span_context2);
  ASSERT_TRUE(bool(tracing::Tracer::ActiveContext()));
  EXPECT_EQ(tracing::Tracer::ActiveContext()->span_id, "sp_id2");
  EXPECT_EQ(tracing::Tracer::ActiveContext()->trace_id, "tr_id2");

  tracing::Tracer::DeactivateContext();

  ASSERT_TRUE(bool(tracing::Tracer::ActiveContext()));
  EXPECT_EQ(tracing::Tracer::ActiveContext()->span_id, "sp_id1");
  EXPECT_EQ(tracing::Tracer::ActiveContext()->trace_id, "tr_id1");

  tracing::Tracer::DeactivateContext();

  EXPECT_FALSE(bool(tracing::Tracer::ActiveContext()));
}

TEST(TestTracer, StartSpan) {
  auto tracer = tracing::Tracer::GetTracer();
  ASSERT_TRUE(bool(tracer));

  auto span1 = tracer->StartSpan("span1");

  span1->AddBaggage("test_key", "test_value");
  span1->AddLocalBaggage("local_test_key", "local_test_value");

  auto span2 = tracer->StartSpan("span2", 1.0, span1->GetContext());
  EXPECT_EQ(span1->GetTraceId(), span2->GetTraceId());
  EXPECT_NE(span1->GetSpanId(), span2->GetSpanId());
  ASSERT_TRUE(span2->GetReference().is_initialized());
  EXPECT_EQ(span2->GetReference()->reference_type,
            tracing::Reference::ReferenceType::kChildOf);
  EXPECT_EQ(span2->GetReference()->context->span_id, span1->GetSpanId());
  EXPECT_EQ(span2->GetReference()->context->trace_id, span1->GetTraceId());
  EXPECT_EQ(span2->GetBaggage().size(), 1u);
  EXPECT_EQ(span2->GetLocalBaggage().size(), 1u);

  {
    auto test_key_iter = span2->GetBaggage().find("test_key");
    ASSERT_NE(test_key_iter, span2->GetBaggage().end());
    EXPECT_EQ(test_key_iter->second, std::string("test_value"));
  }
  {
    auto local_test_key_iter = span2->GetLocalBaggage().find("local_test_key");
    ASSERT_NE(local_test_key_iter, span2->GetLocalBaggage().end());
    EXPECT_EQ(local_test_key_iter->second, std::string("local_test_value"));
  }

  auto span3 = tracer->StartSpan("span3");
  EXPECT_TRUE(span3->GetReference().is_initialized());
  EXPECT_EQ(span3->GetBaggage(), span2->GetBaggage());
  EXPECT_EQ(span3->GetLocalBaggage(), span2->GetLocalBaggage());

  EXPECT_NE(span1->GetSpanId(), span3->GetSpanId());
  EXPECT_EQ(span1->GetTraceId(), span3->GetTraceId());
  EXPECT_NE(span2->GetSpanId(), span3->GetSpanId());
}

TEST(TestTracer, StartSpanWithStack) {
  auto tracer = tracing::Tracer::GetTracer();
  ASSERT_TRUE(bool(tracer));
  EXPECT_FALSE(bool(tracing::Tracer::ActiveContext()));

  auto span1 = tracer->StartSpan("span1");
  ASSERT_TRUE(bool(tracing::Tracer::ActiveContext()));
  EXPECT_EQ(tracing::Tracer::ActiveContext()->span_id, span1->GetSpanId());
  EXPECT_EQ(tracing::Tracer::ActiveContext()->trace_id, span1->GetTraceId());

  span1->AddBaggage("test_key", "test_value");
  span1->AddLocalBaggage("local_test_key", "local_test_value");

  {
    auto test_key_iter =
        tracing::Tracer::ActiveContext()->baggage.find("test_key");
    ASSERT_NE(test_key_iter, tracing::Tracer::ActiveContext()->baggage.end());
    EXPECT_EQ(test_key_iter->second, "test_value");
  }
  {
    auto test_key_iter =
        tracing::Tracer::ActiveContext()->local_baggage.find("local_test_key");
    ASSERT_NE(test_key_iter,
              tracing::Tracer::ActiveContext()->local_baggage.end());
    EXPECT_EQ(test_key_iter->second, "local_test_value");
  }

  auto span2 = tracer->StartSpan("span2");
  ASSERT_TRUE(bool(tracing::Tracer::ActiveContext()));
  EXPECT_EQ(tracing::Tracer::ActiveContext()->span_id, span2->GetSpanId());
  EXPECT_EQ(tracing::Tracer::ActiveContext()->trace_id, span2->GetTraceId());
  ASSERT_TRUE(span2->GetReference().is_initialized());
  EXPECT_EQ(span2->GetReference()->reference_type,
            tracing::Reference::ReferenceType::kChildOf);

  EXPECT_EQ(span2->GetTraceId(), span1->GetTraceId());
  EXPECT_NE(span2->GetSpanId(), span1->GetSpanId());

  {
    auto test_key_iter2 = span2->GetBaggage().find("test_key");
    ASSERT_NE(test_key_iter2, span2->GetBaggage().end());
    EXPECT_EQ(test_key_iter2->second, "test_value");
  }
  {
    auto test_key_iter2 = span2->GetLocalBaggage().find("local_test_key");
    ASSERT_NE(test_key_iter2, span2->GetLocalBaggage().end());
    EXPECT_EQ(test_key_iter2->second, "local_test_value");
  }
}

TEST(TestTracer, StartSpanAsync) {
  auto tracer = tracing::Tracer::GetTracer();
  ASSERT_TRUE(bool(tracer));
  EXPECT_FALSE(bool(tracing::Tracer::ActiveContext()));

  auto span1 = tracer->StartSpanAsync("span1");
  EXPECT_FALSE(bool(tracing::Tracer::ActiveContext()));

  span1->AddBaggage("test_key", "test_value");
  span1->AddLocalBaggage("local_test_key", "local_test_value");

  auto span2 = tracer->StartSpanAsync("span2", 1.0, span1->GetContext());
  EXPECT_EQ(span1->GetTraceId(), span2->GetTraceId());
  EXPECT_NE(span1->GetSpanId(), span2->GetSpanId());
  ASSERT_TRUE(span2->GetReference().is_initialized());
  EXPECT_EQ(span2->GetReference()->reference_type,
            tracing::Reference::ReferenceType::kChildOf);
  EXPECT_EQ(span2->GetReference()->context->span_id, span1->GetSpanId());
  EXPECT_EQ(span2->GetReference()->context->trace_id, span1->GetTraceId());

  {
    EXPECT_EQ(span2->GetBaggage().size(), 1u);
    auto test_key_iter = span2->GetBaggage().find("test_key");
    ASSERT_NE(test_key_iter, span2->GetBaggage().end());
    EXPECT_EQ(test_key_iter->second, std::string("test_value"));
  }
  {
    EXPECT_EQ(span2->GetLocalBaggage().size(), 1u);
    auto test_key_iter = span2->GetLocalBaggage().find("local_test_key");
    ASSERT_NE(test_key_iter, span2->GetLocalBaggage().end());
    EXPECT_EQ(test_key_iter->second, std::string("local_test_value"));
  }

  auto span3 = tracer->StartSpanAsync("span3");
  EXPECT_FALSE(span3->GetReference().is_initialized());
  EXPECT_TRUE(span3->GetBaggage().empty());
  EXPECT_TRUE(span3->GetLocalBaggage().empty());

  EXPECT_FALSE(bool(tracing::Tracer::ActiveContext()));
}

TEST(TestTracer, AsyncSpanContextScope) {
  auto tracer = tracing::Tracer::GetTracer();
  ASSERT_TRUE(bool(tracer));
  EXPECT_FALSE(bool(tracing::Tracer::ActiveContext()));
  EXPECT_NO_THROW({
    tracing::AsyncSpanContextScope scope(tracing::Tracer::ActiveContext());
  });

  auto span_context1 = std::make_shared<const tracing::SpanContext>(
      tracing::SpanContext{"sp_id1", "tr_id1", {}, {}});
  {
    tracing::AsyncSpanContextScope scope(span_context1);
    auto context = tracing::Tracer::ActiveContext();
    EXPECT_TRUE(bool(context));
    EXPECT_EQ("sp_id1", context->span_id);
    EXPECT_EQ("tr_id1", context->trace_id);
    EXPECT_TRUE(context->baggage.empty());
    EXPECT_TRUE(context->local_baggage.empty());
  }

  EXPECT_FALSE(bool(tracing::Tracer::ActiveContext()));

  tracing::Baggage mock_baggage{{tracing::baggage::kLoggedScopeName, "scope2"},
                                {tracing::baggage::kLink, "link2"}};

  auto span_context2 = std::make_shared<const tracing::SpanContext>(
      tracing::SpanContext{"sp_id2", "tr_id2", {}, mock_baggage});

  {
    tracing::AsyncSpanContextScope scope(span_context2);
    auto context = tracing::Tracer::ActiveContext();
    EXPECT_TRUE(bool(context));
    EXPECT_EQ("sp_id2", context->span_id);
    EXPECT_EQ("tr_id2", context->trace_id);
    EXPECT_TRUE(context->baggage.empty());
    EXPECT_EQ(mock_baggage, context->local_baggage);
  }

  EXPECT_FALSE(bool(tracing::Tracer::ActiveContext()));
}

class TestReporter : public tracing::Reporter {
 public:
  explicit TestReporter(std::deque<std::string>& reported_span_ids)
      : reported_span_ids_(reported_span_ids) {}

  void Report(const tracing::Span& span) const override {
    reported_span_ids_.push_back(span.GetSpanId());
  }
  void ConfigureReporting(tracing::Span& /*span*/,
                          double /*sampling*/) const override {
    return;
  }

  bool ShouldReportAsyncTask(const tracing::SpanContextCPtr&) const override {
    return false;
  }

 private:
  std::deque<std::string>& reported_span_ids_;
};

TEST(TestTracer, ReportSetReporter) {
  auto tracer = tracing::Tracer::GetTracer();
  ASSERT_TRUE(bool(tracer));

  std::deque<std::string> actual_span_ids;
  std::deque<std::string> reported_span_ids;
  auto reporter =
      std::shared_ptr<tracing::Reporter>(new TestReporter(reported_span_ids));

  tracer->SetReporter(reporter);

  auto span1 = tracer->StartSpan("span1");
  actual_span_ids.push_back(span1->GetSpanId());

  {
    auto span2 = tracer->StartSpan("span2");
    actual_span_ids.push_front(span2->GetSpanId());
  }

  tracer->Report(*span1);

  EXPECT_EQ(actual_span_ids[0], reported_span_ids[0]);
  EXPECT_EQ(actual_span_ids[1], reported_span_ids[1]);
  EXPECT_FALSE(bool(tracing::Tracer::ActiveContext()));

  // we must do this to avoid dangling reference to reported_span_ids
  // in TestReporter
  reporter.reset();
}

TEST(TestTracer, InjectExtract) {
  auto tracer = tracing::Tracer::GetTracer();
  ASSERT_TRUE(bool(tracer));

  auto span1 = tracer->StartSpan("span1");

  span1->AddBaggage("test_key", "test_value");
  span1->AddBaggage("test_key2", "test_value2");
  span1->AddLocalBaggage("local_test_key", "local_test_value");

  LogExtra log_extra;

  tracing::Tracer::Inject(*span1, log_extra);

  auto context = tracing::Tracer::Extract(log_extra);

  ASSERT_TRUE(bool(context));

  EXPECT_EQ(span1->GetSpanId(), context->span_id);
  EXPECT_EQ(span1->GetTraceId(), context->trace_id);
  EXPECT_EQ(span1->GetBaggage(), context->baggage);
  EXPECT_TRUE(context->local_baggage.empty());
}

constexpr const char* mock_config_json = R"===(
{
  "TRACING_SAMPLING_PROBABILITY": {
    "diagnostics_default": 0.28,
    "jaeger_default": 0.2,
    "default": {
      "es": 0.15,
      "yt_additional_db": {
       "base": 0.3,
       "span_category": {
         "mongo": 0.1,
         "postgres": 0.05,
         "otherdb": 0.15
       }
      }
    },
    "experiments": {
     "es": 0.1,
     "diagnostics": 0.12,
     "jaeger": 0.01,
     "yt_additional_db": {
       "base": 0.2,
       "span_category": {
         "mongo": 0.3,
         "postgres": 0.0
       }
     }
    },
    "nonexistent1": 0.1,
    "nonexistent2": {
     "es": 0.2
    },
    "nonexistent3": {
     "yt_additional_db": {
       "span_category": {
         "mongo": 0.1,
         "postgres": 0.05,
         "default": 0.01
       }
     }
    }
  },
  "TRACING_CPP_LOG_REPORTER_ENABLED": true,
  "JAEGER_BACKEND_CPP_REPORTING_ENABLED": true
}
)===";

constexpr const char* mock_config_no_diagnostics_json = R"===(
{
  "TRACING_SAMPLING_PROBABILITY": {
    "default": {
      "es": 0.15,
      "yt_additional_db": {
       "base": 0.3,
       "span_category": {
         "mongo": 0.1,
         "postgres": 0.05,
         "otherdb": 0.15
       }
      }
    },
    "experiments": {
     "es": 0.1,
     "yt_additional_db": {
       "base": 0.2,
       "span_category": {
         "mongo": 0.3,
         "postgres": 0.0
       }
     }
    }
  },
  "TRACING_CPP_LOG_REPORTER_ENABLED": true,
  "JAEGER_BACKEND_CPP_REPORTING_ENABLED": true
}
)===";

TEST(TestTracerConfig, TracingSamplingProbabilityConfig) {
  auto docs_map = config::DocsMap();
  docs_map.Parse(mock_config_json);
  auto tracing_config = config::TracingConfig(docs_map);

  const auto Es = config::TracingConfig::Es;
  const auto Yt = config::TracingConfig::YtAdditional;
  const auto Diagnostics = config::TracingConfig::Diagnostics;
  const auto Jaeger = config::TracingConfig::Jaeger;

  EXPECT_DOUBLE_EQ(0.0, tracing_config.GetSamplingProbability(Es, ""));
  EXPECT_DOUBLE_EQ(0.0, tracing_config.GetSamplingProbability(Yt, "mongo"));

  config::TracingConfig::SetServiceName("experiments");
  tracing_config = config::TracingConfig(docs_map);

  EXPECT_DOUBLE_EQ(0.1, tracing_config.GetSamplingProbability(Es, ""));
  EXPECT_DOUBLE_EQ(0.2 * 0.3,
                   tracing_config.GetSamplingProbability(Yt, "mongo"));
  EXPECT_DOUBLE_EQ(0.0 * 0.05,
                   tracing_config.GetSamplingProbability(Yt, "postgres"));
  EXPECT_DOUBLE_EQ(0.3 * 0.15,
                   tracing_config.GetSamplingProbability(Yt, "otherdb"));
  EXPECT_DOUBLE_EQ(0.12,
                   tracing_config.GetSamplingProbability(Diagnostics, ""));

  EXPECT_DOUBLE_EQ(0.01, tracing_config.GetSamplingProbability(Jaeger, ""));

  config::TracingConfig::SetServiceName("nonexistent1");
  tracing_config = config::TracingConfig(docs_map);

  EXPECT_DOUBLE_EQ(0.1, tracing_config.GetSamplingProbability(Es, ""));
  EXPECT_DOUBLE_EQ(0.3 * 0.1,
                   tracing_config.GetSamplingProbability(Yt, "mongo"));
  EXPECT_DOUBLE_EQ(0.3 * 0.05,
                   tracing_config.GetSamplingProbability(Yt, "postgres"));
  EXPECT_DOUBLE_EQ(0.3 * 0.15,
                   tracing_config.GetSamplingProbability(Yt, "otherdb"));

  config::TracingConfig::SetServiceName("nonexistent2");
  tracing_config = config::TracingConfig(docs_map);

  EXPECT_DOUBLE_EQ(0.2, tracing_config.GetSamplingProbability(Es, ""));
  EXPECT_DOUBLE_EQ(0.3 * 0.1,
                   tracing_config.GetSamplingProbability(Yt, "mongo"));
  EXPECT_DOUBLE_EQ(0.2, tracing_config.GetSamplingProbability(Jaeger, ""));

  config::TracingConfig::SetServiceName("nonexistent3");
  tracing_config = config::TracingConfig(docs_map);

  EXPECT_DOUBLE_EQ(0.15, tracing_config.GetSamplingProbability(Es, ""));
  EXPECT_DOUBLE_EQ(0.1, tracing_config.GetSamplingProbability(Yt, "mongo"));
  EXPECT_DOUBLE_EQ(0.05, tracing_config.GetSamplingProbability(Yt, "postgres"));
  EXPECT_DOUBLE_EQ(0.01, tracing_config.GetSamplingProbability(Yt, "otherdb"));

  EXPECT_DOUBLE_EQ(0.28,
                   tracing_config.GetSamplingProbability(Diagnostics, ""));

  docs_map.Parse(mock_config_no_diagnostics_json);
  tracing_config = config::TracingConfig(docs_map);
  EXPECT_DOUBLE_EQ(0.0, tracing_config.GetSamplingProbability(Diagnostics, ""));
  EXPECT_DOUBLE_EQ(0.0, tracing_config.GetSamplingProbability(Jaeger, ""));
}

class TestLogReporter : public tracing::LogReporter {
 public:
  TestLogReporter() : tracing::LogReporter(nullptr){};
  LogExtra GetOpentracingLogExtra(const tracing::Span& span) const {
    return tracing::LogReporter::MakeJaegerLogExtra(span);
  }
};

TEST(TestOpentracingReporting, LogExtraData) {
  auto tracer = tracing::Tracer::GetTracer();
  auto reporter = TestLogReporter{};
  utils::datetime::MockNowSet(
      utils::datetime::Stringtime("2020-04-6T18:00:00+0300"));
  auto span = tracer->StartSpan("test_operation");
  span->SetTag("unknown_tag", "doesn't matter");
  span->SetTag(tracing::tags::error, false);
  span->SetTag(tracing::tags::http_status_code, 200);
  span->SetTag(tracing::tags::http_method, std::string("POST"));
  utils::datetime::MockSleep(std::chrono::milliseconds(11));
  span->Finish();
  auto log_extra = reporter.GetOpentracingLogExtra(*span);
  EXPECT_EQ("test_operation", log_extra.Get<std::string>("operation_name"));
  auto serialized_tags = log_extra.Get<std::string>("tags");
  auto json_tags = utils::helpers::ParseJson(serialized_tags);
  EXPECT_EQ(json_tags.size(), 3u);
  for (const auto& json_tag : json_tags) {
    auto key = json_tag["key"].asString();
    if (key == tracing::tags::error) {
      EXPECT_EQ("false", json_tag["value"].asString());
      EXPECT_EQ("bool", json_tag["type"].asString());
    } else if (key == tracing::tags::http_status_code) {
      EXPECT_EQ("200", json_tag["value"].asString());
      EXPECT_EQ("int64", json_tag["type"].asString());
    } else if (key == tracing::tags::http_method) {
      EXPECT_EQ("POST", json_tag["value"].asString());
      EXPECT_EQ("string", json_tag["type"].asString());
    } else {
      FAIL() << "Got unknown key in tags: " << key;
    }
  }
  EXPECT_EQ(11000l, log_extra.Get<long>("duration"));
}

class OpentracingReporter : public tracing::Reporter {
 public:
  void Report(const tracing::Span&) const override {}
  void ConfigureReporting(tracing::Span& span, double) const override {
    span.SetReportOpentracing(report);
  }

  bool ShouldReportAsyncTask(const tracing::SpanContextCPtr&) const override {
    return false;
  }

  bool report{false};
};

TEST(TestOpentracingReporting, ReportingFlagFalse) {
  auto tracer = tracing::Tracer::GetTracer();
  auto reporter = std::make_shared<OpentracingReporter>();
  tracer->SetReporter(reporter);
  auto span1 = tracer->StartSpan("test1");
  EXPECT_FALSE(span1->ReportOpentracing());
  reporter->report = true;
  auto span2 = tracer->StartSpan("test2");
  EXPECT_FALSE(span2->ReportOpentracing());
}

TEST(TestOpentracingReporting, ReportingFlagTrue) {
  auto tracer = tracing::Tracer::GetTracer();
  auto reporter = std::make_shared<OpentracingReporter>();
  reporter->report = true;
  tracer->SetReporter(reporter);
  auto span1 = tracer->StartSpan("test1");
  EXPECT_TRUE(span1->ReportOpentracing());
  reporter->report = false;
  auto span2 = tracer->StartSpan("test2");
  EXPECT_TRUE(span2->ReportOpentracing());
}
