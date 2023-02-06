#include "fail_policy.hpp"
#include "fallback.hpp"

#include <agl/sourcing/sources-polling-state.hpp>

#include <userver/utest/utest.hpp>

#include <stdexcept>

namespace agl::sourcing::tests {

TEST(TestFailPolicy, TestFilters) {
  {
    FailPolicy::Filter filter(FailPolicy::Filter::Kind::TIMEOUT);
    EXPECT_FALSE(filter.Match(FailPolicy::ErrorKind::STATUS_CODE, 400));
    EXPECT_FALSE(filter.Match(FailPolicy::ErrorKind::STATUS_CODE, 504));
    EXPECT_FALSE(filter.Match(FailPolicy::ErrorKind::STATUS_CODE, 500));
    EXPECT_TRUE(filter.Match(FailPolicy::ErrorKind::TIMEOUT, 0));
    EXPECT_FALSE(filter.Match(FailPolicy::ErrorKind::TECH, 0));
  }  // namespace core=core::api_proxy;

  {
    FailPolicy::Filter filter(FailPolicy::Filter::Kind::TECH);
    EXPECT_FALSE(filter.Match(FailPolicy::ErrorKind::STATUS_CODE, 400));
    EXPECT_FALSE(filter.Match(FailPolicy::ErrorKind::STATUS_CODE, 504));
    EXPECT_FALSE(filter.Match(FailPolicy::ErrorKind::STATUS_CODE, 500));
    EXPECT_FALSE(filter.Match(FailPolicy::ErrorKind::TIMEOUT, 0));
    EXPECT_TRUE(filter.Match(FailPolicy::ErrorKind::TECH, 0));
  }

  {
    FailPolicy::Filter filter(FailPolicy::Filter::Kind::ANY);
    EXPECT_TRUE(filter.Match(FailPolicy::ErrorKind::STATUS_CODE, 400));
    EXPECT_TRUE(filter.Match(FailPolicy::ErrorKind::STATUS_CODE, 504));
    EXPECT_TRUE(filter.Match(FailPolicy::ErrorKind::STATUS_CODE, 500));
    EXPECT_TRUE(filter.Match(FailPolicy::ErrorKind::TIMEOUT, 0));
    EXPECT_TRUE(filter.Match(FailPolicy::ErrorKind::TECH, 0));
  }

  {
    FailPolicy::Filter filter(FailPolicy::Filter::Kind::STATUS_CODE, 504);
    EXPECT_FALSE(filter.Match(FailPolicy::ErrorKind::STATUS_CODE, 400));
    EXPECT_TRUE(filter.Match(FailPolicy::ErrorKind::STATUS_CODE, 504));
    EXPECT_FALSE(filter.Match(FailPolicy::ErrorKind::STATUS_CODE, 500));
    EXPECT_FALSE(filter.Match(FailPolicy::ErrorKind::TIMEOUT, 0));
    EXPECT_FALSE(filter.Match(FailPolicy::ErrorKind::TECH, 0));
  }

  {
    FailPolicy::Filter filter(FailPolicy::Filter::Kind::STATUS_CODE_CLASS, 500);
    EXPECT_FALSE(filter.Match(FailPolicy::ErrorKind::STATUS_CODE, 400));
    EXPECT_TRUE(filter.Match(FailPolicy::ErrorKind::STATUS_CODE, 504));
    EXPECT_TRUE(filter.Match(FailPolicy::ErrorKind::STATUS_CODE, 500));
    EXPECT_FALSE(filter.Match(FailPolicy::ErrorKind::TIMEOUT, 0));
    EXPECT_FALSE(filter.Match(FailPolicy::ErrorKind::TECH, 0));
  }
}

TEST(TestFailPolicy, TestActions) {
  {
    SourcesPollingState sources_polling_state;
    FailPolicy::Filter filter;
    FailPolicy::Action action(FailPolicy::Action::Kind::PROPAGATE);
    auto exception =
        std::make_exception_ptr(std::runtime_error("runtime_error"));
    FallbackStorage fallback_storage;
    EXPECT_THROW(action.Do(0, "test-source", exception, fallback_storage,
                           filter, sources_polling_state),
                 std::runtime_error);
  }

  {
    SourcesPollingState sources_polling_state;
    FailPolicy::Filter filter;
    FailPolicy::Action action(FailPolicy::Action::Kind::IGNORE);
    auto exception =
        std::make_exception_ptr(std::runtime_error("runtime_error"));
    FallbackStorage fallback_storage;
    EXPECT_NO_THROW(action.Do(0, "test-source", exception, fallback_storage,
                              filter, sources_polling_state));
  }

  {
    SourcesPollingState sources_polling_state;
    sources_polling_state.Init(1);

    FallbackStorage fallback_storage;
    fallback_storage.Insert(Fallback("fallback", 200,
                                     agl::core::Variant("test-body"),
                                     agl::core::Variant()));

    FailPolicy::Filter filter;
    FailPolicy::Action action(FailPolicy::Action::Kind::FALLBACK, "fallback");
    auto exception =
        std::make_exception_ptr(std::runtime_error("runtime_error"));
    EXPECT_NO_THROW(action.Do(0, "test-source", exception, fallback_storage,
                              filter, sources_polling_state));
    EXPECT_FALSE(sources_polling_state.ResponseDataOf(0));
    EXPECT_TRUE(sources_polling_state.FallbackDataOf(0));
    EXPECT_EQ(sources_polling_state.FallbackDataOf(0)->Name(),
              fallback_storage.GetFallback("fallback").Name());
  }

  {
    FallbackStorage fallback_storage;
    SourcesPollingState sources_polling_state;
    FailPolicy::Filter filter;
    FailPolicy::Action action(FailPolicy::Action::Kind::RETURN,
                              "test-response");
    auto exception =
        std::make_exception_ptr(std::runtime_error("runtime_error"));
    EXPECT_THROW(action.Do(0, "test-source", exception, fallback_storage,
                           filter, sources_polling_state),
                 FailPolicy::Return);
    try {
      action.Do(0, "test-source", exception, fallback_storage, filter,
                sources_polling_state);
    } catch (const FailPolicy::Return& e) {
      EXPECT_EQ(e.Response(), "test-response");
    }
  }
}

}  // namespace agl::sourcing::tests
