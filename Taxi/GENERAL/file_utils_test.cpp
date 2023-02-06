#include <testing/source_path.hpp>

#include <utest/routing/file_utils.hpp>

namespace clients::routing {
namespace utest {

std::string ReadFile(const std::string& name) {
  return fs::blocking::ReadFileContents(
      utils::CurrentSourcePath("tests/static/" + name));
}

}  // namespace utest
}  // namespace clients::routing
