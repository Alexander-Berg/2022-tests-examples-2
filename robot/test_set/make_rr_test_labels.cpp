#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <robot/quality/robotrank/rr_factors_calcer/lemur_env.h>

#include <yweb/robot/ukrop/algo/robotzones/zoneconfig.h>

#include <google/protobuf/text_format.h>
#include <library/cpp/getopt/last_getopt.h>
#include <library/cpp/json/json_reader.h>
#include <library/cpp/resource/resource.h>

#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/util/temp_table.h>

#include <library/cpp/string_utils/url/url.h>
#include <util/stream/file.h>
#include <util/generic/hash_set.h>

class TMakeRRTestPoolLabels : public NYT::IMapper<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
public:
    TMakeRRTestPoolLabels(const TString& labelCfgFile) : LabelConfigFileName(labelCfgFile) {
    }

    TMakeRRTestPoolLabels() = default;

    void Start(NYT::TTableWriter<NRRProto::TPoolEntry>*) override final {

        if (LabelConfigFileName.length()){
            TFileInput input(LabelConfigFileName);
            const TString& data = input.ReadAll();
            if (!NJson::ReadJsonTree(data, &LabelConfig)) {
                throw yexception() << "Saved json data is corrupted";
            }
            NZoneConfig::TZoneConfig zoneProtoConfig;
            if (!google::protobuf::TextFormat::ParseFromString(
                NResource::Find("ZonesCfg"), &zoneProtoConfig)) {
                Y_FAIL("Failed to parse zone config from text protobuf");
            }

            NUkrop::TZoneConfig zoneConfig(zoneProtoConfig);

            NUkrop::TZD zoneDescriptor = zoneConfig.GetZoneDescriptor();
            auto codeToZone = zoneConfig.GetCountryCodeToZone();

            for (auto it = codeToZone.begin(); it != codeToZone.end(); ++it) {
                CodeToStr[it->first] = zoneDescriptor.GetNameByCode(it->second);
            }
        }
    }

    void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        for (; reader->IsValid(); reader->Next()) {
            NRRProto::TPoolEntry result;
            result.SetHost(reader->GetRow().GetHost());
            result.SetPath(reader->GetRow().GetPath());
            result.SetWeight(reader->GetRow().GetWeight());
            result.MutableFactors()->CopyFrom(reader->GetRow().GetFactors());
            result.MutableLabels()->CopyFrom(reader->GetRow().GetLabels());
            result.MutableHostInfo()->CopyFrom(reader->GetRow().GetHostInfo());
            AddUserDataLabels(reader->GetRow(), result.MutableLabels());
            AddSearchBaseLabels(reader->GetRow(), result.MutableLabels());
            AddSpamLabels(reader->GetRow(), result.MutableLabels());
            AddHttpLabel(reader->GetRow(), result.MutableLabels());
            if (LabelConfigFileName.length()) {
                AddZoneLogLabels(reader->GetRow(), result.MutableLabels());
            }
            writer->AddRow(result);
        }
    }

    Y_SAVELOAD_JOB(LabelConfigFileName);

