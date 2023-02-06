#include "test_sr_formula.h"

#include <robot/jupiter/library/opt/common/common.h>
#include <robot/jupiter/library/opt/mropt.h>
#include <robot/jupiter/library/opt/selectionrank.h>

#include <robot/jupiter/library/tables/duplicates.h>
#include <robot/jupiter/library/tables/selectionrank.h>

#include <robot/library/yt/static/command.h>

#include <kernel/urlnorm/normalize.h>
#include <kernel/erfcreator/canonizers.h>
#include <kernel/erfcreator/config.h>
#include <mapreduce/yt/interface/client.h>

#include <util/folder/path.h>
#include <util/generic/maybe.h>
#include <util/generic/size_literals.h>
#include <util/ysaveload.h>

namespace {
    using namespace NJupiter;

    using ::google::protobuf::Message;

    class TCanonizeSRTestUrlsReducer: public NYT::IReducer<NYT::TTableReader<Message>, NYT::TTableWriter<TSRTestUrl>> {
    private:
        enum ESourceTables {
            DuplicatesTable = 0,
            SRTestListTable = 1
        };

    public:
        void Do(NYT::TTableReader<Message>* input, NYT::TTableWriter<TSRTestUrl>* output) final {
            TMaybe<std::tuple<TString, TString>> mainUrlInfo;

            for (; input->IsValid(); input->Next()) {
                switch (input->GetTableIndex()) {
                    case DuplicatesTable:
                        {
                            mainUrlInfo.ConstructInPlace(
                                input->GetRow<TDuplicateInfo>().GetMainHost(),
                                input->GetRow<TDuplicateInfo>().GetMainPath());
                        }
                        break;
                    case SRTestListTable:
                        {
                            TSRTestUrl testUrl = input->GetRow<TSRTestUrl>();
                            if (mainUrlInfo) {
                                testUrl.SetHost(std::get<0>(*mainUrlInfo));
                                testUrl.SetPath(std::get<1>(*mainUrlInfo));
                            }
                            output->AddRow(testUrl);
                        }
                        break;
                }
            }
        }
    };

    REGISTER_REDUCER(TCanonizeSRTestUrlsReducer);

    class TCanonizeSRTestUrlsMapper: public NYT::IMapper<NYT::TTableReader<TDuplicateInfo>, NYT::TTableWriter<TSRTestUrl>> {
    private:
        THashMap<TString, TString> Urls;

    public:
        TCanonizeSRTestUrlsMapper() {
        }

        TCanonizeSRTestUrlsMapper(const THashMap<TString, TString>& urls)
            : Urls(urls)
        {
        }

        void Save(IOutputStream& stream) const override {
            Y_ENSURE(Urls.size() > 0, "Need urls to canonize");
            ::Save(&stream, Urls);
        }

        void Load(IInputStream& stream) override {
            ::Load(&stream, Urls);
        }

        void Do(NYT::TTableReader<TDuplicateInfo>* input, NYT::TTableWriter<TSRTestUrl>* output) final {
            for (; input->IsValid(); input->Next()) {
                TDuplicateInfo dupInfo = input->GetRow();
                auto urlsPtr = Urls.find(dupInfo.GetHost() + dupInfo.GetPath());
                if (urlsPtr != Urls.end()) {
                    TSRTestUrl srTestUrl;
                    srTestUrl.SetHost(dupInfo.GetMainHost());
                    srTestUrl.SetPath(dupInfo.GetMainPath());
                    srTestUrl.SetOriginalUrl(urlsPtr->second);
                    output->AddRow(srTestUrl);
                }
            }
        }
    };

    REGISTER_MAPPER(TCanonizeSRTestUrlsMapper);

    class TGatherSRInfoReducer: public NYT::IReducer<NYT::TTableReader<Message>, NYT::TTableWriter<TSRTestUrl>> {
    private:
        enum ESourceTables {
            SRTestListTable = 0,
            UrlToShardTables,
        };

    public:
        void Do(NYT::TTableReader<Message>* input, NYT::TTableWriter<TSRTestUrl>* output) final {
            TMaybe<TSRTestUrl> srTestUrl;

            for (; input->IsValid(); input->Next()) {
                switch (input->GetTableIndex()) {
                    case SRTestListTable:
                        {
                            srTestUrl = input->GetRow<TSRTestUrl>();
                        }
                        break;
                    default:
                        {
                            if (srTestUrl) {
                                TUrlToShard rec = input->GetRow<TUrlToShard>();
                                srTestUrl->SetShard(rec.GetShard());
                                srTestUrl->SetDocId(rec.GetDocId());
                                srTestUrl->SetCumulativeDocSize(rec.GetCumulativeDocSize());
                                output->AddRow(*srTestUrl);
                            }
                        }
                        break;
                }
            }
        }
    };

