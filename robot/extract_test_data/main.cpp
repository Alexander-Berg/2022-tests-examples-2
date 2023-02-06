#include <robot/lemur/algo/locator/locator.h>
#include <robot/lemur/algo/ytlib/all.h>
#include <robot/lemur/protos/config.pb.h>

#include <yweb/robot/kiwi/clientlib/session.h>
#include <yweb/robot/kiwi/tuplelib/lib/tuple.h>
#include <yweb/robot/kiwi/tuplelib/lib/object.h>

#include <yweb/robot/ukrop/algo/remap/remapcache.h>

#include <library/cpp/getopt/opt.h>
#include <library/cpp/protobuf/util/pb_io.h>

#include <mapreduce/yt/interface/client.h>

#include <util/folder/dirut.h>
#include <util/generic/string.h>

enum ETestDataMode {
    TDM_OWNER,
    TDM_HOST,
    TDM_URL,
    TDM_INCOMING,
    TDM_SHARD,
    TDM_SENDLINK,
    TDM_RENEWED
};

static const TString APP_NAME = "extract_test_data";

class TConfig {
public:
    NLemurConfig::TInstanceConfig ProdInstanceConfig;
    NLemurConfig::TInstanceConfig DevelInstanceConfig;
    TVector<TString> Hosts;
    TString Host;
    TString Url;
    NLemurLocator::EKeyType KeyType;
    ETestDataMode Mode;
    ui64 RecordCount;
    ui32 ShardId;
    bool HasShardId;
    TString TriggersPath;

public:
    TConfig(int argc, const char *argv[])
        : ShardId(0)
        , HasShardId(false)
    {
        TString prodInstanceConfigPath;
        TString develInstanceConfigPath;
        TString keyTypeStr;
        TString mode;
        TString prefix;
        NLastGetopt::TOpts opts = NLastGetopt::TOpts::Default();
        opts.AddLongOption('p', "prod-config", "Path to production instance config (source of data)").RequiredArgument("<path>").Required().StoreResult(&prodInstanceConfigPath);
        opts.AddLongOption('d', "devel-path", "Path to devel instance config (destination for data)").RequiredArgument("<path>").Required().StoreResult(&develInstanceConfigPath);
        opts.AddLongOption('H', "host", "Host to extract (one for owner and host mode, multiple for sendlink mode)").RequiredArgument("<host>").StoreResult(&Host).AppendTo(&Hosts);
        opts.AddLongOption('u', "url", "Url to extract (for url mode)").RequiredArgument("<url>").DefaultValue("").StoreResult(&Url);
        opts.AddLongOption('k', "keytype", "keytype (for url mode)").RequiredArgument("<KT_*/num>").DefaultValue("KT_DOC_DEF").StoreResult(&keyTypeStr);
        opts.AddLongOption('s', "shard", "Shard to extract data (required in shard mode, optional in incoming mode)").RequiredArgument("<shard>").StoreResult(&ShardId).StoreValue(&HasShardId, true);
        opts.AddLongOption('c', "count", "Max record count").RequiredArgument("<count>").DefaultValue("0").StoreResult(&RecordCount);
        opts.AddLongOption('t', "triggers-path", "Path to triggers.pb.txt (for incoming mode)").RequiredArgument("<path>").DefaultValue("").StoreResult(&TriggersPath);
        opts.AddLongOption('m', "mode", "(owner|host|url|shard|incoming|sendlink|renewed)").RequiredArgument("<mode>").DefaultValue("host").StoreResult(&mode);
        opts.AddLongOption("prefix", "Use this prefix instead the one from conf-devel instance config").RequiredArgument("<string>").StoreResult(&prefix);
        opts.AddHelpOption('h');
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);

        ParseFromTextFormat(prodInstanceConfigPath, ProdInstanceConfig);
        ParseFromTextFormat(develInstanceConfigPath, DevelInstanceConfig);
        if (prefix) {
            DevelInstanceConfig.MutableLocatorConfig()->SetBasePrefix(prefix);
        }

        KeyType = static_cast<NLemurLocator::EKeyType>(NKiwi::TSession::ParseKeytype(keyTypeStr));

