#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/util/temp_table.h>

#include <robot/lemur/protos/schema.pb.h>

#include <library/cpp/getopt/last_getopt.h>
#include <library/cpp/getopt/modchooser.h>

#include <google/protobuf/text_format.h>

#include <util/draft/datetime.h>
#include <util/random/random.h>
#include <library/cpp/string_utils/url/url.h>


class TCompatibilityMap : public NYT::IMapper<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NRRProto::TPoolEntry>> {
public:
    void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        for (; reader->IsValid(); reader->Next()) {
            NRRProto::TPoolEntry result;
            reader->MoveRow(&result);
            result.SetUrlColumn(result.GetHost() + result.GetPath());
            writer->AddRow(result);
        }
    }
};

REGISTER_MAPPER(TCompatibilityMap);


class TJoinFactors : public NYT::IReducer<NYT::TTableReader<NProtoBuf::Message>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
    void Do(NYT::TTableReader<NProtoBuf::Message>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        TMaybe<NLemurSchema::TFactorsRow> factorsRow;
        TMaybe<NRRProto::TPoolEntry> labelsRow;
        for (; reader->IsValid(); reader->Next()) {
            if (reader->GetTableIndex() == 0) { // Counters row
                labelsRow = reader->GetRow<NRRProto::TPoolEntry>();
            } else {
                if (!labelsRow) {
                    return;
                }

                const i64 crawlAttemptTimestamp = labelsRow->GetCrawlPolicies().GetMainPolicy().GetTimestamp();
                const i64 currentFactorsRowTimestamp = reader->GetRow<NLemurSchema::TFactorsRow>().GetTimestamp();

                const bool isFactorsAfterCrawlAttempt = crawlAttemptTimestamp < currentFactorsRowTimestamp;
                if (!isFactorsAfterCrawlAttempt){
                    continue;
                }

                if (!factorsRow || currentFactorsRowTimestamp < factorsRow->GetTimestamp()) {
                    factorsRow = reader->GetRow<NLemurSchema::TFactorsRow>();
                }
            }
        }

        if (!factorsRow || !labelsRow) {
            return;
        }

        labelsRow->MutableFactors()->CopyFrom(factorsRow->GetFactorsDump());
        labelsRow->SetLastAccess(factorsRow->GetTimestamp());
        labelsRow->SetHttpCode(factorsRow->GetHTTPCode());
        labelsRow->ClearUrlColumn();
        writer->AddRow(std::move(labelsRow.GetRef()));
    }
};

REGISTER_REDUCER(TJoinFactors);


int JoinFactors(int argc, const char** argv) {
    TString cluster;
    TVector<TString> factorTables;
    TString result;
    TString pool;

    {
        NLastGetopt::TOpts opts = NLastGetopt::TOpts::Default();
        opts.AddHelpOption('h');
        opts.AddLongOption("cluster")
            .RequiredArgument("SERVER")
            .DefaultValue("arnold")
            .StoreResult(&cluster);
        opts.AddLongOption("factors")
            .RequiredArgument("TABLE")
            .Required()
            .AppendTo(&factorTables);
        opts.AddLongOption("pool")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&pool);
        opts.AddLongOption("result")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&result);
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);

    auto tx = client->StartTransaction();
    {
        NYT::TTempTable tmpTable(tx);
        TString tmpTableName = tmpTable.Name();

        tx->Map(
            NYT::TMapOperationSpec()
                .AddInput<NRRProto::TPoolEntry>(pool)
                .AddOutput<NRRProto::TPoolEntry>(NYT::TRichYPath(tmpTableName))
            , new TCompatibilityMap()
        );

        tx->Sort(
           NYT::TSortOperationSpec()
                .AddInput(tmpTableName)
                .Output(tmpTableName)
                .SortBy(NYT::TSortColumns("url"))
        );

        auto joinFactorsSpec = NYT::TReduceOperationSpec();
        joinFactorsSpec.AddInput<NRRProto::TPoolEntry>(tmpTableName);
        for (const auto& factorsTable : factorTables) {
            joinFactorsSpec.AddInput<NLemurSchema::TFactorsRow>(factorsTable);
        }

        joinFactorsSpec.AddOutput<NRRProto::TPoolEntry>(result);
        joinFactorsSpec.ReduceBy(NYT::TSortColumns("url"));
        tx->Reduce(joinFactorsSpec, new TJoinFactors());

        tx->Sort(NYT::TSortOperationSpec()
            .AddInput(result)
            .Output(result)
            .SortBy(NYT::TSortColumns("Host", "Path"))
        );
    }

    tx->Commit();

    return 0;
}
