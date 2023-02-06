#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <mapreduce/yt/interface/client.h>

#include <library/cpp/getopt/last_getopt.h>

#include <google/protobuf/text_format.h>

#include <util/draft/datetime.h>
#include <util/random/random.h>
#include <library/cpp/string_utils/url/url.h>


class TSpiderLogFilter : public NYT::IMapper<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{
public:
    TSpiderLogFilter() = default;

    TSpiderLogFilter(const TString& source)
        : Source(source)
    {}

    void Do(NYT::TTableReader<NYT::TNode>* reader, NYT::TTableWriter<NYT::TNode>* writer) override final {
        for (; reader->IsValid(); reader->Next()) {
            if (reader->GetRow()["record_type"] == "RESULT" && reader->GetRow()["source"] == Source) {
                NYT::TNode result;
                result["Host"] = GetSchemeHostAndPort(reader->GetRow()["url"].AsString(), false, false);
                result["Day"] = reader->GetTableIndex();
                result["Counter"] = ui64(1);
                writer->AddRow(result);
            }
        }
    }

    Y_SAVELOAD_JOB(Source);

private:
    TString Source;
};

REGISTER_MAPPER(TSpiderLogFilter);


class TCrawlStatAggregator : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{
    void Do(NYT::TTableReader<NYT::TNode>* reader, NYT::TTableWriter<NYT::TNode>* writer) override final {
        THashMap<ui64, ui64> dayCounters;
        TString host = reader->GetRow()["Host"].AsString();
        for (; reader->IsValid(); reader->Next()) {
            dayCounters[reader->GetRow()["Day"].AsUint64()] += reader->GetRow()["Counter"].AsUint64();
        }
        for (const auto& pair : dayCounters) {
            NYT::TNode result;
            result["Host"] = host;
            result["Day"] = pair.first;
            result["Counter"] = pair.second;
            writer->AddRow(result);
        }
    }
};

REGISTER_REDUCER(TCrawlStatAggregator);


class TAvgDailyCrawl : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{
    void Do(NYT::TTableReader<NYT::TNode>* reader, NYT::TTableWriter<NYT::TNode>* writer) override final {
        THashMap<ui64, ui64> dayCounters;
        TString host = reader->GetRow()["Host"].AsString();
        for (; reader->IsValid(); reader->Next()) {
            dayCounters[reader->GetRow()["Day"].AsUint64()] += reader->GetRow()["Counter"].AsUint64();
        }
        double totalSum = 0;
        for (const auto& pair : dayCounters) {
            totalSum += pair.second;
        }
        NYT::TNode result;
        result["Host"] = host;
        result["AvgDailyCrawl"] = totalSum / dayCounters.size();
        writer->AddRow(result);
    }
};

REGISTER_REDUCER(TAvgDailyCrawl);



int CalcHostLimit(int argc, const char** argv) {
    TString cluster;
    TString logsDir;
    TString result;
    TString source;
    size_t days;

    {
        NLastGetopt::TOpts opts = NLastGetopt::TOpts::Default();
        opts.AddHelpOption('h');
        opts.AddLongOption("cluster")
            .RequiredArgument("SERVER")
            .DefaultValue("hahn")
            .StoreResult(&cluster);
        opts.AddLongOption("logs-dir")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&logsDir);
        opts.AddLongOption("result")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&result);
        opts.AddLongOption("period")
            .RequiredArgument("DAYS")
            .StoreResult(&days)
            .DefaultValue(30);
        opts.AddLongOption("source")
            .RequiredArgument("STR")
            .Required()
            .StoreResult(&source);
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);

    auto tx = client->StartTransaction();
    NYT::TMapReduceOperationSpec spec;
    for (size_t idx = 1; idx <= days; ++idx) {
        TString date = NDatetime::TSimpleTM::NewLocal((TInstant::Now() - TDuration::Days(idx)).Seconds()).ToString("%Y-%m-%d");
        TString logTable = logsDir + "/" + date;
        if (tx->Exists(logTable)) {
            spec.AddInput<NYT::TNode>(logTable);
        }
    }

    spec.AddOutput<NYT::TNode>(result);
    spec.ReduceBy(NYT::TSortColumns("Host"));
    tx->MapReduce(
        spec
        , new TSpiderLogFilter(source)
        , new TCrawlStatAggregator()
        , new TAvgDailyCrawl()
    );
    tx->Commit();

    return 0;
}
