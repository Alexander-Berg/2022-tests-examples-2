#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <library/cpp/getopt/last_getopt.h>
#include <yweb/robot/ukrop/algo/robotzones/zoneconfig.h>

#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/util/temp_table.h>


class TPassProdHostLimit : public NYT::IReducer<NYT::TTableReader<google::protobuf::Message>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
public:
    TPassProdHostLimit(const TString& policy, const TString& formulaName)
        : Policy(policy)
        , FormulaName(formulaName)
    {}

    TPassProdHostLimit() = default;

    void Do(NYT::TTableReader<google::protobuf::Message>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        THashMap<ui32, double> borders;
        NRRProto::TPoolEntry result;
        THashMap<ui32, double> zonalLimit;
        size_t hostSize = 0;
        for (; reader->IsValid(); reader->Next()) {
            if (reader->GetTableIndex() == 0) {
                for (const auto& border : reader->GetRow<NRRProto::THostBorderInfo>().GetProductionBorders().GetHostBorders()) {
                    if (border.GetPolicyName() == Policy) {
                        borders[border.GetZone()] = border.GetBorder();
                    }
                }
            } else if (reader->GetTableIndex() == 1) {
                ++hostSize;

                if (!result.HasHost()) {
                    result.SetHost(reader->GetRow<NRRProto::TPoolEntry>().GetHost());
                }

                for (const auto& prediction : reader->GetRow<NRRProto::TPoolEntry>().GetPredictions().GetPredictionItems()) {
                    if (prediction.GetFormulaName() != FormulaName) {
                        continue;
                    }
                    if (!borders.contains(prediction.GetZone()) || prediction.GetPrediction() > borders[prediction.GetZone()]) {
                        zonalLimit[prediction.GetZone()] += reader->GetRow<NRRProto::TPoolEntry>().GetWeight();
                    }
                }
            }
        }

        if (hostSize) {
            for (const auto& limit : zonalLimit) {
                auto* newLimit = result.MutableHostInfo()->AddZoneLimitInfo();
                newLimit->SetZone(limit.first);
                newLimit->SetCrawlLimit(limit.second);
            }
            result.MutableHostInfo()->SetUrlCount(hostSize);
            writer->AddRow(result);
        }
    }

    Y_SAVELOAD_JOB(Policy, FormulaName);

private:
    TString Policy;
    TString FormulaName;
};


REGISTER_REDUCER(TPassProdHostLimit);


class TPassProdHostLimitAggregator : public NYT::IReducer<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
public:
    void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        THashMap<ui32, double> zonalLimit;
        NRRProto::TPoolEntry result;
        result.SetHost(reader->GetRow().GetHost());
        result.SetPath("");
        for (; reader->IsValid(); reader->Next()) {
            for (const auto& border : reader->GetRow().GetHostInfo().GetZoneLimitInfo()) {
                zonalLimit[border.GetZone()] += border.GetCrawlLimit();
            }
        }
        for (const auto& limit : zonalLimit) {
            auto* newLimit = result.MutableHostInfo()->AddZoneLimitInfo();
            newLimit->SetZone(limit.first);
            newLimit->SetCrawlLimit(limit.second);
        }
        writer->AddRow(result);
    }
};

REGISTER_REDUCER(TPassProdHostLimitAggregator);


class TCalcHostLimitJoin : public NYT::IReducer<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
public:
    void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        NRRProto::THostInfo hostInfo;
        for (; reader->IsValid(); reader->Next()) {
            if (reader->GetTableIndex() == 0) {
                hostInfo.CopyFrom(reader->GetRow().GetHostInfo());
            } else {
                NRRProto::TPoolEntry result;
                result.CopyFrom(reader->GetRow());
                result.MutableHostInfo()->CopyFrom(hostInfo);
                writer->AddRow(result);
            }
        }
    }
};

REGISTER_REDUCER(TCalcHostLimitJoin);


class TCrawledByPolicy : public NYT::IMapper<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NYT::TNode>> {
public:
    TCrawledByPolicy() = default;

    TCrawledByPolicy(const TString& policy)
        : Policy(policy)
    {}

    void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NYT::TNode>* writer) override final {
        for (; reader->IsValid(); reader->Next()) {
            if (reader->GetRow().GetCrawlPolicies().GetMainPolicy().GetPolicyName() == Policy) {
                writer->AddRow(NYT::TNode()
                    ("Policy", Policy)
                    ("Zone", reader->GetRow().GetCrawlPolicies().GetMainPolicy().GetZone())
                    ("Count", 1.0)
                );
            }
        }
    }
    Y_SAVELOAD_JOB(Policy)

private:
    TString Policy;
};

REGISTER_MAPPER(TCrawledByPolicy);


