#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>
#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/util/temp_table.h>

#include <robot/lemur/algo/kiwi_utils/metadata.h>
#include <robot/lemur/algo/printlib/printlib.h>
#include <robot/lemur/protos/printlib.pb.h>
#include <robot/lemur/protos/schema.pb.h>
#include <robot/lemur/algo/locator/locator.h>

#include <kernel/hosts/extowner/ext_owner.h>

#include <library/cpp/getopt/last_getopt.h>
#include <library/cpp/resource/resource.h>

#include <library/cpp/string_utils/url/url.h>


class TExtractOwner : public NYT::IMapper<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
public:
    void Start(NYT::TTableWriter<NRRProto::TPoolEntry>*) override {
        TString areasLst = NResource::Find("AreasLst");
        TStringStream stream(areasLst);
        OwnerExtractor.Reset(new TOwnerExtractor(stream));
    }

    void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        for (; reader->IsValid(); reader->Next()) {
            auto result = reader->GetRow();
            result.SetOwner(TString{OwnerExtractor->GetOwner(result.GetHost() + result.GetPath())});
            writer->AddRow(result);
        }
    }

private:
    THolder<TOwnerExtractor> OwnerExtractor;
};

REGISTER_MAPPER(TExtractOwner);


class TRenameOwnerColumnMap : public NYT::IMapper<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
public:
    void Do(NYT::TTableReader<NYT::TNode>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        for (; reader->IsValid(); reader->Next()) {
            NRRProto::TPoolEntry result;
            result.SetOwner(reader->GetRow()["key"].AsString());
            writer->AddRow(result);
        }
    }
};

REGISTER_MAPPER(TRenameOwnerColumnMap);


class TSpamJoin : public NYT::IReducer<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
public:
    void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        bool isSpam = false;
        for (; reader->IsValid(); reader->Next()) {
            if (reader->GetTableIndex() == 0) {
                isSpam = true;
            } else {
                auto result = reader->GetRow();
                if (isSpam) {
                    result.MutableSpamInfo()->SetIsSpamOwner(true);
                }
                writer->AddRow(result);
            }
        }
    }
};

REGISTER_REDUCER(TSpamJoin);


int JoinSpam(int argc, const char** argv) {
    TString cluster;
    TString poolTable;
    TString spamOwnersTable;
    TString result;
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
        opts.AddLongOption("spam-owners")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&spamOwnersTable);
        opts.AddLongOption("result")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&result);
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);
    auto tx = client->StartTransaction();
    {
        NYT::TTempTable tmpPoolWithOwnerTable(tx);
        tx->Map(
            NYT::TMapOperationSpec()
                .AddInput<NRRProto::TPoolEntry>(poolTable)
                .AddOutput<NRRProto::TPoolEntry>(tmpPoolWithOwnerTable.Name())
                .MapperSpec(NYT::TUserJobSpec()
                    .MemoryLimit(2ULL * 1024 * 1024 * 1024)
                )
            , new TExtractOwner()
        );

        tx->Sort(
            NYT::TSortOperationSpec()
                .AddInput(tmpPoolWithOwnerTable.Name())
                .Output(tmpPoolWithOwnerTable.Name())
                .SortBy(NYT::TSortColumns("Owner"))
        );

        NYT::TTempTable tmpWithOwnerColumn(tx);

        tx->Map(
            NYT::TMapOperationSpec()
                .AddInput<NYT::TNode>(spamOwnersTable)
                .AddOutput<NRRProto::TPoolEntry>(NYT::TRichYPath(tmpWithOwnerColumn.Name()).SortedBy(NYT::TSortColumns("Owner")))
                .Ordered(true)
            , new TRenameOwnerColumnMap()
        );

        tx->Reduce(
            NYT::TReduceOperationSpec()
                .AddInput<NRRProto::TPoolEntry>(tmpWithOwnerColumn.Name())
                .AddInput<NRRProto::TPoolEntry>(tmpPoolWithOwnerTable.Name())
                .AddOutput<NRRProto::TPoolEntry>(result)
                .ReduceBy(NYT::TSortColumns("Owner"))
            , new TSpamJoin()
        );

        tx->Sort(
            NYT::TSortOperationSpec()
                .AddInput(result)
                .Output(result)
                .SortBy(NYT::TSortColumns("Host", "Path"))
        );
    }
    tx->Commit();
    return 0;
}
