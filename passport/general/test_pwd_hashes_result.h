#pragma once

#include <util/generic/noncopyable.h>
#include <util/generic/string.h>

#include <map>

namespace NPassport::NBb {
    class TTestPwdHashesResult: TMoveOnly {
    public:
        using TDataMap = std::map<TString, bool>;
        using TDataPair = std::pair<TString, bool>;

        TDataMap Data;
    };
}
