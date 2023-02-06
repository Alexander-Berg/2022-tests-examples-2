#include "mock_complements_test.hpp"

namespace plus {

ComplementsAccessor MockComplementsAccessor(Complements& complements) {
  return std::make_shared<MockComplements>(complements);
};

}  // namespace plus
