#include "test_madm_items_generator.h"

namespace NMordaBlocks {

    TTestMadmItemsGenerator::TTestMadmItemsGenerator(ui64 seed)
        : Generator_(seed)
    {
    }

    TTestMadmItemsGenerator::TTestMadmItemsGenerator(const NJson::TJsonValue& fields, ui64 seed)
        : Fields_(fields)
        , Generator_(seed)
    {
    }

    NJson::TJsonValue TTestMadmItemsGenerator::GenerateItems(unsigned int cnt) const {
        NJson::TJsonValue result = NJson::JSON_ARRAY;
        for (unsigned int i = 0; i < cnt; ++i) {
            result.AppendValue(GenerateItem());
        }

        return result;
    }

    NJson::TJsonValue TTestMadmItemsGenerator::GenerateItem() const {
        NJson::TJsonValue result = NJson::JSON_MAP;
        for (const auto& item : Fields_.GetMapSafe()) {
            const TString& fieldName = item.first;
            const NJson::TJsonValue::TArray& fieldValues = item.second.GetArraySafe();

            if (fieldValues.empty()) {
                continue;
            }
            result.InsertValue(fieldName,
                    fieldValues[Generator_.Uniform(fieldValues.size())]);
        }

        return result;
    }

}  // NMordaBlocks
