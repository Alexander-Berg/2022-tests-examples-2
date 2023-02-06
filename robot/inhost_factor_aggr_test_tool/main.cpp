#include <quality/neural_net/train_pools/collect_dwelltime_pool/protos/pool_scheme.pb.h>
#include <robot/samovar/protos/factors.pb.h>

#include <yweb/robot/url_aggregators/ptree_aggregator/url_tokenization.h>

#include <robot/samovar/algo/inhost_factor_aggr/inhost_tree_builder.h>
#include <robot/samovar/algo/inhost_factor_aggr/inhost_factor_calcer.h>
#include <robot/samovar/algo/clientlib/clientlib.h>
#include <robot/samovar/algo/ranks/compressed_slices.h>
#include <robot/samovar/algo/record/complex_attrs/inhost_partitions_state/inhost_partitions_state.h>
#include <robot/samovar/protos/factor_dump.pb.h>
#include <robot/mercury/protos/factors_dump.pb.h>
#include <robot/jupiter/protos/sr_learn.pb.h>

#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/util/ypath_join.h>

#include <yt/yt/core/misc/shutdown.h>

#include <util/draft/date.h>
#include <util/folder/dirut.h>
#include <util/generic/adaptor.h>
#include <util/generic/hash.h>
#include <util/random/fast.h>
#include <util/string/vector.h>

#include <library/cpp/getopt/last_getopt.h>
#include <library/cpp/getopt/modchooser.h>
#include <library/cpp/string_utils/url/url.h>
#include <library/cpp/protobuf/util/pb_io.h>

#include <kernel/urlnorm/normalize.h>

namespace {
    const TString SERPS_DAILY_SUFFIX = ".serps";
    const size_t MONSTER_SAMPLING_BUCKETS_COUNT = 100;
    THashMap<TString, TUrlTokenization> TokenizationCache;
    THashMap<TString, THashSet<TString>> AllTokensCache;
    const size_t SIMPLE_FACTORS_CALC_COUNT = 26 * 2 + 18 * 4;
    const size_t BOILER_DEFAULT_CHUNK_SIZE = 1000000;

    ui64 GetDocumentMaxDwelltime(const NCollectDwellTimePool::TSerp::TDocumentList::TDocument& document) {
        ui64 result = 0;
        for (size_t idx = 0; idx < document.ClickSize(); ++idx) {
            result = Max(result, document.GetClick(idx).GetDwellTime());
        }
        return result;
    }
};

class TMapCollectShowsClicks : public NYT::IMapper<NYT::TTableReader<NCollectDwellTimePool::TSerp>, NYT::TTableWriter<NYT::TNode>> {
public:
    void Do(NYT::TTableReader<NCollectDwellTimePool::TSerp>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        for (; input->IsValid(); input->Next()) {
            const auto& serp = input->GetRow();
            for (size_t documentIndex = 0; documentIndex < serp.GetDocumentList().DocumentSize(); ++documentIndex) {
                const NCollectDwellTimePool::TSerp::TDocumentList::TDocument& document = serp.GetDocumentList().GetDocument(documentIndex);
                TString url = document.GetUrl();
                if (!url.empty()) {
                    ui64 maxDt = GetDocumentMaxDwelltime(document);
                    NYT::TNode outRow = NYT::TNode::CreateMap();
                    Y_ENSURE(GetSchemePrefixSize(url) > 0);
                    outRow["url"] = url;
                    outRow["shows"] = 1ULL;
                    if (maxDt > 0) {
                        outRow["clicks"] = 1ULL;
                    } else {
                        outRow["clicks"] = 0ULL;
                    }
                    output->AddRow(outRow);
                }
            }
        }
    }
};
REGISTER_MAPPER(TMapCollectShowsClicks);

class TReduceSumShowsClicks
    : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{
public:
    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        TString url;
        ui64 shows = 0;
        ui64 clicks = 0;
        {
            url = input->GetRow()["url"].AsString();
        }
        for (; input->IsValid(); input->Next()) {
            auto inRow = input->GetRow().AsMap();
            Y_ENSURE(inRow["url"].AsString() == url);
            shows += inRow["shows"].AsUint64();
            clicks += inRow["clicks"].AsUint64();
        }
        {
            NYT::TNode outRow = NYT::TNode::CreateMap();
            outRow["url"] = url;
            outRow["shows"] = shows;
            outRow["clicks"] = clicks;
            output->AddRow(outRow);
        }
    }
};
REGISTER_REDUCER(TReduceSumShowsClicks)

int main_collect_shows_clicks(int argc, const char* argv[])
{
    NLastGetopt::TOpts options;

    TString mrServerStr;
    TString outputTable;
    TString dailyTablesDirectory;
    TVector<TDate> dates;

    options
        .AddCharOption('s', "--  MapReduce server")
        .StoreResult(&mrServerStr)
        .DefaultValue("hahn")
        .Optional();

    options.AddLongOption("daily-tables-dir", "directory with daily tables")
        .Required()
        .RequiredArgument("YT_PATH")
        .StoreResult(&dailyTablesDirectory);

    options.AddLongOption('d', "dates", "date strings (YYYYMMDD-YYYYMMDD,YYYYMMDD,YYYYMMDD...)")
        .Required()
        .RequiredArgument("DATES")
        .RangeSplitHandler(&dates, ',', '-');

    options
        .AddCharOption('o', "-- output table")
        .StoreResult(&outputTable)
        .Required();

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);
    auto client = NYT::CreateClient(mrServerStr);
    {
        NYT::TMapOperationSpec mapSpec;
        for (const auto& date : dates) {
            auto srcTable = NYT::JoinYPaths(dailyTablesDirectory, date.ToStroka("%Y-%m-%d") + SERPS_DAILY_SUFFIX);
            Y_ENSURE(client->Exists(srcTable), "Error: " + srcTable + " does not exist.");
            mapSpec.AddInput<NCollectDwellTimePool::TSerp>(srcTable);
        }
        mapSpec.AddOutput<NYT::TNode>(outputTable);
        client->Map(
            mapSpec,
            new TMapCollectShowsClicks
        );
    }
    client->Sort(NYT::TSortOperationSpec().AddInput(outputTable).Output(outputTable).SortBy({"url"}));
    {
        client->Reduce(
            NYT::TReduceOperationSpec()
                .AddInput<NYT::TNode>(outputTable)
                .AddOutput<NYT::TNode>(NYT::TRichYPath(outputTable).SortedBy("url"))
                .ReduceBy("url"),
                new TReduceSumShowsClicks
        );
    }

    return 0;
}

void InitConfing(const TString& configFileName) {
    NSamovar::TInhostFactorAggrConfig::InitStatic(configFileName);
}

void CheckConfig() {
    Cerr << NSamovar::TInhostFactorAggrConfig::Get()->GetMaxSamplesSizeSecondStage() << Endl;

    for (auto workingSignal : NSamovar::TInhostFactorAggrConfig::Get()->GetWorkingSignals()) {
        Cerr << (size_t)workingSignal << " ";
    }
    Cerr << Endl;

    for (auto sampleSourceSignal : NSamovar::TInhostFactorAggrConfig::Get()->GetSampleSourceSignals()) {
        Cerr << (size_t)sampleSourceSignal << " ";
    }
    Cerr << Endl;

    Cerr << NSamovar::TInhostFactorAggrConfig::Get()->GetWorkingSignalIndex(NSamovarConfig::TInhostFactorAggrConfig::ST_NONE) << Endl;
    Cerr << NSamovar::TInhostFactorAggrConfig::Get()->GetWorkingSignalIndex(NSamovarConfig::TInhostFactorAggrConfig::ST_SHOWS_3_MONTHS) << Endl;
    Cerr << NSamovar::TInhostFactorAggrConfig::Get()->GetWorkingSignalIndex(NSamovarConfig::TInhostFactorAggrConfig::ST_SAMOVAR_DOWNLOADS_3_MONTH) << Endl;
    Cerr << NSamovar::TInhostFactorAggrConfig::Get()->GetWorkingSignalIndex(NSamovarConfig::TInhostFactorAggrConfig::ST_CLICKS_3_MONTHS) << Endl;

    TVector<float> toFix = {0.3};
    NSamovar::TInhostFactorAggrConfig::Get()->CheckAndFixSignalList(toFix);
    for (float f : toFix) {
        Cerr << f << ";";
    }
    Cerr << Endl;

    TVector<float> sample1 = {0, 1, 0, 0, 0};
    TVector<float> sample2 = {0, 0, 0, 0, 1};
    TVector<float> sample3 = {0, 0, 0, 0, 0};
    TVector<float> sample4 = {1, 1, 1, 1, 1};
    Cerr << NSamovar::TInhostFactorAggrConfig::Get()->IsAcceptableForSample(sample1, 0) << " "
         << NSamovar::TInhostFactorAggrConfig::Get()->IsAcceptableForSample(sample2, 0) << " "
         << NSamovar::TInhostFactorAggrConfig::Get()->IsAcceptableForSample(sample3, 0) << " "
         << NSamovar::TInhostFactorAggrConfig::Get()->IsAcceptableForSample(sample4, 0) << Endl;
    Cerr << NSamovar::TInhostFactorAggrConfig::Get()->IsAcceptableForSample(sample1, 1) << " "
         << NSamovar::TInhostFactorAggrConfig::Get()->IsAcceptableForSample(sample2, 1) << " "
         << NSamovar::TInhostFactorAggrConfig::Get()->IsAcceptableForSample(sample3, 1) << " "
         << NSamovar::TInhostFactorAggrConfig::Get()->IsAcceptableForSample(sample4, 1) << Endl;
    Cerr << NSamovar::TInhostFactorAggrConfig::Get()->IsAcceptableForSample(sample1, 2) << " "
         << NSamovar::TInhostFactorAggrConfig::Get()->IsAcceptableForSample(sample2, 2) << " "
         << NSamovar::TInhostFactorAggrConfig::Get()->IsAcceptableForSample(sample3, 2) << " "
         << NSamovar::TInhostFactorAggrConfig::Get()->IsAcceptableForSample(sample4, 2) << Endl;
    Cerr << Endl;
/*
expected
WorkingSignal: [
    ST_CLICKS_3_MONTHS,
    ST_SHOWS_3_MONTHS,
    ST_CLICKS_1_DAY,
    ST_SHOWS_1_DAY,
    ST_SAMOVAR_DOWNLOADS_3_MONTH
]

SampleSourceSignal: [
    ST_SHOWS_3_MONTHS,
    ST_SAMOVAR_DOWNLOADS_3_MONTH,
    ST_NONE
]

MaxSamplesSizeSecondStage : 50000


50000
2 1 4 3 5
1 5 0
-1
1
4
0
0.3;0;0;0;0;
1 0 0 1
0 1 0 1
1 1 1 1
*/
}

TString PrintTokens(const TVector<TString>& v) {
    return "[" + JoinStrings(v.begin(), v.end(), ";") + "]";
}

TString PrintTokens(const TString& url) {
    const auto tokens = NSamovar::TInhostFactorAggrUtils::GetUrlTokens(url);
    TVector<TString> allTokens, dir1Tokens, dirTokens, paramTokens, wordV1Tokens, wordV2Tokens;
    NSamovar::TInhostFactorAggrUtils::GetOnlyNeededTokens(tokens, NSamovarConfig::TInhostFactorAggrConfig::PT_ALL, allTokens);
    NSamovar::TInhostFactorAggrUtils::GetOnlyNeededTokens(tokens, NSamovarConfig::TInhostFactorAggrConfig::PT_DIR1, dir1Tokens);
    NSamovar::TInhostFactorAggrUtils::GetOnlyNeededTokens(tokens, NSamovarConfig::TInhostFactorAggrConfig::PT_DIR, dirTokens);
    NSamovar::TInhostFactorAggrUtils::GetOnlyNeededTokens(tokens, NSamovarConfig::TInhostFactorAggrConfig::PT_PARAM, paramTokens);
    NSamovar::TInhostFactorAggrUtils::GetOnlyNeededTokens(tokens, NSamovarConfig::TInhostFactorAggrConfig::PT_WORD_V1, wordV1Tokens);
    NSamovar::TInhostFactorAggrUtils::GetOnlyNeededTokens(tokens, NSamovarConfig::TInhostFactorAggrConfig::PT_WORD_V2, wordV2Tokens);
    return PrintTokens(allTokens) + PrintTokens(dir1Tokens) + PrintTokens(dirTokens) + PrintTokens(paramTokens)
      + PrintTokens(wordV1Tokens)+ PrintTokens(wordV2Tokens);
}

TString PrintCurrentSamples(const NSamovar::TInhostTreeBuilder* const inhostTreeBuilder) {
    const auto& samples = inhostTreeBuilder->DbgGetCurrentSamples();
    TString currentSamplesDbg = "numSamples=" + ToString(samples.size()) + ", samples =";
    TString details;
    for (size_t i = 0; i < samples.size(); ++i) {
        currentSamplesDbg = currentSamplesDbg + " " + ToString(samples[i].size());
        details += " |";
        for (size_t j = 0; j < Min<size_t>(4, samples[i].size()); ++j) {
            details += (" " + samples[i][j].first + " " + PrintTokens(samples[i][j].first));
            for (size_t k = 0; k < samples[i][j].second.size(); ++k) {
                details += (" " + ToString(samples[i][j].second[k]));
            }
        }
    }
    return currentSamplesDbg + details;
}

