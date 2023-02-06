#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <mapreduce/yt/interface/client.h>

#include <kernel/remap/remap_table.h>

#include <library/cpp/getopt/last_getopt.h>

#include <util/folder/path.h>

class TApplyRemap : public NYT::IMapper<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
public:
    TApplyRemap() = default;
    TApplyRemap(const THashMap<TString, TString>& remap)
        : RemapFiles(remap)
    {
    }

    void Start(NYT::TTableWriter<NRRProto::TPoolEntry>*) override final {
        for (auto remapFile : RemapFiles) {
            TVector<float> values;
            TFileInput in(remapFile.second);
            TString val;
            while (in.ReadLine(val)) {
                values.push_back(FromString<float>(val));
            }
            Remap[remapFile.first] = TRemapTable(values.data(), values.size());
        }
    }

    void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        for (; reader->IsValid(); reader->Next()) {
            auto result = reader->GetRow();
            for (auto& prediction : *result.MutablePredictions()->MutablePredictionItems()) {
                double remapedPrediction = Remap[prediction.GetFormulaName()].Remap(prediction.GetPrediction());
                prediction.SetPrediction(remapedPrediction);
            }
            writer->AddRow(result);
        }
    }

    Y_SAVELOAD_JOB(RemapFiles);

private:
    THashMap<TString, TString> RemapFiles;

    THashMap<TString, TRemapTable> Remap;
};

REGISTER_MAPPER(TApplyRemap);


int ApplyRemap(int argc, const char** argv) {
    NYT::Initialize(argc, argv);
    TString cluster;
    TString fmlName;
    TString remapFile;
    TString pool;
    TString result;

    {
        NLastGetopt::TOpts opts = NLastGetopt::TOpts::Default();
        opts.AddHelpOption('h');
        opts.AddLongOption("cluster")
            .RequiredArgument("SERVER")
            .DefaultValue("arnold")
            .StoreResult(&cluster);
        opts.AddLongOption("fml-name")
            .RequiredArgument("STR")
            .StoreResult(&fmlName)
            .Required();
        opts.AddLongOption("remap-file")
            .RequiredArgument("FILE")
            .StoreResult(&remapFile)
            .Required();
        opts.AddLongOption("predictions")
            .RequiredArgument("TABLE")
            .StoreResult(&pool)
            .Required();
        opts.AddLongOption("result")
            .StoreResult(&result)
            .RequiredArgument("TABLE")
            .Required();
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);

    auto tx = client->StartTransaction();

    {
        THashMap<TString, TString> remap = {std::make_pair(fmlName, TFsPath(remapFile).Basename())};
        tx->Map(
            NYT::TMapOperationSpec()
                .AddInput<NRRProto::TPoolEntry>(pool)
                .AddOutput<NRRProto::TPoolEntry>(NYT::TRichYPath(result).SortedBy(NYT::TSortColumns("Host", "Path")))
                .MapperSpec(NYT::TUserJobSpec()
                    .AddLocalFile(remapFile)
                )
                .Ordered(true)
            , new TApplyRemap(remap)
        );
    }

    tx->Commit();

    return 0;
}
