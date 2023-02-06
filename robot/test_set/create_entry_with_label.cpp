#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <library/cpp/getopt/last_getopt.h>

#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/util/temp_table.h>

#include <library/cpp/string_utils/url/url.h>
#include <util/stream/file.h>


int CreateEntryWithLabel(int argc, const char** argv) {
    TString cluster;
    TString urlsFile;
    TString resultTable;
    TString label;
    double entryWeight;
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
        opts.AddLongOption("label")
            .RequiredArgument("STR")
            .Required()
            .StoreResult(&label);
        opts.AddLongOption("result")
            .RequiredArgument("TABLE")
            .Required()
            .StoreResult(&resultTable);
        opts.AddLongOption("entry-weight")
            .RequiredArgument("DOUBLE")
            .Required()
            .StoreResult(&entryWeight);
        NLastGetopt::TOptsParseResult res(&opts, argc, argv);
    }

    auto client = NYT::CreateClient(cluster);

    auto tx = client->StartTransaction();

    {
        auto writerTx = tx->StartTransaction();
        auto writer = writerTx->CreateTableWriter<NRRProto::TPoolEntry>(resultTable);
        TString url;
        TFileInput input(urlsFile);

        while (input.ReadLine(url)) {
            NRRProto::TPoolEntry entry;
            TString host, path;
            SplitUrlToHostAndPath(url, host, path);
            entry.SetHost(host);
            entry.SetPath(path);
            auto* newLabel = entry.MutableLabels()->AddLabelItems();
            newLabel->SetName(label);
            newLabel->SetCounter(1.0);
            writer->AddRow(entry);
        }
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