class TReduceBoilerFirstStage
    : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{
private:
    TString ConfigFileName;
    THashMap<TString, size_t> HostCount;

    NSamovar::TInhostTreeBuilder* InhostTreeBuilder = nullptr;

    TString CurrentHostName;
    TVector<std::pair<TString, TVector<float>>> UrlSignals;
    size_t Readed = 0;
    size_t TotalAdded = 0;

public:
    Y_SAVELOAD_JOB(ConfigFileName, HostCount);

    TReduceBoilerFirstStage() {}
    TReduceBoilerFirstStage(const TString& configFileName, const THashMap<TString, size_t>& hostCount)
        : ConfigFileName(configFileName)
        , HostCount(hostCount)
    {
    }

    void Dump(NYT::TTableWriter<NYT::TNode>* output) {
        if (UrlSignals.empty()) {
            return;
        }
        Y_ENSURE(UrlSignals.size() <= BOILER_DEFAULT_CHUNK_SIZE);
        Y_ENSURE(!CurrentHostName.empty());

        size_t hostSize = 10;
        auto it = HostCount.find(CurrentHostName);
        if (it != HostCount.end()) {
            hostSize = it->second;
        }
        InhostTreeBuilder->StartHostSamplesBuild(hostSize);
        for (const auto& pr : UrlSignals) {
            InhostTreeBuilder->AddUrl(pr.first, pr.second);
        }
        NYT::TNode outRow = NYT::TNode::CreateMap();
        outRow["host"] = CurrentHostName;
        TString dataStr = InhostTreeBuilder->FinishHostSamplesBuild();
        outRow["data"] = dataStr;
        Y_ENSURE(NSamovar::TInhostFactorAggrConfig::Get()->GetSampleSourceSignals()[2] == NSamovarConfig::TInhostFactorAggrConfig::ST_NONE);
        TotalAdded += InhostTreeBuilder->DbgTotalAdded()[2];
        output->AddRow(outRow);
        {
            //dbg
            NYT::TNode outRowDbg = NYT::TNode::CreateMap();
            outRowDbg["host"] = CurrentHostName;
            outRowDbg["hostSize"] = hostSize;
            outRowDbg["UrlSignals.size()"] = UrlSignals.size();
            outRowDbg["Decimation"] = ToString(InhostTreeBuilder->DbgGetDecimationRounds()) + " " + ToString(InhostTreeBuilder->DbgDecimationLastReduceSize());
            outRowDbg["data.size()"] = dataStr.size();
            const auto& samples = InhostTreeBuilder->DbgGetCurrentSamples();
            TString currentSamplesDbg = "numSamples=" + ToString(samples.size()) + ", samples =";
            TString details;
            for (size_t i = 0; i < samples.size(); ++i) {
                currentSamplesDbg = currentSamplesDbg + " " + ToString(samples[i].size());
                details += " |";
                for (size_t j = 0; j < Min<size_t>(5, samples[i].size()); ++j) {
                    details += (" " + samples[i][j].first);
                    for (size_t k = 0; k < samples[i][j].second.size(); ++k) {
                        details += (" " + ToString(samples[i][j].second[k]));
                    }
                }
            }
            outRowDbg["InhostTreeBuilder->DbgGetCurrentSamples()"] = PrintCurrentSamples(InhostTreeBuilder);
            const auto& totalAdded = InhostTreeBuilder->DbgTotalAdded();
            TString totalAddedStr;
            for (const auto& add : totalAdded) {
                if (!totalAddedStr.empty()) totalAddedStr += " ";
                totalAddedStr += ToString(add);
            }
            outRowDbg["InhostTreeBuilder->DbgTotalAdded()"] = totalAddedStr;
            output->AddRow(outRowDbg, 1);
        }
        UrlSignals.clear();
    }

    void Finish(NYT::TTableWriter<NYT::TNode>* output) override {
        Dump(output);
        Y_ENSURE(TotalAdded == Readed);
        delete InhostTreeBuilder;
    }

    void Start(NYT::TTableWriter<NYT::TNode>*) override {
        NSamovar::TInhostFactorAggrConfig::InitStatic(ConfigFileName);
        InhostTreeBuilder = new NSamovar::TInhostTreeBuilder(NSamovar::TInhostFactorAggrConfig::Get());
        CurrentHostName = "";
        UrlSignals.clear();
        Readed = 0;
        TotalAdded = 0;
    }

    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        for (; input->IsValid(); input->Next()) {
            ++Readed;
            const auto& inRow = input->GetRow();
            const TString& host = inRow["host"].AsString();
            if (host != CurrentHostName) {
                Dump(output);
                CurrentHostName = host;
            }
            Y_ENSURE(!CurrentHostName.empty() && host == CurrentHostName);
            const TString& url = inRow["url"].AsString();
            TVector<TString> tokens;
            StringSplitter(inRow["signals"].AsString()).Split(' ').AddTo(&tokens);
            Y_ENSURE(tokens.size() == NSamovar::TInhostFactorAggrConfig::Get()->GetWorkingSignals().size());
            TVector<float> v;
            for (const auto& token : tokens) {
                v.push_back(FromString<float>(token));
            }
            UrlSignals.emplace_back(url, v);
            if (UrlSignals.size() == BOILER_DEFAULT_CHUNK_SIZE) {
                Dump(output);
            }
        }
    }
};
REGISTER_REDUCER(TReduceBoilerFirstStage)

int main_calc_factors_prod_first_stage(int argc, const char* argv[])
{
    NLastGetopt::TOpts options;

    TString mrServerStr;
    TString inputTable;
    TString outputTable;
    TString configPath;

    options
        .AddCharOption('s', "--  MapReduce server")
        .StoreResult(&mrServerStr)
        .DefaultValue("hahn")
        .Optional();

    options
        .AddCharOption('i', "-- input table")
        .StoreResult(&inputTable)
        .Required();

    options
        .AddCharOption('o', "-- output table")
        .StoreResult(&outputTable)
        .Required();

    options
        .AddCharOption('c', "-- config file name")
        .StoreResult(&configPath)
        .Required();

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);
    auto client = NYT::CreateClient(mrServerStr);

    InitConfing(configPath);
    CheckConfig();
    THashMap<TString, size_t> hostCount;
    {
        auto reader = client->CreateTableReader<NYT::TNode>(inputTable + ".host");
        for (; reader->IsValid(); reader->Next()) {
            const auto& row = reader->GetRow();
            hostCount[row["host"].AsString()] = row["count"].AsUint64();
        }
    }
    {
        client->Reduce(
            NYT::TReduceOperationSpec()
                .AddInput<NYT::TNode>(inputTable)
                .AddOutput<NYT::TNode>(NYT::TRichYPath(outputTable).SortedBy({"host"}))
                .AddOutput<NYT::TNode>(NYT::TRichYPath(outputTable + ".dbg").SortedBy({"host"}))
                .ReducerSpec(NYT::TUserJobSpec().AddLocalFile(configPath))
                .ReduceBy({"host", "urlhash"}),
                new TReduceBoilerFirstStage(GetFileNameComponent(configPath), hostCount)
        );
    }
    client->Sort(NYT::TSortOperationSpec().AddInput(outputTable).Output(outputTable).SortBy("host"));

    return 0;
}

void PrintPartitions(NYT::TNode& outRow, const NSamovar::NRecord::TInhostPartitions& partitions) {
    for (size_t partitionIndex = 0; partitionIndex < partitions.PartitionSize(); ++partitionIndex) {
        const auto& partition = partitions.GetPartition(partitionIndex);
        const auto& total = partition.GetTotal();
        TString dbgStr = "total.GetSize()=" + ToString(total.GetSize()) + ", tree size=" + ToString(partition.TreeNodesSize());
        for (size_t scIndex = 0; scIndex < total.SignalCountersSize(); ++scIndex) {
            const NSamovar::NRecord::TInhostSignalCounters& signalCounters = total.GetSignalCounters(scIndex);
            dbgStr += "[" + ToString((size_t)signalCounters.GetSignal()) + ","
                 + ToString(signalCounters.GetMax()) + ","
                 + ToString(signalCounters.GetSum()) + ","
                 + ToString(signalCounters.GetSumLog()) + ","
                 + ToString(signalCounters.GetCountNonZero()) + ","
                 + ToString(signalCounters.GetDisp()) + ","
                 + ToString(signalCounters.GetMedianNonZero()) + "]";
        }
        for (size_t treeNodesIndex = 0; treeNodesIndex < partition.TreeNodesSize(); ++treeNodesIndex) {
            if (treeNodesIndex == 0) {
                dbgStr += " Tree=";
            } else {
                dbgStr += ";";
            }
            const NSamovar::NRecord::TInhostTreeNode& treeNode = partition.GetTreeNodes(treeNodesIndex);
            dbgStr += treeNode.GetSplit() + "-" + ToString(treeNode.GetLeftChildrenIndex()) + "-" + ToString(treeNode.GetNodeDataIndex());
            if (treeNode.GetLeftChildrenIndex() == 0) { //leaf
                Y_ENSURE(treeNode.GetSplit().empty());
                size_t dataIndex = treeNode.GetNodeDataIndex();
                const NSamovar::NRecord::TInhostNodeData& nodeData = partition.GetNodeData(dataIndex);
                dbgStr += "[" + ToString(nodeData.GetSize()) + "]";
            } else {
                Y_ENSURE(!treeNode.GetSplit().empty());
            }
        }
        outRow[partition.GetName() + "_partition"] = dbgStr;
    }
}

void PrintPartitions(NYT::TNode& outRow, const TString& partitionsStr) {
    NSamovar::NRecord::TInhostPartitions partitions;
    Y_PROTOBUF_SUPPRESS_NODISCARD partitions.ParseFromString(partitionsStr);
    PrintPartitions(outRow, partitions);
}

class TReduceBoilerSecondStage
    : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{
private:
    TString ConfigFileName;

    NSamovar::TInhostTreeBuilder* InhostTreeBuilder = nullptr;

    size_t StatCount = 0;
    size_t StatMaxAttrSize = 0;
    size_t StatSumAttrSize = 0;

public:
    Y_SAVELOAD_JOB(ConfigFileName);

    TReduceBoilerSecondStage() {}
    TReduceBoilerSecondStage(const TString& configFileName)
        : ConfigFileName(configFileName)
    {
    }

    void Finish(NYT::TTableWriter<NYT::TNode>* output) override {
        delete InhostTreeBuilder;
        if (StatCount > 0) {
            NYT::TNode outRow = NYT::TNode::CreateMap();
            outRow["count"] = StatCount;
            outRow["max_attr_size"] = StatMaxAttrSize;
            outRow["avg_attr_size"] = StatSumAttrSize / (float)StatCount;
            output->AddRow(outRow, 2);
        }
    }

    void Start(NYT::TTableWriter<NYT::TNode>*) override {
        NSamovar::TInhostFactorAggrConfig::InitStatic(ConfigFileName);
        InhostTreeBuilder = new NSamovar::TInhostTreeBuilder(NSamovar::TInhostFactorAggrConfig::Get());
        StatCount = 0;
        StatMaxAttrSize = 0;
        StatSumAttrSize = 0;
    }

    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        InhostTreeBuilder->StartCombineHost();
        TString host = input->GetRow()["host"].AsString();
        size_t partsToCombine = 0;
        TString partsToCombineSizes;
        for (; input->IsValid(); input->Next()) {
            NSamovar::NRecord::TInhostSamples protoSamples;
            Y_PROTOBUF_SUPPRESS_NODISCARD protoSamples.ParseFromString(input->GetRow()["data"].AsString());
            InhostTreeBuilder->PushHostCombineData(protoSamples);

            ++partsToCombine;
            if (partsToCombine <= 5) {
                for (size_t sampleIndex = 0; sampleIndex < protoSamples.SamplesSize(); ++sampleIndex) {
                    if (sampleIndex == 0) {
                        if (partsToCombine > 1) {
                            partsToCombineSizes += " | ";
                        }
                    } else {
                        partsToCombineSizes += " ";
                    }
                    partsToCombineSizes += ToString(protoSamples.GetSamples(sampleIndex).DocumentsSize());
                }
            }
        }
        TString combineResult = InhostTreeBuilder->FinishCombineHost();
        ++StatCount;
        StatMaxAttrSize = Max<size_t>(StatMaxAttrSize, combineResult.size());
        StatSumAttrSize += combineResult.size();
        {
            NYT::TNode outRow = NYT::TNode::CreateMap();
            outRow["host"] = host;
            outRow["result"] = combineResult;
            output->AddRow(outRow);
        }
        {
            //if (partsToCombine > 1) {
                NYT::TNode outRow = NYT::TNode::CreateMap();
                outRow["host"] = host;
                outRow["parts_to_combine"] = partsToCombine;
                outRow["parts_to_combine_sizes"] = partsToCombineSizes;
                outRow["current_samples"] = PrintCurrentSamples(InhostTreeBuilder);
                const auto& partitionsDbg = InhostTreeBuilder->GetPartitionsDbg();
                for (const auto& pr : partitionsDbg) {
                    outRow[pr.first + "_dbg"] = pr.second;
                }
                PrintPartitions(outRow, combineResult);
                output->AddRow(outRow, 1);
            //}
        }
    }
};
REGISTER_REDUCER(TReduceBoilerSecondStage)

int main_calc_factors_prod_second_stage(int argc, const char* argv[])
{
    NLastGetopt::TOpts options;

    TString mrServerStr;
    TString inputTable;
    TString outputTable;
    TString configPath;

    options
        .AddCharOption('s', "--  MapReduce server")
        .StoreResult(&mrServerStr)
        .DefaultValue("hahn")
        .Optional();

    options
        .AddCharOption('i', "-- input table")
        .StoreResult(&inputTable)
        .Required();

    options
        .AddCharOption('o', "-- output table")
        .StoreResult(&outputTable)
        .Required();

    options
        .AddCharOption('c', "-- config file name")
        .StoreResult(&configPath)
        .Required();

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);
    auto client = NYT::CreateClient(mrServerStr);
    {
        client->Reduce(
            NYT::TReduceOperationSpec()
                .AddInput<NYT::TNode>(inputTable)
                .AddOutput<NYT::TNode>(NYT::TRichYPath(outputTable).SortedBy("host"))
                .AddOutput<NYT::TNode>(NYT::TRichYPath(outputTable + ".dbg").SortedBy("host"))
                .AddOutput<NYT::TNode>(NYT::TRichYPath(outputTable + ".stat"))
                .ReducerSpec(NYT::TUserJobSpec().AddLocalFile(configPath))
                .ReduceBy("host"),
                new TReduceBoilerSecondStage(GetFileNameComponent(configPath))
        );
    }

    return 0;
}

class TMapPrepareLearningPool : public NYT::IMapper<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>> {
public:
    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        for (; input->IsValid(); input->Next()) {
            const NYT::TNode& node = input->GetRow();
            TVector<TString> tokens;
            StringSplitter(node["value"].AsString()).Split('\t').AddTo(&tokens);
            Y_ENSURE(tokens.size() > 1);
            const TString& url = tokens[1];
            TString normalizedURL;
            bool normResult = NUrlNorm::NormalizeUrl(url, normalizedURL);
            Y_ENSURE(normResult);
            TString host, path;
            SplitUrlToHostAndPath(normalizedURL, host, path);

            NYT::TNode outRow = NYT::TNode::CreateMap();
            outRow["url"] = url;
            outRow["host"] = host;
            outRow["url_norm"] = normalizedURL;
            outRow["key"] = node["key"];
            outRow["index"] = node["index"];
            outRow["value"] = node["value"];
            output->AddRow(outRow);
        }
    }
};
REGISTER_MAPPER(TMapPrepareLearningPool);

class TReduceCalcFeaturesProd
    : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{
private:
    TString ConfigFileName;

public:
    Y_SAVELOAD_JOB(ConfigFileName);

    TReduceCalcFeaturesProd() {}
    TReduceCalcFeaturesProd(const TString& configFileName)
        : ConfigFileName(configFileName)
    {
    }

    void Start(NYT::TTableWriter<NYT::TNode>*) override {
        NSamovar::TInhostFactorAggrConfig::InitStatic(ConfigFileName);
    }

    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        TString protoStr;
        if (input->GetTableIndex() == 0) {
            protoStr = input->GetRow()["result"].AsString();
            Y_ENSURE(!protoStr.empty());
            input->Next();
        }
        NSamovar::TInhostFactorCalcer factorCalcer(NSamovar::TInhostFactorAggrConfig::Get());
        for (; input->IsValid(); input->Next()) {
            Y_ENSURE(input->GetTableIndex() == 1);
            const auto& url = input->GetRow()["url"].AsString();
            const auto& host = input->GetRow()["host"].AsString();
            //const auto& urlNorm = input->GetRow()["url_norm"].AsString(); //TODO - check coverage

            TVector<float> factors;
            NYT::TNode outRow = NYT::TNode::CreateMap();
            NSamovar::NRecord::TInhostPartitions partitions;
            if (!protoStr.empty()) {
                Y_PROTOBUF_SUPPRESS_NODISCARD partitions.ParseFromString(protoStr);
            }
            PrintPartitions(outRow, partitions);
            factors = factorCalcer.CalcFactors(partitions, url);

            Y_ENSURE(factors.size() == NSamovar::TInhostFactorAggrConfig::Get()->GetAllFactorNames().size());
            outRow["url"] = url;
            outRow["host"] = host;
            TString factorsStr;
            for (const auto& f : factors) {
                if (!factorsStr.empty()) factorsStr += "\t";
                factorsStr += ToString(f);
            }
            outRow["factors"] = factorsStr;
            output->AddRow(outRow);
        }
    }
};
REGISTER_REDUCER(TReduceCalcFeaturesProd)

