#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <library/cpp/getopt/last_getopt.h>

#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/util/temp_table.h>
#include <robot/jupiter/protos/acceptance.pb.h>
#include <robot/jupiter/protos/duplicates.pb.h>

#include <library/cpp/string_utils/url/url.h>


class TAddJupiterLabels : public NYT::IReducer<NYT::TTableReader<google::protobuf::Message>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
public:
    void Do(NYT::TTableReader<google::protobuf::Message>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        NRRProto::TSearchBaseInfo searchBaseInfo;
        for (; reader->IsValid(); reader->Next()) {
            if (reader->GetTableIndex() == 0) {
                const auto& row = reader->GetRow<NJupiter::TAcceptanceUrlForWebMasterRecord>();
                searchBaseInfo.SetInBase(true);
                if (row.GetIsSearchable()) {
                    searchBaseInfo.SetIsSearchable(true);
                }
            } else if(reader->GetTableIndex() == 1) {
                searchBaseInfo.SetIsMain(reader->GetRow<NJupiter::TDuplicateInfo>().GetIsMain());
                searchBaseInfo.SetDupGroupSize(reader->GetRow<NJupiter::TDuplicateInfo>().GetDupGroupSize());
            } else if (reader->GetTableIndex() == 2) {
                auto result = reader->GetRow<NRRProto::TPoolEntry>();
                result.MutableSearchBaseInfo()->CopyFrom(searchBaseInfo);
                writer->AddRow(result, 0);
                return;
            }
        }
    }
};

REGISTER_REDUCER(TAddJupiterLabels);


int GetSearchBaseInfo(int argc, const char** argv) {
    TString cluster;
    TString poolTable;
    TString jupiterUrlInfoTable;
    TString dupsTable;
    TString resultTable;
    {
        NLastGetopt::TOpts opts = NLastGetopt::TOpts::Default();
        opts.AddHelpOption('h');
        opts.AddLongOption("cluster")
            .RequiredArgument("SERVER")
            .DefaultValue("arnold")
            .StoreResult(&cluster);
        opts.AddLongOption("pool")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&poolTable);
        opts.AddLongOption("jupiter-urlinfo")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&jupiterUrlInfoTable);
        opts.AddLongOption("dups-info")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&dupsTable);
        opts.AddLongOption("result")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&resultTable);
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }
    auto client = NYT::CreateClient(cluster);

    auto tx = client->StartTransaction();

    {
        NYT::TTempTable tmpSorted(tx);
        tx->Sort(
            NYT::TSortOperationSpec()
                .AddInput(poolTable)
                .Output(tmpSorted.Name())
                .SortBy(NYT::TSortColumns("Host", "Path"))
        );
        tx->Reduce(
            NYT::TReduceOperationSpec()
                .AddInput<NJupiter::TAcceptanceUrlForWebMasterRecord>(jupiterUrlInfoTable)
                .AddInput<NJupiter::TDuplicateInfo>(dupsTable)
                .AddInput<NRRProto::TPoolEntry>(tmpSorted.Name())
                .AddOutput<NRRProto::TPoolEntry>(NYT::TRichYPath(resultTable).SortedBy(NYT::TSortColumns("Host", "Path")))
                .ReduceBy(NYT::TSortColumns("Host", "Path"))
            , new TAddJupiterLabels()
        );
    }

    tx->Commit();

    return 0;
}
