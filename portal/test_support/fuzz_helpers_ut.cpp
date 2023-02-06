#include "fuzz_helpers.h"

#include <portal/morda/blocks/types/context_types.h>
#include <portal/morda/blocks/types/regions.h>

#include <library/cpp/json/writer/json_value.h>
#include <library/cpp/testing/unittest/gtest.h>
#include <library/cpp/testing/unittest/registar.h>

#include <util/stream/mem.h>

namespace NMordaBlocks {

    using namespace NTest;

    namespace {

        TString CreateInput(char symb, int size) {
            TString result;
            for (int i = 0; i < size; ++i) {
                result.append(symb);
            }

            return result;
        }

    }  // namespace

    class TFuzzHelpersTest : public ::testing::Test {
    public:
        TFuzzHelpersTest() = default;
        virtual ~TFuzzHelpersTest() = default;
    };

    TEST_F(TFuzzHelpersTest, GetRandStringTest) {
        TString value1;
        {
            TString str = CreateInput('\x00', 1000);
            TMemoryInput input{str};
            EXPECT_TRUE(GetRandString(input, &value1));
        }
        TString value2;
        {
            TString str = CreateInput('\xff', 1000);
            TMemoryInput input{str};
            EXPECT_TRUE(GetRandString(input, &value1));
        }
        EXPECT_NE(value1, value2);
    }

    TEST_F(TFuzzHelpersTest, GetRandBoolTest) {
        bool value1 = 0;
        {
            TString str = CreateInput('\x00', 1000);
            TMemoryInput input{str};
            EXPECT_TRUE(GetRandBool(input, &value1));
        }
        bool value2 = 0;
        {
            TString str = CreateInput('\xff', 1000);
            TMemoryInput input{str};
            EXPECT_TRUE(GetRandBool(input, &value1));
        }
        EXPECT_NE(value1, value2);
    }

    TEST_F(TFuzzHelpersTest, GetRandIntegerTest) {
        int value1 = 0;
        {
            TString str = CreateInput('\x00', 1000);
            TMemoryInput input{str};
            EXPECT_TRUE(GetRandInteger(input, &value1));
        }
        int value2 = 0;
        {
            TString str = CreateInput('\xff', 1000);
            TMemoryInput input{str};
            EXPECT_TRUE(GetRandInteger(input, &value1));
        }
        EXPECT_NE(value1, value2);
    }

    TEST_F(TFuzzHelpersTest, JsonGettersTest) {
        {
            TString str = CreateInput('\x00', 1000);
            TMemoryInput input{str};
            EXPECT_FALSE(GetStringJsonValue(input).IsDefined());
            EXPECT_FALSE(GetIntegerJsonValue(input).IsDefined());
            EXPECT_FALSE(GetUIntegerJsonValue(input).IsDefined());
            EXPECT_FALSE(GetBooleanJsonValue(input).IsDefined());
            EXPECT_FALSE(GetArrayJsonValue(input).IsDefined());
            EXPECT_FALSE(GetMapJsonValue(input).IsDefined());
            EXPECT_FALSE(GetApiNameJsonValue(input).IsDefined());
            EXPECT_FALSE(GetAuthInfoJsonValue(input).IsDefined());
            EXPECT_FALSE(GetYCookiesJsonValue(input).IsDefined());
            EXPECT_FALSE(GetTargetingInfoJsonValue(input).IsDefined());
            EXPECT_EQ(GetRegionJsonValue(input, static_cast<ERegion>(42), static_cast<ERegion>(100)).GetInteger(), 42);
            EXPECT_EQ(GetLocaleJsonValue(input, {"ru", "en"}, "ru").GetString(), "ru");
            EXPECT_EQ(GetMordaZoneJsonValue(input, "en").GetString(), "en");
            EXPECT_EQ(GetTimeJsonValue(input, 1234).GetInteger(), 1234);
        }
        {
            TString str = CreateInput('\xff', 1000);
            TMemoryInput input{str};
            EXPECT_TRUE(GetStringJsonValue(input).IsString());
            EXPECT_TRUE(GetIntegerJsonValue(input).IsInteger());
            EXPECT_TRUE(GetUIntegerJsonValue(input).IsUInteger());
            EXPECT_TRUE(GetBooleanJsonValue(input).IsBoolean());
            EXPECT_TRUE(GetArrayJsonValue(input).IsArray());
            EXPECT_TRUE(GetMapJsonValue(input).IsMap());
            EXPECT_TRUE(GetApiNameJsonValue(input).IsString());
            EXPECT_TRUE(GetAuthInfoJsonValue(input).Has("login"));
            EXPECT_TRUE(GetYCookiesJsonValue(input).Has("S"));
            EXPECT_TRUE(GetTargetingInfoJsonValue(input).Has("promo-groups"));
            EXPECT_NE(GetRegionJsonValue(input, static_cast<ERegion>(42), static_cast<ERegion>(100)).GetInteger(), 42);
            EXPECT_NE(GetLocaleJsonValue(input, {"ru", "en"}, "ru").GetString(), "ru");
            EXPECT_NE(GetMordaZoneJsonValue(input, "en").GetString(), "en");
            EXPECT_NE(GetTimeJsonValue(input, 1234).GetInteger(), 1234);
        }
    }

} // namespace NMordaBlocks
