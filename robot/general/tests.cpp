#include "../args.h"

using namespace NYT;
using namespace NSR;


class TTestsGetter : public IReducer<TTableReader<::google::protobuf::Message>, TTableWriter<TSample>> {
    TVector<TString> Tests;
    TVector<TString> Formulas;

public:
    TTestsGetter() = default;

    TTestsGetter(TVector<TString> tests, TVector<TString> formulas)
        : Tests(std::move(tests)),
          Formulas(std::move(formulas)) {
    }

    Y_SAVELOAD_JOB(Tests, Formulas);

    void Do(TReader *reader, TWriter *writer) final {
        TVector<TSample> samples;
        TVector<ui32> tiers;

        for (; reader->IsValid(); reader->Next()) {
            auto id = reader->GetTableIndex();

            if (id < Tests.size()) {
                const auto &src = reader->GetRow<TSample>();
                TSample dst;

                dst.SetDataset(src.GetDataset());
                dst.SetWeight(src.GetWeight());

                dst.SetTest(Tests[id]);
                samples.push_back(dst);

                continue;
            }
            id -= Tests.size();
            if (id < 2) {
                tiers.resize(Formulas.size(), 2);
                continue;
            }
            id -= 2;
            auto shard = reader->GetRow<TShardedUrl>().GetShard();
            tiers[id] = Min(tiers[id], GetTierId(shard));
        }
        for (auto &dst : samples) {
            for (ui32 id = 0; id < Formulas.size(); ++id) {
                dst.SetFormula(Formulas[id]);

                auto tierId = tiers.empty() ? 3 : tiers[id];
                dst.SetTierId(tierId);

                writer->AddRow(dst);
            }
        }
    }
};

REGISTER_REDUCER(TTestsGetter);


class TTestsCounter : public IReducer<TTableReader<TSample>, TTableWriter<TSample>> {
public:
    TTestsCounter() = default;

    void Do(TReader *reader, TWriter *writer) override {
        auto sample = reader->GetRow();

        double weight = 0;
        for (; reader->IsValid(); reader->Next()) {
            weight += reader->GetRow().GetWeight();
        }
        sample.SetWeight(weight);
        writer->AddRow(sample);
    }
};

REGISTER_REDUCER(TTestsCounter);

namespace NReports {

int Tests(int argc, const char **argv) {
    TArgs args(argc, argv, "ru");
    auto dstTable = args.WorkDir + "/reports/" + args.Label + "/tests";

    auto testsDir = args.WorkDir + "/tests";
    TVector<TString> tests;
    for (const auto &node : args.Client->List(testsDir)) {
        tests.push_back(node.AsString());
    }
    TTempTable temp(args.Client);
    {
        auto spec = TReduceOperationSpec();

        TVector<TString> srcTables;
        for (const auto &test : tests) {
            auto srcTable = testsDir + '/' + test + "/pos_samples";
            srcTables.push_back(srcTable);

            spec.AddInput<TSample>(srcTable);
        }
        TString candidatesDir = args.WorkDir + "/candidates";
        spec.AddInput<TCandidate>(candidatesDir + "/shard_candidates");
        spec.AddInput<TCandidate>(candidatesDir + '/' + args.State);

        auto formulasDir = args.WorkDir + "/formulas";
        TString shardsTable = "selectionrank/" + FAKE_STATE + "/0/shard_urls_without_doc_id";

        for (const auto &formula : args.Formulas) {
            auto srcTable = formulasDir + '/' + formula + '/' + shardsTable;
            srcTables.push_back(srcTable);
            spec.AddInput<TShardedUrl>(srcTable);
        }
        spec.AddOutput<TSample>(temp.Name());
        const TVector<TString> cols = {"Host", "Path"};

        args.Client->Reduce(
            spec.ReduceBy(cols),
            new TTestsGetter(tests, args.Formulas)
        );
    }
    {
        const TVector<TString> cols = {"Formula", "Test", "Dataset", "TierId"};
        args.Sort(temp.Name(), cols);

        args.Client->Reduce(
            TReduceOperationSpec()
                .ReduceBy(cols)
                .SortBy(cols)
                .AddInput<TSample>(temp.Name())
                .AddOutput<TSample>(TRichYPath(dstTable).SortedBy(cols)),
            new TTestsCounter
        );
    }

    return 0;
}

}