int main_calc_factors_prod(int argc, const char* argv[])
{
    NLastGetopt::TOpts options;

    TString mrServerStr;
    TString inputTable;
    TString outputTable;
    TString configPath;
    TString poolDir;

    options
        .AddCharOption('s', "--  MapReduce server")
        .StoreResult(&mrServerStr)
        .DefaultValue("hahn")
        .Optional();

    options
        .AddCharOption('i', "-- input table")
        .StoreResult(&inputTable)
        .Required();

    options
        .AddCharOption('o', "-- output table")
        .StoreResult(&outputTable)
        .Required();

    options
        .AddCharOption('c', "-- config file name")
        .StoreResult(&configPath)
        .Required();

    options
        .AddCharOption('p', "-- pool directory")
        .StoreResult(&poolDir)
        .Required();

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);
    auto client = NYT::CreateClient(mrServerStr);

    TString poolUrls = outputTable + ".pool_urls";
    client->Map(
        NYT::TMapOperationSpec()
            .AddInput<NYT::TNode>(poolDir + "/features")
            .AddOutput<NYT::TNode>(NYT::TRichYPath(poolUrls)),
        new TMapPrepareLearningPool
    );
    client->Sort(NYT::TSortOperationSpec().AddInput(poolUrls).Output(poolUrls).SortBy("host"));
    {
        NYT::TReduceOperationSpec reduceSpec;
        reduceSpec.AddInput<NYT::TNode>(inputTable);
        reduceSpec.AddInput<NYT::TNode>(poolUrls);
        reduceSpec.AddOutput<NYT::TNode>(NYT::TRichYPath(outputTable).SortedBy("host"));
        reduceSpec.ReducerSpec(NYT::TUserJobSpec().AddLocalFile(configPath));
        reduceSpec.ReduceBy("host");
        client->Reduce(
            reduceSpec,
            new TReduceCalcFeaturesProd(GetFileNameComponent(configPath))
        );
    }
    client->Sort(NYT::TSortOperationSpec().AddInput(outputTable).Output(outputTable).SortBy("url"));

    return 0;
}

class TExtractHostUrlHash : public NYT::IMapper<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>> {
public:
    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        for (; input->IsValid(); input->Next()) {
            NYT::TNode row = input->GetRow();
            const auto& url = row["url"].AsString();
            TString host, path;
            SplitUrlToHostAndPath(url, host, path);
            row["type"] = input->GetTableIndex();
            row["host"] = host;
            row["urlhash"] = ComputeHash(url);
            output->AddRow(row);
        }
    }
};
REGISTER_MAPPER(TExtractHostUrlHash);

class TReduceMergeSignals
    : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{
private:
    TMap<TString, size_t> HostCount;
    TString ConfigFileName;

public:
    Y_SAVELOAD_JOB(ConfigFileName);

    TReduceMergeSignals() {}
    TReduceMergeSignals(const TString& configFileName)
        : ConfigFileName(configFileName)
    {
    }

    void Finish(NYT::TTableWriter<NYT::TNode>* output) override {
        for (const auto& pr : HostCount) {
            NYT::TNode outRow = NYT::TNode::CreateMap();
            outRow["host"] = pr.first;
            outRow["count"] = pr.second;
            output->AddRow(outRow, 1);
        }
    }

    void Start(NYT::TTableWriter<NYT::TNode>*) override {
        HostCount.clear();
        NSamovar::TInhostFactorAggrConfig::InitStatic(ConfigFileName);
    }

    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        TVector<float> signals(NSamovar::TInhostFactorAggrConfig::Get()->GetWorkingSignals().size(), 0.0f);
        TString url, host;
        {
            const auto& inRow = input->GetRow();
            url = inRow["url"].AsString();
            host = inRow["host"].AsString();
        }
        for (; input->IsValid(); input->Next()) {
            const auto& inRow = input->GetRow();
            if (inRow["type"].AsUint64() == 1) {
                signals[NSamovar::TInhostFactorAggrConfig::Get()->GetWorkingSignalIndex(NSamovarConfig::TInhostFactorAggrConfig::ST_SAMOVAR_DOWNLOADS_3_MONTH)] = inRow["count"].AsUint64();
            } else {
                Y_ENSURE(inRow["type"].AsUint64() == 0);
                signals[NSamovar::TInhostFactorAggrConfig::Get()->GetWorkingSignalIndex(NSamovarConfig::TInhostFactorAggrConfig::ST_SHOWS_3_MONTHS)] = inRow["shows"].AsUint64();
                signals[NSamovar::TInhostFactorAggrConfig::Get()->GetWorkingSignalIndex(NSamovarConfig::TInhostFactorAggrConfig::ST_CLICKS_3_MONTHS)] = inRow["clicks"].AsUint64();
            }
        }
        NYT::TNode outRow = NYT::TNode::CreateMap();
        outRow["url"] = url;
        outRow["urlhash"] = ComputeHash(url);
        outRow["host"] = host;
        ++HostCount[host];
        TString signalsStr;
        for (const float f : signals) {
            if (!signalsStr.empty()) signalsStr += " ";
            signalsStr += ToString(f);
        }
        outRow["signals"] = signalsStr;
        output->AddRow(outRow, 0);
    }
};
REGISTER_REDUCER(TReduceMergeSignals)

class TReduceSumHostCount
    : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>> {
public:
    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        size_t sum = 0;
        TString host = input->GetRow()["host"].AsString();
        for (; input->IsValid(); input->Next()) {
            const auto& row = input->GetRow();
            Y_ENSURE(row["host"].AsString() == host);
            sum += row["count"].AsUint64();
        }
        if (sum > 1000) {
            NYT::TNode outRow = NYT::TNode::CreateMap();
            outRow["host"] = host;
            outRow["count"] = sum;
            output->AddRow(outRow);
        }
    }
};
REGISTER_REDUCER(TReduceSumHostCount)

int main_prepare_for_first_stage(int argc, const char* argv[])
{
    NLastGetopt::TOpts options;

    TString mrServerStr;
    TString inputUserdata;
    TString inputSamovar;
    TString outputTable;
    TString configPath;

    options
        .AddCharOption('s', "--  MapReduce server")
        .StoreResult(&mrServerStr)
        .DefaultValue("hahn")
        .Optional();

    options.AddLongOption("userdata", "input userdata")
        .Required()
        .RequiredArgument("YT_PATH")
        .StoreResult(&inputUserdata);

    options.AddLongOption("samovar", "input samovar")
        .Required()
        .RequiredArgument("YT_PATH")
        .StoreResult(&inputSamovar);

    options
        .AddCharOption('o', "-- output table")
        .StoreResult(&outputTable)
        .Required();

    options
        .AddCharOption('c', "-- config file name")
        .StoreResult(&configPath)
        .Required();

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);
    auto client = NYT::CreateClient(mrServerStr);
    NYT::TMapOperationSpec mapSpec;
    mapSpec.AddInput<NYT::TNode>(inputUserdata);
    mapSpec.AddInput<NYT::TNode>(inputSamovar);
    mapSpec.AddOutput<NYT::TNode>(NYT::TRichYPath(outputTable));
    client->Map(
        mapSpec,
        new TExtractHostUrlHash
    );
    client->Sort(NYT::TSortOperationSpec().AddInput(outputTable).Output(outputTable).SortBy({"host", "urlhash"}));
    {
        client->Reduce(
            NYT::TReduceOperationSpec()
                .AddInput<NYT::TNode>(outputTable)
                .AddOutput<NYT::TNode>(NYT::TRichYPath(outputTable).SortedBy({"host", "urlhash"}))
                .AddOutput<NYT::TNode>(NYT::TRichYPath(outputTable + ".host").SortedBy({"host"}))
                .ReducerSpec(NYT::TUserJobSpec().AddLocalFile(configPath))
                .ReduceBy({"host", "urlhash"}),
                new TReduceMergeSignals(GetFileNameComponent(configPath))
        );
    }
    {
        NYT::TReduceOperationSpec reduceSpec;
        reduceSpec.AddInput<NYT::TNode>(outputTable + ".host");
        reduceSpec.AddOutput<NYT::TNode>(NYT::TRichYPath(outputTable + ".host").SortedBy("host"));
        reduceSpec.ReduceBy("host");
        client->Reduce(
            reduceSpec,
            new TReduceSumHostCount
        );
    }
    return 0;
}

class TMapMergeForFactorsCalc : public NYT::IMapper<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>> {
public:
    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        TReallyFastRng32 rng(input->GetRowIndex());
        for (; input->IsValid(); input->Next()) {
            NYT::TNode row = input->GetRow();
            const auto& url = row["url"].AsString();
            TString host, path;
            SplitUrlToHostAndPath(url, host, path);
            row["type"] = input->GetTableIndex();
            row["host"] = host;
            row["monster_sampling_bucket"] = rng.Uniform(MONSTER_SAMPLING_BUCKETS_COUNT);
            row["rng"] = rng.GenRandReal2();
            output->AddRow(row);
        }
    }
};
REGISTER_MAPPER(TMapMergeForFactorsCalc);

class TReduceSampleMonters
    : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{
public:
    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        size_t type1Count = 0;
        for (; input->IsValid(); input->Next()) {
            const auto& inRow = input->GetRow();
            if (inRow["type"].AsUint64() == 1) {
                ++type1Count;
                if (type1Count > 1000000 / MONSTER_SAMPLING_BUCKETS_COUNT) {
                    continue;
                }
            }
            output->AddRow(inRow);
        }
    }
};
REGISTER_REDUCER(TReduceSampleMonters)

int main_merge_for_factors_calc(int argc, const char* argv[])
{
    NLastGetopt::TOpts options;

    TString mrServerStr;
    TString inputUserdata;
    TString inputSamovar;
    TString outputTable;

    options
        .AddCharOption('s', "--  MapReduce server")
        .StoreResult(&mrServerStr)
        .DefaultValue("hahn")
        .Optional();

    options.AddLongOption("userdata", "input userdata")
        .Required()
        .RequiredArgument("YT_PATH")
        .StoreResult(&inputUserdata);

    options.AddLongOption("samovar", "input samovar")
        .Required()
        .RequiredArgument("YT_PATH")
        .StoreResult(&inputSamovar);

    options
        .AddCharOption('o', "-- output table")
        .StoreResult(&outputTable)
        .Required();

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);
    auto client = NYT::CreateClient(mrServerStr);

    NYT::TMapOperationSpec mapSpec;
    mapSpec.AddInput<NYT::TNode>(inputUserdata);
    mapSpec.AddInput<NYT::TNode>(inputSamovar);
    mapSpec.AddOutput<NYT::TNode>(NYT::TRichYPath(outputTable));
    client->Map(
        mapSpec,
        new TMapMergeForFactorsCalc
    );
    client->Sort(NYT::TSortOperationSpec().AddInput(outputTable).Output(outputTable).SortBy({"host", "monster_sampling_bucket", "rng"}));
    {
        client->Reduce(
            NYT::TReduceOperationSpec()
                .AddInput<NYT::TNode>(outputTable)
                .AddOutput<NYT::TNode>(NYT::TRichYPath(outputTable).SortedBy({"host", "monster_sampling_bucket", "rng"}))
                .ReduceBy({"host", "monster_sampling_bucket"}),
                new TReduceSampleMonters
        );
    }
    return 0;
}

struct TSimplePartition {
    TVector<TString> Partitions;
    TVector<float> Factors;
    TVector<NYT::TNode> RandomSamples;
    TVector<NYT::TNode> ShowsSamples;
};

typedef TVector<TSimplePartition> TSimplePartitions;


const TString& GetUrl(const NYT::TNode& node) {
    return node["url"].AsString();
}

void SavePartitions(const TSimplePartitions& simplePartitions, NYT::TNode& result) {
    result = NYT::TNode::CreateList();
    for (const auto& partition : simplePartitions) {
        NYT::TNode outMap = NYT::TNode::CreateMap();
        outMap["partitions"] = NYT::TNode::CreateList();
        for (const TString& p : partition.Partitions) {
            outMap["partitions"].AsList().push_back(p);
        }
        outMap["factors"] = NYT::TNode::CreateList();
        for (const float& f : partition.Factors) {
            outMap["factors"].AsList().push_back(f);
        }
        result.AsList().push_back(outMap);
    }
}

void LoadPartitions(const NYT::TNode& inRow, TSimplePartitions& result) {
    result.clear();
    for (const auto& listItem1 : inRow.AsList()) {
        TSimplePartition simplePartition;
        for (const auto& listItem2 : listItem1["partitions"].AsList()) {
            simplePartition.Partitions.push_back(listItem2.AsString());
        }
        for (const auto& listItem2 : listItem1["factors"].AsList()) {
            simplePartition.Factors.push_back(listItem2.AsDouble());
        }
        result.push_back(simplePartition);
    }
}

const TUrlTokenization& GetTokenezationFromCache(const TString& url) {
    Y_ENSURE(!url.empty());
    auto it = TokenizationCache.find(url);
    if (it != TokenizationCache.end()) {
        return it->second;
    }
    return TokenizationCache[url] = GetURLTokenization(url);
}

const TUrlTokenization& GetTokenezationFromCache(const NYT::TNode& node) {
    return GetTokenezationFromCache(GetUrl(node));
}

bool IsNegationToken(const TString& token) {
    return token.StartsWith('~');
}

TString FromNegation(const TString& token) {
    Y_ENSURE(IsNegationToken(token));
    return token.substr(1);
}

TString Negation(const TString& token) {
    return "~" + token;
}

TString NormToken(TString token) {
    while (IsNegationToken(token)) {
        token = FromNegation(token);
    }
    return token;
}

void AddToken(THashSet<TString>& result, const TString& token) {
    if (!token.empty()) {
        result.insert(token);
    }
}

const THashSet<TString>& GetAllTokensFromCache(const TString& url) {
    auto it = AllTokensCache.find(url);
    if (it != AllTokensCache.end()) {
        return it->second;
    }
    THashSet<TString>& result = AllTokensCache[url];
    const TUrlTokenization& tokenization = GetTokenezationFromCache(url);
    for (const auto& pr : tokenization) {
        if (pr.first.StartsWith("pathLevel_")) {
            AddToken(result, NormToken(pr.second));
        } else if (!pr.first.EndsWith("_WITHOUT_VALUE")) {
            AddToken(result, NormToken(pr.first));
            AddToken(result, NormToken(pr.second));
        }
    }
    return result;
}

const THashSet<TString>& GetAllTokensFromCache(const NYT::TNode& node) {
    return GetAllTokensFromCache(GetUrl(node));
}

TString GetDir1(const TString& url) {
    const auto& tokenezation = GetTokenezationFromCache(url);
    auto it = tokenezation.find("pathLevel_0");
    if (it != tokenezation.end()) {
        return NormToken(it->second);
    }
    return "";
}


TString GetDir1(const NYT::TNode& node) {
    return GetDir1(GetUrl(node));
}

size_t GetPartitionIndex(const TSimplePartitions& simplePartitions, const TString& url) {
    const auto& allTokens = GetAllTokensFromCache(url);
    for (size_t index = 0; index < simplePartitions.size(); ++index) {
        if (simplePartitions[index].Partitions.empty()) {
            Y_ENSURE(index + 2 == simplePartitions.size());
        }
        bool allMatch = true;
        for (const auto& partition : simplePartitions[index].Partitions) {
            if (!IsNegationToken(partition)) {
                if (!allTokens.contains(partition)) {
                    allMatch = false;
                    break;
                }
            } else {
                if (allTokens.contains(FromNegation(partition))) {
                    allMatch = false;
                    break;
                }
            }
        }
        if (allMatch) {
            return index;
        }
    }
    Y_ENSURE(false);
    return 0;
}

size_t GetPartitionIndex(const TSimplePartitions& simplePartitions, const NYT::TNode& node) {
    return GetPartitionIndex(simplePartitions, GetUrl(node));
}

TString PartitionInformation(const TSimplePartition& partition) {
    TString result = "(";
    for (size_t i = 0; i < partition.Partitions.size(); ++i) {
        if (i > 0) result += ",";
        result += partition.Partitions[i];
    }
    result += ")";
    return result;
}

class TReduceCalcHostAggrSimple : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{
private:
    size_t MaxRepresentativeCount = 0;
    typedef std::array<float, 3>  TFactorsForClustering;
    THashMap<TString, TFactorsForClustering> UrlFactorsCache;

    void AddVec(TFactorsForClustering& ret, const TFactorsForClustering& rhs) {
        ret[0] += rhs[0];
        ret[1] += rhs[1];
        ret[2] += rhs[2];
    }

