#include "any_of_dummy.hpp"

#include <candidates/filters/test/any_of_dummy_info.hpp>

namespace candidates::filters::test {

AnyOfDummyFactory::AnyOfDummyFactory()
    : AnyOfFactory(info::kAnyOfDummy, {
                                          "test/disallow_all",
                                          "test/ignore_all",
                                          "test/sleep",
                                          "test/allow_all",
                                      }) {}

}  // namespace candidates::filters::test
