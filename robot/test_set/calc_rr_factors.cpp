#include <robot/quality/robotrank/rr_factors_calcer/calcer.h>
#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <library/cpp/getopt/last_getopt.h>

#include <mapreduce/yt/interface/client.h>

#include <library/cpp/string_utils/url/url.h>
#include <util/stream/file.h>
#include <util/system/guard.h>
#include <util/thread/pool.h>


int CalcRRFactors(int argc, const char** argv) {
    TString cluster;
    TString urlsFile;
    TString resultTable;
    TRRCalcerConfigs configs = GetBuildinConfigs();
    size_t maxInFlight;
    {
        NLastGetopt::TOpts opts = NLastGetopt::TOpts::Default();
        opts.AddHelpOption('h');
        opts.AddLongOption("cluster")
            .RequiredArgument("SERVER")
            .DefaultValue("arnold")
            .StoreResult(&cluster);
        opts.AddLongOption("urls")
            .RequiredArgument("FILE")
            .Required()
            .StoreResult(&urlsFile);
        opts.AddLongOption("result")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&resultTable);
        opts.AddLongOption("max-in-flight")
            .RequiredArgument("INT")
            .DefaultValue(10)
            .StoreResult(&maxInFlight);
       opts.AddLongOption("policy-config")
            .RequiredArgument("FILE")
            .StoreResult(&configs.PolicyCfgPath);
        opts.AddLongOption("triggers-config")
            .RequiredArgument("FILE")
            .StoreResult(&configs.TriggersCfgPath);
        opts.AddLongOption("zone-config")
            .RequiredArgument("FILE")
            .StoreResult(&configs.ZoneCfgPath);
        opts.AddLongOption("source-config")
            .RequiredArgument("FILE")
            .StoreResult(&configs.SourceCfgPath);
        opts.AddLongOption("aggr-config")
            .RequiredArgument("FILE")
            .StoreResult(&configs.AggrCfgPath);
        opts.AddLongOption("fresh-config")
            .RequiredArgument("FILE")
            .StoreResult(&configs.FreshCfgPath);
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);

    auto tx = client->StartTransaction();
    {
        TRRFactorsCalcer calcer(tx, configs);
        TString url;
        TFileInput input(urlsFile);

        TMutex writeMutex;
        auto writerTx = tx->StartTransaction();
        auto writer = writerTx->CreateTableWriter<NRRProto::TPoolEntry>(resultTable);

        auto func = [&calcer, &writeMutex, &writer] (TString url) {
            NRRProto::TPoolEntry result;
            TString host, path;
            SplitUrlToHostAndPath(url, host, path);

            result.SetHost(host);
            result.SetPath(path);

            result.SetLastAccess(TInstant::Now().Seconds());
            result.SetHttpCode(200);

            calcer.CalcFactors(url, result.MutableFactors());

            Cerr << "factors fetched for " << url << Endl;

            {
                TGuard<TMutex> guard(writeMutex);
                writer->AddRow(result);
            }
        };

        TThreadPool queue;
        queue.Start(maxInFlight);

        while (input.ReadLine(url)) {
            queue.SafeAddFunc([url, &func](){func(url);});
        }

        queue.Stop();

        writer->Finish();
        writerTx->Commit();

        tx->Sort(
            NYT::TSortOperationSpec()
                .AddInput(resultTable)
                .Output(resultTable)
                .SortBy(NYT::TSortColumns("Host", "Path"))
        );
    }

    tx->Commit();

    return 0;
}
