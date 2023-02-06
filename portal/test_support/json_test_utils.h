#pragma once

#include <util/generic/strbuf.h>
#include <util/generic/string.h>

namespace NJson {
    class TJsonValue;
} // namespace NJson

namespace NMordaBlocks {
    namespace NTest {
        NJson::TJsonValue ReadJsonFromString(TStringBuf jsonString);

        bool JsonsEqual(const NJson::TJsonValue& lhs, const NJson::TJsonValue& rhs);
        bool JsonsEqual(TStringBuf jsonRaw, const NJson::TJsonValue& rhs);

        TString ConvertToString(const NJson::TJsonValue& json);

        TString JsonStringDiff(const NJson::TJsonValue& first, const NJson::TJsonValue& second);
        TString JsonStringDiff(TStringBuf jsonRawFirst, const NJson::TJsonValue& second);

        namespace NInternal {
            template <class T>
            inline bool JsonsEqualT(const T& value, const NJson::TJsonValue& rhs) {
                return JsonsEqual(TStringBuf(value), rhs);
            }

            template <>
            inline bool JsonsEqualT<NJson::TJsonValue>(const NJson::TJsonValue& value, const NJson::TJsonValue& rhs) {
                return JsonsEqual(value, rhs);
            }

            template <class T>
            inline TString JsonStringDiffT(const T& value, const NJson::TJsonValue& rhs) {
                return JsonStringDiff(TStringBuf(value), rhs);
            }

            template <>
            inline TString JsonStringDiffT<NJson::TJsonValue>(const NJson::TJsonValue& value, const NJson::TJsonValue& rhs) {
                return JsonStringDiff(value, rhs);
            }

        } // namespace NInternal

    } // namespace NTest

} // namespace NMordaBlocks

#define UNIT_ASSERT_JSONS_EQUAL(expected, actual)                  \
    UNIT_ASSERT_C(NTest::NInternal::JsonsEqualT(expected, actual), \
                  TStringBuilder() << "With Diff: " << NTest::NInternal::JsonStringDiffT(expected, actual));
