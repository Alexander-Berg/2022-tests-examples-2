#include <boost/filesystem.hpp>
#include <fstream>
#include <set>

namespace utils {

boost::filesystem::path MakeRandomDumpDirectory() {
  auto result =
      boost::filesystem::temp_directory_path() /
      boost::filesystem::path{"yandex"} /
      boost::filesystem::path{"cache-dump-test"} /
      boost::filesystem::unique_path("%%%%%%%%-%%%%%%%%-%%%%%%%%-%%%%%%%%");
  assert(!boost::filesystem::exists(result));
  return result;
}

void ClearDirectory(const boost::filesystem::path& dir) {
  boost::filesystem::remove_all(dir);
}

void CreateFile(const boost::filesystem::path& path) {
  std::ofstream ofs(path.native());
}

std::set<std::string> ListDirectory(const boost::filesystem::path& dir) {
  namespace bfs = boost::filesystem;

  std::set<std::string> result;

  const bfs::directory_iterator end_itr;
  for (bfs::directory_iterator i(dir); i != end_itr; ++i) {
    result.insert(i->path().native());
  }

  return result;
}

}  // namespace utils
