#include <library/cpp/json/writer/json_value.h>
#include <library/cpp/json/json_reader.h>
#include <util/stream/file.h>

#include <library/cpp/testing/unittest/registar.h>
#include <robot/rthub/yql/udfs/turbopages/library/image_finder.h>

#include <library/cpp/archive/yarchive.h>
#include <util/memory/blob.h>

static const unsigned char TEST_DATA[] = {
        #include "test_data.inc"
};

TArchiveReader Archive(TBlob::NoCopy(TEST_DATA, sizeof(TEST_DATA)));

TString ReadResource(const TString& name)
{
    return Archive.ObjectByKey("/" + name)->ReadAll();
}

using namespace NTurboPages;

void RunSliderTest()
{
    NJson::TJsonValue sliders;
    NJson::ReadJsonTree(ReadResource("test_sliders.json"), &sliders);
    for (auto test_block: sliders.GetArray()) {
        auto sliderNode = test_block["slider"];
        auto expectedView = test_block["expected_view"];
        TSliderBlock sBlock(&sliderNode);
        sBlock.Process();
        UNIT_ASSERT_VALUES_EQUAL(sliderNode["view"], expectedView);
    }
}

void RunImageRatioTest()
{
    NJson::TJsonValue images;
    NJson::ReadJsonTree(ReadResource("test_images.json"), &images);
    for (auto test_block: images.GetArray()) {
        auto imageNode = test_block["image"];
        auto expectedView = test_block["expected_view"];
        EImageRatio imageRatio;
        bool is_small;
        std::tie(imageRatio, is_small) = DetermineImageRatio(imageNode);
        auto factView = ToString(imageRatio);
        UNIT_ASSERT_VALUES_EQUAL(expectedView, factView);
    }
}

Y_UNIT_TEST_SUITE(TSliderBlockTest) {
    Y_UNIT_TEST(TestSliderProcess) {
        RunSliderTest();
    }
    Y_UNIT_TEST(TestDetermineRatio) {
        RunImageRatioTest();
    }
}
