#include <mapreduce/yt/interface/client.h>
#include <robot/lemur/algo/ytlib/all.h>
#include <robot/lemur/protos/config.pb.h>
#include <robot/lemur/protos/locator.pb.h>
#include <robot/lemur/protos/schema.pb.h>
#include <robot/lemur/algo/locator/table.h>
#include <robot/lemur/algo/locator/locator.h>
#include <util/system/env.h>

using namespace NLemur;

using TPrepareTablesFunc = std::function<void(
        NYT::IClientPtr,
        TString&,
        TTable<NLemurSchema::TBinaryKeyRow>&,
        TTable<NLemurSchema::TCanonizationRow>&,
        TTable<NLemurSchema::TBinaryKeyRow>&,
        TString&,
        size_t&
        )>;

using TPrepareBinaryKeyTablesFunc = std::function<void(
        NYT::IClientPtr,
        TString&,
        TTable<NLemurSchema::TBinaryKeyRow>&,
        TTable<NLemurSchema::TBinaryKeyRow>&,
        TTable<NLemurSchema::TBinaryKeyRow>&,
        TString&,
        size_t&
        )>;



void ToProto(const TBinaryKey& key, NLemurSchema::TCanonizationRow& row) {
    row.SetOwnerKey(key.OwnerKey);
    row.SetHostKey(key.HostKey);
    row.SetUrlKey(key.UrlKey);
    row.SetKeyType(key.KeyType);
}

namespace NLemur {

    class TTestReduce : public ILemurReduceBase {
    public:
        TTestReduce() {
        }

        void Do(TTableReaderYT* reader, TTableWriterYT* writer) override {
            TBinaryKeyRowTableIterator iterator(NYT::CreateConcreteProtobufReader<NLemurSchema::TBinaryKeyRow>(reader).Get());
            TJoinIterator joinIterator(&iterator);
            joinIterator.SetJoinTableIndexes({0});
            while (joinIterator.IsValid()) {
                Cerr << "Got join record" << joinIterator.GetKey().ToHumanReadable() << " " << joinIterator.GetValue() << Endl;
                NLemurSchema::TBinaryKeyRow out;
                joinIterator.GetKey().ToProto(out);
                Cerr << "Got key" << Endl;
                out.SetValue(TString{joinIterator.GetValue()});
                writer->AddRow(out);
                Cerr << "Result written" << Endl;
                joinIterator.Next();
                Cerr << "joinIterator.Next()" << Endl;
            }
            Cerr << "Join stopped at table " << reader->GetTableIndex() << Endl;
            while (reader->IsValid()) {
                DoDo(reader, writer);
            }
        }

        void DoDo(TTableReaderYT* reader, TTableWriterYT* writer) {
            for (; reader->IsValid(); reader->Next()) {
                Cerr << "DoDo reader" << Endl;
                if (reader->GetTableIndex() == 1) {
                    const auto& row = reader->GetRow<NLemurSchema::TCanonizationRow>();
                    Cerr << "Got record of TCanonizationRow" << " " << row.GetSubKey() << " " << row.GetValue() << Endl;
                    NLemurSchema::TBinaryKeyRow out;
                    out.SetHostKey(row.GetHostKey());
                    out.SetOwnerKey(row.GetOwnerKey());
                    out.SetKeyType(row.GetKeyType());
                    out.SetUrlKey(row.GetUrlKey());
                    out.SetValue(row.GetValue());
                    writer->AddRow(out);
                }
                if (reader->GetTableIndex() == 2) {
                    const auto& row = reader->GetRow<NLemurSchema::TBinaryKeyRow>();
                    auto curKey = TBinaryKey();
                    curKey.FromProto(row);
                    Cerr << "Got record " << curKey.ToHumanReadable() << " " << row.GetSubKey() << " " << row.GetValue() << Endl;
                    writer->AddRow(row);
                }
            }
            Cerr << "End DoDo" << Endl;
        }
    };




    class TTestReduce_BinaryKeyRowLemurReduce : public IBinaryKeyRowLemurReduce {
        void DoDo(const TBinaryKey& key, TBinaryKeyRowTableIterator* input, TLemurUpdate* output) override {
            Cerr << "DoDo: Process key " << key.ToHumanReadable() << Endl;
            while (input->IsValid()) {
                Cerr << "read record from table " << input->GetTableIndex();
                Cerr << " " << input->GetKey().ToHumanReadable() << " " << input->GetValue() << Endl;
                NLemurSchema::TBinaryKeyRow out;
                input->GetKey().ToProto(out);
                out.SetValue(TString{input->GetValue()});
                output->AddProto(0, out);
                input->Next();
            }
        }

