#pragma once

#include <util/generic/string.h>

#include <memory>

namespace NPassport::NCommon {
    class TRequest;
}
namespace NPassport::NBb {
    class TDbFetcher;
    class TDbProfile;
    class TGrantsChecker;

    class TTestPinHelper {
    public:
        TTestPinHelper(TDbFetcher& fetcher, const NCommon::TRequest& request);

        static void CheckGrants(TGrantsChecker& checker);

        std::unique_ptr<bool> Result(const TDbProfile* profile) const;

    private:
        int PinAttr_ = -1;
        TString PinStr_;
    };

}
