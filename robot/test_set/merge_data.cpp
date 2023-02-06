#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <robot/quality/robotrank/rr_factors_calcer/lemur_env.h>

#include <yweb/robot/ukrop/algo/robotzones/zoneconfig.h>

#include <library/cpp/getopt/last_getopt.h>

#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/util/temp_table.h>

#include <library/cpp/string_utils/url/url.h>


class TMergeData : public NYT::IReducer<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
public:
    enum class ETableType {
        USERDATA_INFO,
        SEARCH_BASE_INFO,
        FACTORS,
        SPAM_INFO,
        CUSTOM_FACTORS,
        CUSTOM_LABELS,
    };

    TMergeData() = default;

    TMergeData(const TVector<ETableType>& tableTypes)
        : TableTypes(tableTypes)
    {}


    void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        NRRProto::TPoolEntry result;
        for (; reader->IsValid(); reader->Next()) {
            auto tableType = TableTypes[reader->GetTableIndex()];
            const auto row = reader->GetRow();

            switch (tableType) {
                case ETableType::FACTORS: {
                    result.SetHost(row.GetHost());
                    result.SetPath(row.GetPath());
                    result.SetWeight(1.0);
                    result.MutableFactors()->CopyFrom(row.GetFactors());
                    result.MutableCrawlPolicies()->CopyFrom(row.GetCrawlPolicies());
                    result.SetLastAccess(row.GetLastAccess());
                    result.SetHttpCode(row.GetHttpCode());
                    break;
                }
                case ETableType::CUSTOM_FACTORS: {
                    if (!result.HasFactors()) {
                        result.SetHost(row.GetHost());
                        result.SetPath(row.GetPath());
                        result.SetWeight(0.0);
                        result.MutableFactors()->CopyFrom(row.GetFactors());
                    }
                    break;
                }
                case ETableType::USERDATA_INFO: {
                    result.MutableUserDataHisto()->CopyFrom(row.GetUserDataHisto());
                    break;
                }
                case ETableType::SEARCH_BASE_INFO: {
                    result.MutableSearchBaseInfo()->CopyFrom(row.GetSearchBaseInfo());
                    break;
                }
                case ETableType::CUSTOM_LABELS: {
                    result.MutableLabels()->MergeFrom(row.GetLabels());
                }
                case ETableType::SPAM_INFO: {
                    result.MutableSpamInfo()->CopyFrom(row.GetSpamInfo());
                }
            };
        }
        if (result.HasHost()) { // check for factors.
            writer->AddRow(result);
        }
    }

    Y_SAVELOAD_JOB(TableTypes);

private:
    TVector<ETableType> TableTypes;
};

REGISTER_REDUCER(TMergeData);


int MergeData(int argc, const char** argv) {
    TString cluster;
    TString userdataInfoTable;
    TString searchBaseInfoTable;
    TString factorsTable;
    TString spamInfoTable;
    TVector<TString> customSamples;
    TVector<TString> customFactors;
    TString resultTable;

    {
        NLastGetopt::TOpts opts = NLastGetopt::TOpts::Default();
        opts.AddHelpOption('h');
        opts.AddLongOption("cluster")
            .RequiredArgument("SERVER")
            .DefaultValue("arnold")
            .StoreResult(&cluster);
        opts.AddLongOption("userdata-info")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&userdataInfoTable);
        opts.AddLongOption("search-base-info")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&searchBaseInfoTable);
        opts.AddLongOption("spam-info")
            .RequiredArgument("TABLE")
            .StoreResult(&spamInfoTable);
        opts.AddLongOption("factors")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&factorsTable);
        opts.AddLongOption("custom-labels")
            .RequiredArgument("TABLE")
            .AppendTo(&customSamples);
        opts.AddLongOption("custom-factors")
            .RequiredArgument("TABLE")
            .AppendTo(&customFactors);
        opts.AddLongOption("result")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&resultTable);
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);

    auto tx = client->StartTransaction();

    {
        auto spec = NYT::TReduceOperationSpec();

        TVector<TMergeData::ETableType> tableTypes;

        spec.AddInput<NRRProto::TPoolEntry>(factorsTable);
        tableTypes.push_back(TMergeData::ETableType::FACTORS);

        spec.AddInput<NRRProto::TPoolEntry>(userdataInfoTable);
        tableTypes.push_back(TMergeData::ETableType::USERDATA_INFO);

        spec.AddInput<NRRProto::TPoolEntry>(searchBaseInfoTable);
        tableTypes.push_back(TMergeData::ETableType::SEARCH_BASE_INFO);

        if (!spamInfoTable.empty()) {
            spec.AddInput<NRRProto::TPoolEntry>(spamInfoTable);
            tableTypes.push_back(TMergeData::ETableType::SPAM_INFO);
        }

        for (const auto& custom : customSamples) {
            spec.AddInput<NRRProto::TPoolEntry>(custom);
            tableTypes.push_back(TMergeData::ETableType::CUSTOM_LABELS);
        }

        for (const auto& custom : customFactors) {
            spec.AddInput<NRRProto::TPoolEntry>(custom);
            tableTypes.push_back(TMergeData::ETableType::CUSTOM_FACTORS);
        }

        spec.AddOutput<NRRProto::TPoolEntry>(NYT::TRichYPath(resultTable).SortedBy(NYT::TSortColumns("Host", "Path")));

        spec.ReduceBy(NYT::TSortColumns("Host", "Path"));

        tx->Reduce(
            spec,
            new TMergeData(tableTypes)
        );
    }

    tx->Commit();

    return 0;
}
