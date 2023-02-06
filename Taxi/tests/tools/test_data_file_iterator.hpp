#pragma once

#include <string>
#include <vector>

#include "testutils.hpp"

namespace hejmdal::testutils {

class TestDataFileIterator {
 public:
  explicit TestDataFileIterator(const std::string& dir);

  bool HasNext() const;
  [[nodiscard]] const TestCircuitData& Next();
  [[nodiscard]] const std::string& GetCurrentFileName() const;

 private:
  std::vector<std::string> files_;
  std::size_t current_file_;
  TestCircuitData current_data_;
};

}  // namespace hejmdal::testutils
