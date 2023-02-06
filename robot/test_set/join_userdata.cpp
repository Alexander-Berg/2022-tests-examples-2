#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>
#include <robot/quality/robotrank/rr_factors_calcer/lemur_env.h>

#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/util/temp_table.h>

#include <robot/lemur/algo/kiwi_utils/metadata.h>
#include <robot/lemur/algo/printlib/printlib.h>
#include <robot/lemur/protos/printlib.pb.h>
#include <robot/lemur/protos/schema.pb.h>
#include <robot/lemur/algo/locator/locator.h>

#include <yweb/robot/ukrop/algo/exportparsers/extdatarank_export_parser.h>
#include <yweb/robot/ukrop/fresh/algo/filters/filters.h>

#include <library/cpp/getopt/last_getopt.h>
#include <library/cpp/getopt/modchooser.h>

#include <google/protobuf/messagext.h>

#include <util/folder/path.h>
#include <util/draft/datetime.h>
#include <util/random/random.h>
#include <library/cpp/string_utils/url/url.h>


class TMakeBinaryKey : public NYT::IMapper<NYT::TTableReader<NRRProto::TPoolEntry>, NYT::TTableWriter<NLemurSchema::TBinaryKeyRow>>
{
    void Do(NYT::TTableReader<NRRProto::TPoolEntry>* reader, NYT::TTableWriter<NLemurSchema::TBinaryKeyRow>* writer) override final {
        for (; reader->IsValid(); reader->Next()) {
            auto row = reader->GetRow();
            auto key = NLemur::TBinaryKey::Create(reader->GetRow().GetHost() + reader->GetRow().GetPath(), NLemurLocator::KT_DOC_DEF);
            if (key) {
                NLemurSchema::TBinaryKeyRow result;
                result.SetOwnerKey(key->OwnerKey);
                result.SetHostKey(key->HostKey);
                result.SetUrlKey(key->UrlKey);
                result.SetKeyType(key->KeyType);
                writer->AddRow(result);
            }
        }
    }
};

REGISTER_MAPPER(TMakeBinaryKey);


class TJoinWithUserdata : public NYT::IReducer<NYT::TTableReader<NLemurSchema::TBinaryKeyRow>, NYT::TTableWriter<NRRProto::TPoolEntry>>
{
public:
    const size_t MAX_URL_LENGH = 8192;

    TJoinWithUserdata() = default;

    TJoinWithUserdata(const TString& triggersCfg)
        : TriggersConfPath(triggersCfg)
    {}

    void Start(NYT::TTableWriter<NRRProto::TPoolEntry>*) override final {
        TupleMeta.Reset(new NLemur::TTupleMeta(TriggersConfPath));
        AttrPrinter.Reset(new NLemur::TAttrPrinter(*TupleMeta, false));
    }

    void Do(NYT::TTableReader<NLemurSchema::TBinaryKeyRow>* reader, NYT::TTableWriter<NRRProto::TPoolEntry>* writer) override final {
        bool urlInPool = false;
        for(; reader->IsValid(); reader->Next()) {
            if (reader->GetTableIndex() == 0) {
                urlInPool = true;
            } else if (reader->GetTableIndex() == 1) {
                if (!urlInPool) {
                    continue;
                }

                NLemurPrint::TObject decodedObject;
                AttrPrinter->ParseObject(decodedObject, static_cast<NKwTupleMeta::EKeyType>(reader->GetRow().GetKeyType()), reader->GetRow().GetValue().data(), reader->GetRow().GetValue().size());

                TString url;
                TString userdataHisto;

                NRRProto::TPoolEntry result;

                for (const auto& tuple : decodedObject.GetTuples()) {
                    if (tuple.GetAttrName() == "URL") {
                        TString host, path;
                        SplitUrlToHostAndPath(tuple.GetValue().GetString(), host, path);
                        result.SetHost(host);
                        result.SetPath(path);
                    }
                    if (tuple.GetAttrName() == "UserDataHistogram") {
                        result.MutableUserDataHisto()->CopyFrom(tuple.GetValue().GetUserDataHisto());
                    }
                }
                writer->AddRow(result);
            }
        }
    }

    Y_SAVELOAD_JOB(TriggersConfPath);

private:
    TString TriggersConfPath;

    THolder<NLemur::TTupleMeta> TupleMeta;
    THolder<NLemur::TAttrPrinter> AttrPrinter;
};

REGISTER_REDUCER(TJoinWithUserdata);


int JoinUserdata(int argc, const char** argv) {
    TString cluster;
    TString poolTable;
    TString edrTable;
    TString result;
    auto configs = GetBuildinConfigs();

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
        opts.AddLongOption("userdata")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&edrTable);
        opts.AddLongOption("triggers-config")
            .RequiredArgument("FILE")
            .StoreResult(&configs.TriggersCfgPath);
        opts.AddLongOption("result")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&result);
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);
    auto tx = client->StartTransaction();
    {
        NYT::TTempTable tmpTable(tx);
        TString tmpTableName = tmpTable.Name();
        tx->Map(
            NYT::TMapOperationSpec()
                .AddInput<NRRProto::TPoolEntry>(poolTable)
                .AddOutput<NLemurSchema::TBinaryKeyRow>(tmpTableName)
            , new TMakeBinaryKey()
        );
        tx->Sort(
            NYT::TSortOperationSpec()
                .AddInput(tmpTableName)
                .Output(tmpTableName)
                .SortBy(NYT::TSortColumns("ownerkey", "hostkey", "urlkey", "keytype"))
        );
        tx->Reduce(
            NYT::TReduceOperationSpec()
                .AddInput<NLemurSchema::TBinaryKeyRow>(tmpTableName)
                .AddInput<NLemurSchema::TBinaryKeyRow>(edrTable)
                .AddOutput<NRRProto::TPoolEntry>(result)
                .ReduceBy(NYT::TSortColumns("ownerkey", "hostkey", "urlkey", "keytype"))
                .ReducerSpec(
                    NYT::TUserJobSpec()
                        .AddLocalFile(configs.TriggersCfgPath)
                )
           , new TJoinWithUserdata(TFsPath(configs.TriggersCfgPath).Basename())
        );

        tx->Sort(NYT::TSortOperationSpec()
            .AddInput(result)
            .Output(result)
            .SortBy(NYT::TSortColumns("Host", "Path"))
         );
    }
    tx->Commit();
    return 0;
}
