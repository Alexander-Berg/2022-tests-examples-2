#include <algorithm>

#include <boost/algorithm/string/predicate.hpp>
#include <boost/filesystem.hpp>

#if defined(__APPLE__)
#include "open_files_count_on_mac.hpp"
#endif

#include <userver/logging/log.hpp>

namespace testing {

// jemalloc opens /proc/sys/vm/overcommit_memory, other libraries may also
// open some files randomly. To avoid problems in tests and make them reliable
// we have a function that counts open file descriptors only for files that
// start with prefix.
inline size_t OpenFilesCountWithPrefix(const boost::filesystem::path& fs_pref) {
  boost::system::error_code err;
  LOG_DEBUG() << "fs_prefix: " << fs_pref;
  auto prefix = boost::filesystem::read_symlink(fs_pref, err);
  if (err) {
    prefix = fs_pref;
  }
  LOG_DEBUG() << "prefix: " << prefix;

#if defined(__APPLE__)
  return OpenFilesCountWithPrefixOnMac(prefix.string());
#else
  size_t result{0};

  boost::filesystem::path p = "/proc/";
  const auto pid = getpid();
  p /= std::to_string(pid);
  p /= "fd";

  boost::filesystem::directory_iterator it{p}, end;
  for (; it != end; ++it) {
    LOG_DEBUG() << "Found path: " << it->path();

    const auto path = boost::filesystem::read_symlink(it->path(), err);
    LOG_DEBUG() << "path after read_symlink: " << path;
    if (!err && boost::algorithm::starts_with(path.string(), prefix.string())) {
      ++result;
    }
  }

  return result;
#endif
}

}  // namespace testing
