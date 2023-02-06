#pragma once

#include <fstream>

#include <boost/filesystem/operations.hpp>
#include <boost/filesystem/path.hpp>

namespace utils {

inline boost::filesystem::path CreateUniqueFile() {
  auto path = boost::filesystem::temp_directory_path() /
              ("." + boost::filesystem::unique_path().string());
  std::ofstream{path.string()}.flush();
  return path;
}

inline boost::filesystem::path CreateUniqueFile(
    const boost::filesystem::path& directory) {
  auto path = directory / ("." + boost::filesystem::unique_path().string());
  std::ofstream{path.string()}.flush();
  return path;
}

}  // namespace utils
