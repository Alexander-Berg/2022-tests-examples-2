#include <library/cpp/getoptpb/getoptpb.h>
#include <robot/library/yt/static/command.h>
#include <robot/library/yt/tests/recoverable_command_ut/test_mode_params.pb.h>


using namespace NYT;
using namespace NJupiter;

static constexpr auto MetaSavePath = "//tmp/TestMeta";
static constexpr auto InputTableName = "//tmp/TestInput";
static constexpr auto OutputTableName = "//tmp/TestOutput";


class TTestMapper final : public IMapper<TTableReader<TNode>, TTableWriter<TNode>> {
    TString SomeState;
public:
    TTestMapper() = default;
    TTestMapper(TString someState) : SomeState(std::move(someState))
    {
    }

    void Load(IInputStream& stream) override {
        ::Load(&stream, SomeState);
    }

    void Save(IOutputStream& stream) const override {
        ::Save(&stream, SomeState);
    }

    void Do(TTableReader<TNode>* reader, TTableWriter<TNode>* writer) override {
        for (; reader->IsValid(); reader->Next())
            writer->AddRow(reader->GetRow());
    }
};

REGISTER_MAPPER(TTestMapper);

int main(int argc, const char* argv[]) {
    Initialize(argc, argv);
    TTestModeParams opts = NGetoptPb::GetoptPbOrAbort(argc, argv, { .DumpConfig = false });

    auto client = CreateClient(GetEnv("YT_PROXY"));

    auto map = TMapCmd<TTestMapper>(client, new TTestMapper(opts.GetMapperState()))
        .Input<TNode>(InputTableName)
        .Output<TNode>(OutputTableName)
        .OperationWeight(opts.GetOperationWeight())
        .MakeRecoverable(MetaSavePath, GENERATE_TCOMMAND_KEY());

    if (opts.HasYtFile())
        map.AddYtFile(opts.GetYtFile());
    if (opts.HasLocalFile())
        map.AddLocalFile(opts.GetLocalFile());

    auto mapOp = map.DoAsync();
    Endl(Cout << GetGuidAsString(mapOp->GetId()));
    map.Wait();

    auto sort = TSortCmd<TNode>(client)
        .Input<TNode>(OutputTableName)
        .Output<TNode>(OutputTableName)
        .By({"SomeField"})
        .MakeRecoverable(MetaSavePath, "TestKey2");

    auto sortOp = sort.DoAsync();
    Endl(Cout << GetGuidAsString(sortOp->GetId()));
    sort.Wait();

    return 0;
}
