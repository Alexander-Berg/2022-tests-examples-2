#include <robot/blrt/library/collect_debug_logs/log_collector.h>
#include <robot/blrt/protos/resharder_offer.pb.h>

#include <irt/bannerland/proto/offer/offer.pb.h>
#include <market/idx/datacamp/proto/api/ExportMessage.pb.h>

#include <library/cpp/testing/unittest/registar.h>

#include <google/protobuf/util/message_differencer.h>


namespace {

    constexpr ui32 TestShopId = 123;
    constexpr ui32 TestBusinessId = 456;
    constexpr ui64 TestOfferYabsId = 789;
    constexpr ui64 TestTimestamp = 123456789;

    NBlrt::TResharderOfferPtr CreateResharderOffer() {
        auto resharderOffer = MakeAtomicShared<NBlrt::TResharderOffer>();
        auto datacampfOffer = resharderOffer->MutableExportMessage()->mutable_offer();
        datacampfOffer->set_shop_id(TestShopId);
        datacampfOffer->set_business_id(TestBusinessId);
        datacampfOffer->set_offer_yabs_id(TestOfferYabsId);
        return resharderOffer;
    }

    bool CompareProtos(const google::protobuf::Message& msg1, const google::protobuf::Message& msg2, TString& diff) {
        google::protobuf::io::StringOutputStream stream(&diff);
        google::protobuf::util::MessageDifferencer::StreamReporter reporter(&stream);

        google::protobuf::util::MessageDifferencer differencer;
        differencer.ReportDifferencesTo(&reporter);

        return differencer.Compare(msg1, msg2);
    }

}

Y_UNIT_TEST_SUITE(LogCollectorTest) {

    Y_UNIT_TEST(SkipOfferForDisabledShopId) {
        auto offer = CreateResharderOffer();
        auto collector = NBlrt::TLogCollector();

        collector.Add({offer});
        const auto chunks = collector.GetRecords(TestTimestamp);

        UNIT_ASSERT(chunks.empty());
    }

    Y_UNIT_TEST(BuildLogRecordFromChunks) {
        auto offer = CreateResharderOffer();
        auto shopIds = { TestShopId };
        auto collector = NBlrt::TLogCollector({shopIds.begin(), shopIds.end()});

        collector.Add({offer});

        const auto chunks = collector.GetRecords(TestTimestamp);
        const auto record = NBlrt::BuildLogRecordFromChunks(chunks);

        Y_ENSURE(record);
        UNIT_ASSERT_EQUAL(chunks.size(), 1);
        UNIT_ASSERT_EQUAL(record->GetShopId(), TestShopId);
        UNIT_ASSERT_EQUAL(record->GetBusinessId(), TestBusinessId);
        UNIT_ASSERT_EQUAL(record->GetOfferYabsId(), TestOfferYabsId);
        UNIT_ASSERT_EQUAL(record->GetTimestamp(), TestTimestamp);

        NBlrt::TLogRecordData data;
        UNIT_ASSERT(data.ParseFromString(record->GetData()));

        TString diff;
        const auto datacampOffer = offer->GetExportMessage().offer();
        const bool isEqual = CompareProtos(data.GetOffer(), datacampOffer, diff);
        UNIT_ASSERT_C(isEqual, diff);
    }

}
