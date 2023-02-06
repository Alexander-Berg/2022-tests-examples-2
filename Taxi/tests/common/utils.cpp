#include "utils.hpp"

#include <boost/filesystem.hpp>
#include <fstream>
#include <sstream>

#ifdef ARCADIA_ROOT
#include <library/cpp/testing/common/env.h>
#endif

namespace tests {
namespace common {

std::string GetTestResourcePath(const std::string& relative_path) {
#ifdef ARCADIA_ROOT
  const std::string kTestDataDir =
      (boost::filesystem::path(ArcadiaSourceRoot()) /
       "taxi/ml/taxi_ml_cxx/lib/tests/static" / relative_path)
          .native();
#else
  const std::string kTestDataDir =
      (boost::filesystem::path{__FILE__}.parent_path().parent_path() /
       "static" / relative_path)
          .native();
#endif
  return kTestDataDir;
}

}  // namespace common
}  // namespace tests
