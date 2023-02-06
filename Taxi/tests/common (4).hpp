#pragma once

// for testing std::optional/null
#include <userver/formats/parse/common_containers.hpp>
#include <userver/formats/serialize/common_containers.hpp>
#include <userver/utest/utest.hpp>

#include <formats/js/exception.hpp>
#include <formats/js/serialize.hpp>
#include <formats/js/value.hpp>
#include <formats/js/value_builder.hpp>

#include <tests/js_helper.hpp>

// clang-format off
#define ASSERT_THROW_MSG(expr, type, msg)            \
  ASSERT_THROW(try { expr; } catch (const type& e) { \
    ASSERT_STREQ(e.what(), msg);                     \
    throw;                                           \
  },                                                 \
               type)

#define EXPECT_THROW_MSG(expr, type, msg)            \
  EXPECT_THROW(try { expr; } catch (const type& e) { \
    EXPECT_STREQ(e.what(), msg);                     \
    throw;                                           \
  },                                                 \
               type)

#define ASSERT_THROW_MSG_CONTAINS(expr, type, msg)                             \
  ASSERT_THROW(try { expr; } catch (const type& e) {                           \
    auto* what = e.what();                                                     \
    if (!strstr(what, msg)) {                                                  \
      FAIL() << fmt::format("Exception message \"{}\" doesn't contain \"{}\"", \
                            what, msg);                                        \
    }                                                                          \
    throw;                                                                     \
  },                                                                           \
               type)

#define EXPECT_THROW_MSG_CONTAINS(expr, type, msg)                       \
  EXPECT_THROW(try { expr; } catch (const type& e) {                     \
    auto* what = e.what();                                               \
    if (!strstr(what, msg)) {                                            \
      ADD_FAILURE() << fmt::format(                                      \
          "Exception message \"{}\" doesn't contain \"{}\"", what, msg); \
    }                                                                    \
    throw;                                                               \
  },                                                                     \
               type)
// clang-format on

using namespace std::chrono_literals;

constexpr const auto kShortTimeout = 1000ms;
/// wait in total for 50 ms for async functions and JS to complete
constexpr const auto kTotal50MsTimeout =
    js::execution::channel::TimeoutControl{{}, /*total_timeout=*/50ms};
constexpr const auto kMaxSeconds = std::chrono::seconds::max();

struct Fixture : public ::testing::Test, public ::js::testing::Helper {};

template <typename T>
void CheckIsSleeping(js::execution::channel::Out<T>& ch) {
  if (ch.Wait(kTotal50MsTimeout) != engine::CvStatus::kTimeout) {
    FAIL() << "bad status; value: " << ch.Get({});
  }
}
