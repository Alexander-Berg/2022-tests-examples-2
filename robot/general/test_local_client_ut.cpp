#include "test_local_client.h"
#include "ut/typed_fakes_ut.h"

#include <library/cpp/testing/unittest/registar.h>

using namespace NRtDoc;
using namespace NRtDocTest;

using THelper = NRtDocTest::TTestClientHelper;

class TRtDocTestClientTest: public NUnitTest::TTestBase {
    UNIT_TEST_SUITE(TRtDocTestClientTest)
        UNIT_TEST(TestBasics);
        UNIT_TEST(TestHelpers);
    UNIT_TEST_SUITE_END();

private:
    THolder<TTestLocalClient> TestClient;

public:
    void SetUp() override {
        const TFsPath parentDir = TFsPath::Cwd();
        TestClient = MakeHolder<TTestLocalClient>(parentDir);
    }

    void TearDown() override {
        if (TestClient) {
            TestClient->CleanupTempFiles();
            // CleanupTempFiles() is not called automatically, because the user might want
            // to keep the "test_local_index" folder when the test run fails
            TestClient.Destroy();
        }
    }

    void TestBasics() {
        NYT::IIOClient& ytClient = TestClient->AsIOClient();

        TVector<IMockItem::TPtr> portionC{
            MakeIntrusive<TPortionItem<TDocPortionC>>("", "row10", 72u), // 'docId' is set at random here - no monotonic requirements or whatever
            MakeIntrusive<TPortionItem<TDocPortionC>>("", "row20", 0u),
        };

        TVector<IMockItem::TPtr> portionE{
            MakeIntrusive<TBatchPortionItem<TBatchPortionE>>("", "row0", 1234u),
        };

        {
            auto writer1 = ytClient.CreateTableWriter<TDocPortionC>("c");
            WriteTable(portionC, writer1);

            auto writer2 = ytClient.CreateTableWriter<TBatchPortionE>("e");
            WriteTable(portionE, writer2);
        }

        TestClient->FinishWriters();

        {
            auto reader1 = ytClient.CreateTableReader<TDocPortionC>("c");
            UNIT_ASSERT_VALUES_EQUAL("c:72:row10 c:0:row20", THelper::Dump(ReadTable("c", reader1)));

            auto reader2 = ytClient.CreateTableReader<TBatchPortionE>("e");
            UNIT_ASSERT_VALUES_EQUAL("e:1234:row0", THelper::Dump(ReadTable("e", reader2)));
        }
    }

    void TestHelpers() {
        NYT::IIOClient& ytClient = TestClient->AsIOClient();

        TPortionItem<TDocPortionC> item1("", "row1", 22u);
        TPortionItem<TDocPortionC> item2("", "row2", 27u);
        const auto& itemData1 = static_cast<const TDocPortionC&>(item1.GetProtobuf());
        const auto& itemData2 = static_cast<const TDocPortionC&>(item2.GetProtobuf());

        auto doubleWriter = TestClient->CreateCombinedWriter<TDocPortionC, TDocPortionC>("c", "ca");
        doubleWriter->AddRow(itemData1, 0);
        doubleWriter->AddRow(itemData2, 1);

        TestClient->FinishWriters();

        {
            auto reader1 = ytClient.CreateTableReader<TDocPortionC>("c");
            UNIT_ASSERT_VALUES_EQUAL("c:22:row1", THelper::Dump(ReadTable("c", reader1)));

            auto reader2 = ytClient.CreateTableReader<TDocPortionC>("ca");
            UNIT_ASSERT_VALUES_EQUAL("ca:27:row2", THelper::Dump(ReadTable("ca", reader2)));
        }
    }
};

UNIT_TEST_SUITE_REGISTRATION(TRtDocTestClientTest);