class TCrawledByPolicyCounter : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>> {
public:
    void Do(NYT::TTableReader<NYT::TNode>* reader, NYT::TTableWriter<NYT::TNode>* writer) override final {
        NYT::TNode result = reader->GetRow();
        double count = 0;
        reader->Next();
        for (; reader->IsValid(); reader->Next()) {
            count += reader->GetRow()["Count"].AsDouble();
        }
        result["Count"] = count;
        writer->AddRow(result);
    }
};

REGISTER_REDUCER(TCrawledByPolicyCounter);


int CalcBorders(int argc, const char** argv) {
    TString cluster;
    TString inputTable;
    TString resultTable;
    TString predictionsTable;
    TString hostBordersTable;
    TString policy;
    TString zoneCfgFile;
    TString formulaName;
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
            .StoreResult(&inputTable);
        opts.AddLongOption("policy")
            .RequiredArgument("STR")
            .Required()
            .StoreResult(&policy);
        opts.AddLongOption("formula-name")
            .RequiredArgument("STR")
            .Required()
            .StoreResult(&formulaName);
        opts.AddLongOption("predictions")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&predictionsTable);
        opts.AddLongOption("host-borders")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&hostBordersTable);
        opts.AddLongOption("result")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&resultTable);
        opts.AddLongOption('z', "zone-config")
            .RequiredArgument("FILE")
            .Required()
            .StoreResult(&zoneCfgFile);
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }
    auto client = NYT::CreateClient(cluster);

    auto tx = client->StartTransaction();

    {
        NYT::TTempTable tmpHostCounters(tx);
        tx->JoinReduce(
            NYT::TJoinReduceOperationSpec()
                .AddInput<NRRProto::THostBorderInfo>(NYT::TRichYPath(hostBordersTable).Foreign(true))
                .AddInput<NRRProto::TPoolEntry>(predictionsTable)
                .AddOutput<NRRProto::TPoolEntry>(NYT::TRichYPath(tmpHostCounters.Name()).SortedBy("Host"))
                .JoinBy(NYT::TSortColumns("Host"))
            , new TPassProdHostLimit(policy, formulaName)
        );

        tx->Reduce(
            NYT::TReduceOperationSpec()
                .AddInput<NRRProto::TPoolEntry>(tmpHostCounters.Name())
                .AddOutput<NRRProto::TPoolEntry>(NYT::TRichYPath(tmpHostCounters.Name()).SortedBy(NYT::TSortColumns("Host", "Path")))
                .ReduceBy(NYT::TSortColumns("Host"))
            , new TPassProdHostLimitAggregator()
        );

        tx->JoinReduce(
            NYT::TJoinReduceOperationSpec()
                .AddInput<NRRProto::TPoolEntry>(NYT::TRichYPath(tmpHostCounters.Name()).Foreign(true))
                .AddInput<NRRProto::TPoolEntry>(inputTable)
                .AddOutput<NRRProto::TPoolEntry>(NYT::TRichYPath(resultTable).SortedBy(NYT::TSortColumns("Host", "Path")))
                .JoinBy(NYT::TSortColumns("Host"))
           , new TCalcHostLimitJoin()
        );

        NYT::TTempTable tmpZonalBorders(tx);
        tx->MapReduce(
            NYT::TMapReduceOperationSpec()
                .AddInput<NRRProto::TPoolEntry>(inputTable)
                .AddOutput<NYT::TNode>(tmpZonalBorders.Name())
                .SortBy(NYT::TSortColumns("Policy", "Zone"))
            , new TCrawledByPolicy(policy)
            , new TCrawledByPolicyCounter()
            , new TCrawledByPolicyCounter()
        );
        NUkrop::TZoneConfig zoneConfig(zoneCfgFile);
        auto reader = tx->CreateTableReader<NYT::TNode>(tmpZonalBorders.Name());
        double border = 0;
        NYT::TNode zonalBorders;

        const double approx = 10;

        for (; reader->IsValid(); reader->Next()) {
            TString zoneName = reader->GetRow()["Zone"].AsString();
            border += reader->GetRow()["Count"].AsDouble() * approx;
            NUkrop::TUkropZoneCode zoneCode;
            Y_VERIFY(zoneConfig.GetZoneDescriptor().GetCodeByName(zoneName, zoneCode));
            zonalBorders["zonal"][zoneName]["border"] = reader->GetRow()["Count"].AsDouble() * approx;
            zonalBorders["zonal"][zoneName]["zone_code"] = zoneCode;
        }

        zonalBorders["global_border"] = border;
        NYT::TNode poolInfo;
        poolInfo["global_border"] = border; // for compatibility
        poolInfo["borders"] = zonalBorders;

        tx->Set(resultTable + "/@pool_info", poolInfo);
    }

    tx->Commit();

    return 0;
}
