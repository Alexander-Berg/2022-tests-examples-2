#include <boost/filesystem.hpp>
#include <set>

namespace utils {

boost::filesystem::path MakeRandomDumpDirectory();

void ClearDirectory(const boost::filesystem::path& dir);

void CreateFile(const boost::filesystem::path& path);

std::set<std::string> ListDirectory(const boost::filesystem::path& dir);

}  // namespace utils
