#pragma once

#include <helpers/invoice/invoice.hpp>
#include <taxi_config/taxi_config.hpp>

namespace debts::invoice {

class MockInvoice : public InvoiceStorage {
 public:
  explicit MockInvoice(const std::optional<Invoice>& invoice)
      : invoice_(invoice){};
  std::optional<Invoice> GetInvoice(const std::string&,
                                    const taxi_config::TaxiConfig&) override {
    return invoice_;
  };

 private:
  const std::optional<Invoice> invoice_;
};

InvoiceAccessor MockInvoiceAccessor(const std::optional<Invoice>& invoice);

}  // namespace debts::invoice