    void DivVec(TFactorsForClustering& ret, float f) {
        ret[0] /= f;
        ret[1] /= f;
        ret[2] /= f;
    }

    void NormVector(TFactorsForClustering& ret) {
        float norm = sqrt(ret[0] * ret[0] + ret[1] * ret[1] + ret[2] * ret[2]);
        DivVec(ret, norm);
    }

    float CosineDistance(const TFactorsForClustering& lhs, const TFactorsForClustering& rhs) {
        return lhs[0] * rhs[0] + lhs[1] * rhs[1] + lhs[2] * rhs[2];
    }

    float DistanceSqr(const TFactorsForClustering& lhs, const TFactorsForClustering& rhs) {
        return (lhs[0] - rhs[0]) * (lhs[0] - rhs[0]) +
               (lhs[1] - rhs[1]) * (lhs[1] - rhs[1]) +
               (lhs[2] - rhs[2]) * (lhs[2] - rhs[2]);
    }

    ui64 Get(const NYT::TNode& node, const TString& key) {
        return node[key].AsUint64();
    }

    ui64 GetOrZero(const NYT::TNode& node, const TString& key) {
        if (node[key].IsUndefined()) {
            return 0;
        }
        return Get(node, key);
    }

    void FillUrlFactorsCache(const TVector<NYT::TNode>& randomSample, const TVector<NYT::TNode>& showsSample) {
        UrlFactorsCache.clear();
        TFactorsForClustering init{0.0f, 0.0f, 0.0f};
        for (const auto& s : randomSample) {
            UrlFactorsCache[GetUrl(s)] = init;
        }
        for (const auto& s : showsSample) {
            UrlFactorsCache[GetUrl(s)] = init;
        }
        for (const auto& s : randomSample) {
            UrlFactorsCache[GetUrl(s)][0] = log2(Get(s, "count") + 1ULL);
        }
        for (const auto& s : showsSample) {
            auto& arr = UrlFactorsCache[GetUrl(s)];
            arr[1] = log2(Get(s, "shows") + 1ULL);
            arr[2] = log2(Get(s, "clicks") + 1ULL);
        }
        //for (auto& pr : UrlFactorsCache) {
        //    NormVector(pr.second);
        //}
    }

    TFactorsForClustering CalcCenter(const TSimplePartition& partition) {
        TFactorsForClustering center{0, 0, 0};
        for (const auto& s : partition.RandomSamples) {
            AddVec(center, UrlFactorsCache[GetUrl(s)]);
        }
        for (const auto& s : partition.ShowsSamples) {
            AddVec(center, UrlFactorsCache[GetUrl(s)]);
        }
        float div = partition.RandomSamples.size() + partition.ShowsSamples.size();
        Y_ENSURE(div > 0);
        DivVec(center, partition.RandomSamples.size() + partition.ShowsSamples.size());
        return center;
    }

    float CalcDispersionTotal(const TSimplePartition& partition) {
        TFactorsForClustering center = CalcCenter(partition);
        float result = 0;
        for (const auto& s : partition.RandomSamples) {
            result += DistanceSqr(center, UrlFactorsCache[GetUrl(s)]);
        }
        for (const auto& s : partition.ShowsSamples) {
            result += DistanceSqr(center, UrlFactorsCache[GetUrl(s)]);
        }
        return result;
    }

    float CalcDispersion(const TSimplePartition& partition) {
        float sumSimilarity = CalcDispersionTotal(partition);
        size_t totalSize = partition.RandomSamples.size() + partition.ShowsSamples.size();
        Y_ENSURE(totalSize > 0);
        return sumSimilarity / (float)totalSize;
    }


    void KeepOnlyTopByHash(TVector<NYT::TNode>& showsSample) {
        Sort(showsSample.begin(), showsSample.end(), [=](const auto& lhs, const auto& rhs) {
            return ComputeHash(GetUrl(lhs)) < ComputeHash(GetUrl(rhs));
        });
        if (showsSample.size() < MaxRepresentativeCount) {
            return;
        }
        showsSample.resize(MaxRepresentativeCount);
    }

    TString PrintFirstVecValues(const TVector<NYT::TNode>& sample, size_t maxPrint) {
        TString result = "count=" + ToString(sample.size());
        result += ", values=";
        for (size_t i = 0; i < Min(maxPrint, sample.size()); ++i) {
            const TString& url = sample[i]["url"].AsString();
            result += " " + url
                + " " + ToString(GetOrZero(sample[i], "count"))
                + " " + ToString(GetOrZero(sample[i], "shows"))
                + " " + ToString(GetOrZero(sample[i], "clicks"))
                + " (" + ToString(UrlFactorsCache[url][0])
                + "," + ToString(UrlFactorsCache[url][1])
                + "," + ToString(UrlFactorsCache[url][2]) + ")";
        }
        return result;
    }

    void Split(TSimplePartitions& result, size_t bestScoreIndex, TString bestScoreToken, size_t expectedHas, size_t expectedNotHas) {
        Y_ENSURE(!IsNegationToken(bestScoreToken));
        Y_ENSURE(result[bestScoreIndex].RandomSamples.size() + result[bestScoreIndex].ShowsSamples.size() == expectedHas + expectedNotHas);
        TSimplePartition beforePartition = result[bestScoreIndex];

        result[bestScoreIndex].RandomSamples.clear();
        result[bestScoreIndex].ShowsSamples.clear();
        result[bestScoreIndex].Partitions.push_back(bestScoreToken);

        size_t hasNoIndex = result.size();
        result.emplace_back(TSimplePartition());
        result[hasNoIndex].Partitions = beforePartition.Partitions;
        result[hasNoIndex].Partitions.push_back(Negation(bestScoreToken));

        for (const auto& s : beforePartition.RandomSamples) {
            size_t index = bestScoreIndex;
            if (!GetAllTokensFromCache(s).contains(bestScoreToken)) {
                index = hasNoIndex;
            }
            result[index].RandomSamples.push_back(s);
        }
        for (const auto& s : beforePartition.ShowsSamples) {
            size_t index = bestScoreIndex;
            if (!GetAllTokensFromCache(s).contains(bestScoreToken)) {
                index = hasNoIndex;
            }
            result[index].ShowsSamples.push_back(s);
        }
        Y_ENSURE(result[bestScoreIndex].RandomSamples.size() + result[bestScoreIndex].ShowsSamples.size() == expectedHas);
        Y_ENSURE(result[hasNoIndex].RandomSamples.size() + result[hasNoIndex].ShowsSamples.size() == expectedNotHas);
    }

    enum ETokensSource {
        TS_ALL = 0,
        TS_PARAM = 1,
        TS_DIR = 2,
        TS_DIR1 = 3,
        TS_END = 4
    };

    void AddTokenToVec(TVector<TString>& result, const TString& token) {
        if (!token.empty()) {
            result.push_back(token);
        }
    }

    TVector<TString> GetSourceTokens(const TString& url, ETokensSource tokensSource) {
        const TUrlTokenization& tokenization = GetTokenezationFromCache(url);
        TVector<TString> result;
        for (const auto& pr : tokenization) {
            if (pr.first.StartsWith("pathLevel_")) {
                if (tokensSource == TS_DIR1 && pr.first == "pathLevel_0") {
                    AddTokenToVec(result, NormToken(pr.second));
                } else if (tokensSource == TS_ALL || tokensSource == TS_DIR) {
                    AddTokenToVec(result, NormToken(pr.second));
                }
            } else if (!pr.first.EndsWith("_WITHOUT_VALUE")) {
                if (tokensSource == TS_ALL || tokensSource == TS_PARAM) {
                    AddTokenToVec(result, NormToken(pr.first));
                    AddTokenToVec(result, NormToken(pr.second));
                }
            }
        }
        return result;
    }

    void GetSourceTopTokens(const TVector<NYT::TNode>& randomSample, const TVector<NYT::TNode>& showsSample, ETokensSource tokensSource, THashMap<TString, THashSet<TString>>& topTokens) {
        THashMap<TString, size_t> tokenCount;
        for (const auto& s : randomSample) {
            auto allTokens = GetSourceTokens(GetUrl(s), tokensSource);
            for (const auto& token : allTokens) {
                ++tokenCount[token];
            }
        }
        for (const auto& s : showsSample) {
            auto allTokens = GetSourceTokens(GetUrl(s), tokensSource);
            for (const auto& token : allTokens) {
                ++tokenCount[token];
            }
        }
        TVector<std::pair<TString, size_t>> tokenCountVec(tokenCount.begin(), tokenCount.end());
        Sort(tokenCountVec.begin(), tokenCountVec.end(), [=](const std::pair<TString, size_t>& lhs, const std::pair<TString, size_t>& rhs) {
            return lhs.second > rhs.second;
        });
        if (tokenCountVec.size() > 100) { //TODO const
            tokenCountVec.resize(100);
        }

        for (const auto& s : randomSample) {
            const TString& url = GetUrl(s);
            const auto& allTokens = GetAllTokensFromCache(url);
            THashSet<TString>& ut = topTokens[url];
            for (const auto& token : allTokens) {
                for (const auto& pr : tokenCountVec) {
                    if (pr.first == token) {
                        ut.insert(pr.first);
                        break;
                    }
                }
            }
        }
        for (const auto& s : showsSample) {
            const TString& url = GetUrl(s);
            const auto& allTokens = GetAllTokensFromCache(url);
            THashSet<TString>& ut = topTokens[url];
            for (const auto& token : allTokens) {
                for (const auto& pr : tokenCountVec) {
                    if (pr.first == token) {
                        ut.insert(pr.first);
                        break;
                    }
                }
            }
        }
    }

    void GetClusterPartitions(const TVector<NYT::TNode>& randomSample, const TVector<NYT::TNode>& showsSample, TSimplePartitions& result, bool greedy, TString& history,
            size_t maxPartitions, size_t minUrlsInPartition, ETokensSource tokensSource) {
        THashMap<TString, THashSet<TString>> topTokens;
        GetSourceTopTokens(randomSample, showsSample, tokensSource, topTokens);

        result.emplace_back(TSimplePartition());
        for (const auto& s : randomSample) {
            result.back().RandomSamples.push_back(s);
        }
        for (const auto& s : showsSample) {
            result.back().ShowsSamples.push_back(s);
        }
        while (result.size() < maxPartitions) {
            float bestScore = 0;
            size_t bestScoreIndex = Max<size_t>();
            TString bestScoreToken;
            size_t expectedHas = 0;
            size_t expectedNotHas = 0;
            if (greedy) {
                for (size_t partitionIndex = 0; partitionIndex < result.size(); ++partitionIndex) {
                    THashMap<TString, size_t> hasTokenCount;
                    for (const auto& s : result[partitionIndex].RandomSamples) {
                        const auto& allTokens = topTokens[GetUrl(s)];
                        for (const auto& token : allTokens) {
                            ++hasTokenCount[token];
                        }
                    }
                    for (const auto& s : result[partitionIndex].ShowsSamples) {
                        const auto& allTokens = topTokens[GetUrl(s)];
                        for (const auto& token : allTokens) {
                            ++hasTokenCount[token];
                        }
                    }
                    size_t totalInPartition = result[partitionIndex].RandomSamples.size() + result[partitionIndex].ShowsSamples.size();
                    Y_ENSURE(totalInPartition > 0);
                    for (const auto& pr : hasTokenCount) {
                        size_t hasSize = pr.second;
                        Y_ENSURE(hasSize <= totalInPartition);
                        size_t notHasSize = totalInPartition - hasSize;
                        size_t score = Min(hasSize, notHasSize);
                        if (score > bestScore) {
                            bestScore = score;
                            bestScoreIndex = partitionIndex;
                            bestScoreToken = pr.first;
                            expectedHas = hasSize;
                            expectedNotHas = notHasSize;
                        }
                    }
                }
            } else {
                Y_ENSURE(false);
/*
                for (size_t partitionIndex = 0; partitionIndex < result.size(); ++partitionIndex) {
                    float initial = CalcDispersionTotal(result[partitionIndex]);
                    if (initial < 0.001) {
                        continue;
                    }
                    TVector<THashSet<TString>> partTokens;
                    TVector<TFactorsForClustering> partFactors;
                    for (const auto& s : result[partitionIndex].RandomSamples) {
                        partTokens.push_back(topTokens[GetUrl(s)]);
                        partFactors.push_back(UrlFactorsCache[GetUrl(s)]);
                    }
                    for (const auto& s : result[partitionIndex].ShowsSamples) {
                        partTokens.push_back(topTokens[GetUrl(s)]);
                        partFactors.push_back(UrlFactorsCache[GetUrl(s)]);
                    }
                    if (partTokens.size() < minUrlsInPartition * 2) {
                        continue;
                    }

                    for (const auto& tcPr : tokenCountVec) {
                        const auto& token = tcPr.first;
                        TFactorsForClustering centerHas{0.0f, 0.0f, 0.0f}, centerNotHas{0.0f, 0.0f, 0.0f};
                        TVector<TFactorsForClustering> mulHas, mulNotHas;
                        for (size_t urlIndex = 0; urlIndex < partTokens.size(); ++urlIndex) {
                            if (partTokens[urlIndex].contains(token)) {
                                mulHas.push_back(partFactors[urlIndex]);
                                AddVec(centerHas, mulHas.back());
                            } else {
                                mulNotHas.push_back(partFactors[urlIndex]);
                                AddVec(centerNotHas, mulNotHas.back());
                            }
                        }
                        if (mulHas.size() < minUrlsInPartition || mulNotHas.size() < minUrlsInPartition) {
                            continue;
                        }
                        DivVec(centerHas, mulHas.size());
                        DivVec(centerNotHas, mulNotHas.size());
                        float sumHas = 0.0;
                        float sumNotHas = 0.0;
                        for (const auto& v : mulHas) {
                            sumHas += DistanceSqr(centerHas, v);
                        }
                        for (const auto& v : mulNotHas) {
                            sumNotHas += DistanceSqr(centerNotHas, v);
                        }
                        if (initial - sumHas - sumNotHas > bestScore) {
                            bestScore = initial - sumHas - sumNotHas;
                            bestScoreIndex = partitionIndex;
                            bestScoreToken = token;
                            expectedHas = mulHas.size();
                            expectedNotHas = mulNotHas.size();
                            //float dbgSumSimilarityInititial = 0.0, dbgSumSimilarityHas = 0.0f, dbgSumSimilarityNotHas = 0.0f;
                            dbgSumSimilarityInititial = initial;
                            dbgSumSimilarityHas = sumHas;
                            dbgSumSimilarityNotHas = sumNotHas;
                        }
                    }
                }
*/
            }
            if (expectedHas < minUrlsInPartition || expectedNotHas < minUrlsInPartition || bestScore == 0) {
                break;
            } else {
                Y_ENSURE(bestScoreIndex < result.size());
                if (!history.empty()) history += "; ";
                history += PartitionInformation(result[bestScoreIndex]) + " -> ";
                size_t beforeSize = result[bestScoreIndex].RandomSamples.size() + result[bestScoreIndex].ShowsSamples.size();
                Split(result, bestScoreIndex, bestScoreToken, expectedHas, expectedNotHas);
                history += bestScoreToken + " " + PartitionInformation(result[bestScoreIndex]) + " " + PartitionInformation(result.back());
                history += "[" + ToString(beforeSize) + "," + ToString(expectedHas) + "," + ToString(expectedNotHas) + "]";
            }
        }

        result.emplace_back(TSimplePartition());
        result.back().Partitions.push_back("__all__");
        for (const auto& s : randomSample) {
            result.back().RandomSamples.push_back(s);
        }
        for (const auto& s : showsSample) {
            result.back().ShowsSamples.push_back(s);
        }
        size_t totalAdd = 0;
        for (const auto& item : result) {
            Y_ENSURE(item.RandomSamples.size() + item.ShowsSamples.size() > 0);
            totalAdd += item.RandomSamples.size();
            totalAdd += item.ShowsSamples.size();
        }
        Y_ENSURE(totalAdd == (randomSample.size() + showsSample.size()) * 2);
    }

