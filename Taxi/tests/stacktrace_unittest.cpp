#include <gtest/gtest.h>

#include <boost/stacktrace.hpp>

TEST(stacktrace, basic) {
  boost::stacktrace::stacktrace trace;
  ASSERT_TRUE(trace) << "Trace is empty";
}

TEST(stacktrace, has_main) {
  boost::stacktrace::stacktrace trace;
  std::stringstream ss;
  ss << trace;
  ASSERT_NE(ss.str().find("main"), std::string::npos)
      << "Trace does not have main(): " << trace;
}
