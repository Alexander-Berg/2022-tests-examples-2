#include "test_url_generator.h"

#include <portal/morda/blocks/services/url_generator/base_url_generator.h>
#include <portal/morda/blocks/types/scale_factor.h>
#include <portal/morda/blocks/utils/url_utils.h>

#include <util/generic/map.h>

namespace NMordaBlocks {

    namespace {
        constexpr auto APPSEARCH_HEADER = "appsearch_header=1";
    } // namespace

    TTestUrlGenerator::TTestUrlGenerator() {
        SetForTests(this);
    }

    TTestUrlGenerator::~TTestUrlGenerator() {
        SetForTests(nullptr);
    }

    TString TTestUrlGenerator::MakeIconUrl(std::initializer_list<TStringBuf> pathFragments) const {
        return NMordaBlocks::MakeIconUrl(pathFragments, EScaleFactor::Scale100);
    }

    TString TTestUrlGenerator::MakeIntent(const TString& baseUrl,
                                          const TIntentParams& intentParams) const {
        Y_UNUSED(intentParams);
        return TString() + "<Intent>" + baseUrl;
    }

    TString TTestUrlGenerator::AppendAppSearchHeader(const TString& url) const {
        if (url.find(APPSEARCH_HEADER) == TString::npos)
            return NUtils::UrlParamGlue(url, APPSEARCH_HEADER);

        return url;
    }

    TString TTestUrlGenerator::MakeBrowserDeeplink(const TString& baseUrl, bool noRedir,
                                                   bool needAppSearchHeader) const {
        const TString url = needAppSearchHeader ? AppendAppSearchHeader(baseUrl) : baseUrl;
        return TString("browser://?noredir=") + (noRedir ? "1" : "0") + "&url=" + NUtils::PercentEncode(url);
    }

    TString TTestUrlGenerator::MakeYellowSkinUrl(const TString& url, const TString& blockId) const {
        Y_UNUSED(blockId);
        return TString("yellowskin://?url=") + NUtils::PercentEncode(url);
    }

    TString TTestUrlGenerator::MakeViewPortUrl(const TString& strUrl) const {
        return "viewport://?" + strUrl;
    }

    TString TTestUrlGenerator::MakeViewPortUrlFromQuery(const TMap<TString, TString>& query) const {
        TString result = "viewport://?";
        for (const auto& it : query) {
            result += it.first + "=" + NUtils::PercentEncode(it.second);
            result += "&";
        }
        if (result.back() == '&') {
            result.pop_back();
        }

        return result;
    }

    bool TTestUrlGenerator::IsReady() const {
        return true;
    }

    void TTestUrlGenerator::Start() {
    }

    void TTestUrlGenerator::BeforeShutDown() {
    }

    void TTestUrlGenerator::ShutDown() {
    }

    TString TTestUrlGenerator::GetServiceName() const {
        return "TestUrlGenerator";
    }

} // namespace NMordaBlocks