    void GetDirPartitions1Level(size_t maxPartitions, const TVector<NYT::TNode>& randomSample, const TVector<NYT::TNode>& showsSample, TSimplePartitions& result) {
        THashMap<TString, size_t> dirCount;
        for (const auto& s : randomSample) {
            const TString dir = GetDir1(s);
            if (!dir.empty()) {
                Y_ENSURE(GetAllTokensFromCache(s).contains(dir));
                ++dirCount[dir];
            }
        }
        for (const auto& s : showsSample) {
            const TString dir = GetDir1(s);
            if (!dir.empty()) {
                Y_ENSURE(GetAllTokensFromCache(s).contains(dir));
                ++dirCount[dir];
            }
        }
        TVector<std::pair<TString, size_t>> dirCountVec(dirCount.begin(), dirCount.end());
        Sort(dirCountVec.begin(), dirCountVec.end(), [=](const std::pair<TString, size_t>& lhs, const std::pair<TString, size_t>& rhs) {
            return lhs.second > rhs.second;
        });
        if (dirCountVec.size() > maxPartitions) {
            dirCountVec.resize(maxPartitions);
        }
        //is all to other?
        size_t totalCount = 0;
        for (const auto& pr : dirCountVec) {
            totalCount += pr.second;
        }

        for (const auto& pr : dirCountVec) {
            result.emplace_back(TSimplePartition());
            result.back().Partitions.push_back(pr.first);
        }
        result.emplace_back(TSimplePartition());
        result.emplace_back(TSimplePartition());
        result.back().Partitions.push_back("__all__");
        Y_ENSURE(result.size() >= 2);
        size_t allIndex = result.size() - 1;
        Y_ENSURE(result[allIndex].Partitions[0] == "__all__");
        for (const auto& s : randomSample) {
            size_t index = GetPartitionIndex(result, s);
            Y_ENSURE(index < allIndex);
            result[index].RandomSamples.push_back(s);
            result[allIndex].RandomSamples.push_back(s);
        }
        for (const auto& s : showsSample) {
            size_t index = GetPartitionIndex(result, s);
            Y_ENSURE(index < allIndex);
            result[index].ShowsSamples.push_back(s);
            result[allIndex].ShowsSamples.push_back(s);
        }
        bool allToEmpty = false;
        size_t emptyIndex = result.size() - 2;
        if (result[emptyIndex].ShowsSamples.empty() && result[emptyIndex].RandomSamples.empty()) {
            allToEmpty = true;
            for (const auto& s : randomSample) {
                result[emptyIndex].RandomSamples.push_back(s);
            }
            for (const auto& s : showsSample) {
                result[emptyIndex].ShowsSamples.push_back(s);
            }
        }
        //trim
        size_t curIndex = 0;
        for (size_t index = 0; index < result.size(); ++index) {
            if (!result[index].ShowsSamples.empty() || !result[index].RandomSamples.empty()) {
                if (curIndex != index) {
                    result[curIndex] = result[index];
                }
                ++curIndex;
            }
        }
        Y_ENSURE(curIndex >= 2);
        result.resize(curIndex);

        size_t totalAdd = 0;
        for (const auto& item : result) {
            Y_ENSURE(item.RandomSamples.size() + item.ShowsSamples.size() > 0);
            totalAdd += item.RandomSamples.size();
            totalAdd += item.ShowsSamples.size();
        }
        if (allToEmpty) {
            Y_ENSURE(totalAdd == (randomSample.size() + showsSample.size()) * 3);
        } else {
            Y_ENSURE(totalAdd == (randomSample.size() + showsSample.size()) * 2);
        }
    }

    void AddStatFactors(TSimplePartitions& result) {
        ui64 allTotal = result.back().RandomSamples.size() + result.back().ShowsSamples.size();
        Y_ENSURE(allTotal > 0);
        for (auto& partition : result) {
            partition.Factors.push_back(partition.RandomSamples.size() + partition.ShowsSamples.size());
            partition.Factors.push_back((partition.RandomSamples.size() + partition.ShowsSamples.size()) / (float)allTotal);
        }
    }

    void AddFactors(TSimplePartitions& result, bool randomSample, TString counterName) {
        ui64 allTotal = 0;
        for (const auto& node : randomSample ? result.back().RandomSamples : result.back().ShowsSamples) {
            allTotal += Get(node, counterName);
        }
        for (auto& partition : result) {
            ui64 total = 0;
            ui64 maxV = 0;
            ui64 countNonzero = 0;
            for (const auto& node : randomSample ? partition.RandomSamples : partition.ShowsSamples) {
                ui64 val = Get(node, counterName);
                maxV = Max(val, maxV);
                total += val;
                if (val > 0) {
                    ++countNonzero;
                }
            }
            partition.Factors.push_back(maxV);
            partition.Factors.push_back(total);
            partition.Factors.push_back(countNonzero);
            if (countNonzero > 0) {
                partition.Factors.push_back((float)total / (float)countNonzero);
            } else {
                partition.Factors.push_back(0.0f);
            }
            if (allTotal > 0) {
                partition.Factors.push_back((float)total / (float)allTotal);
            } else {
                partition.Factors.push_back(0.0f);
            }
        }
    }

    void AddFactors(TSimplePartitions& result, TString counterName) {
        ui64 allTotal = 0;
        for (const auto& node : result.back().RandomSamples) {
            allTotal += GetOrZero(node, counterName);
        }
        for (const auto& node : result.back().ShowsSamples) {
            allTotal += GetOrZero(node, counterName);
        }
        for (auto& partition : result) {
            TVector<ui64> values;
            for (const auto& node : partition.RandomSamples) {
                values.push_back(GetOrZero(node, counterName));
            }
            for (const auto& node : partition.ShowsSamples) {
                values.push_back(GetOrZero(node, counterName));
            }
            ui64 total = 0;
            ui64 maxV = 0;
            ui64 countNonzero = 0;
            ui64 partitionSize = 0;
            float totalLog = 0;
            for (auto val : values) {
                totalLog += log2(val + 1);
                maxV = Max(val, maxV);
                total += val;
                ++partitionSize;
                if (val > 0) {
                    ++countNonzero;
                }
            }
            partition.Factors.push_back(maxV);
            partition.Factors.push_back(total);
            partition.Factors.push_back(countNonzero);
            Y_ENSURE(partitionSize > 0);
            float avg = (float)total / (float)partitionSize;
            float avgLog = (float)totalLog / (float)partitionSize;
            partition.Factors.push_back(avg);
            partition.Factors.push_back(avgLog);
            if (countNonzero > 0) {
                //partition.Factors.push_back((float)total / (float)countNonzero);
                partition.Factors.push_back(totalLog / (float)countNonzero);
            } else {
                Y_ENSURE(total == 0);
                //partition.Factors.push_back(0.0f);
                partition.Factors.push_back(0.0f);
            }
            if (allTotal > 0) {
                partition.Factors.push_back((float)total / (float)allTotal);
            } else {
                partition.Factors.push_back(0.0f);
            }
            float disp = 0;
            for (auto val : values) {
                disp += ((float)log2(val + 1) - avgLog) * ((float)log2(val + 1) - avgLog);
            }
            partition.Factors.push_back(disp / (float)partitionSize);

            //TODO
            //avg by showed on search
            //avg by download samovar
        }
    }

public:
    Y_SAVELOAD_JOB(MaxRepresentativeCount);
    TReduceCalcHostAggrSimple() {}
    TReduceCalcHostAggrSimple(size_t maxRepresentativeCount)
        : MaxRepresentativeCount(maxRepresentativeCount)
    {
    }

    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        TVector<NYT::TNode> randomSample;
        TVector<NYT::TNode> showsSample;
        TokenizationCache.clear();
        AllTokensCache.clear();
        const TString host = input->GetRow()["host"].AsString();
        TString rndUrl;
        for (; input->IsValid(); input->Next()) {
            const auto& row = input->GetRow();
            if (row["type"].AsUint64() == 1 && randomSample.size() < MaxRepresentativeCount) {
                randomSample.push_back(row);
                rndUrl = row["url"].AsString();
            }
            if (row["type"].AsUint64() == 0) {
                showsSample.push_back(row);
                if (showsSample.size() > MaxRepresentativeCount * 5) {
                    KeepOnlyTopByHash(showsSample);
                }
            }
        }
        KeepOnlyTopByHash(showsSample);
        Y_ENSURE(randomSample.size() <= MaxRepresentativeCount);
        Y_ENSURE(showsSample.size() <= MaxRepresentativeCount);
        FillUrlFactorsCache(randomSample, showsSample);

        NYT::TNode outRow = NYT::TNode::CreateMap();
        outRow["host"] = host;
        outRow["random_sample_first_5"] = PrintFirstVecValues(randomSample, 5);
        outRow["top_shows_sample_first_5"] = PrintFirstVecValues(showsSample, 5);
        for (const TString& partitionName : {"clusters_greedy_15cl_5urlmin", "clusters_greedy_200cl_2urlmin"
                    , "clusters_greedy_50cl_2urlmin_param", "clusters_greedy_50cl_2urlmin_dir", "clusters_greedy_50cl_2urlmin_dir1"}) {
            TSimplePartitions partitions;
            if (partitionName == "clusters_greedy_15cl_5urlmin") {
                TString history;
                GetClusterPartitions(randomSample, showsSample, partitions, true, history, 15, 5, TS_ALL);
                outRow["clusters_greedy_15cl_5urlmin_history"] = history;
            } else if (partitionName == "clusters_greedy_200cl_2urlmin") {
                TString history;
                GetClusterPartitions(randomSample, showsSample, partitions, true, history, 300, 1, TS_ALL);
            } else if (partitionName == "clusters_greedy_50cl_2urlmin_param") {
                TString history;
                GetClusterPartitions(randomSample, showsSample, partitions, true, history, 50, 1, TS_PARAM);
                outRow["clusters_greedy_50cl_2urlmin_param_history"] = history;
            } else if (partitionName == "clusters_greedy_50cl_2urlmin_dir") {
                TString history;
                GetClusterPartitions(randomSample, showsSample, partitions, true, history, 50, 1, TS_DIR);
                outRow["clusters_greedy_50cl_2urlmin_dir_history"] = history;
            } else if (partitionName == "clusters_greedy_50cl_2urlmin_dir1") {
                TString history;
                GetClusterPartitions(randomSample, showsSample, partitions, true, history, 50, 1, TS_DIR1);
                outRow["clusters_greedy_50cl_2urlmin_dir1_history"] = history;
            } else {
                Y_ENSURE(false);
            }
            //2
            AddStatFactors(partitions);
            //8 * 2/3
            AddFactors(partitions, "count");
            AddFactors(partitions, "shows");
            if (partitionName == "clusters_greedy_50cl_2urlmin_param") {
                AddFactors(partitions, "clicks");
            }

            NYT::TNode partitionNode;
            SavePartitions(partitions, partitionNode);
            outRow[partitionName] = partitionNode;
        }
        if (!rndUrl.empty()) {
            outRow["rnd_url"] = rndUrl;
            auto it = AllTokensCache.find(rndUrl);
            Y_ENSURE(it != AllTokensCache.end());
            outRow["rnd_url_tokens_cache"] = JoinStrings(it->second.begin(), it->second.end(), ";");
            TString differentSourcesDbg;
            auto v = GetSourceTokens(rndUrl, TS_ALL);
            differentSourcesDbg = "all_sources=" + JoinStrings(v.begin(), v.end(), ";");
            v = GetSourceTokens(rndUrl, TS_PARAM);
            differentSourcesDbg = differentSourcesDbg + ", param=" + JoinStrings(v.begin(), v.end(), ";");
            v = GetSourceTokens(rndUrl, TS_DIR);
            differentSourcesDbg = differentSourcesDbg + ", dir=" + JoinStrings(v.begin(), v.end(), ";");
            v = GetSourceTokens(rndUrl, TS_DIR1);
            differentSourcesDbg = differentSourcesDbg + ", dir1=" + JoinStrings(v.begin(), v.end(), ";");
            outRow["rnd_url_different_sources"] = differentSourcesDbg;
        }
        output->AddRow(outRow);
    }
};
REGISTER_REDUCER(TReduceCalcHostAggrSimple)

class TReduceCalcFeatures
    : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{
private:
    void AddFactors(TVector<float>& factors, const TString& url, const TSimplePartitions& partitions) {
        size_t index = GetPartitionIndex(partitions, url);
        Y_ENSURE(index + 1 < partitions.size());
        for (const auto f : partitions[index].Factors) {
            factors.push_back(f);
        }
    }

    void AddHostFactors(TVector<float>& factors, const TSimplePartitions& partitions) {
        Y_ENSURE(partitions.size() >= 2);
        Y_ENSURE(partitions.back().Partitions[0] == "__all__");
        for (const auto f : partitions.back().Factors) {
            factors.push_back(f);
        }
    }

public:
    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        bool hasHostFeatures = false;
        TSimplePartitions partitionsClustersGreedy15Cl5UrlMin, partitionsClustersGreedy200Cl2UrlMin,
            partitionsClustersGreedy50Cl2UrlMinParam, partitionsClustersGreedy50Cl2UrlMinDir, partitionsClustersGreedy50Cl2UrlMinDir1;
        if (input->GetTableIndex() == 0) {
            hasHostFeatures = true;
            LoadPartitions(input->GetRow()["clusters_greedy_15cl_5urlmin"], partitionsClustersGreedy15Cl5UrlMin);
            LoadPartitions(input->GetRow()["clusters_greedy_200cl_2urlmin"], partitionsClustersGreedy200Cl2UrlMin);
            LoadPartitions(input->GetRow()["clusters_greedy_50cl_2urlmin_param"], partitionsClustersGreedy50Cl2UrlMinParam);
            LoadPartitions(input->GetRow()["clusters_greedy_50cl_2urlmin_dir"], partitionsClustersGreedy50Cl2UrlMinDir);
            LoadPartitions(input->GetRow()["clusters_greedy_50cl_2urlmin_dir1"], partitionsClustersGreedy50Cl2UrlMinDir1);
            input->Next();
        }
        for (; input->IsValid(); input->Next()) {
            Y_ENSURE(input->GetTableIndex() == 1);
            const auto& url = input->GetRow()["url"].AsString();
            const auto& host = input->GetRow()["host"].AsString();
            const auto& urlNorm = input->GetRow()["url_norm"].AsString();
            TVector<float> factors;
            if (!hasHostFeatures) {
                factors = TVector<float>(SIMPLE_FACTORS_CALC_COUNT, 0);
            } else {
                AddHostFactors(factors, partitionsClustersGreedy50Cl2UrlMinParam);
                AddFactors(factors, urlNorm, partitionsClustersGreedy15Cl5UrlMin);
                AddFactors(factors, urlNorm, partitionsClustersGreedy200Cl2UrlMin);
                AddFactors(factors, urlNorm, partitionsClustersGreedy50Cl2UrlMinParam);
                AddFactors(factors, urlNorm, partitionsClustersGreedy50Cl2UrlMinDir);
                AddFactors(factors, urlNorm, partitionsClustersGreedy50Cl2UrlMinDir1);
            }
            Y_ENSURE(factors.size() == SIMPLE_FACTORS_CALC_COUNT);

            NYT::TNode outRow = NYT::TNode::CreateMap();
            outRow["url"] = url;

            NYT::TNode partitionsClustersGreedy15Cl5UrlMinDbg;
            SavePartitions(partitionsClustersGreedy15Cl5UrlMin, partitionsClustersGreedy15Cl5UrlMinDbg);
            outRow["clusters_greedy_15cl_5urlmin"] = partitionsClustersGreedy15Cl5UrlMinDbg;

            NYT::TNode partitionsClustersGreedy200Cl2UrlMinDbg;
            SavePartitions(partitionsClustersGreedy200Cl2UrlMin, partitionsClustersGreedy200Cl2UrlMinDbg);
            outRow["clusters_greedy_200cl_2urlmin"] = partitionsClustersGreedy200Cl2UrlMinDbg;

            NYT::TNode partitionsClustersGreedy50Cl2UrlMinParamDbg;
            SavePartitions(partitionsClustersGreedy50Cl2UrlMinParam, partitionsClustersGreedy50Cl2UrlMinParamDbg);
            outRow["clusters_greedy_50cl_2urlmin_param"] = partitionsClustersGreedy50Cl2UrlMinParamDbg;

            NYT::TNode partitionsClustersGreedy50Cl2UrlMinDirDbg;
            SavePartitions(partitionsClustersGreedy50Cl2UrlMinDir, partitionsClustersGreedy50Cl2UrlMinDirDbg);
            outRow["clusters_greedy_50cl_2urlmin_dir"] = partitionsClustersGreedy50Cl2UrlMinDirDbg;

            NYT::TNode partitionsClustersGreedy50Cl2UrlMinDir1Dbg;
            SavePartitions(partitionsClustersGreedy50Cl2UrlMinDir1, partitionsClustersGreedy50Cl2UrlMinDir1Dbg);
            outRow["clusters_greedy_50cl_2urlmin_dir1"] = partitionsClustersGreedy50Cl2UrlMinDir1Dbg;

            outRow["host"] = host;
            TString factorsStr;
            for (const auto& f : factors) {
                if (!factorsStr.empty()) factorsStr += "\t";
                factorsStr += ToString(f);
            }
            outRow["factors"] = factorsStr;
            output->AddRow(outRow);
        }
    }
};
REGISTER_REDUCER(TReduceCalcFeatures)

