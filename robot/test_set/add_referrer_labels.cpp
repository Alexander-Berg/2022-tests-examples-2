#include "edr_labels.h"

#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/util/temp_table.h>

#include <robot/lemur/protos/schema.pb.h>
#include <yweb/robot/ukrop/algo/exportparsers/extdatarank_export_parser.h>
#include <yweb/robot/ukrop/fresh/algo/filters/filters.h>

#include <library/cpp/getopt/last_getopt.h>
#include <library/cpp/getopt/modchooser.h>

#include <google/protobuf/messagext.h>

#include <util/draft/datetime.h>
#include <util/random/random.h>
#include <library/cpp/string_utils/url/url.h>
#include <util/folder/path.h>


class TExtractEDRLabels : public NYT::IMapper<NYT::TTableReader<NRRProto::TYamrRow>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
public:
    TExtractEDRLabels(const TString& zoneCfgFileName)
        : ZoneCfgFileName(zoneCfgFileName)
    {}

    TExtractEDRLabels() = default;

    void Start(NYT::TTableWriter<NRRProto::TPoolEntry>*) override final {
        ZoneConfig.Reset(new NUkrop::TZoneConfig(ZoneCfgFileName));
    }

    void Do(NYT::TTableReader<NRRProto::TYamrRow>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        NKiwiWorm::TRecord record;
        TMemoryInput memInput(reader->GetRow().GetValue().data(), reader->GetRow().GetValue().size());

        google::protobuf::io::TCopyingInputStreamAdaptor input(&memInput);
        if (!google::protobuf::io::ParseFromZeroCopyStreamSeq(&record, &input)) {
            ythrow yexception() << "Can't parse NKiwiWorm::TRecord for key " << reader->GetRow().GetKey();
        }

        NUkrop::TEDRSample sample(record, ZoneConfig);

        NRRProto::TPoolEntry result;

        if (sample.RefererUrl.empty() || !sample.AddTime) {
            return;
        }

        result.SetAddTime(*sample.AddTime);

        TString host, path;
        SplitUrlToHostAndPath(sample.RefererUrl, host, path);
        result.SetHost(host);
        result.SetPath(path);

        AddEdrLabels(ZoneConfig, sample, result.MutableLabels());

        writer->AddRow(result);
    }

    Y_SAVELOAD_JOB(ZoneCfgFileName);

private:
    TString ZoneCfgFileName;

    NUkrop::TZoneConfigPtr ZoneConfig;
};

REGISTER_MAPPER(TExtractEDRLabels);


class TJoinWithEdrLabels : public NYT::IReducer<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
public:
    void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        TMaybe<NRRProto::TPoolEntry> result;

        for (; reader->IsValid(); reader->Next()) {
            if (reader->GetTableIndex() == 0) { // Pool row
                result = reader->GetRow();
            } else if (reader->GetTableIndex() == 1 && result && result->GetLastAccess() < reader->GetRow().GetAddTime()) {
                for (const auto& label : reader->GetRow().GetLabels().GetLabelItems()) {
                    auto newLabel = result->MutableLabels()->AddLabelItems();
                    newLabel->CopyFrom(label);
                }
                break;
            }
        }
        if (result) {
            writer->AddRow(*result);
        }
    }
};

REGISTER_REDUCER(TJoinWithEdrLabels);


int AddReferrerLabels(int argc, const char** argv) {
    TString cluster;
    TString poolTable;
    TString edrTable;
    TString result;
    TString zoneCfgFile;

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
        opts.AddLongOption("edr")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&edrTable);
        opts.AddLongOption("zone-config")
            .RequiredArgument("FILE")
            .Required()
            .StoreResult(&zoneCfgFile);
        opts.AddLongOption("result")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&result);
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);
    auto tx = client->StartTransaction();
    {
        NYT::TTempTable tmpEdrLabels(tx);
        tx->Map(
            NYT::TMapOperationSpec()
                .AddInput<NRRProto::TYamrRow>(edrTable)
                .AddOutput<NRRProto::TPoolEntry>(tmpEdrLabels.Name())
                .MapperSpec(NYT::TUserJobSpec()
                    .AddLocalFile(zoneCfgFile)
                )
            , new TExtractEDRLabels(TFsPath(zoneCfgFile).Basename())
        );
        tx->Sort(
           NYT::TSortOperationSpec()
              .AddInput(tmpEdrLabels.Name())
              .Output(tmpEdrLabels.Name())
              .SortBy(NYT::TSortColumns("Host", "Path"))
        );

        NYT::TTempTable tmpSortedInput(tx);

        tx->Sort(
           NYT::TSortOperationSpec()
              .AddInput(poolTable)
              .Output(tmpSortedInput.Name())
              .SortBy(NYT::TSortColumns("Host", "Path"))
        );

        tx->Reduce(
            NYT::TReduceOperationSpec()
                .AddInput<NRRProto::TPoolEntry>(tmpSortedInput.Name())
                .AddInput<NRRProto::TPoolEntry>(tmpEdrLabels.Name())
                .AddOutput<NRRProto::TPoolEntry>(NYT::TRichYPath(result).SortedBy(NYT::TSortColumns("Host", "Path")))
                .ReduceBy(NYT::TSortColumns("Host", "Path"))
            , new TJoinWithEdrLabels()
        );
    }
    tx->Commit();
    return 0;
}
