#include "mock_cashback_test.hpp"

namespace plus {

CashbackAccessor MockCashbackAccessor(Cashback cashback) {
  return std::make_shared<CashbackMock>(cashback);
}

}  // namespace plus
