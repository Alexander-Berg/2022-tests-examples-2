#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/util/temp_table.h>

#include <library/cpp/getopt/last_getopt.h>

using TDailyCrawlStatInfo = THashMap<std::pair<ui64, TString>, double>;


class TDailyStatMap : public NYT::IMapper<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NRRProto::TDailyCrawlStat>> {
public:
    TDailyStatMap() = default;

    TDailyStatMap(const TString& policyName)
        : PolicyName(policyName)
    {}

  void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NRRProto::TDailyCrawlStat>* writer) override final {
        for (; reader->IsValid(); reader->Next()) {
            if (reader->GetRow().GetCrawlPolicies().GetMainPolicy().GetPolicyName() != PolicyName) {
                continue;
            }
            for (const auto& crawlPolicies : reader->GetRow().GetCrawlPolicies().GetPolicies()) {
                if (crawlPolicies.GetPolicyName() == PolicyName) {
                    NRRProto::TDailyCrawlStat result;
                    result.SetDay(crawlPolicies.GetTimestamp() / 60 / 60 / 24);
                    result.SetCount(1.0);
                    result.SetZone(crawlPolicies.GetZone());
                    writer->AddRow(result);
                    break;
                }
            }
        }
   }
   Y_SAVELOAD_JOB(PolicyName);

private:
    TString PolicyName;
};


REGISTER_MAPPER(TDailyStatMap);


class TDailyStatReduce : public NYT::IReducer<NYT::TTableReader<NRRProto::TDailyCrawlStat>, NYT::TTableWriter<NRRProto::TDailyCrawlStat>> {
public:
   void Do(NYT::TTableReader<NRRProto::TDailyCrawlStat>* reader, NYT::TTableWriter<NRRProto::TDailyCrawlStat>* writer) override final {
       ui64 day = reader->GetRow().GetDay();
       TString zone = reader->GetRow().GetZone();
       double count = 0;
       for (; reader->IsValid(); reader->Next()) {
            count += reader->GetRow().GetCount();
       }
       NRRProto::TDailyCrawlStat result;
       result.SetDay(day);
       result.SetZone(zone);
       result.SetCount(count);
       writer->AddRow(result);
   }
};

REGISTER_REDUCER(TDailyStatReduce);


class TMakeUnbiased : public NYT::IMapper<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NRRProto::TPoolEntry>> {
public:
    TMakeUnbiased() = default;

    TMakeUnbiased(const TDailyCrawlStatInfo& dailyStat, const TString& policyName)
        : DailyStat(dailyStat)
        , PolicyName(policyName)
    {}

    void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        for (; reader->IsValid(); reader->Next()) {
            for (const auto& crawlPolicies : reader->GetRow().GetCrawlPolicies().GetPolicies()) {
                if (crawlPolicies.GetPolicyName() == PolicyName) {
                    if (crawlPolicies.GetBetterUrlsCount() < DailyStat[std::make_pair(crawlPolicies.GetTimestamp() / 60 / 60 / 24, crawlPolicies.GetZone())]) {
                        auto result = reader->GetRow();
                        result.SetWeight(1.0);
                        writer->AddRow(result);
                    }
                    break;
                }
            }
        }
   }

   Y_SAVELOAD_JOB(DailyStat, PolicyName);

private:
    TDailyCrawlStatInfo DailyStat;
    TString PolicyName;
};

REGISTER_MAPPER(TMakeUnbiased);


int MakeUnbiased(int argc, const char** argv) {
    TString cluster;
    TString input;
    TString result;
    TString policyName;

    {
        NLastGetopt::TOpts opts = NLastGetopt::TOpts::Default();
        opts.AddHelpOption('h');
        opts.AddLongOption("cluster")
            .RequiredArgument("SERVER")
            .DefaultValue("arnold")
            .StoreResult(&cluster);
        opts.AddLongOption("input")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&input);
        opts.AddLongOption("result")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&result);
        opts.AddLongOption("policy")
            .RequiredArgument("STR")
            .Required()
            .StoreResult(&policyName);
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);

    auto tx = client->StartTransaction(NYT::TStartTransactionOptions().Timeout(TDuration::Seconds(10)));
    {
        NYT::TTempTable tmpDailyStat(tx);
        tx->MapReduce(
            NYT::TMapReduceOperationSpec()
                .AddInput<NRRProto::TPoolEntry>(input)
                .AddOutput<NRRProto::TDailyCrawlStat>(tmpDailyStat.Name())
                .ReduceBy(NYT::TSortColumns("Day", "Zone"))
            , new TDailyStatMap(policyName)
            , new TDailyStatReduce()
            , new TDailyStatReduce()
        );

        TDailyCrawlStatInfo dailyStat;
        auto reader = tx->CreateTableReader<NRRProto::TDailyCrawlStat>(tmpDailyStat.Name());
        for (; reader->IsValid(); reader->Next()) {
            dailyStat[std::make_pair(reader->GetRow().GetDay(), reader->GetRow().GetZone())] = reader->GetRow().GetCount();
        }

        tx->Map(
            NYT::TMapOperationSpec()
                .AddInput<NRRProto::TPoolEntry>(input)
                .AddOutput<NRRProto::TPoolEntry>(result)
            , new TMakeUnbiased(dailyStat, policyName)
        );
    }

    tx->Commit();
    return 0;
}

