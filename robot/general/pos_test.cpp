#include "../args.h"

using namespace NYT;
using namespace NSR;


class TGetPosTest : public IMapper<TTableReader<TSample>, TTableWriter<TSample>> {
    TVector<TDataset> Datasets;
    double PosProbability;

public:
    TGetPosTest() = default;

    explicit TGetPosTest(TVector<TDataset> datasets, double posProbability)
        : Datasets(std::move(datasets)),
          PosProbability(posProbability) {
    }

    Y_SAVELOAD_JOB(Datasets, PosProbability);

    void Do(TReader *reader, TWriter *writer) final {
        for (; reader->IsValid(); reader->Next()) {
            auto sample = reader->MoveRow();

            for (const auto &dataset : Datasets) {
                if (dataset.Label == sample.GetDataset() && TryProbability(PosProbability)) {
                    sample.SetZoneId(dataset.ZoneId);
                    writer->AddRow(sample);
                    break;
                }
            }
        }
    }
};

REGISTER_MAPPER(TGetPosTest);


int PosTest(int argc, const char **argv) {
    TArgs args(argc, argv, "relevance");

    TString srcTable = args.WorkDir + "/datasets/" + args.Label + "/pos_samples";
    TString dstTable = args.WorkDir + "/tests/" + args.Label + "/pos_samples";

    ui64 posSamplesCount = args.Client->Get(srcTable + "/@row_count").AsInt64();
    double posProbability = double(POS_SAMPLES_COUNT * 0.1) / posSamplesCount;

    args.Client->Map(
        TMapOperationSpec()
            .AddInput<TSample>(srcTable)
            .AddOutput<TSample>(dstTable),
        new TGetPosTest(args.Datasets, posProbability),
        CommonYTOptions()
    );
    args.Sort(dstTable, {"Host", "Path"});

    return 0;
}
