#include <robot/samovar/protos/direct_data.pb.h>
#include <robot/samovar/protos/factor_dump.pb.h>
#include <robot/lemur/algo/userdata/protos/userdata.pb.h>

#include <robot/samovar/algo/ranks/rank_calcer.h>
#include <robot/samovar/algo/ranks/ranks_calcer.h>

#include <robot/samovar/algo/ranks/compressed_slices.h>
#include <robot/samovar/algo/locator/key.h>

#include <google/protobuf/messagext.h>
#include <mapreduce/yt/interface/client.h>
#include <mapreduce/library/io/proto/proto.h>

#include <library/cpp/getopt/last_getopt.h>
#include <util/string/join.h>

#include <kernel/remap/remap_table.h>
#include <iostream>
#include <fstream>


using namespace NYT;
using namespace NSamovar;
namespace fs = std::filesystem;

class TRemapPredictions: public IMapper<TTableReader<TNode>, TTableWriter<TNode>>
{
private:
    TString RemapFile;
    TRemapTable RemapTable;

public:
    TRemapPredictions() = default;
    TRemapPredictions(const TString remapFile)
        : RemapFile(remapFile){}


    void Start(NYT::TTableWriter<TNode>*) override final {
        TVector<float> values;
        TFileInput in(RemapFile);
        TString val;
        while (in.ReadLine(val)) {
            values.push_back(FromString<float>(val));
        }
        RemapTable = TRemapTable(values.data(), values.size());
    }

    void Do(TTableReader<TNode>* input, TTableWriter<TNode>* output) override {
        for (; input->IsValid(); input->Next()) {
            const auto& row = input->GetRow();
            TNode outrow = row;
            TVector<TString> factors = StringSplitter(row["value"].AsString()).Split('\t');
            double prediction = std::stod(factors[3]);
            double remapedPrediction = RemapTable.Remap(static_cast<float>(prediction));
            outrow["prediction"] = prediction;
            outrow["remaped_prediction"] = remapedPrediction;
            output->AddRow(outrow);
        }
    }

    Y_SAVELOAD_JOB(RemapFile);
};
REGISTER_MAPPER(TRemapPredictions);


int main(int argc, const char* argv[])
{
    Initialize(argc, argv);

    TString cluster;
    TString inputTable;
    TString outputTable;
    TString remap;
    float border;

    {
        NLastGetopt::TOpts opts = NLastGetopt::TOpts::Default();
        opts.AddHelpOption('h');
        opts.AddLongOption("cluster")
            .RequiredArgument("SERVER")
            .DefaultValue("arnold")
            .StoreResult(&cluster);
        opts.AddLongOption("border")
            .DefaultValue(0.1)
            .StoreResult(&border);
        opts.AddLongOption("input")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&inputTable);
        opts.AddLongOption("output")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&outputTable);
        opts.AddLongOption("remap")
            .Required()
            .StoreResult(&remap);

        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);
    auto tx = client->StartTransaction();


    tx->Map(
        TMapOperationSpec()
        .AddInput<TNode>(inputTable)
        .AddOutput<TNode>(outputTable)
        .MapperSpec(NYT::TUserJobSpec()
            .AddLocalFile(remap))
        , new TRemapPredictions(remap));

    tx->Sort(
        TSortOperationSpec()
        .AddInput(outputTable)
        .Output(outputTable)
        .SortBy("remaped_prediction"));

    tx->Commit();
    return 0;
}

