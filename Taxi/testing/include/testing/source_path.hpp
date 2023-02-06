#pragma once

#include <string>

#include <boost/filesystem.hpp>

#ifdef ARCADIA_ROOT
#include <library/cpp/testing/common/env.h>
#endif

namespace utils {
inline std::string CurrentSourcePath(const std::string& path) {
#ifdef ARCADIA_ROOT
  boost::filesystem::path result(ArcadiaSourceRoot());
  result.append(CURRENT_SOURCE_ROOT);
#else
  boost::filesystem::path result(CURRENT_SOURCE_DIR);
#endif
  result /= path;
  return result.native();
}

inline std::string CurrentWorkPath(const std::string& path) {
#ifdef ARCADIA_ROOT
  boost::filesystem::path result(GetWorkPath());
#else
  boost::filesystem::path result(CURRENT_SOURCE_DIR);
#endif
  result /= path;
  return result.native();
}
}  // namespace utils