        if (mode == "owner") {
            Mode = TDM_OWNER;
            Y_VERIFY(Hosts.size() == 1, "Set exactly one host for owner mode");
        } else if (mode == "host") {
            Mode = TDM_HOST;
            Y_VERIFY(Hosts.size() == 1, "Set exactly one host for host mode");
        } else if (mode == "url") {
            Mode = TDM_URL;
            Y_VERIFY(!Url.empty(), "Please, specify url for url mode");
        } else if (mode == "shard") {
            Mode = TDM_SHARD;
        } else if (mode == "incoming") {
            Mode = TDM_INCOMING;
            Y_VERIFY(NFs::Exists(TriggersPath), "No triggers!");
        } else if (mode == "sendlink") {
            Mode = TDM_SENDLINK;
            Y_VERIFY((RecordCount > 0 && HasShardId) || (Hosts.size() > 0), "Set count and shard id/or some hosts for sendlink mode");
        } else if (mode == "renewed") {
            Mode = TDM_RENEWED;
        } else {
            ythrow yexception() << "Unknown mode: " << mode;
        }
    }
};

class TExtractKeyAttrReduce: public NLemur::IBinaryKeyRowLemurReduce {
private:
    THashSet<ui32> KeyAttrIds;

private:
    int SaveOperation(IBinSaver &f) override {
        f.Add(2, &KeyAttrIds);
        return 0;
    }

public:
    TExtractKeyAttrReduce() {
    }

    TExtractKeyAttrReduce(const TString& instanceConfig, const NLemur::TJobConfig& jobConfig, THashSet<ui32>& keyAttrIds)
        : IBinaryKeyRowLemurReduce(instanceConfig, jobConfig)
        , KeyAttrIds(keyAttrIds)
    {
    }

    void DoDo(const NLemur::TBinaryKey& key, NLemur::TBinaryKeyRowTableIterator* input, NLemur::TLemurUpdate* output) override {
        for (;input->IsValid(); input->Next()) {
            NKiwi::TKiwiObject resultObject;
            TString url;
            ui8 keyType = key.GetKeyType();
            for (NKiwi::NTuples::TTupleIterator tupleIt(input->GetValue().data(), input->GetValue().size()); tupleIt.IsValid(); ++tupleIt) {
                const NKiwi::NTuples::TTuple* tuple = tupleIt.Current();
                if (!tuple || tuple->IsStub() || tuple->IsNull()) {
                    continue;
                }
                if (KeyAttrIds.contains(tuple->GetId())) {
                    url = tuple->AsStringBuf();
                    break;
                }
            }
            Y_VERIFY(url.size() != 0, "No key AttrId!");
            output->AddSub(0, url, TStringBuf((const char*)&keyType, sizeof(keyType)), input->GetValue());
        }
    }
};
REGISTER_REDUCER(TExtractKeyAttrReduce);

/**
 * @brief Calculates key range corresponding to rows in interval [0; rowCount].
 */
NYT::TReadRange CalculateKeyRange(
        const NYT::IClientBasePtr& client,
        const TString& tablePath,
        const ui64 rowCount) {
    NYT::TReadRange findRange;
    findRange.LowerLimit(NYT::TReadLimit().RowIndex(rowCount));

    const auto tableReader =
            client->CreateTableReader<NLemurSchema::TBinaryKeyRow>(
                NYT::TRichYPath(tablePath).AddRange(findRange));

    NLemur::TBinaryKeyRowTableIterator iterator(tableReader.Get());
    Y_VERIFY(iterator.IsValid(), "Not valid iterator");

    NLemur::TBinaryKey upperBound = iterator.GetKey();
    upperBound.HostKey -= 1;
    upperBound.UrlKey = Max<ui64>();
    upperBound.KeyType = Max<ui16>();

    NYT::TReadRange result;
    result.UpperLimit(NYT::TReadLimit().Key(NLemur::ToYTKey(upperBound)));

    return result;
}

