#include "utils.hpp"

namespace cart_delivery_fee::tests {

std::ostream& operator<<(std::ostream& os, const CartFeePair& pair) {
  os << "{subtotal: " << pair.subtotal
     << ", delivery_fee: " << pair.delivery_fee << "}";
  return os;
}

std::ostream& operator<<(std::ostream& os, const CartFeeSurge& pair) {
  os << "{subtotal: " << pair.subtotal
     << ", delivery_fee: " << pair.delivery_fee
     << ", surge_part: " << pair.surge_part << "}";
  return os;
}

}  // namespace cart_delivery_fee::tests
