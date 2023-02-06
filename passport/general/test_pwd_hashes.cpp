#include "test_pwd_hashes.h"

#include <passport/infra/daemons/blackbox/src/blackbox_impl.h>
#include <passport/infra/daemons/blackbox/src/grants/consumer.h>
#include <passport/infra/daemons/blackbox/src/grants/grants_checker.h>
#include <passport/infra/daemons/blackbox/src/misc/exception.h>
#include <passport/infra/daemons/blackbox/src/misc/password_checker.h>
#include <passport/infra/daemons/blackbox/src/misc/strings.h>
#include <passport/infra/daemons/blackbox/src/misc/utils.h>
#include <passport/infra/daemons/blackbox/src/output/test_pwd_hashes_result.h>

#include <passport/infra/libs/cpp/utils/string/split.h>

namespace NPassport::NBb {
    TTestPwdHashesProcessor::TTestPwdHashesProcessor(const TBlackboxImpl& impl, const NCommon::TRequest& request)
        : Blackbox_(impl)
        , Request_(request)
    {
    }

    TGrantsChecker TTestPwdHashesProcessor::CheckGrants(const TConsumer& consumer, bool throwOnError) {
        TGrantsChecker checker(Request_, consumer, throwOnError);

        checker.CheckMethodAllowed(TBlackboxMethods::TestPwdHashes);

        return checker;
    }

    std::unique_ptr<TTestPwdHashesResult> TTestPwdHashesProcessor::Process(const TConsumer& consumer) {
        CheckGrants(consumer);

        const TString& password = TUtils::GetCheckedArg(Request_, TStrings::PASSWORD);
        const TString& rawHashes = TUtils::GetCheckedArg(Request_, TStrings::HASHES);
        const TString& uid = TUtils::GetUIntArg(Request_, TStrings::UID);

        std::vector<TString> hashes = NUtils::ToVector(rawHashes, ',');

        TTestPwdHashesResult::TDataMap result;
        for (TString& h : hashes) {
            if (result.find(h) != result.end()) {
                continue;
            }

            TTestPwdHashesResult::TDataPair pair;
            // find matching password, allowing all type of hashes
            pair.second = Blackbox_.PasswordChecker().PasswordMatches(
                password, NUtils::Base64ToBin(h), uid, true);
            pair.first = std::move(h);
            result.insert(std::move(pair));
        }

        std::unique_ptr<TTestPwdHashesResult> res = std::make_unique<TTestPwdHashesResult>();
        res->Data = std::move(result);

        return res;
    }
}