private:
    void AddUserDataLabels(const NRRProto::TPoolEntry& poolRow, NRRProto::TLabels* labels) {
        bool hasAnyUserData = false;
        bool hasShows  = false;
        bool hasClicks = false;
        for (const auto& dailyInfo : poolRow.GetUserDataHisto().GetDateHistoRec()) {
            if (dailyInfo.GetDate() < poolRow.GetLastAccess()) {
                continue;
            }
            if (dailyInfo.LogCountersSize()) {
                hasAnyUserData = true;
            }
            for (const auto& logCounter : dailyInfo.GetLogCounters()) {
                if (logCounter.GetLogType() == NLemurUserData::LCT_YANDEX_WEB_SHOWS) {
                    hasShows = true;
                }
                if (logCounter.GetLogType() == NLemurUserData::LCT_YANDEX_WEB_CLICKS) {
                    hasClicks = true;
                }
            }
        }

        if (hasAnyUserData) {
            auto label = labels->AddLabelItems();
            label->SetName("HasNewUserdataSinceCrawl");
        }

        if (hasShows) {
            auto label = labels->AddLabelItems();
            label->SetName("HasShows");
        }

        if (hasClicks) {
            auto label = labels->AddLabelItems();
            label->SetName("HasClicks");
        }
    }


    void AddHttpLabel(const NRRProto::TPoolEntry& poolRow, NRRProto::TLabels* labels) {
        const auto& oldHttpCode = poolRow.GetFactors().GetInfo().GetHttpCode();
        const auto& newHttpCode = poolRow.GetHttpCode();
        int changed = 0;
        if (oldHttpCode && oldHttpCode >= 400 && newHttpCode == 200){
            auto label = labels->AddLabelItems();
            changed = 1;
            label->SetName("ChangedHttpToGood");
        }
        const auto& searchBaseInfo = poolRow.GetSearchBaseInfo();
        if (searchBaseInfo.GetIsSearchable() && changed){
            auto label = labels->AddLabelItems();
            label->SetName("ChangedHttpToGoodSearchable");
        }
    }


    void AddSearchBaseLabels(const NRRProto::TPoolEntry& poolRow, NRRProto::TLabels* labels) {
        const auto& searchBaseInfo = poolRow.GetSearchBaseInfo();
        if (searchBaseInfo.GetIsSearchable()) {
            auto label = labels->AddLabelItems();
            label->SetName("Searchable");
        }
        if (searchBaseInfo.GetIsMain()) {
            auto label = labels->AddLabelItems();
            label->SetName("MainInGroup");
        }
        if (searchBaseInfo.GetDupGroupSize() == 1) {
            auto label = labels->AddLabelItems();
            label->SetName("NewGroup");
        }
        if (searchBaseInfo.GetIsSearchable() && searchBaseInfo.GetIsMain()) {
            auto label = labels->AddLabelItems();
            label->SetName("SearchableMainInGroup");
        }
        if (searchBaseInfo.GetIsSearchable() && searchBaseInfo.GetDupGroupSize() == 1) {
            auto label = labels->AddLabelItems();
            label->SetName("SearchableNewGroup");
        }
        if (searchBaseInfo.GetInBase() && !searchBaseInfo.GetIsMain()) {
            auto label = labels->AddLabelItems();
            label->SetName("IsDup");
        }
        if (searchBaseInfo.GetInBase()) {
            auto label = labels->AddLabelItems();
            label->SetName("InBase");
        }
    }

    void AddSpamLabels(const NRRProto::TPoolEntry& poolRow, NRRProto::TLabels* labels) {
        if (poolRow.GetSpamInfo().GetIsSpamOwner()) {
            auto label = labels->AddLabelItems();
            label->SetName("SpamOwner");

            bool hasShows = false;
            for (const auto& label : labels->GetLabelItems()) {
                if (label.GetName() == "HasShows") {
                    hasShows = true;
                    break;
                }
            }
            if (hasShows) {
                auto label = labels->AddLabelItems();
                label->SetName("HasShowsSpamOwner");
            }
        }
    }
    void AddZoneLogLabels(const NRRProto::TPoolEntry& poolRow, NRRProto::TLabels* labels) {
        THashMap<TString, THashSet<TString>> logZones;
        auto logDescriptor = NLemurUserData::ELogCounterType_descriptor();
        for (const auto& dailyInfo : poolRow.GetUserDataHisto().GetDateHistoRec()) {
            for (const auto& logCounter : dailyInfo.GetLogCounters()) {
                TString countryCode, logType;

                if (logCounter.HasCountryCode()) {
                    countryCode = CodeToStr[logCounter.GetCountryCode()];
                }
                else {
                    countryCode = "";
                }

                logType = logDescriptor->FindValueByNumber(logCounter.GetLogType())->name();

                logZones[logType].insert(countryCode);
            }
        }
        for (auto& label : LabelConfig["labels"].GetArray()) {
            TString curLog = label["log"].GetString();

            if (label.Has("zones")) {
                for (auto& zone : label["zones"].GetArray()) {
                    if (logZones.contains(curLog) && logZones[curLog].count(zone.GetString())) {
                        auto addedLabel = labels->AddLabelItems();
                        addedLabel->SetName(label["name"].GetString());
                        break;
                    }
                }
            }
            else {
                if (logZones.contains(curLog)) {
                    auto addedLabel = labels->AddLabelItems();
                    addedLabel->SetName(label["name"].GetString());
                }
            }
        }
    }