        void Join(TJoinIterator* joinData) override {
            while (joinData->IsValid()) {
                Cerr << "Join: Got join record" << joinData->GetKey().ToHumanReadable() << " " << joinData->GetValue() << Endl;
                joinData->Next();
            }
        }
    };


}
REGISTER_REDUCER(NLemur::TTestReduce);
REGISTER_REDUCER(NLemur::TTestReduce_BinaryKeyRowLemurReduce);



void TestCase1(
        NYT::IClientPtr client,
        TString& basePrefix,
        TTable<NLemurSchema::TBinaryKeyRow>& joinTable,
        TTable<NLemurSchema::TCanonizationRow>& t1Table,
        TTable<NLemurSchema::TBinaryKeyRow>& t2Table,
        TString& resTableName,
        size_t& resRecordCount
        )
{
    Cerr << "TestCase1 Join table has 1 record and two tables contain 2 records with the same key\n"
        "Expected result: 5 records in output table" << Endl;
    resTableName = basePrefix + "result_TestCase1";
    resRecordCount = 5;

    TBinaryKey testKey(536032072068819u, 16930028694574207757u, 805172322240778831u, 50);

    {
        joinTable.CheckOrCreate(client.Get());
        auto writer = joinTable.GetWriter(client.Get());
        NLemurSchema::TBinaryKeyRow row;
        testKey.ToProto(row);
        row.SetSubKey("jsubkey");
        row.SetValue("jvalue");
        writer->AddRow(row);
        writer->Finish();
        joinTable.Sort(client.Get());
    }

    {
        t1Table.CheckOrCreate(client.Get());
        auto writer = t1Table.GetWriter(client.Get());
        { NLemurSchema::TCanonizationRow row;
        ToProto(testKey, row);
        row.SetSubKey("t1subkey");
        row.SetValue("t1value");
        writer->AddRow(row); }
        { NLemurSchema::TCanonizationRow row;
        ToProto(testKey, row);
        row.SetSubKey("t1subkey2");
        row.SetValue("t1value2");
        writer->AddRow(row); }
        writer->Finish();
        t1Table.Sort(client.Get());
    }

    {
        t2Table.CheckOrCreate(client.Get());
        auto writer = t2Table.GetWriter(client.Get());
        { NLemurSchema::TBinaryKeyRow row;
        testKey.ToProto(row);
        row.SetSubKey("t2subkey");
        row.SetValue("t2value");
        writer->AddRow(row); }
        { NLemurSchema::TBinaryKeyRow row;
        testKey.ToProto(row);
        row.SetSubKey("t2subkey2");
        row.SetValue("t2value2");
        writer->AddRow(row); }
        writer->Finish();
        t2Table.Sort(client.Get());
    }
}




void TestCase2(
        NYT::IClientPtr client,
        TString& basePrefix,
        TTable<NLemurSchema::TBinaryKeyRow>& joinTable,
        TTable<NLemurSchema::TCanonizationRow>& t1Table,
        TTable<NLemurSchema::TBinaryKeyRow>& t2Table,
        TString& resTableName,
        size_t& resRecordCount
        )
{
    Cerr << "TestCase2 Join table has 1 record and two tables contain 2 records with DIFFERENT keys\n"
        "Expected result: 5 records in output table" << Endl;
    resTableName = basePrefix + "result_TestCase2";
    resRecordCount = 5;

    TBinaryKey testKey(536032072068819u, 16930028694574207757u, 805172322240778831u, 50);

    {
        joinTable.CheckOrCreate(client.Get());
        auto writer = joinTable.GetWriter(client.Get());
        NLemurSchema::TBinaryKeyRow row;
        testKey.ToProto(row);
        row.SetSubKey("jsubkey");
        row.SetValue("jvalue");
        writer->AddRow(row);
        writer->Finish();
        joinTable.Sort(client.Get());
    }

    {
        t1Table.CheckOrCreate(client.Get());
        auto writer = t1Table.GetWriter(client.Get());
        { NLemurSchema::TCanonizationRow row;
        ToProto(testKey, row);
        row.SetSubKey("t1subkey");
        row.SetValue("t1value");
        writer->AddRow(row); }
        { NLemurSchema::TCanonizationRow row;
        ToProto(testKey, row);
        row.SetUrlKey(testKey.UrlKey + 1);
        row.SetSubKey("t1subkey2");
        row.SetValue("t1value2");
        writer->AddRow(row); }
        writer->Finish();
        t1Table.Sort(client.Get());
    }

    {
        t2Table.CheckOrCreate(client.Get());
        auto writer = t2Table.GetWriter(client.Get());
        { NLemurSchema::TBinaryKeyRow row;
        testKey.ToProto(row);
        row.SetUrlKey(testKey.UrlKey + 1);
        row.SetSubKey("t2subkey");
        row.SetValue("t2value");
        writer->AddRow(row); }
        { NLemurSchema::TBinaryKeyRow row;
        testKey.ToProto(row);
        row.SetSubKey("t2subkey2");
        row.SetValue("t2value2");
        writer->AddRow(row); }
        writer->Finish();
        t2Table.Sort(client.Get());
    }
}








