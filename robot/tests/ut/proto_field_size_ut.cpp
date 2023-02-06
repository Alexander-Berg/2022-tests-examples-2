#include <robot/rthub/misc/proto_field_size.h>
#include <robot/rthub/infrastructure/tests/ut/protos/test_messages.pb.h>
#include <library/cpp/testing/unittest/registar.h>

using namespace NRTHub;

using NRTHubTest::TMessage;
using NRTHubTest::test_marker;

namespace {
void ExpectMapEquals(const THashMap<TString, ui64>& m1, const THashMap<TString, ui64>& m2) {
    UNIT_ASSERT_VALUES_EQUAL(m1.size(), m2.size());
    for (auto p : m1) {
        auto v = m2.FindPtr(p.first);
        UNIT_ASSERT_C(v, p.first);
        UNIT_ASSERT_VALUES_EQUAL(*v, p.second);
    }
}
}

Y_UNIT_TEST_SUITE(TProtoFieldSizeTests) {

    Y_UNIT_TEST(WithoutAnnotation) {
        TMessage msg;
        msg.SetNoAnnotationStrData("ABC");
        auto map = CollectProtoFieldNamesAndSizes(msg, test_marker);
        ExpectMapEquals(map, { });
    }

    Y_UNIT_TEST(StrAndBytesField) {
        TMessage msg;
        msg.SetStrData("ABC");
        msg.SetBytesData("123456789");
        auto map = CollectProtoFieldNamesAndSizes(msg, test_marker);
        ExpectMapEquals(map, { {"StrData", 3}, { "BytesData", 9 } });
    }

    Y_UNIT_TEST(ScalarFields) {
        TMessage msg;
        msg.SetIntData(123);
        msg.SetBoolData(true);
        msg.MutableIntRepData()->Add(12345);
        msg.MutableStrRepData()->Add("99999999999");
        auto map = CollectProtoFieldNamesAndSizes(msg, test_marker);
        ExpectMapEquals(map, { { "IntData", 0 }, { "BoolData", 0 }, { "IntRepData", 0 }, { "StrRepData", 0 } });
    }

    Y_UNIT_TEST(SubmessageFields) {
        TMessage msg;
        msg.MutableSubMsgData()->SetData("0123456789");

        msg.MutableSubMsgRepData()->Add()->SetData("0123456789");
        msg.MutableSubMsgRepData()->Add()->SetData("0123456789");
        msg.MutableSubMsgRepData()->Add()->SetData("0123456789");

        auto map = CollectProtoFieldNamesAndSizes(msg, test_marker);
        // 2 bytes for meta
        ExpectMapEquals(map, { { "SubMsgData", 12 }, { "SubMsgRepData", 3 * 12 } });
    }

}
