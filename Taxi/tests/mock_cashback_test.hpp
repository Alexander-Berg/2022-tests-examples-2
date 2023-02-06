#pragma once

#include <helpers/cashback/cashback.hpp>

namespace plus {

class CashbackMock : public CashbackStorage {
 public:
  explicit CashbackMock(Cashback cashback) : cashback_(std::move(cashback)){};
  virtual ~CashbackMock() = default;

  Cashback GetOrderCashback(const CashbackOrder&) override { return cashback_; }

 private:
  Cashback cashback_;
};

CashbackAccessor MockCashbackAccessor(Cashback cashback);

}  // namespace plus