int main(int argc, const char *argv[]) {
    NYT::Initialize(argc, argv);
    TConfig config(argc, argv);

    NLemur::TLocator prodLocator(config.ProdInstanceConfig.GetLocatorConfig());
    NLemur::TLocator develLocator(config.DevelInstanceConfig.GetLocatorConfig());
    Y_VERIFY(prodLocator.GetBasePrefix() != develLocator.GetBasePrefix());
    Y_VERIFY(develLocator.GetBasePrefix() != "home/lemur/");

    NYT::IClientPtr client = NYT::CreateClient(config.ProdInstanceConfig.GetMRConfig().GetServer());

    if (config.Mode == TDM_OWNER || config.Mode == TDM_HOST) {
        TMaybe<NLemur::TBinaryKey> binaryKey = NLemur::TBinaryKey::Create(config.Host, NLemurLocator::KT_HOST);
        Y_VERIFY(binaryKey, "Can't parse host %s", config.Host.data());

        NLemur::TLocator::TShardId shardId = prodLocator.GetShardId(binaryKey.GetRef());
        Cout << "ShardId: " << shardId << Endl;

        NLemur::TBinaryKey lowerBound = binaryKey.GetRef();
        lowerBound.UrlKey = 0;
        lowerBound.KeyType = 0;

        NLemur::TBinaryKey upperBound = binaryKey.GetRef();
        upperBound.UrlKey = Max<ui64>();
        upperBound.KeyType = Max<ui16>();

        if (config.Mode == TDM_OWNER) {
            lowerBound.HostKey = 0;
            upperBound.HostKey = Max<ui64>();
        }

        TString srcHostTable = NLemur::FixYTPath(prodLocator.GetPersistentHostDataTable(shardId));
        TString dstHostTable = NLemur::FixYTPath(develLocator.GetPersistentHostDataTable(shardId));

        TString srcUrlTable = NLemur::FixYTPath(prodLocator.GetPersistentUrlDataTable(shardId));
        TString dstUrlTable = NLemur::FixYTPath(develLocator.GetPersistentUrlDataTable(shardId));
        auto transaction = client->StartTransaction();

        NLemur::CheckOrCreateTable(transaction.Get(), dstHostTable);
        NLemur::CheckOrCreateTable(transaction.Get(), dstUrlTable);

        {
            NYT::TReadRange readRange;
            readRange.LowerLimit(NYT::TReadLimit().Key(NLemur::ToYTKey(lowerBound)));
            readRange.UpperLimit(NYT::TReadLimit().Key(NLemur::ToYTKey(upperBound)));

            transaction->Merge(NYT::TMergeOperationSpec()
                                   .AddInput(NYT::TRichYPath(srcHostTable).AddRange(readRange))
                                   .Output(NYT::TRichYPath(dstHostTable).Append(false))
                                   .MergeBy(NLemur::GetBinaryKeyRowSortKey())
                                   .Mode(NYT::MM_SORTED));
        }
        {
            ui64 lowerIndex = client->CreateTableReader<NLemurSchema::TBinaryKeyRow>(NYT::TRichYPath(srcUrlTable).AddRange(NYT::TReadRange().LowerLimit(NYT::TReadLimit().Key(NLemur::ToYTKey(lowerBound)))))->GetRowIndex();
            ui64 upperIndex = client->CreateTableReader<NLemurSchema::TBinaryKeyRow>(NYT::TRichYPath(srcUrlTable).AddRange(NYT::TReadRange().LowerLimit(NYT::TReadLimit().Key(NLemur::ToYTKey(upperBound)))))->GetRowIndex();

            if ((config.RecordCount > 0) && (lowerIndex + config.RecordCount < upperIndex)) {
                upperIndex = lowerIndex + config.RecordCount;
            }

            NYT::TReadRange readRange;
            readRange.LowerLimit(NYT::TReadLimit().RowIndex(lowerIndex));
            readRange.UpperLimit(NYT::TReadLimit().RowIndex(upperIndex));

            transaction->Merge(NYT::TMergeOperationSpec()
                                   .AddInput(NYT::TRichYPath(srcUrlTable).AddRange(readRange))
                                   .Output(NYT::TRichYPath(dstUrlTable).Append(false))
                                   .MergeBy(NLemur::GetBinaryKeyRowSortKey())
                                   .Mode(NYT::MM_SORTED));
        }

        transaction->Commit();
        return 0;
    } else if (config.Mode == TDM_URL) {
        TMaybe<NLemur::TBinaryKey> binaryKey = NLemur::TBinaryKey::Create(config.Url, config.KeyType);
        Y_VERIFY(binaryKey, "Can't parse url %s", config.Url.data());

        TMaybe<NLemur::TBinaryKey> hostBinaryKey = NLemur::TBinaryKey::Create(config.Url, NLemurLocator::KT_HOST);
        Y_VERIFY(hostBinaryKey, "Can't parse host for url %s", config.Url.data());

        NLemur::TLocator::TShardId shardId = prodLocator.GetShardId(binaryKey.GetRef());
        Cout << "ShardId: " << shardId << Endl;

        TString srcHostTable = NLemur::FixYTPath(prodLocator.GetPersistentHostDataTable(shardId));
        TString dstHostTable = NLemur::FixYTPath(develLocator.GetPersistentHostDataTable(shardId));

        TString srcUrlTable = NLemur::FixYTPath(prodLocator.GetPersistentUrlDataTable(shardId));
        TString dstUrlTable = NLemur::FixYTPath(develLocator.GetPersistentUrlDataTable(shardId));

        auto transaction = client->StartTransaction();
        NLemur::CheckOrCreateTable(transaction.Get(), dstHostTable);
        NLemur::CheckOrCreateTable(transaction.Get(), dstUrlTable);

        {
            NLemur::TBinaryKey lowerBound = hostBinaryKey.GetRef();
            NLemur::TBinaryKey upperBound = hostBinaryKey.GetRef();
            ++upperBound.KeyType;

            NYT::TReadRange readRange;
            readRange.LowerLimit(NYT::TReadLimit().Key(NLemur::ToYTKey(lowerBound)));
            readRange.UpperLimit(NYT::TReadLimit().Key(NLemur::ToYTKey(upperBound)));

            transaction->Merge(NYT::TMergeOperationSpec()
                                   .AddInput(NYT::TRichYPath(srcHostTable).AddRange(readRange))
                                   .Output(NYT::TRichYPath(dstHostTable).Append(false))
                                   .MergeBy(NLemur::GetBinaryKeyRowSortKey())
                                   .Mode(NYT::MM_SORTED));
        }
        {
            NLemur::TBinaryKey lowerBound = binaryKey.GetRef();
            NLemur::TBinaryKey upperBound = binaryKey.GetRef();
            ++upperBound.KeyType;

            NYT::TReadRange readRange;
            readRange.LowerLimit(NYT::TReadLimit().Key(NLemur::ToYTKey(lowerBound)));
            readRange.UpperLimit(NYT::TReadLimit().Key(NLemur::ToYTKey(upperBound)));

            transaction->Merge(NYT::TMergeOperationSpec()
                                   .AddInput(NYT::TRichYPath(srcUrlTable).AddRange(readRange))
                                   .Output(NYT::TRichYPath(dstUrlTable).Append(false))
                                   .MergeBy(NLemur::GetBinaryKeyRowSortKey())
                                   .Mode(NYT::MM_SORTED));
        }

        transaction->Commit();
        return 0;
    } else if (config.Mode == TDM_SHARD) {
        if (config.RecordCount == 0) {
            return 0;
        }
        TString srcHostTable = NLemur::FixYTPath(prodLocator.GetPersistentHostDataTable(config.ShardId));
        TString dstHostTable = NLemur::FixYTPath(develLocator.GetPersistentHostDataTable(config.ShardId));

        TString srcUrlTable = NLemur::FixYTPath(prodLocator.GetPersistentUrlDataTable(config.ShardId));
        TString dstUrlTable = NLemur::FixYTPath(develLocator.GetPersistentUrlDataTable(config.ShardId));

        auto transaction = client->StartTransaction();

        NLemur::CheckOrCreateTable(transaction.Get(), dstHostTable);
        NLemur::CheckOrCreateTable(transaction.Get(), dstUrlTable);

        const NYT::TReadRange readRange = CalculateKeyRange(client, srcUrlTable, config.RecordCount);

        transaction->Merge(NYT::TMergeOperationSpec()
                               .AddInput(NYT::TRichYPath(srcHostTable).AddRange(readRange))
                               .Output(NYT::TRichYPath(dstHostTable).Append(false))
                               .MergeBy(NLemur::GetBinaryKeyRowSortKey())
                               .Mode(NYT::MM_SORTED));
        transaction->Merge(NYT::TMergeOperationSpec()
                               .AddInput(NYT::TRichYPath(srcUrlTable).AddRange(readRange))
                               .Output(NYT::TRichYPath(dstUrlTable).Append(false))
                               .MergeBy(NLemur::GetBinaryKeyRowSortKey())
                               .Mode(NYT::MM_SORTED));

        transaction->Commit();
        return 0;
    } else if (config.Mode == TDM_INCOMING) {
        if (config.RecordCount == 0) {
            return 0;
        }

        NLemur::TTupleMeta tupleMeta(config.TriggersPath);
        THolder<NUkrop::TRemap> remap(new NUkrop::TRemap(tupleMeta.GetMetaProto()));
        THashSet<ui32> attrIds;
        attrIds.insert(NUkrop::TUCA::URL);
        attrIds.insert(NUkrop::TUCA::Name);

        auto dstTable = develLocator.GetCommonTable<NLemurSchema::TYaMRRow>(NLemur::FixYTPath(develLocator.GetIncomingFinalPrefix() + "extract_test_data_" + ToString(TInstant::Now().Seconds())));
        {
            auto transaction = client->StartTransaction();
            for (size_t shardId = 0; shardId < prodLocator.GetShardCount(); ++shardId) {
                if (config.HasShardId && (shardId != config.ShardId)) {
                    continue;
                }

                auto srcHostTable = prodLocator.GetPersistentHostDataTable(shardId);
                auto srcUrlTable = prodLocator.GetPersistentUrlDataTable(shardId);

                NYT::TReadRange findRange;
                findRange.LowerLimit(NYT::TReadLimit().RowIndex(config.RecordCount));
                auto tableReader = client->CreateTableReader<NLemurSchema::TBinaryKeyRow>(NYT::TRichYPath(srcUrlTable).AddRange(findRange));
                NLemur::TBinaryKeyRowTableIterator iterator(tableReader.Get());
                Y_VERIFY(iterator.IsValid(), "Not valid iterator");
                NLemur::TBinaryKey upperBound = iterator.GetKey();
                upperBound.HostKey -= 1;
                upperBound.UrlKey = Max<ui64>();
                upperBound.KeyType = Max<ui16>();

                ui64 hostUpperIndex = srcHostTable.AddRange(
                        NYT::TReadRange().LowerLimit(NYT::TReadLimit().Key(NLemur::ToYTKey(upperBound)))
                        ).GetReader(client.Get())
                    ->GetRowIndex();

                ui64 urlUpperIndex = srcUrlTable.AddRange(
                        NYT::TReadRange().LowerLimit(NYT::TReadLimit().Key(NLemur::ToYTKey(upperBound)))
                        ).GetReader(client.Get())
                    ->GetRowIndex();

                if (hostUpperIndex == 0 || urlUpperIndex == 0) {
                    // If there are no full hosts in first RecordCount records, cut RecordCount records from the firsr host.
                    hostUpperIndex = 1;
                    urlUpperIndex = config.RecordCount;
                }

                NLemur::TJobConfig jobConfig(APP_NAME, NLemur::LL_NO);

                auto cmd = NLemur::MakeReduceCmd(
                        client.Get(),
                        transaction.Get(),
                        jobConfig,
                        config.DevelInstanceConfig.GetMRConfig()
                        );
                cmd
                    .Input(srcHostTable.AddRange(NYT::TReadRange::FromRowIndices(0, hostUpperIndex)))
                    .Input(srcUrlTable.AddRange(NYT::TReadRange::FromRowIndices(0, urlUpperIndex)))
                    .Output(dstTable.Append(true))
                    .SortBy(srcHostTable.GetDefaultSortColumns())
                    .ReduceBy(srcHostTable.GetDefaultReduceColumns());
                cmd.Do(new TExtractKeyAttrReduce(config.DevelInstanceConfig.SerializeAsString(), jobConfig, attrIds));
            }
            transaction->Commit();
        }
        return 0;
    } else if ((config.Mode == TDM_SENDLINK) && (config.Hosts.size() == 0)) {
        Y_VERIFY(config.RecordCount > 0);

        TString srcHostCanonTable = NLemur::FixYTPath(prodLocator.GetHostCanonizationDataTable());
        TString dstHostCanonTable = NLemur::FixYTPath(develLocator.GetHostCanonizationDataTable());

        TString srcGemCanonTable = NLemur::FixYTPath(prodLocator.GetGeminiCanonizationDataTable());
        TString dstGemCanonTable = NLemur::FixYTPath(develLocator.GetGeminiCanonizationDataTable());

        TString srcGeminiTable = NLemur::FixYTPath(prodLocator.GetGeminiTable());
        TString dstGeminiTable = NLemur::FixYTPath(develLocator.GetGeminiTable());

        auto transaction = client->StartTransaction();

        NLemur::CheckOrCreateTable(transaction.Get(), dstHostCanonTable);
        NLemur::CheckOrCreateTable(transaction.Get(), dstGemCanonTable);
        NLemur::CheckOrCreateTable(transaction.Get(), dstGeminiTable);

        const TString srcUrlTable = NLemur::FixYTPath(prodLocator.GetPersistentUrlDataTable(config.ShardId));
        NYT::TReadRange readRange = CalculateKeyRange(client, srcUrlTable, config.RecordCount);

        const NLemur::TBinaryKey shardLowerBound = prodLocator.GetLowerBound(config.ShardId);
        readRange.LowerLimit(NYT::TReadLimit().Key(NLemur::ToYTKey(shardLowerBound)));

        transaction->Merge(NYT::TMergeOperationSpec()
                               .AddInput(NYT::TRichYPath(srcHostCanonTable).AddRange(readRange))
                               .Output(NYT::TRichYPath(dstHostCanonTable).Append(false))
                               .MergeBy(NLemur::GetBinaryKeyRowSortKey())
                               .Mode(NYT::MM_SORTED));
        transaction->Merge(NYT::TMergeOperationSpec()
                               .AddInput(NYT::TRichYPath(srcGemCanonTable).AddRange(readRange))
                               .Output(NYT::TRichYPath(dstGemCanonTable).Append(false))
                               .MergeBy(NLemur::GetBinaryKeyRowSortKey())
                               .Mode(NYT::MM_SORTED));
        transaction->Merge(NYT::TMergeOperationSpec()
                               .AddInput(NYT::TRichYPath(srcGeminiTable).AddRange(readRange))
                               .Output(NYT::TRichYPath(dstGeminiTable).Append(false))
                               .MergeBy(NLemur::GetBinaryKeyRowSortKey())
                               .Mode(NYT::MM_SORTED));

        transaction->Commit();

        return 0;
    } else if ((config.Mode == TDM_SENDLINK) && (config.Hosts.size() > 0)) {
        TString srcHostCanonTable = NLemur::FixYTPath(prodLocator.GetHostCanonizationDataTable());
        TString dstHostCanonTable = NLemur::FixYTPath(develLocator.GetHostCanonizationDataTable());

        TString srcGemCanonTable = NLemur::FixYTPath(prodLocator.GetGeminiCanonizationDataTable());
        TString dstGemCanonTable = NLemur::FixYTPath(develLocator.GetGeminiCanonizationDataTable());

        TString srcGeminiTable = NLemur::FixYTPath(prodLocator.GetGeminiTable());
        TString dstGeminiTable = NLemur::FixYTPath(develLocator.GetGeminiTable());

        NYT::TMergeOperationSpec hostCanonSpec;
        hostCanonSpec.Output(NYT::TRichYPath(dstHostCanonTable).Append(false)).MergeBy(NLemur::GetBinaryKeyRowSortKey()).Mode(NYT::MM_SORTED);

        NYT::TMergeOperationSpec gemCanonSpec;
        NYT::TMergeOperationSpec geminiSpec;

        gemCanonSpec.Output(NYT::TRichYPath(dstGemCanonTable).Append(false)).MergeBy(NLemur::GetBinaryKeyRowSortKey()).Mode(NYT::MM_SORTED);
        geminiSpec.Output(NYT::TRichYPath(dstGeminiTable).Append(false)).MergeBy(NLemur::GetBinaryKeyRowSortKey()).Mode(NYT::MM_SORTED);

        for (const auto& host : config.Hosts) {
            TString preparedHost;
            TMaybe<NLemur::TBinaryKey> binaryKey = NLemur::TBinaryKey::Create(host, NLemurLocator::KT_HOST, &preparedHost);
            Y_VERIFY(binaryKey, "Can't parse host %s", host.data());
            NLemur::TBinaryKey lowerBound = binaryKey.GetRef();
            lowerBound.UrlKey = 0;
            lowerBound.KeyType = 0;

            NLemur::TBinaryKey upperBound = binaryKey.GetRef();
            upperBound.UrlKey = Max<ui64>();
            upperBound.KeyType = Max<ui16>();

            const NYT::TReadRange readRange =
                    NYT::TReadRange()
                    .LowerLimit(NYT::TReadLimit().Key(NLemur::ToYTKey(lowerBound)))
                    .UpperLimit(NYT::TReadLimit().Key(NLemur::ToYTKey(upperBound)));

            // hostcanon table range
            hostCanonSpec.AddInput(NYT::TRichYPath(srcHostCanonTable).AddRange(readRange));

            // gemini canon table range
            gemCanonSpec.AddInput(NYT::TRichYPath(srcGemCanonTable).AddRange(readRange));

            // gemini table range
            geminiSpec.AddInput(NYT::TRichYPath(srcGeminiTable).AddRange(readRange));
        }

        auto transaction = client->StartTransaction();

        NLemur::CheckOrCreateTable(transaction.Get(), dstHostCanonTable);
        transaction->Merge(hostCanonSpec);

        NLemur::CheckOrCreateTable(transaction.Get(), dstGemCanonTable);
        transaction->Merge(gemCanonSpec);

        NLemur::CheckOrCreateTable(transaction.Get(), dstGeminiTable);
        transaction->Merge(geminiSpec);

        transaction->Commit();

        return 0;
    } else if (config.Mode == TDM_RENEWED) {
        if (config.RecordCount == 0) {
            return 0;
        }

        const TString srcUrlTable = NLemur::FixYTPath(prodLocator.GetPersistentUrlDataTable(config.ShardId));
        const NYT::TReadRange readRange = CalculateKeyRange(client, srcUrlTable, config.RecordCount);

        const NYT::ITransactionPtr transaction = client->StartTransaction();

        const TString renewedPath = NLemur::FixYTPath(prodLocator.GetRenewedDataPrefix(config.ShardId));
        const NYT::TNode::TListType tables = client->List(renewedPath);
        for (const NYT::TNode& table : tables) {
            const TString sourceTable =
                    NLemur::FixYTPath(
                        prodLocator.GetRenewedDataTable(config.ShardId, table.AsString()));

            const TString targetTable =
                    NLemur::FixYTPath(
                        develLocator.GetRenewedDataTable(config.ShardId, table.AsString()));

            NLemur::CheckOrCreateTable(transaction.Get(), targetTable);

            transaction->Merge(
                        NYT::TMergeOperationSpec()
                        .AddInput(NYT::TRichYPath(sourceTable).AddRange(readRange))
                        .Output(NYT::TRichYPath(targetTable).Append(false))
                        .MergeBy(NLemur::GetBinaryKeyRowSortKey())
                        .Mode(NYT::MM_SORTED));
        }

        transaction->Commit();

        return 0;
    }

    return 1;
}
