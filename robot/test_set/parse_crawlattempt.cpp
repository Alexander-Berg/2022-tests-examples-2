#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <mapreduce/yt/interface/client.h>

#include <library/cpp/getopt/last_getopt.h>

#include <google/protobuf/text_format.h>

#include <util/draft/datetime.h>
#include <util/random/random.h>
#include <library/cpp/string_utils/url/url.h>
#include <util/string/split.h>


void ParsePolicyRow(const TString& policyRow, const bool isRotor, const ui64 timestamp, NRRProto::TCrawlAttempt* crawlAttempt){
        TStringBuf policyRowBuf(policyRow);
        auto nameAndZone = policyRowBuf.NextTok('=');
        const auto name = TString{nameAndZone.NextTok('.')};
        const auto zone = TString{nameAndZone};
        const auto rank = FromString<float>(TString{policyRowBuf.NextTok(';')});
        const auto betterUrlsCount = FromString<ui64>(TString{policyRowBuf});

        auto newPolicy = crawlAttempt->AddPolicies();
        newPolicy->SetTimestamp(timestamp);
        newPolicy->SetPolicyName(name);
        newPolicy->SetZone(zone);
        newPolicy->SetRank(rank);
        newPolicy->SetBetterUrlsCount(betterUrlsCount);
        newPolicy->SetIsRotor(isRotor);
}


class TCrawlAttemptParser : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
public:

    void Do(NYT::TTableReader<NYT::TNode>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        TString host, path;
        SplitUrlToHostAndPath(reader->GetRow()["key"].AsString(), host, path);
        NRRProto::TPoolEntry finalResult;
        ui64 finalTimestamp = 0;
        for (; reader->IsValid(); reader->Next()) {
            NRRProto::TPoolEntry result;
            result.SetHost(host);
            result.SetPath(path);
            const auto row = reader->GetRow();
            const auto timestamp =  FromString<ui64>(row["subkey"].AsString());
            const auto tokens = StringSplitter(row["value"].AsString()).Split(' ').ToList<TString>();
            Y_ENSURE(tokens.size() >= 2, "Can't parse log");

            auto crawlAttempt = result.MutableCrawlPolicies();
            crawlAttempt->SetIsNew(row["is_new"].AsBool());
            TStringBuf mainPolicyDescr = row["main_policy"].AsString();
            crawlAttempt->MutableMainPolicy()->SetPolicyName(TString{mainPolicyDescr.NextTok('.')});
            crawlAttempt->MutableMainPolicy()->SetZone(TString{mainPolicyDescr});

            for (size_t idx = 2; idx < tokens.size(); ++idx) {
                ParsePolicyRow(tokens[idx], false, timestamp, crawlAttempt);
            }

            if (!row["rotor_policies"].IsUndefined()) {
                const auto rotorTokens = StringSplitter(row["rotor_policies"].AsString()).Split(' ').ToList<TString>();
                for (size_t idx = 0; idx < rotorTokens.size(); ++idx) {
                    ParsePolicyRow(rotorTokens[idx], true, timestamp, crawlAttempt);
                }
            }

            if (finalTimestamp < timestamp) {
                finalResult = result;
                finalTimestamp = timestamp;
            }
        }
        writer->AddRow(finalResult);
    }
};

REGISTER_REDUCER(TCrawlAttemptParser);


int ParseCrawlAttempt(int argc, const char** argv) {
    TString cluster;
    TString logsDir;
    TString result;
    size_t days;

    {
        NLastGetopt::TOpts opts = NLastGetopt::TOpts::Default();
        opts.AddHelpOption('h');
        opts.AddLongOption("cluster")
            .RequiredArgument("SERVER")
            .DefaultValue("arnold")
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
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);

    auto tx = client->StartTransaction();

    NYT::TMapReduceOperationSpec spec;
    for (size_t idx = 0; idx < days; ++idx) {
        TString date = NDatetime::TSimpleTM::NewLocal((TInstant::Now() - TDuration::Days(idx)).Seconds()).ToString("%Y%m%d");
        TString logTable = logsDir + "/" + date;
        if (tx->Exists(logTable)) {
            spec.AddInput<NYT::TNode>(logTable);
        }
    }

    spec.AddOutput<NRRProto::TPoolEntry>(result);
    spec.ReduceBy(NYT::TSortColumns("key"));

    tx->MapReduce(
        spec
        , nullptr
        , new TCrawlAttemptParser
        , NYT::TOperationOptions().Spec(NYT::TNode()("reducer", NYT::TNode()("memory_limit", (i64)10 * 1024 * 1024 * 1024)))
    );
    tx->Commit();

    return 0;
}