void TestCase3(
        NYT::IClientPtr client,
        TString& basePrefix,
        TTable<NLemurSchema::TBinaryKeyRow>& joinTable,
        TTable<NLemurSchema::TCanonizationRow>& t1Table,
        TTable<NLemurSchema::TBinaryKeyRow>& t2Table,
        TString& resTableName,
        size_t& resRecordCount
        )
{
    Cerr << "TestCase3 Join table has 1 record and two tables contain 2 records . ALL KEYS DIFFERENT for each record\n"
        "Expected result: 5 records in output table" << Endl;
    resTableName = basePrefix + "result_TestCase3";
    resRecordCount = 5;

    TBinaryKey testKey(536032072068819u, 16930028694574207757u, 805172322240778831u, 50);

    {
        joinTable.CheckOrCreate(client.Get());
        auto writer = joinTable.GetWriter(client.Get());
        NLemurSchema::TBinaryKeyRow row;
        testKey.ToProto(row);
        row.SetSubKey("jsubkey");
        row.SetValue("jvalue");
        writer->AddRow(row);
        writer->Finish();
        joinTable.Sort(client.Get());
    }

    {
        t1Table.CheckOrCreate(client.Get());
        auto writer = t1Table.GetWriter(client.Get());
        { NLemurSchema::TCanonizationRow row;
        ToProto(testKey, row);
        row.SetUrlKey(testKey.UrlKey + 1);
        row.SetSubKey("t1subkey");
        row.SetValue("t1value");
        writer->AddRow(row); }
        { NLemurSchema::TCanonizationRow row;
        ToProto(testKey, row);
        row.SetUrlKey(testKey.UrlKey + 2);
        row.SetSubKey("t1subkey2");
        row.SetValue("t1value2");
        writer->AddRow(row); }
        writer->Finish();
        t1Table.Sort(client.Get());
    }

    {
        t2Table.CheckOrCreate(client.Get());
        auto writer = t2Table.GetWriter(client.Get());
        { NLemurSchema::TBinaryKeyRow row;
        testKey.ToProto(row);
        row.SetUrlKey(testKey.UrlKey + 3);
        row.SetSubKey("t2subkey");
        row.SetValue("t2value");
        writer->AddRow(row); }
        { NLemurSchema::TBinaryKeyRow row;
        testKey.ToProto(row);
        row.SetUrlKey(testKey.UrlKey + 4);
        row.SetSubKey("t2subkey2");
        row.SetValue("t2value2");
        writer->AddRow(row); }
        writer->Finish();
        t2Table.Sort(client.Get());
    }
}








