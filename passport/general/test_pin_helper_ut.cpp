#include <passport/infra/daemons/blackbox/ut/common/common.h>

#include <passport/infra/daemons/blackbox/src/grants/grants_checker.h>
#include <passport/infra/daemons/blackbox/src/helpers/test_pin_helper.h>

#include <passport/infra/libs/cpp/request/test/request.h>

#include <library/cpp/testing/unittest/registar.h>

using namespace NPassport;
using namespace NPassport::NBb;

Y_UNIT_TEST_SUITE(PasspUtTestPinHelper) {
    static TTestDbHolder& Db() {
        return TTestDbHolder::GetSingleton();
    }

    Y_UNIT_TEST(testPinHelper) {
        NTest::TRequest req;

        std::unique_ptr<TTestDbFetcher> fetcher = Db().CreateFetcher();
        auto& attrs = const_cast<TDbProfile::TAttrs&>(fetcher->DefaultProfile().Attrs());

        // no pintotest arg
        TTestPinHelper h1(*fetcher, req);

        UNIT_ASSERT(attrs.empty());
        UNIT_ASSERT(!h1.Result(nullptr));
        UNIT_ASSERT(!h1.Result(&fetcher->DefaultProfile()));

        req.Args["pintotest"] = "";

        TTestPinHelper h2(*fetcher, req);
        UNIT_ASSERT_VALUES_EQUAL(attrs, TDbProfile::TAttrs({{TAttr::ACCOUNT_2FA_PIN, TDbValue()}, {TAttr::ACCOUNT_TOTP_SECRET, TDbValue()}}));

        UNIT_ASSERT(!h2.Result(nullptr));
        UNIT_ASSERT(h2.Result(&fetcher->DefaultProfile()));
        UNIT_ASSERT(!*h2.Result(&fetcher->DefaultProfile()));

        attrs[TAttr::ACCOUNT_2FA_PIN] = TDbValue("1234");

        UNIT_ASSERT(!h2.Result(nullptr));
        UNIT_ASSERT(h2.Result(&fetcher->DefaultProfile()));
        UNIT_ASSERT(!*h2.Result(&fetcher->DefaultProfile()));

        req.Args["pintotest"] = "1234";
        TTestPinHelper h3(*fetcher, req);

        UNIT_ASSERT(!h3.Result(nullptr));
        UNIT_ASSERT(h3.Result(&fetcher->DefaultProfile()));
        UNIT_ASSERT(*h3.Result(&fetcher->DefaultProfile()));
    }

    Y_UNIT_TEST(checkGrants) {
        NTest::TRequest req;
        TConsumer c;
        TGrantsChecker checker(req, c, false);

        auto check = [&](const std::set<TString>& expected) {
            TTestPinHelper::CheckGrants(checker);
            UNIT_ASSERT_VALUES_EQUAL(checker.GetResult().Errors, expected);
            const_cast<decltype(checker.GetResult().Errors)*>(&checker.GetResult().Errors)->clear();
        };

        check({});

        req.Args["pintotest"] = "";
        check({
            "no grants to test pin",
        });

        c.SetAllowPinTest(true);
        check({});
    }
}
