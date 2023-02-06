#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <library/cpp/getopt/last_getopt.h>

#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/util/temp_table.h>

#include <library/cpp/string_utils/url/url.h>
#include <util/random/random.h>


class TSample : public NYT::IMapper<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
public:
    TSample() = default;

    TSample(double sampleProb)
        : SampleProb(sampleProb)
    {}

    void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        for (; reader->IsValid(); reader->Next()) {
            if (RandomNumber<double>() < SampleProb) {
                writer->AddRow(reader->GetRow());
            }
        }
    }

    Y_SAVELOAD_JOB(SampleProb);

private:
    double SampleProb;
};

REGISTER_MAPPER(TSample);


int ShrinkPool(int argc, const char** argv) {
    TString cluster;
    TString poolTable;
    TString resultTable;
    ui64 poolSize;

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
        opts.AddLongOption("result")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&resultTable);
        opts.AddLongOption("pool-size")
            .RequiredArgument("INT")
            .Required()
            .StoreResult(&poolSize);
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);

    auto tx = client->StartTransaction();

    {
        i64 rowCount = tx->Get(poolTable + "/@row_count").AsInt64();

        double sampleProb = static_cast<double>(poolSize) / rowCount;

        tx->Map(
            NYT::TMapOperationSpec()
                .AddInput<NRRProto::TPoolEntry>(poolTable)
                .AddOutput<NRRProto::TPoolEntry>(resultTable)
            , new TSample(sampleProb)
        );

        tx->Sort(
            NYT::TSortOperationSpec()
                .AddInput(resultTable)
                .Output(resultTable)
                .SortBy(NYT::TSortColumns("Host", "Path"))
        );
    }

    tx->Commit();

    return 0;
}