int main_calc_factors_simple(int argc, const char* argv[])
{
    NLastGetopt::TOpts options;

    TString mrServerStr;
    TString inputTable;
    TString poolDir;
    TString outputTable;

    options
        .AddCharOption('s', "--  MapReduce server")
        .StoreResult(&mrServerStr)
        .DefaultValue("hahn")
        .Optional();

    options
        .AddCharOption('i', "-- input table")
        .StoreResult(&inputTable)
        .Required();

    options
        .AddCharOption('p', "-- pool directory")
        .StoreResult(&poolDir)
        .Required();

    options
        .AddCharOption('o', "-- output table")
        .StoreResult(&outputTable)
        .Required();


    NLastGetopt::TOptsParseResult parser(&options, argc, argv);
    auto client = NYT::CreateClient(mrServerStr);

    TString hostAggrTable = outputTable + ".host_aggr";
    TString poolUrls = outputTable + ".pool_urls";
    {
        client->Reduce(
            NYT::TReduceOperationSpec()
                .AddInput<NYT::TNode>(inputTable)
                .AddOutput<NYT::TNode>(NYT::TRichYPath(hostAggrTable).SortedBy("host"))
                .ReduceBy("host"),
                new TReduceCalcHostAggrSimple(50000)
        );
    }
    client->Map(
        NYT::TMapOperationSpec()
            .AddInput<NYT::TNode>(poolDir + "/features")
            .AddOutput<NYT::TNode>(NYT::TRichYPath(poolUrls)),
        new TMapPrepareLearningPool
    );
    client->Sort(NYT::TSortOperationSpec().AddInput(poolUrls).Output(poolUrls).SortBy("host"));
    {
        NYT::TReduceOperationSpec reduceSpec;
        reduceSpec.AddInput<NYT::TNode>(hostAggrTable);
        reduceSpec.AddInput<NYT::TNode>(poolUrls);
        reduceSpec.AddOutput<NYT::TNode>(NYT::TRichYPath(outputTable).SortedBy("host"));
        reduceSpec.ReduceBy("host");
        client->Reduce(
            reduceSpec,
            new TReduceCalcFeatures
        );
    }
    client->Sort(NYT::TSortOperationSpec().AddInput(outputTable).Output(outputTable).SortBy("url"));
    return 0;
}

void CopyAndPatchRobotPoolTables(NYT::IClientPtr client, const TString& applyPool, const TString& outputFolder) {
    {
        client->Copy(applyPool +  "/factor_slices", outputFolder + "/factor_slices", NYT::TCopyOptions().Force(true).Recursive(true));
    }
    TString slicesStr;
    {
        auto reader = client->CreateTableReader<NYT::TNode>(outputFolder + "/factor_slices");
        Y_ENSURE(reader->IsValid());
        slicesStr = reader->GetRow()["value"].AsString();
        reader->Next();
        Y_ENSURE(!reader->IsValid());
    }
    size_t offset = 0;
    {
        auto reader = client->CreateTableReader<NYT::TNode>(applyPool + "/factor_names");
        auto writer = client->CreateTableWriter<NYT::TNode>(outputFolder + "/factor_names");
        for (; reader->IsValid(); reader->Next()) {
            const auto& row = reader->GetRow();
            Y_ENSURE(row["key"].AsString() == ToString(offset));
            writer->AddRow(row);
            ++offset;
        }
        const TVector<TString>& factorNames = NSamovar::TInhostFactorAggrConfig::Get()->GetAllFactorNames();
        slicesStr = slicesStr + " joined[" + ToString(offset) + ";" + ToString(offset + factorNames.size()) + ")";
        for (size_t i = 0; i < factorNames.size(); ++i) {
            writer->AddRow(NYT::TNode()("key", ToString(offset + i))("value", factorNames[i]));
        }
    }
    {
        auto writer = client->CreateTableWriter<NYT::TNode>(outputFolder + "/factor_slices");
        writer->AddRow(NYT::TNode()("key", "0")("value", slicesStr));
    }
}

class TReduceJoinFeatures
    : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{

public:
    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        Y_ENSURE(input->GetTableIndex() == 0);
        TString factorsStr = input->GetRow()["factors"].AsString();
        for (; input->IsValid(); input->Next()) {
            if (input->GetTableIndex() == 1) {
                const auto& inRow = input->GetRow();
                Y_ENSURE(!factorsStr.empty());
                NYT::TNode outRow = NYT::TNode::CreateMap();
                outRow["joined"] = factorsStr;
                outRow["key"] = inRow["key"];
                outRow["index"] = inRow["index"];
                outRow["value"] = inRow["value"].AsString() + "\t" + factorsStr;
                output->AddRow(outRow);
            } else {
                Y_ENSURE(input->GetRow()["factors"].AsString() == factorsStr);
            }
        }
    }
};
REGISTER_REDUCER(TReduceJoinFeatures)

int main_join_factors(int argc, const char* argv[])
{
    NLastGetopt::TOpts options;

    TString mrServerStr;
    TString inputDir;
    TString featuresTable;
    TString outputDir;
    TString configPath;

    options
        .AddCharOption('s', "--  MapReduce server")
        .StoreResult(&mrServerStr)
        .DefaultValue("hahn")
        .Optional();

    options
        .AddCharOption('i', "-- input pool dir")
        .StoreResult(&inputDir)
        .Required();

    options
        .AddCharOption('o', "-- output pool dir")
        .StoreResult(&outputDir)
        .Required();

    options
        .AddCharOption('f', "-- features table")
        .StoreResult(&featuresTable)
        .Required();

    options
        .AddCharOption('c', "-- config file name")
        .StoreResult(&configPath)
        .Required();

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);
    auto client = NYT::CreateClient(mrServerStr);

    InitConfing(configPath);

    CopyAndPatchRobotPoolTables(client, inputDir, outputDir);
    client->Map(
        NYT::TMapOperationSpec()
            .AddInput<NYT::TNode>(inputDir + "/features")
            .AddOutput<NYT::TNode>(NYT::TRichYPath(outputDir + "/features")),
        new TMapPrepareLearningPool
    );
    client->Sort(NYT::TSortOperationSpec().AddInput(outputDir + "/features").Output(outputDir + "/features").SortBy("url"));
    {
        NYT::TReduceOperationSpec reduceSpec;
        reduceSpec.AddInput<NYT::TNode>(featuresTable);
        reduceSpec.AddInput<NYT::TNode>(outputDir + "/features");
        reduceSpec.AddOutput<NYT::TNode>(NYT::TRichYPath(outputDir + "/features").SortedBy("url"));
        reduceSpec.ReduceBy("url");
        client->Reduce(
            reduceSpec,
            new TReduceJoinFeatures
        );
    }

    return 0;
}

int main_generate_factor_groups(int argc, const char* argv[])
{
    NLastGetopt::TOpts options;

    TString outputFile;
    TString configPath;

    options
        .AddCharOption('o', "-- output file")
        .StoreResult(&outputFile)
        .Required();

    options
        .AddCharOption('c', "-- config file name")
        .StoreResult(&configPath)
        .Required();

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);

    InitConfing(configPath);
    {
        TFixedBufferFileOutput outputStream(outputFile);
        for (size_t partitionIndex = 0; partitionIndex < NSamovar::TInhostFactorAggrConfig::Get()->PartitionSize(); ++partitionIndex) {
            const NSamovarConfig::TInhostFactorAggrConfig::TPartition& partitionConfig = NSamovar::TInhostFactorAggrConfig::Get()->GetPartition(partitionIndex);
            TVector<bool> isHostVec = {false};
            if (partitionConfig.GetName() == "WORD1_TOKENS_30_SIZE_ALL_SIGNALS") {
                isHostVec = {true, false};
            }
            for (bool isHost : isHostVec) {
                TString isHostStr = isHost ? "true" : "false";
                outputStream << "    {" << Endl;
                outputStream << "        PartitionName: \"" << partitionConfig.GetName() << "\"," << Endl;
                outputStream << "        Signal: ST_NONE," << Endl;
                outputStream << "        IsHost: " << isHostStr << "," << Endl;
                outputStream << "        IsStat: true" << Endl;
                outputStream << "    }," << Endl;
                for (size_t si = 0; si < partitionConfig.SignalsSize(); ++si) {
                    NSamovarConfig::TInhostFactorAggrConfig::EInhostFactorAggrSignalType signalType = partitionConfig.GetSignals(si);
                    outputStream << "    {" << Endl;
                    outputStream << "        PartitionName: \"" << partitionConfig.GetName() << "\"," << Endl;
                    outputStream << "        Signal: " << NSamovarConfig::TInhostFactorAggrConfig::EInhostFactorAggrSignalType_Name(signalType)
                            << "," << Endl;
                    outputStream << "        IsHost: " << isHostStr << "," << Endl;
                    outputStream << "        IsStat: false" << Endl;
                    outputStream << "    }," << Endl;
                }
            }
        }
    }

    return 0;
}

int main_generate_factor_names(int argc, const char* argv[])
{
    NLastGetopt::TOpts options;

    TString outputFile;
    TString configPath;

    options
        .AddCharOption('o', "-- output file")
        .StoreResult(&outputFile)
        .Required();

    options
        .AddCharOption('c', "-- config file name")
        .StoreResult(&configPath)
        .Required();

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);

    InitConfing(configPath);
    {
        TFixedBufferFileOutput outputStream(outputFile);
        outputStream << "enum EInhostFactor {" << Endl;
        const TVector<TString>& factorNames = NSamovar::TInhostFactorAggrConfig::Get()->GetAllFactorNames();
        for (size_t i = 0; i < factorNames.size(); ++i) {
            outputStream << "    " << factorNames[i] << " = " << i << ";" << Endl;
        }
        outputStream << "}" << Endl;
    }

    return 0;
}

namespace NSamovar {

    struct TUserData {
        size_t Shows7 = 0;
        size_t Shows15 = 0;
        size_t Shows90 = 0;
        size_t Clicks45 = 0;
        size_t Browse7 = 0;
        size_t Browse70 = 0;
    };

        void CollectUserdataCounters(const TUrlRecord& url, TUserData& userData) {
            if (!url.HasDirectData() || url.GetDirectData().GetUserData().DateHistoRecSize() == 0) {
                return;
            }
            for (const auto& rec : Reversed(url.GetDirectData().GetUserData().GetDateHistoRec())) {
                for (const auto& counter : rec.GetLogCounters()) {
                    const auto count = counter.GetCount();
                    switch (counter.GetLogType()) {
                        case NLemurUserData::LCT_YANDEX_WEB_SHOWS: {
                            if (rec.GetDate() + TDuration::Days(7).Seconds() >= GetNow().Seconds()) {
                                userData.Shows7 += count;
                            }
                            if (rec.GetDate() + TDuration::Days(15).Seconds() >= GetNow().Seconds()) {
                                userData.Shows15 += count;
                            }
                            if (rec.GetDate() + TDuration::Days(90).Seconds() >= GetNow().Seconds()) {
                                userData.Shows90 += count;
                            }
                            break;
                        }
                        case NLemurUserData::LCT_YANDEX_WEB_CLICKS: {
                            if (rec.GetDate() + TDuration::Days(45).Seconds() >= GetNow().Seconds()) {
                                userData.Clicks45 += count;
                            }
                            break;
                        }
                        case NLemurUserData::LCT_SPY_LOG_URL:
                        case NLemurUserData::LCT_WATCH_LOG_URL:
                        {
                            if (rec.GetDate() + TDuration::Days(7).Seconds() >= GetNow().Seconds()) {
                                userData.Browse7 += count;
                            }
                            if (rec.GetDate() + TDuration::Days(70).Seconds() >= GetNow().Seconds()) {
                                userData.Browse70 += count;
                            }
                            break;
                        }
                        default:
                            break;
                    }
                }
            }
        }

};

int main_test_collect_userdata(int argc, const char* argv[])
{
    NLastGetopt::TOpts options;

    TString configPath;

    options
        .AddCharOption('c', "-- config file name")
        .StoreResult(&configPath)
        .Required();

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);

    NSamovarConfig::TInstanceConfig instanceConfig;
    ParseFromTextFormat(configPath, instanceConfig);

    auto pool = NYT::New<NYT::NConcurrency::TThreadPool>(16, "pool");
    auto invoker = pool->GetInvoker();
    NSamovar::TSamovarClient samovarClient(instanceConfig, invoker);
    auto urlRecord = samovarClient.GetUrlRecord("https://vk.com");
    Y_ENSURE(urlRecord);

    NSamovar::TUserData userData;
    NSamovar::CollectUserdataCounters(*urlRecord, userData);
    Cerr << "counters: " << userData.Shows7 << " " << userData.Shows15 << " " << userData.Shows90 << " "
         << userData.Clicks45 << " " << userData.Browse7 << " " << userData.Browse70 << Endl;

    return 0;
}


class TReduceKeepOneHost
    : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{
public:
    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        NYT::TNode outRow = NYT::TNode::CreateMap();
        outRow["host"] = input->GetRow()["host"];
        output->AddRow(outRow);
    }
};
REGISTER_REDUCER(TReduceKeepOneHost)

bool HasUserData(const NSamovar::NRecord::TInhostPartitions& partitions) {
    for (size_t partitionIndex = 0; partitionIndex < partitions.PartitionSize(); ++partitionIndex) {
        const auto& partition = partitions.GetPartition(partitionIndex);
        if (partition.GetName() == "WORD1_TOKENS_30_SIZE_ALL_SIGNALS") {
            const NSamovar::NRecord::TInhostNodeData& total = partition.GetTotal();
            for (size_t signalCountersIndex = 0; signalCountersIndex < total.SignalCountersSize(); ++signalCountersIndex) {
                const auto& signalCountersTotal = total.GetSignalCounters(signalCountersIndex);
                if (signalCountersTotal.GetCountNonZero() > 0 && (signalCountersTotal.GetSignal() == NSamovarConfig::TInhostFactorAggrConfig::ST_SHOWS_7_DAYS ||
                    signalCountersTotal.GetSignal() == NSamovarConfig::TInhostFactorAggrConfig::ST_SHOWS_15_DAYS ||
                    signalCountersTotal.GetSignal() == NSamovarConfig::TInhostFactorAggrConfig::ST_SHOWS_90_DAYS ||
                    signalCountersTotal.GetSignal() == NSamovarConfig::TInhostFactorAggrConfig::ST_CLICKS_45_DAYS ||
                    signalCountersTotal.GetSignal() == NSamovarConfig::TInhostFactorAggrConfig::ST_BROWSE_7_DAYS ||
                    signalCountersTotal.GetSignal() == NSamovarConfig::TInhostFactorAggrConfig::ST_BROWSE_70_DAYS)) {
                    return true;
                }
            }
        }
    }
    return false;
}

