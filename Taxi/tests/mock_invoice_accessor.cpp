#include "mock_invoice_accessor.hpp"

namespace debts::invoice {

InvoiceAccessor MockInvoiceAccessor(const std::optional<Invoice>& invoice) {
  return std::make_shared<MockInvoice>(invoice);
}

}  // namespace debts::invoice
