#include "service_test.h"

#include <portal/morda/blocks/core/core.h>
#include <portal/morda/blocks/core/session/session.h>

#include <utility>

namespace NMordaBlocks {
    TServiceTest::TServiceTest() = default;

    TServiceTest::~TServiceTest() = default;

    void TServiceTest::CreateServices() {
    }

    void TServiceTest::SetUp() {
        TTestWithCoreBase::SetUp();
        CreateServices();
        Session_ = std::make_unique<TSession>(true);
    }

    void TServiceTest::TearDown() {
        Session_.reset();
        if (TCore::Get()->IsStarted()) {
            TCore::Get()->Stop();
        }
        TTestWithCoreBase::TearDown();
    }

} // namespace NMordaBlocks
