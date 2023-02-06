#include "test_pin_helper.h"

#include <passport/infra/daemons/blackbox/src/grants/grants_checker.h>
#include <passport/infra/daemons/blackbox/src/misc/db_fetcher.h>
#include <passport/infra/daemons/blackbox/src/misc/db_profile.h>
#include <passport/infra/daemons/blackbox/src/misc/db_types.h>
#include <passport/infra/daemons/blackbox/src/misc/exception.h>
#include <passport/infra/daemons/blackbox/src/misc/strings.h>

#include <passport/infra/libs/cpp/request/request.h>

namespace NPassport::NBb {
    TTestPinHelper::TTestPinHelper(TDbFetcher& fetcher, const NCommon::TRequest& request) {
        if (!request.HasArg(TStrings::PINTOTEST)) {
            return;
        }

        PinAttr_ = fetcher.AddAttr(TAttr::ACCOUNT_2FA_PIN);
        PinStr_ = request.GetArg(TStrings::PINTOTEST);
    }

    void TTestPinHelper::CheckGrants(TGrantsChecker& checker) {
        if (checker.GetRequest().HasArg(TStrings::PINTOTEST) && !checker.GetConsumer().IsPinTestAllowed()) {
            checker.Add("no grants to test pin");
        }
    }

    std::unique_ptr<bool>
    TTestPinHelper::Result(const TDbProfile* profile) const {
        if (!profile || PinAttr_ < 0) {
            return std::unique_ptr<bool>();
        }

        const TString& pin = profile->Get(PinAttr_)->Value;
        bool status = !pin.empty() && pin == PinStr_;

        return std::make_unique<bool>(status);
    }

}
