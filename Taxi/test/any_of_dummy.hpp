#pragma once

#include <filters/infrastructure/any_of/any_of.hpp>

namespace candidates::filters::test {

class AnyOfDummyFactory : public infrastructure::AnyOfFactory {
 public:
  AnyOfDummyFactory();
};

}  // namespace candidates::filters::test
