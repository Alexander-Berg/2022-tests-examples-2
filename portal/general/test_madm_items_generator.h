#pragma once

#include <library/cpp/json/writer/json_value.h>

#include <util/random/fast.h>

namespace NMordaBlocks {

    class TTestMadmItemsGenerator {
    public:
        TTestMadmItemsGenerator(ui64 seed);
        explicit TTestMadmItemsGenerator(const NJson::TJsonValue& fields, ui64 seed);
        ~TTestMadmItemsGenerator() = default;

        void SetFields(const NJson::TJsonValue& fields) {
            Fields_ = fields;
        }

        NJson::TJsonValue GenerateItems(unsigned int cnt) const;

    private:
        NJson::TJsonValue GenerateItem() const;

    private:
        NJson::TJsonValue Fields_;
        mutable TFastRng64 Generator_;
    };

}  // NMordaBlocks
