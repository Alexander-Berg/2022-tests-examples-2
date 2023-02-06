#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>
#include <robot/quality/robotrank/rr_factors_calcer/lemur_env.h>

#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/util/temp_table.h>

#include <robot/lemur/algo/kiwi_utils/metadata.h>
#include <robot/lemur/algo/printlib/printlib.h>
#include <robot/lemur/protos/printlib.pb.h>
#include <robot/lemur/protos/schema.pb.h>
#include <yweb/robot/ukrop/fresh/algo/filters/filters.h>
#include <yweb/robot/ukrop/fresh/info_states/host_borders_state.h>

#include <library/cpp/getopt/last_getopt.h>
#include <library/cpp/getopt/modchooser.h>

#include <google/protobuf/text_format.h>

#include <util/draft/datetime.h>
#include <util/random/random.h>
#include <library/cpp/string_utils/url/url.h>


class TFetchPolicyBorder : public NYT::IMapper<NYT::TTableReader<NLemurSchema::TBinaryKeyRow>, NYT::TTableWriter<NRRProto::THostBorderInfo>>
{
public:
    TFetchPolicyBorder(const TString& policy)
        : Policy(policy)
    {}

    TFetchPolicyBorder() = default;

    void Do(NYT::TTableReader<NLemurSchema::TBinaryKeyRow>* reader, NYT::TTableWriter<NRRProto::THostBorderInfo>* writer) override final {
        TLemurEnv lemurEnv(GetBuildinConfigs(), nullptr);

        for (; reader->IsValid(); reader->Next()) {
            NUkrop::TUkropObject hostObj(reader->GetRow().GetValue());
            TString host = hostObj.GetAttr(TUCA::Name, 0)->GetValue<TString>();
            TFastUkropObject<TRemap> hostFast(lemurEnv.Remap.Get(), 10, host, hostObj, 0);
            auto bordersInfo = hostFast.GetInfoState<THostBordersInfoState>(lemurEnv.PolicyConfig->GetHostLimitCoeff());

            if (bordersInfo == nullptr) {
                continue;
            }

            auto borders = bordersInfo->GetBorders();

            NRRProto::THostBorderInfo result;
            result.SetHost(host);

            NUkrop::TPolicyInfos policyInfos;

            if (Policy == "any") {
                policyInfos = lemurEnv.PolicyConfig->GetPolicyInfos();
            }
            else {
                ui32 id = lemurEnv.PolicyConfig->GetPolicyId(Policy);
                policyInfos = TMap<ui32, TAtomicSharedPtr<TPolicyInfo>> {{id, lemurEnv.PolicyConfig->GetPolicyInfos().at(id)}};
            }

            for (auto zone : lemurEnv.PolicyConfig->GetZoneDescriptor().GetAllRobotZones()) {
                for (auto& [id, policyInfo] : policyInfos) {
                    TPackedPolicyLabel label(id, zone);
                    auto policyBorderIt = borders.find(label.GetPack());
                    if (policyBorderIt != borders.end()) {
                        auto borderValue = result.MutableProductionBorders()->AddHostBorders();
                        borderValue->SetPolicyName(policyInfo->Name);
                        borderValue->SetPolicyId(id);
                        borderValue->SetZone(zone);
                        borderValue->SetBorder(policyBorderIt->second);
                    }
                }
             }

             if (result.GetProductionBorders().HostBordersSize()) {
                writer->AddRow(result);
             }
        }
    }

    Y_SAVELOAD_JOB(Policy);

private:
    TString Policy;
};

REGISTER_MAPPER(TFetchPolicyBorder)


int FetchHostBorders(int argc, const char** argv) {
    TString cluster;
    TString lemurHome;
    TString result;
    TString policy;
    size_t lemurShards;

    {
        NLastGetopt::TOpts opts = NLastGetopt::TOpts::Default();
        opts.AddHelpOption('h');
        opts.AddLongOption("cluster")
            .RequiredArgument("SERVER")
            .DefaultValue("arnold")
            .StoreResult(&cluster);
        opts.AddLongOption("lemur-home")
            .RequiredArgument("TABLE")
            .DefaultValue("//home/lemur")
            .StoreResult(&lemurHome);
        opts.AddLongOption("result")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&result);
        opts.AddLongOption("policy")
            .RequiredArgument("STR")
            .Required()
            .StoreResult(&policy);
        opts.AddLongOption("lemur-shards")
            .RequiredArgument("INT")
            .DefaultValue(128)
            .StoreResult(&lemurShards);
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);
    auto tx = client->StartTransaction();

    {
        auto hostSpec =
            NYT::TMapOperationSpec()
                .MapperSpec(NYT::TUserJobSpec()
                    .MemoryLimit(4LL * 1024 * 1024 * 1024)
                )
                .AddOutput<NRRProto::THostBorderInfo>(result);

        for (size_t tableIdx = 0; tableIdx < lemurShards; ++tableIdx) {
            hostSpec.AddInput<NLemurSchema::TBinaryKeyRow>(Sprintf("%s/data/%08zu/persistent/hostdata", lemurHome.data(), tableIdx));
        }

        tx->Map(
            hostSpec,
            new TFetchPolicyBorder(policy)
        );

        tx->Sort(
            NYT::TSortOperationSpec()
                .AddInput(result)
                .Output(result)
                .SortBy(NYT::TSortColumns("Host"))
        );
    }
    tx->Commit();
    return 0;
}
