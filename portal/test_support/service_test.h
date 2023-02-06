#pragma once

#include "test_with_core.h"

#include <memory>

namespace NMordaBlocks {
    class TCore;
    class TSession;

    // The base class for testing services.
    // The core will be available, but not started.
    class TServiceTest : public TTestWithCoreBase {
    public:
        TServiceTest();

        ~TServiceTest() override;

        // Create services which is used by testing service.
        virtual void CreateServices();

        void SetUp() override;

        void TearDown() override;
    private:
        std::unique_ptr<TSession> Session_;
    };

} // namespace NMordaBlocks