int main_test_prod_inhost_partitions(int argc, const char* argv[])
{
    NLastGetopt::TOpts options;

    TString mrServerStr;
    TString instanceConfigPath;
    TString outputTable;
    TString configPath;
    TString poolDir;

    options
        .AddCharOption('s', "--  MapReduce server")
        .StoreResult(&mrServerStr)
        .DefaultValue("hahn")
        .Optional();

    options
        .AddCharOption('i', "-- instance config path")
        .StoreResult(&instanceConfigPath)
        .Required();

    options
        .AddCharOption('o', "-- output table")
        .StoreResult(&outputTable)
        .Required();

    options
        .AddCharOption('c', "-- config file name")
        .StoreResult(&configPath)
        .Required();

    options
        .AddCharOption('p', "-- pool directory")
        .StoreResult(&poolDir)
        .Required();

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);
    auto client = NYT::CreateClient(mrServerStr);

    TString poolUrls = outputTable + ".pool_urls";
    TString hostsTable = outputTable + ".hosts";
    TString protosTable = outputTable + ".protos";
    {
        client->Map(
            NYT::TMapOperationSpec()
                .AddInput<NYT::TNode>(poolDir + "/features")
                .AddOutput<NYT::TNode>(NYT::TRichYPath(poolUrls)),
            new TMapPrepareLearningPool
        );
    }
    client->Sort(NYT::TSortOperationSpec().AddInput(poolUrls).Output(poolUrls).SortBy("host"));
    {
        NYT::TReduceOperationSpec reduceSpec;
        reduceSpec.AddInput<NYT::TNode>(poolUrls);
        reduceSpec.AddOutput<NYT::TNode>(NYT::TRichYPath(hostsTable).SortedBy("host"));
        reduceSpec.ReduceBy("host");
        client->Reduce(
            reduceSpec,
            new TReduceKeepOneHost
        );
    }
    TVector<TString> hosts;
    {
        auto reader = client->CreateTableReader<NYT::TNode>(hostsTable);
        for (; reader->IsValid(); reader->Next()) {
            hosts.push_back(reader->GetRow()["host"].AsString());
        }
    }
    Cerr << "All hosts readed from MR" << Endl;
    {
        size_t totalHostsWriten = 0;
        auto writer = client->CreateTableWriter<NYT::TNode>(protosTable);
        NSamovarConfig::TInstanceConfig instanceConfig;
        ParseFromTextFormat(instanceConfigPath, instanceConfig);

        auto pool = NYT::New<NYT::NConcurrency::TThreadPool>(16, "pool");
        auto invoker = pool->GetInvoker();
        NSamovar::TSamovarClient samovarClient(instanceConfig, invoker);
        size_t batchSize = 2000;
        size_t curPos = 0;
        while (curPos < hosts.size()) {
            size_t curEnd = Min(curPos + batchSize, hosts.size());
            TVector<TString> batchHosts;
            for (size_t i = curPos; i < curEnd; ++i) {
                batchHosts.push_back(hosts[i]);
            }
            while (true) {
                try {
                    auto batchResult = samovarClient.GetHostRecords(batchHosts);
                    for (const auto& res : batchResult) {
                        if (res.second && !res.second->GetHost().empty() && res.second->GetInhostPartitionsState().Exists()) {
                            NYT::TNode outRow = NYT::TNode::CreateMap();
                            outRow["host"] = res.second->GetHost();
                            outRow["result"] = res.second->GetInhostPartitionsState().GetProto().SerializeAsString();
                            outRow["has_user_data"] = HasUserData(res.second->GetInhostPartitionsState().GetProto());
                            writer->AddRow(outRow);
                            ++totalHostsWriten;
                        }
                    }
                    break;
                } catch (const NYT::TErrorException& e) {
                    Cerr << e.what() << Endl;
                }
            }
            Cerr << "Batch finished [" << curPos << "," << curEnd << ")" << Endl;
            curPos = curEnd;
        }
        Cerr << "End write protosTable, totalHostsWriten=" << totalHostsWriten << Endl;
    }
    client->Sort(NYT::TSortOperationSpec().AddInput(protosTable).Output(protosTable).SortBy("host"));
    {
        NYT::TReduceOperationSpec reduceSpec;
        reduceSpec.AddInput<NYT::TNode>(protosTable);
        reduceSpec.AddInput<NYT::TNode>(poolUrls);
        reduceSpec.AddOutput<NYT::TNode>(NYT::TRichYPath(outputTable).SortedBy("host"));
        reduceSpec.ReducerSpec(NYT::TUserJobSpec().AddLocalFile(configPath));
        reduceSpec.ReduceBy("host");
        client->Reduce(
            reduceSpec,
            new TReduceCalcFeaturesProd(GetFileNameComponent(configPath))
        );
    }
    client->Sort(NYT::TSortOperationSpec().AddInput(outputTable).Output(outputTable).SortBy("url"));
    return 0;
}

int main_test_factors_dump(int argc, const char* argv[])
{
    NLastGetopt::TOpts options;

    TString mrServerStr;
    TString inputTable;

    options
        .AddCharOption('s', "--  MapReduce server")
        .StoreResult(&mrServerStr)
        .DefaultValue("arnold")
        .Optional();

    options
        .AddCharOption('i', "-- input table")
        .StoreResult(&inputTable)
        .Required();

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);
    auto client = NYT::CreateClient(mrServerStr);

    {
        auto reader = client->CreateTableReader<NYT::TNode>(inputTable);
        for (; reader->IsValid(); reader->Next()) {
            Cerr << reader->GetRow()["Key"].AsString() << Endl;
            NSamovarFactorDump::TFactorsDump factorsDump;
            bool res = factorsDump.ParseFromString(reader->GetRow()["Data"].AsString());
            Y_ENSURE(res);
            NSamovar::DecompressSlicesIfNeed(factorsDump);
            for (size_t i = 0; i < factorsDump.SlicesSize(); ++i) {
                const auto& slice = factorsDump.GetSlices(i);
                if (slice.GetSliceId() == NSamovarFactorSlice::ESamovarFactorSlice::Inhost) {
                    for (size_t j = 0; j < slice.ByZoneFactorsSize(); ++j) {
                        const auto& zoneFactors = slice.GetByZoneFactors(j);
                        TString outStr = ToString(zoneFactors.GetZoneId()) + " " + ToString(zoneFactors.FactorsSize());
                        for (size_t k = 0; k < zoneFactors.FactorsSize(); ++k) {
                            outStr += " " + ToString(zoneFactors.GetFactors(k));
                        }
                        Cerr << outStr << Endl;
                    }
                }
            }
        }
    }
    return 0;
}

struct TPartitionsFilter : public NYT::ISerializableForJob {
public:
    size_t MinUserSearchAndUserBrowse = 0;
    size_t MinUserSearch = 0;
    size_t MinUserBrowse = 0;
    size_t MinHostSize = 0;

    Y_SAVELOAD_JOB(MinUserSearchAndUserBrowse, MinUserSearch, MinUserBrowse, MinHostSize);

    void AddOptions(NLastGetopt::TOpts& options) {
        options.AddLongOption("min-user-search-and-user-browse", "MinUserSearchAndUserBrowse")
            .StoreResult(&MinUserSearchAndUserBrowse)
            .DefaultValue("0")
            .Optional();
        options.AddLongOption("min-user-search", "MinUserSearch")
            .StoreResult(&MinUserSearch)
            .DefaultValue("0")
            .Optional();
        options.AddLongOption("min-user-browse", "MinUserBrowse")
            .StoreResult(&MinUserBrowse)
            .DefaultValue("0")
            .Optional();
        options.AddLongOption("min-host-size", "MinHostSize")
            .StoreResult(&MinHostSize)
            .DefaultValue("0")
            .Optional();
    }

    void Print() {
        Cerr << "MinUserSearchAndUserBrowse=" << MinUserSearchAndUserBrowse << Endl;
        Cerr << "MinUserSearch=" << MinUserSearch << Endl;
        Cerr << "MinUserBrowse=" << MinUserBrowse << Endl;
        Cerr << "MinHostSize=" << MinHostSize << Endl;
    }

    bool IsPass(ui64 hostSize, double countShows90, double countBrowse70) {
        if (MinUserSearchAndUserBrowse > 0) {
            if (countShows90 + countBrowse70 >= MinUserSearchAndUserBrowse) {
                return true;
            }
        } else {
            if (MinUserSearch > 0 && countShows90 >= MinUserSearch) {
                return true;
            }
            if (MinUserBrowse > 0 && countBrowse70 >= MinUserBrowse) {
                return true;
            }
        }
        if (MinHostSize > 0 && hostSize >= MinHostSize) {
            return true;
        }
        return false;
    }
};


class TVanishTrashHostsPool: public NYT::IMapper<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>> {
private:
    TPartitionsFilter PartitionsFilter;
    size_t FirstInhostFactorIndex;

    size_t FeatureIndexWithOffset(size_t featureIndex) {
        return featureIndex + 3;
    }

public:
    Y_SAVELOAD_JOB(PartitionsFilter, FirstInhostFactorIndex);

    TVanishTrashHostsPool() {
    }

    TVanishTrashHostsPool(const TPartitionsFilter& partitionsFilter, size_t firstInhostFactorIndex)
        : PartitionsFilter(partitionsFilter)
        , FirstInhostFactorIndex(firstInhostFactorIndex)
    {
    }

    void Do(TReader* reader, TWriter* writer) override {
        for (; reader->IsValid(); reader->Next()) {
            const auto& row = reader->GetRow();
            TVector<TString> valueTokens;
            Split(row["value"].AsString(), "\t", valueTokens);
            bool needVanish = false;
            ui64 hostSizeMin = FromString<float>(valueTokens[FeatureIndexWithOffset(FirstInhostFactorIndex +
                NSamovarFactors::EInhostFactor::WORD1_TOKENS_30_SIZE_ALL_SIGNALS__HOST__STAT__SIZE)]);
            double countShows90 = FromString<float>(valueTokens[FeatureIndexWithOffset(FirstInhostFactorIndex +
                NSamovarFactors::EInhostFactor::WORD1_TOKENS_30_SIZE_ALL_SIGNALS__ST_SHOWS_90_DAYS__HOST__SUM)]);
            double countBrowse70 = FromString<float>(valueTokens[FeatureIndexWithOffset(FirstInhostFactorIndex +
                NSamovarFactors::EInhostFactor::WORD1_TOKENS_30_SIZE_ALL_SIGNALS__ST_BROWSE_70_DAYS__HOST__SUM)]);
            if (!PartitionsFilter.IsPass(hostSizeMin, countShows90, countBrowse70)) {
                needVanish = true;
            }
            if (needVanish) {
                for (size_t i = FeatureIndexWithOffset(FirstInhostFactorIndex); i < valueTokens.size(); ++i) {
                    valueTokens[i] = "0";
                }
            }
            TString newValueStr;
            for (const auto& str : valueTokens) {
                if (!newValueStr.empty()) newValueStr += "\t";
                newValueStr += str;
            }

            NYT::TNode outRow = NYT::TNode::CreateMap();
            outRow["key"] = row["key"];
            outRow["index"] = row["index"];
            outRow["value"] = newValueStr;
            writer->AddRow(outRow);
        }
    }
};
REGISTER_MAPPER(TVanishTrashHostsPool);

int main_vanish_trash_hosts_pool(int argc, const char* argv[]) {
    NLastGetopt::TOpts options;

    TString mrServerStr;
    TString inputDir;
    TString outputDir;
    TPartitionsFilter PartitionsFilter;
    size_t firstInhostFactorIndex = 0;

    options
        .AddCharOption('s', "--  MapReduce server")
        .StoreResult(&mrServerStr)
        .DefaultValue("hahn")
        .Optional();

    options
        .AddCharOption('i', "-- input pool dir")
        .StoreResult(&inputDir)
        .Required();

    options
        .AddCharOption('o', "-- output pool dir")
        .StoreResult(&outputDir)
        .Required();

    options
        .AddCharOption('f', "-- firstInhostFactorIndex")
        .StoreResult(&firstInhostFactorIndex)
        .Required();

    PartitionsFilter.AddOptions(options);

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);
    auto client = NYT::CreateClient(mrServerStr);
    PartitionsFilter.Print();
    Cerr << firstInhostFactorIndex << Endl;

    {
        client->Copy(inputDir +  "/factor_slices", outputDir + "/factor_slices", NYT::TCopyOptions().Force(true).Recursive(true));
        client->Copy(inputDir +  "/factor_names", outputDir + "/factor_names", NYT::TCopyOptions().Force(true));
        client->Copy(inputDir +  "/features", outputDir + "/features", NYT::TCopyOptions().Force(true));
    }
    client->Map(
        NYT::TMapOperationSpec()
            .AddInput<NYT::TNode>(inputDir +  "/features")
            .AddOutput<NYT::TNode>(NYT::TRichYPath(outputDir + "/features")),
        new TVanishTrashHostsPool(PartitionsFilter, firstInhostFactorIndex)
    );

    return 0;
}

class TVanishTrashHostsProd: public NYT::IMapper<NYT::TTableReader<NSamovarSchema::TPrimaryHostDataRow>, NYT::TTableWriter<NSamovarSchema::TPrimaryHostDataRow>> {
private:
    TPartitionsFilter PartitionsFilter;

    bool IsNotTrashPartitions(const NSamovar::NRecord::TInhostPartitions& partitions) {
        ui64 hostSizeMin = 0;
        double countShows90 = 0;
        double countBrowse70 = 0;
        for (size_t partitionIndex = 0; partitionIndex < partitions.PartitionSize(); ++partitionIndex) {
            const auto& partition = partitions.GetPartition(partitionIndex);
            if (partition.GetName() == "DIR1_TOKENS_10_SIZE_ALL_SIGNALS") {
                const NSamovar::NRecord::TInhostNodeData& total = partition.GetTotal();
                hostSizeMin = total.GetSize();
                for (size_t signalCountersIndex = 0; signalCountersIndex < total.SignalCountersSize(); ++signalCountersIndex) {
                    const auto& signalCountersTotal = total.GetSignalCounters(signalCountersIndex);
                    if (signalCountersTotal.GetSignal() == NSamovarConfig::TInhostFactorAggrConfig::ST_SHOWS_90_DAYS) {
                        countShows90 = signalCountersTotal.GetSum();
                    }
                    if (signalCountersTotal.GetSignal() == NSamovarConfig::TInhostFactorAggrConfig::ST_BROWSE_70_DAYS) {
                        countBrowse70 = signalCountersTotal.GetSum();
                    }
                }
            }
        }
        return PartitionsFilter.IsPass(hostSizeMin, countShows90, countBrowse70);
    }

public:
    Y_SAVELOAD_JOB(PartitionsFilter);

    TVanishTrashHostsProd() {
    }

    TVanishTrashHostsProd(const TPartitionsFilter& partitionsFilter)
        : PartitionsFilter(partitionsFilter)
    {
    }

    void Do(TReader* reader, TWriter* writer) override {
        for (; reader->IsValid(); reader->Next()) {
            auto& row = reader->GetRow();
            NSamovar::NRecord::TInhostPartitions partitions;
            bool parseResult = partitions.ParseFromString(row.GetInhostPartitionsRaw());
            Y_ENSURE(parseResult);
            if (IsNotTrashPartitions(partitions)) {
                writer->AddRow(row);
            }
        }
    }
};
REGISTER_MAPPER(TVanishTrashHostsProd);

