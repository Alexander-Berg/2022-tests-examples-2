#pragma once

#include <passport/infra/libs/cpp/request/request.h>

#include <memory>

namespace NPassport::NBb {
    class TBlackboxImpl;
    class TConsumer;
    class TTestPwdHashesResult;
    class TGrantsChecker;

    class TTestPwdHashesProcessor {
    public:
        TTestPwdHashesProcessor(const TBlackboxImpl& impl, const NCommon::TRequest& request);

        TGrantsChecker CheckGrants(const TConsumer& consumer, bool throwOnError = true);
        std::unique_ptr<TTestPwdHashesResult> Process(const TConsumer& consumer);

    private:
        const TBlackboxImpl& Blackbox_;
        const NCommon::TRequest& Request_;
    };
}