    REGISTER_REDUCER(TGatherSRInfoReducer);

    void TestSRFormula(const TMrOpts& mrOpts, const TCommonOpts& commonOpts, const TSelectionRankOpts& selectionRankOpts) {
        auto client = NYT::CreateClient(mrOpts.ServerName);

        TSelectionRankTables selectionrankTables(client, commonOpts.MrPrefix, commonOpts.CurrentState, commonOpts.BucketsCount);

        TDuplicatesTables duplicatesTables(client, commonOpts.MrPrefix, commonOpts.CurrentState);

        THashMap<TString, TString> urls;
        TFsPath urls_cache = "urls.cache";
        if (urls_cache.Exists()) {
            TIFStream reader(urls_cache);
            ::Load(&reader, urls);
        } else {
            TIFStream reader(selectionRankOpts.SRTestUrls);

            TErfCreateConfig ErfConfig;

            ErfConfig.UseMappedMirrors = true;
            ErfConfig.Mirrors = ".";

            TCanonizers Canonizers;
            auto mirrorResolver = GetMirrorResolver(ErfConfig);
            Canonizers.InitCanonizers(mirrorResolver, new TFakeMirrorHostCanonizer());

            TString line;
            while (reader.ReadLine(line)) {
                TString url = StripInPlace(line);
                TStringBuf hostBuf;
                TStringBuf pathBuf;
                SplitUrlToHostAndPath(url, hostBuf, pathBuf);
                TString host = Canonizers.MirrorCanonizer->CanonizeMirrors(
                    TString{GetSchemeHostAndPort(hostBuf,  /*trimHttp=*/true, /*trimDefaultPort=*/false)}
                );

                TString normalizedUrl;

                size_t prefixSize = GetSchemePrefixSize(host);
                if (prefixSize == 0) {
                    host = NUrlNorm::DEFAULT_SCHEME + host;
                }

                Y_ENSURE(NUrlNorm::NormalizeUrl(host + TString{pathBuf}, normalizedUrl), "Failed to normalize url: " << url);
                urls.emplace(normalizedUrl, url);
            }
            TFileOutput output(urls_cache);
            ::Save(&output, urls);
        }

        TMapCmd<TCanonizeSRTestUrlsMapper>(client, new TCanonizeSRTestUrlsMapper(urls))
            .Input(duplicatesTables.GetDuplicatesTable())
            .Output(selectionrankTables.GetSRTestUrlsCanonizedTable())
            .OperationWeight(commonOpts.OperationWeight)
            .MemoryLimit(4_GBs)
            .MakeRecoverable(selectionrankTables.GetRecoverableCmdMetaPath(), GENERATE_TCOMMAND_KEY())
            .Do();

        SortCmd(client, selectionrankTables.GetSRTestUrlsCanonizedTable())
            .By({"Host", "Path"})
            .OperationWeight(commonOpts.OperationWeight)
            .MakeRecoverable(selectionrankTables.GetRecoverableCmdMetaPath(), GENERATE_TCOMMAND_KEY())
            .Do();

        TReduceCmd<TGatherSRInfoReducer>(client)
            .Input(selectionrankTables.GetSRTestUrlsCanonizedTable())
            .Inputs(selectionrankTables.GetUrlToShardTables())
            .Output(selectionrankTables.GetSRTestUrlsTable().AsSortedOutput())
            .ReduceBy({"Host", "Path"})
            .OperationWeight(commonOpts.OperationWeight)
            .MakeRecoverable(selectionrankTables.GetRecoverableCmdMetaPath(), GENERATE_TCOMMAND_KEY())
            .Do();
    }


} // namespace

namespace NJupiter {

    int TestSRFormula(int argc, const char* argv[]) {
        TCmdParams params;

        TMrOpts mrOpts;
        TMrOptsParser(params, mrOpts)
            .AddServerName();

        TCommonOpts commonOpts;
        TCommonOptsParser(params, commonOpts)
            .AddMrPrefix()
            .AddCurrentState()
            .AddOperationWeight()
            .AddBucketsCount();

        TSelectionRankOpts selectionRankOpts;
        TSelectionRankOptsParser(params, selectionRankOpts)
            .AddSRTestUrls();

        params.Parse(argc, argv);

        ::TestSRFormula(mrOpts, commonOpts, selectionRankOpts);

        return 0;
    }

} // namespace NJupiter