int main_vanish_trash_hosts_prod(int argc, const char* argv[]) {
    NLastGetopt::TOpts options;

    TString mrServerStr;
    TString inputTable;
    TString outputTable;
    TPartitionsFilter PartitionsFilter;

    options
        .AddCharOption('s', "--  MapReduce server")
        .StoreResult(&mrServerStr)
        .DefaultValue("hahn")
        .Optional();

    options
        .AddCharOption('i', "-- input table")
        .StoreResult(&inputTable)
        .Required();

    options
        .AddCharOption('o', "-- output table")
        .StoreResult(&outputTable)
        .Required();

    PartitionsFilter.AddOptions(options);

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);
    auto client = NYT::CreateClient(mrServerStr);
    PartitionsFilter.Print();

    client->Map(
        NYT::TMapOperationSpec()
            .AddInput<NSamovarSchema::TPrimaryHostDataRow>(inputTable)
            .AddOutput<NSamovarSchema::TPrimaryHostDataRow>(outputTable)
            .Ordered(true),
        new TVanishTrashHostsProd(PartitionsFilter)
    );



    return 0;
}

int main_print_factors_dump(int argc, const char* argv[]) {
    NLastGetopt::TOpts options;

    TString mrServerStr;
    TString inputTable;

    options
        .AddCharOption('s', "--  MapReduce server")
        .StoreResult(&mrServerStr)
        .DefaultValue("hahn")
        .Optional();

    options
        .AddCharOption('i', "-- input table")
        .StoreResult(&inputTable)
        .Required();

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);
    auto client = NYT::CreateClient(mrServerStr);

    auto reader = client->CreateTableReader<NJupiter::TSRLearn>(inputTable);
    size_t counter = 0;
    size_t filled = 0;
    for (; reader->IsValid() && counter < 10000; reader->Next(), ++counter) {
        auto srLearn = reader->GetRow();
        if (srLearn.HasSelectionRankFactors()) {
            const auto& srFactors = srLearn.GetSelectionRankFactors();
            TString factorsStr;
            size_t maxId = 0;
            for (size_t i = 0; i < srFactors.FactorsSize(); ++i) {
                if (!factorsStr.empty()) factorsStr += ",";
                maxId = Max<size_t>(maxId, srFactors.GetFactors(i).GetId());
                factorsStr += "[" + ToString(srFactors.GetFactors(i).GetId()) + "," + ToString(srFactors.GetFactors(i).GetValue()) + "]";
            }
            if (maxId >= 6) {
                ++filled;
                Cerr << counter << ") " << srLearn.GetHost() + srLearn.GetPath() + " - " + factorsStr << Endl;
            }
        }
    }
    Cerr << filled << Endl;
    return 0;
}


void CopyAndPatchSendlinkPoolTables(NYT::IClientPtr client, const TString& applyPool, const TString& outputFolder) {
    {
        client->Copy(applyPool +  "/factor_slices", outputFolder + "/factor_slices", NYT::TCopyOptions().Force(true).Recursive(true));
        client->Copy(applyPool +  "/features", outputFolder + "/features", NYT::TCopyOptions().Force(true));
    }
    TString slicesStr;
    {
        auto reader = client->CreateTableReader<NYT::TNode>(outputFolder + "/factor_slices");
        Y_ENSURE(reader->IsValid());
        slicesStr = reader->GetRow()["value"].AsString();
        reader->Next();
        Y_ENSURE(!reader->IsValid());
    }
    size_t offset = 0;
    {
        auto reader = client->CreateTableReader<NYT::TNode>(applyPool + "/factor_names");
        auto writer = client->CreateTableWriter<NYT::TNode>(outputFolder + "/factor_names");
        for (; reader->IsValid(); reader->Next()) {
            const auto& row = reader->GetRow();
            Y_ENSURE(row["key"].AsString() == ToString(offset));
            writer->AddRow(row);
            ++offset;
        }
        const TVector<TString>& factorNames = NSamovar::TInhostFactorAggrConfig::Get()->GetAllOutlinksFactorNames();
        slicesStr = slicesStr + " joined_factors[" + ToString(offset) + ";" + ToString(offset + factorNames.size()) + ")";
        for (size_t i = 0; i < factorNames.size(); ++i) {
            writer->AddRow(NYT::TNode()("key", ToString(offset + i))("value", factorNames[i]));
        }
    }
    {
        auto writer = client->CreateTableWriter<NYT::TNode>(outputFolder + "/factor_slices");
        writer->AddRow(NYT::TNode()("key", "0")("value", slicesStr));
    }
}

class TMapProcessLinksTable: public NYT::IMapper<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{
public:
    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override

    {
        for (; input->IsValid(); input->Next()) {
            const auto& row = input->GetRow();

            NSamovarData::TOutSendLinkFactors s_dump;
            bool parseSuccess = s_dump.ParseFromString(row["Factors"].AsString());
            Y_ENSURE(parseSuccess);
            ui64 sentTime = s_dump.GetInfo().GetTime();
            TString originalUrl = row["OriginalUrl"].AsString();
            //TODO - do I need normalize???
            TString host, path;
            SplitUrlToHostAndPath(originalUrl, host, path);

            NYT::TNode outRow;
            outRow["OriginalUrl"] = originalUrl;
            outRow["Host"] = host;
            outRow["sendlinkTime"] = sentTime;
            outRow["JustCreated"] = row["JustCreated"];
            outRow["HttpCode"] = row["HttpCode"];
            outRow["Key"] = row["Key"];
            output->AddRow(outRow);
        }
    }
};

REGISTER_MAPPER(TMapProcessLinksTable);

class TReduceCalcInhostForSendlinkFeatures
    : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{
private:
    TString ConfigFileName;

    struct TLink {
        TString Link;
        bool JustCreated = false;
    };

    void Dump(NYT::TTableWriter<NYT::TNode>* output, TVector<TLink>& links, const TString& lastUrl, ui64 lastTs, const NSamovar::NRecord::TInhostPartitions& partitions) {
        Y_ENSURE(!links.empty());
        TString orHost, orPath;
        SplitUrlToHostAndPath(lastUrl, orHost, orPath);

        NSamovar::TInhostFactorCalcer::TInputOutlinks inputOutlinks;
        for (const auto& link : links) {
            TString host, path;
            SplitUrlToHostAndPath(link.Link, host, path);
            if (host == orHost) {
                inputOutlinks.insert(link.Link);
            }
            {
                NYT::TNode outRow;
                outRow["OriginalUrl"] = lastUrl;
                outRow["sendlinkTime"] = lastTs;
                outRow["Link"] = link.Link;
                outRow["same_host"] = (host == orHost);
                outRow["link_tokens"] = PrintTokens(link.Link);
                output->AddRow(outRow, 1);
            }
        }
        NSamovar::TInhostFactorCalcer factorCalcer(NSamovar::TInhostFactorAggrConfig::Get());
        auto factors = factorCalcer.CalcOutlinksFactors(partitions, inputOutlinks);
        Y_ENSURE(factors.size() == NSamovar::TInhostFactorAggrConfig::Get()->GetAllOutlinksFactorNames().size());
        TString resultFactorsStr;
        for (float f : factors) {
            resultFactorsStr += "\t" + ToString(f);
        }
        NYT::TNode outRow;
        outRow["OriginalUrl"] = lastUrl;
        outRow["sendlinkTime"] = lastTs;
        outRow["factors"] = resultFactorsStr;
        //dbg
        NSamovar::TInhostFactorCalcer::TInputOutlinks tmp;
        factorCalcer.SampleOutlinks(inputOutlinks, tmp);
        outRow["sample_dbg"] = ToString(inputOutlinks.size()) + " " + ToString(tmp.size());

        output->AddRow(outRow);

        links.clear();
    }

public:
    Y_SAVELOAD_JOB(ConfigFileName);
    TReduceCalcInhostForSendlinkFeatures() {}
    TReduceCalcInhostForSendlinkFeatures(const TString& configFileName)
        : ConfigFileName(configFileName)
    {
    }

    void Start(NYT::TTableWriter<NYT::TNode>*) override {
        NSamovar::TInhostFactorAggrConfig::InitStatic(ConfigFileName);
    }

    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        NSamovar::NRecord::TInhostPartitions partitions;
        bool partitionsParsed = false;
        TVector<TLink> links;
        TString lastUrl;
        ui64 lastTs = 0;
        for (; input->IsValid(); input->Next()) {
            switch (input->GetTableIndex()) {
                case 0:
                    {
                        partitionsParsed = partitions.ParseFromString(input->GetRow()["InhostPartitionsRaw"].AsString());
                        Y_ENSURE(partitionsParsed);
                        break;
                    }
                case 1:
                    {
                        const auto& inRow = input->GetRow();
                        if (!links.empty() && (lastUrl != inRow["OriginalUrl"].AsString() || lastTs != inRow["sendlinkTime"].AsUint64())) {
                            Dump(output, links, lastUrl, lastTs, partitions);
                        }
                        lastUrl = inRow["OriginalUrl"].AsString();
                        lastTs = inRow["sendlinkTime"].AsUint64();
                        TLink link;
                        link.Link = inRow["Key"].AsString();
                        link.JustCreated = inRow["JustCreated"].AsBool();
                        links.push_back(link);
                        break;
                    }
                default:
                    Y_ENSURE(false);
            }
        }
        if (!links.empty()) {
            Dump(output, links, lastUrl, lastTs, partitions);
        }
    }
};
REGISTER_REDUCER(TReduceCalcInhostForSendlinkFeatures)

class TReduceJoinToInhostPool
    : public NYT::IReducer<NYT::TTableReader<NYT::TNode>, NYT::TTableWriter<NYT::TNode>>
{
public:
    void Do(NYT::TTableReader<NYT::TNode>* input, NYT::TTableWriter<NYT::TNode>* output) override {
        Y_ENSURE(input->GetTableIndex() == 0);
        TString addStr = input->GetRow()["factors"].AsString();

        for (; input->IsValid(); input->Next()) {
            if (input->GetTableIndex() == 1) {
                auto inRow = input->GetRow();
                inRow["value"] = inRow["value"].AsString() + addStr;
                inRow["addStr"] = addStr;
                output->AddRow(inRow);
            }
        }
    }
};
REGISTER_REDUCER(TReduceJoinToInhostPool)

int main_test_inhost_for_sendlink(int argc, const char* argv[]) {
    NLastGetopt::TOpts options;

    TString mrServerStr;
    TString inputDir;
    TString outputDir;
    TString inhostTable;
    TString linksTable;
    TString configPath;

    options
        .AddCharOption('s', "--  MapReduce server")
        .StoreResult(&mrServerStr)
        .DefaultValue("hahn")
        .Optional();

    options
        .AddCharOption('i', "-- input pool dir")
        .StoreResult(&inputDir)
        .Required();

    options
        .AddCharOption('o', "-- output pool dir")
        .StoreResult(&outputDir)
        .Required();

    options
        .AddCharOption('l', "-- links")
        .StoreResult(&linksTable)
        .Required();

    options
        .AddLongOption("inhost", "-- table with inhost backup")
        .StoreResult(&inhostTable)
        .Required();

    options
        .AddCharOption('c', "-- config file name")
        .StoreResult(&configPath)
        .Required();

    NLastGetopt::TOptsParseResult parser(&options, argc, argv);
    auto client = NYT::CreateClient(mrServerStr);

    InitConfing(configPath);
    CopyAndPatchSendlinkPoolTables(client, inputDir, outputDir);
    client->Sort(NYT::TSortOperationSpec().AddInput(outputDir + "/features").Output(outputDir + "/features").SortBy({"OriginalUrl", "sendlinkTime"}));

    client->Map(
        NYT::TMapOperationSpec()
            .AddInput<NYT::TNode>(linksTable)
            .AddOutput<NYT::TNode>(NYT::TRichYPath(outputDir + "/tmp1")),
        new TMapProcessLinksTable
    );
    client->Sort(NYT::TSortOperationSpec().AddInput(outputDir + "/tmp1").Output(outputDir + "/tmp1").SortBy({"Host", "OriginalUrl", "sendlinkTime"}));

    client->JoinReduce(
        NYT::TJoinReduceOperationSpec()
            .AddInput<NYT::TNode>(NYT::TRichYPath(inhostTable).Foreign(true))
            .AddInput<NYT::TNode>(NYT::TRichYPath(outputDir + "/tmp1").Primary(true))
            .AddOutput<NYT::TNode>(NYT::TRichYPath(outputDir + "/tmp2"))
            .AddOutput<NYT::TNode>(NYT::TRichYPath(outputDir + "/tmp3"))
            .ReducerSpec(NYT::TUserJobSpec().AddLocalFile(configPath))
            .JoinBy("Host"),
        new TReduceCalcInhostForSendlinkFeatures(GetFileNameComponent(configPath))
    );

    client->Sort(NYT::TSortOperationSpec().AddInput(outputDir + "/tmp2").Output(outputDir + "/tmp2").SortBy({"OriginalUrl", "sendlinkTime"}));
    {
        NYT::TReduceOperationSpec reduceSpec;
        reduceSpec.AddInput<NYT::TNode>(outputDir + "/tmp2");
        reduceSpec.AddInput<NYT::TNode>(outputDir + "/features");
        reduceSpec.AddOutput<NYT::TNode>(NYT::TRichYPath(outputDir + "/features").SortedBy({"OriginalUrl", "sendlinkTime"}));
        reduceSpec.ReduceBy({"OriginalUrl", "sendlinkTime"});
        client->Reduce(
            reduceSpec,
            new TReduceJoinToInhostPool
        );
    }

    return 0;
}

int main(int argc, const char* argv[]) {
    NYT::Initialize(argc, argv);

    TModChooser modeChooser;
    modeChooser.AddMode("collect-shows-clicks", main_collect_shows_clicks, "collect shows and clicks");
    modeChooser.AddMode("merge-for-factors-calc", main_merge_for_factors_calc, "merge for factors calc");
    modeChooser.AddMode("calc-factors-simple", main_calc_factors_simple, "calc factors simple");
    modeChooser.AddMode("prepare-for-first-stage", main_prepare_for_first_stage, "prepare for first stage");
    modeChooser.AddMode("calc-factors-prod-first-stage", main_calc_factors_prod_first_stage, "calc factors prod (first stage)");
    modeChooser.AddMode("calc-factors-prod-second-stage", main_calc_factors_prod_second_stage, "calc factors prod (second stage)");
    modeChooser.AddMode("calc-factors-prod", main_calc_factors_prod, "calc factors prod");
    modeChooser.AddMode("join-factors", main_join_factors, "join factors");
    modeChooser.AddMode("generate-factor-groups", main_generate_factor_groups, "generate factor groups");
    modeChooser.AddMode("generate-factor-names", main_generate_factor_names, "generate factor names");
    modeChooser.AddMode("test-collect-userdata", main_test_collect_userdata, "test collect userdata");
    modeChooser.AddMode("test-prod-inhost-partitions", main_test_prod_inhost_partitions, "test prod inhost partitions");
    modeChooser.AddMode("test-factors-dump", main_test_factors_dump, "test factors dump");
    modeChooser.AddMode("vanish-trash-hosts-pool", main_vanish_trash_hosts_pool, "vanish trash hosts pool");
    modeChooser.AddMode("vanish-trash-hosts-prod", main_vanish_trash_hosts_prod, "vanish trash hosts prod");
    modeChooser.AddMode("print-factors-dump", main_print_factors_dump, "print factors dump");
    modeChooser.AddMode("test-inhost-for-sendlink", main_test_inhost_for_sendlink, "test inhost factors for sendlink");
    modeChooser.Run(argc, argv);

    return 0;
}