private:
    THashMap<TString, TString> CodeToStr;
    TString LabelConfigFileName;
    NJson::TJsonValue LabelConfig;
};

REGISTER_MAPPER(TMakeRRTestPoolLabels);


class TCalcLabelsStatMap : public NYT::IMapper<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NYT::TNode>> {
     void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NYT::TNode>* writer) override final {
         for (; reader->IsValid(); reader->Next()) {
            for (const auto& label : reader->GetRow().GetLabels().GetLabelItems()) {
                writer->AddRow(NYT::TNode()
                    ("Label", label.GetName())
                    ("Count", 1.0)
                );
            }
         }
     }
};

REGISTER_MAPPER(TCalcLabelsStatMap);


class TCalcLabelsStatAggregator : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>> {
     void Do(NYT::TTableReader<NYT::TNode>* reader, NYT::TTableWriter<NYT::TNode>* writer) override final {
         TString label = reader->GetRow()["Label"].AsString();
         double count = 0;
         for (; reader->IsValid(); reader->Next()) {
             count += reader->GetRow()["Count"].AsDouble();
         }
         writer->AddRow(NYT::TNode()
            ("Label", label)
            ("Count", count)
         );
     }
};

REGISTER_REDUCER(TCalcLabelsStatAggregator);


class TUniqHostReduce : public NYT::IReducer<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
    void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        writer->AddRow(reader->GetRow());
        return;
    }
};

REGISTER_REDUCER(TUniqHostReduce);


int MakeRRTestPoolLabels(int argc, const char** argv) {
    TString cluster;
    TString poolTable;
    TString resultTable;
    TString labelConfigFile;
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
        opts.AddLongOption("userdata-labels")
            .RequiredArgument("JSON FILE")
            .Optional()
            .StoreResult(&labelConfigFile);
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);

    auto tx = client->StartTransaction();

    {
        TString basename;
        auto mapperSpec = NYT::TUserJobSpec();
        if (labelConfigFile.length()) {
            mapperSpec.AddLocalFile(labelConfigFile);
            basename = TFsPath(labelConfigFile).Basename();
        }

        tx->Map(
            NYT::TMapOperationSpec()
                .AddInput<NRRProto::TPoolEntry>(poolTable)
                .MapperSpec(mapperSpec)
                .AddOutput<NRRProto::TPoolEntry>(NYT::TRichYPath(resultTable).SortedBy(NYT::TSortColumns("Host", "Path")))
                .Ordered(true)
            , new TMakeRRTestPoolLabels(basename)
        );

        NYT::TTempTable tmpHosts(tx);
        tx->MapReduce(
            NYT::TMapReduceOperationSpec()
                .AddInput<NRRProto::TPoolEntry>(NYT::TRichYPath(resultTable).Columns(NYT::TSortColumns("Host")))
                .AddOutput<NRRProto::TPoolEntry>(tmpHosts.Name())
                .ReduceBy(NYT::TSortColumns("Host"))
            , nullptr
            , new TUniqHostReduce()
            , new TUniqHostReduce()
        );

        NYT::TTempTable tmpLabelsStat(tx);
        tx->MapReduce(
            NYT::TMapReduceOperationSpec()
                .AddInput<NRRProto::TPoolEntry>(resultTable)
                .AddOutput<NYT::TNode>(tmpLabelsStat.Name())
                .ReduceBy(NYT::TSortColumns("Label"))
            , new TCalcLabelsStatMap()
            , new TCalcLabelsStatAggregator()
            , new TCalcLabelsStatAggregator()
        );

        NYT::TNode labelsCount;

        auto labelsCountReader = tx->CreateTableReader<NYT::TNode>(tmpLabelsStat.Name());

        for (; labelsCountReader->IsValid(); labelsCountReader->Next()) {
            labelsCount[labelsCountReader->GetRow()["Label"].AsString()] = labelsCountReader->GetRow()["Count"].AsDouble();
        }

        double hostsCount = static_cast<double>(tx->Get(tmpHosts.Name() + "/@row_count").AsInt64());
        labelsCount["HostDiversity"] = hostsCount;

        NYT::TNode poolInfo = tx->Get(poolTable + "/@pool_info");
        poolInfo["labels_count"] = labelsCount;

        tx->Set(resultTable + "/@pool_info", poolInfo);
    }

    tx->Commit();

    return 0;
}
