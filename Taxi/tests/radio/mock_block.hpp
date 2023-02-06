#pragma once

#include <radio/blocks/block.hpp>

namespace hejmdal::radio::blocks {

class MockBlock : public Block {
 public:
  MockBlock() : Block("mock_block") {}

  const std::string& GetType() const override { return kType; }

  formats::json::Value Serialize() const override {
    return formats::json::MakeObject();
  }

  const std::string kType = "mock_block_type";
};

class Counter : public MockBlock {
 public:
  void DataIn(const Meta&, const time::TimePoint&, double) override {
    data_count++;
  }
  void StateIn(const Meta&, const time::TimePoint&, const State&) override {
    state_count++;
  }
  void BoundsIn(const Meta&, const time::TimePoint&, double, double) override {
    bounds_count++;
  }

  std::size_t data_count = 0;
  std::size_t state_count = 0;
  std::size_t bounds_count = 0;
};

}  // namespace hejmdal::radio::blocks
