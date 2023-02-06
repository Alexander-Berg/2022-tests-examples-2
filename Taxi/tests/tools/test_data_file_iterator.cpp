#include "test_data_file_iterator.hpp"

#include <boost/filesystem.hpp>

#include "test_data_file_reader.hpp"

#include <models/time_series.hpp>

namespace hejmdal::testutils {

TestDataFileIterator::TestDataFileIterator(const std::string& dir)
    : files_(), current_file_(0), current_data_() {
  if (dir.empty()) {
    return;
  }
  boost::filesystem::directory_iterator end_itr;
  for (boost::filesystem::directory_iterator itr(dir); itr != end_itr; ++itr) {
    if (is_regular_file(itr->path())) {
      files_.push_back(itr->path().string());
    }
  }
}

bool TestDataFileIterator::HasNext() const {
  return current_file_ < files_.size();
}

const TestCircuitData& TestDataFileIterator::Next() {
  auto reader = testutils::TestDataFileReader(files_[current_file_++]);
  current_data_ = reader.GetTestCircuitData();
  return current_data_;
}

const std::string& TestDataFileIterator::GetCurrentFileName() const {
  return files_[current_file_ - 1];
}

}  // namespace hejmdal::testutils
