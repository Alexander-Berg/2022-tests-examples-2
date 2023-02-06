#pragma once

#include <clients/order-core/client.hpp>
#include <helpers/complements/complements.hpp>

namespace plus {

class MockComplements : public ComplementsStorage {
 public:
  explicit MockComplements(Complements complements)
      : complements_(std::move(complements)){};
  virtual ~MockComplements() = default;

  Complements GetOrderComplements(const ComplementsOrder&) override {
    return complements_;
  };

 private:
  Complements complements_;
};

ComplementsAccessor MockComplementsAccessor(Complements&);

}  // namespace plus
