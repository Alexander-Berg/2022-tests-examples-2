#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/util/temp_table.h>

#include <robot/lemur/algo/kiwi_utils/metadata.h>
#include <robot/lemur/algo/printlib/printlib.h>
#include <robot/lemur/protos/printlib.pb.h>
#include <robot/lemur/protos/schema.pb.h>
#include <yweb/robot/ukrop/fresh/algo/filters/filters.h>

#include <library/cpp/getopt/last_getopt.h>
#include <library/cpp/getopt/modchooser.h>

#include <google/protobuf/text_format.h>

#include <util/draft/datetime.h>
#include <util/random/random.h>
#include <library/cpp/string_utils/url/url.h>


class TDnsSpamHostsExtractor : public NYT::IMapper<NYT::TTableReader<NLemurSchema::TBinaryKeyRow>, NYT::TTableWriter<NRRProto::THostEntry>>
{
public:
    TDnsSpamHostsExtractor() = default;

    void Do(NYT::TTableReader<NLemurSchema::TBinaryKeyRow>* reader, NYT::TTableWriter<NRRProto::THostEntry>* writer) override final {
        NLemur::TTupleMeta tupleMeta("triggers.pb.txt");
        NLemur::TAttrPrinter attrPrinter(tupleMeta, false);

        for(; reader->IsValid(); reader->Next()) {
            if (reader->GetRow().GetKeyType() != 10) {
                continue;
            }
            NLemurPrint::TObject decodedObject;
            attrPrinter.ParseObject(decodedObject, static_cast<NKwTupleMeta::EKeyType>(reader->GetRow().GetKeyType()), reader->GetRow().GetValue().data(), reader->GetRow().GetValue().size());
            NRRProto::THostEntry result;
            for (const auto& tuple : decodedObject.GetTuples()) {
                if (tuple.GetAttrName() == "Name") {
                    result.SetHost(tuple.GetValue().GetString());
                }
                if (tuple.GetAttrName() == "IsSpamHostSample") {
                    auto spamLabel = result.MutableLabels()->AddLabelItems();
                    spamLabel->SetName("DnsSpam");
                }
            }
            if (result.GetLabels().LabelItemsSize()) {
                writer->AddRow(result);
            }
        }
    }
};

REGISTER_MAPPER(TDnsSpamHostsExtractor)


class TMergeHostLabels : public NYT::IReducer<NYT::TTableReader<google::protobuf::Message>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
    void Do(NYT::TTableReader<google::protobuf::Message>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        TMaybe<NRRProto::THostEntry> hostEntry;
        for (; reader->IsValid(); reader->Next()) {
            if (reader->GetTableIndex() == 0) {
                hostEntry = reader->GetRow<NRRProto::THostEntry>();
            } else {
                NRRProto::TPoolEntry poolEntry = reader->GetRow<NRRProto::TPoolEntry>();
                if (hostEntry) {
                    for (const auto& label : hostEntry->GetLabels().GetLabelItems()) {
                        auto newLabel  = poolEntry.MutableLabels()->AddLabelItems();
                        newLabel->CopyFrom(label);
                    }
                }
                writer->AddRow(poolEntry);
            }
        }
    }
};

REGISTER_REDUCER(TMergeHostLabels);


int MarkDnsSpam(int argc, const char** argv) {
    TString cluster;
    TString poolTable;
    TString lemurHome;
    TString result;
    TString triggersCfgFile;
    size_t lemurShards;

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
        opts.AddLongOption("lemur-home")
            .RequiredArgument("TABLE")
            .DefaultValue("//home/lemur")
            .StoreResult(&lemurHome);
        opts.AddLongOption("triggers-config")
            .RequiredArgument("FILE")
            .Required()
            .StoreResult(&triggersCfgFile);
        opts.AddLongOption("result")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&result);
        opts.AddLongOption("lemur-shards")
            .RequiredArgument("INT")
            .DefaultValue(128)
            .StoreResult(&lemurShards);
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);
    auto tx = client->StartTransaction();
    {
        NYT::TTempTable tmpTableHost(tx);
        TString tmpTableHostName;
        tmpTableHostName = tmpTableHost.Name();

        NYT::TTempTable tmpTablePool(tx);
        TString tmpTablePoolName;
        tmpTablePoolName = tmpTableHost.Name();

        auto hostSpec =
            NYT::TMapOperationSpec()
                .MapperSpec(NYT::TUserJobSpec()
                    .MemoryLimit(2LL * 1024 * 1024 * 1024)
                    .AddLocalFile(triggersCfgFile)
                )
                .AddOutput<NRRProto::THostEntry>(tmpTableHostName);

        for (size_t tableIdx = 0; tableIdx < lemurShards; ++tableIdx) {
            hostSpec.AddInput<NLemurSchema::TBinaryKeyRow>(Sprintf("%s/data/%08zu/persistent/hostdata", lemurHome.data(), tableIdx));
        }

        client->Map(
            hostSpec
            , new TDnsSpamHostsExtractor()
        );

        tx->Sort(
            NYT::TSortOperationSpec()
                .AddInput(tmpTableHostName)
                .Output(tmpTableHostName)
                .SortBy(NYT::TSortColumns("Host"))
        );

        tx->Sort(
            NYT::TSortOperationSpec()
                .AddInput(poolTable)
                .Output(tmpTablePoolName)
                .SortBy(NYT::TSortColumns("Host"))
        );

        tx->Reduce(
            NYT::TReduceOperationSpec()
                .AddInput<NRRProto::THostEntry>(tmpTableHostName)
                .AddInput<NRRProto::TPoolEntry>(tmpTablePoolName)
                .AddOutput<NRRProto::TPoolEntry>(result)
                .ReduceBy(NYT::TSortColumns("Host"))
                .ReducerSpec(NYT::TUserJobSpec()
                    .AddLocalFile(triggersCfgFile)
                )
            , new TMergeHostLabels()
        );
    }
    tx->Commit();
    return 0;
}