void TestCase_BinaryKeyRowLemurReduce1(
        NYT::IClientPtr client,
        TString& basePrefix,
        TTable<NLemurSchema::TBinaryKeyRow>& joinTable,
        TTable<NLemurSchema::TBinaryKeyRow>& t1Table,
        TTable<NLemurSchema::TBinaryKeyRow>& t2Table,
        TString& resTableName,
        size_t& resRecordCount
        )
{
    Cerr << "TestCase_BinaryKeyRowLemurReduce1 Join table has 4 records;"
        "two other tables contain 6 records each. \n"
        "join key 0 - table 1 url key\n"
        "join key 1 - table 1 and table 2 keys\n"
        "join key 2 - table 2 key\n"
        "join key 3 - no url keys\n"
        "Expected result: 12 records in output table" << Endl;
    resTableName = basePrefix + "result_TestCase_BinaryKeyRowLemurReduce1";
    resRecordCount = 12;

    TBinaryKey testKey(536032072068819u, 16930028694574207757u, 805172322240778831u, 50);

    {
        Cerr << "Create 4 different host keys" << Endl;
        joinTable.CheckOrCreate(client.Get());
        auto writer = joinTable.GetWriter(client.Get());
        for (int i = 0 ; i < 4; ++i) {
            NLemurSchema::TBinaryKeyRow row;
            testKey.ToProto(row);
            row.SetHostKey(testKey.HostKey + i);
            row.SetSubKey("jsubkey");
            row.SetValue("jvalue");
            writer->AddRow(row);
        }
        writer->Finish();
        joinTable.Sort(client.Get());
    }

    {
        Cerr << "For key 0 and 1 in join table create 3 records for each one" << Endl;
        t1Table.CheckOrCreate(client.Get());
        auto writer = t1Table.GetWriter(client.Get());
        for (int i = 0 ; i < 2; ++i) {
            for (int j = 0 ; j < 3 ; ++j) {
                NLemurSchema::TBinaryKeyRow row;
                testKey.ToProto(row);
                row.SetHostKey(testKey.HostKey + i);
                row.SetUrlKey(testKey.UrlKey + j);
                row.SetSubKey("t1subkey");
                row.SetValue("t1value");
                writer->AddRow(row);
            }
        }
        writer->Finish();
        t1Table.Sort(client.Get());
    }

    {
        Cerr << "For key 1 and 2 in join table create 3 records for each one" << Endl;
        t2Table.CheckOrCreate(client.Get());
        auto writer = t2Table.GetWriter(client.Get());
        for (int i = 1 ; i < 3; ++i) {
            for (int j = 0 ; j < 3 ; ++j) {
                NLemurSchema::TBinaryKeyRow row;
                testKey.ToProto(row);
                row.SetHostKey(testKey.HostKey + i);
                row.SetUrlKey(testKey.UrlKey + j);
                row.SetSubKey("t2subkey");
                row.SetValue("t2value");
                writer->AddRow(row);
            }
        }
        writer->Finish();
        t2Table.Sort(client.Get());
    }

    Cerr << "Host key 3 left without url records" << Endl;
}



////////////////////////////////////////////////////////////
// RunTest_BinaryKeyRowLemurReduce
////////////////////////////////////////////////////////////



int RunTest(int argc, const char* argv[], TPrepareTablesFunc prepareTablesFunc) {
    Cerr << "Test join iterator with yt reader" << Endl;
    TString basePrefix = "//tmp/test_join_iter/";
    NLemurConfig::TInstanceConfig instanceConfig;

    NLemur::ExitIfWeAreInJob(argc, argv);
    //NLemur::InitializeMRAndLocator(argc, argv, instanceConfig);
    TLocator::InitStaticLocator(basePrefix);

    NYT::IClientPtr client = NYT::CreateClient("banach");
    auto transaction = client->StartTransaction();
    try {
        TJobConfig jobConfig("test_join_iter", LL_NO);

        auto joinTable = TTable<NLemurSchema::TBinaryKeyRow>(basePrefix + "join");
        auto t1Table = TTable<NLemurSchema::TCanonizationRow>(basePrefix + "t1");
        auto t2Table = TTable<NLemurSchema::TBinaryKeyRow>(basePrefix + "t2");

        TString resTableName;
        size_t resRecordCount = 0;
        prepareTablesFunc(client, basePrefix, joinTable, t1Table, t2Table, resTableName, resRecordCount);
        auto resTable = TTable<NLemurSchema::TBinaryKeyRow>(resTableName);

        auto cmd = MakeReduceCmd(
                client.Get(),
                transaction.Get(),
                jobConfig,
                instanceConfig.GetMRConfig()
                );
        cmd
            .Input(joinTable.Foreign())
            .Input(t1Table)
            .Input(t2Table)
            .Output(resTable)
            .JoinBy(t1Table.GetDefaultJoinColumns())
            .SortBy(t1Table.GetDefaultSortColumns())
            .ReduceBy(t1Table.GetDefaultReduceColumns());

        Cerr << "Start operation" << Endl;
        cmd.Do(new TTestReduce());

        transaction->Commit();

        size_t cnt = 0;
        auto reader = resTable.GetReader(client.Get());
        while (reader->IsValid()) {
            auto& row = reader->GetRow();
            TBinaryKey key;
            key.FromProto(row);
            Cerr << key.ToHumanReadable() << " " << row.GetValue() << Endl;
            reader->Next();
            cnt++;
        }
        if (cnt != resRecordCount) {
            Y_FAIL("Output row count differs. Got %zu expected %zu", cnt, resRecordCount);
        }

        joinTable.Drop(client.Get());
        t1Table.Drop(client.Get());
        t2Table.Drop(client.Get());
        resTable.Drop(client.Get());
        Cerr << "DONE" << Endl;

    } catch (...) {
        transaction->Abort();
        throw;
    }
    return 0;
}

