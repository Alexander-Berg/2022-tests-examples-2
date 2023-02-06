#pragma once

#include <core/context/time_formatter.hpp>

namespace routestats::test {

class EtaFormatterMock : public core::TimeFormatter {
 public:
  std::string GetFormattedValue(std::chrono::seconds value,
                                const core::TimeFormattingOptions&) override {
    return std::to_string(value.count()) + " sec";
  }
};

}  // namespace routestats::test