////////////////////////////////////////////////////////////
// RunTest_BinaryKeyRowLemurReduce
////////////////////////////////////////////////////////////



int RunTest_BinaryKeyRowLemurReduce(int argc, const char* argv[], TPrepareBinaryKeyTablesFunc prepareTablesFunc) {
    Cerr << "Test BinaryKeyRowLemurReduce, join iterator with tableiterator" << Endl;
    TString basePrefix = "//tmp/test_join_iter/";
    NLemurConfig::TInstanceConfig instanceConfig;

    NLemur::ExitIfWeAreInJob(argc, argv);
    //NLemur::InitializeMRAndLocator(argc, argv, instanceConfig);
    TLocator::InitStaticLocator(basePrefix);

    NYT::IClientPtr client = NYT::CreateClient("banach");
    auto transaction = client->StartTransaction();
    try {
        TJobConfig jobConfig("test_join_iter", LL_NO);

        auto joinTable = TTable<NLemurSchema::TBinaryKeyRow>(basePrefix + "join");
        auto t1Table = TTable<NLemurSchema::TBinaryKeyRow>(basePrefix + "t1");
        auto t2Table = TTable<NLemurSchema::TBinaryKeyRow>(basePrefix + "t2");

        TString resTableName;
        size_t resRecordCount = 0;
        prepareTablesFunc(client, basePrefix, joinTable, t1Table, t2Table, resTableName, resRecordCount);
        auto resTable = TTable<NLemurSchema::TBinaryKeyRow>(resTableName);

        auto cmd = MakeReduceCmd(
                client.Get(),
                transaction.Get(),
                jobConfig,
                instanceConfig.GetMRConfig()
                );
        cmd
            .Input(joinTable.Foreign())
            .Input(t1Table)
            .Input(t2Table)
            .Output(resTable)
            .JoinBy(t1Table.GetDefaultJoinColumns())
            .SortBy(t1Table.GetDefaultSortColumns())
            .ReduceBy(t1Table.GetDefaultReduceColumns());

        Cerr << "Start operation" << Endl;
        cmd.Do(new TTestReduce_BinaryKeyRowLemurReduce());

        transaction->Commit();

        size_t cnt = 0;
        auto reader = resTable.GetReader(client.Get());
        while (reader->IsValid()) {
            auto& row = reader->GetRow();
            TBinaryKey key;
            key.FromProto(row);
            Cerr << key.ToHumanReadable() << " " << row.GetValue() << Endl;
            reader->Next();
            cnt++;
        }
        if (cnt != resRecordCount) {
            Y_FAIL("Output row count differs. Got %zu expected %zu", cnt, resRecordCount);
        }
        joinTable.Drop(client.Get());
        t1Table.Drop(client.Get());
        t2Table.Drop(client.Get());
        resTable.Drop(client.Get());
        Cerr << "DONE" << Endl;

    } catch (...) {
        transaction->Abort();
        throw;
    }
    return 0;
}

int main(int argc, const char* argv[]) {
    SetEnv("YT_USE_CLIENT_PROTOBUF", "0");

    RunTest(argc, argv, TestCase1);
    RunTest(argc, argv, TestCase2);
    RunTest(argc, argv, TestCase3);
    RunTest_BinaryKeyRowLemurReduce(argc, argv, TestCase_BinaryKeyRowLemurReduce1);
    return 0;
}


