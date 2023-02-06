#include "check_test.h"
#include "common.h"
#include "tables.h"
#include "sample_common.h"

#include <robot/jupiter/library/opt/common/common.h>
#include <robot/jupiter/library/opt/mropt.h>
#include <robot/jupiter/library/tables/export.h>

#include <robot/library/field_splitter/field_splitter.h>

#include <util/generic/serialized_enum.h>

namespace NMercury {
    using namespace NJupiter;
    namespace {
        constexpr auto RECRAWL_TABLE_ERROR = "Something wrong with recrawl table: ";
        constexpr auto MERCURY_UNION_TABLE_ERROR = "Something wrong with mercury union table: ";

        template <typename TProto>
        NYT::TTableReaderPtr<TProto> GetTableReader(int argc, const char* argv[]) {
            TCmdParams params;
            TString tablePath;

            TMrOpts mrOpts;
            TMrOptsParser(params, mrOpts)
                .AddServerName();

            params.AddRequired("table-path", "Path to test table", "<path>", &tablePath);

            params.Parse(argc, argv);

            NYT::IClientPtr client = NYT::CreateClient(mrOpts.ServerName);
            TTable<TProto> table{client, tablePath};
            table.EnsureExists();
            return table.GetReader();
        }

        THashMap<TString, TFastAnnotationSourcePtr> GetSpecialHostMap(const TVector<ERowDestiny>& destinies, const TVector<ERowAvailability>& availabilities, bool includeCandidates) {
            THashMap<TString, TFastAnnotationSourcePtr> result;
            auto sources = TFastAnnotationTables::GetFastAnnotationSources();
            for (auto source : sources) {
                if (!includeCandidates && source->IsCandidate()) {
                    continue;
                }
                for (auto destiny : destinies) {
                    for (auto availability : (source->IsFilterProof() ? GetEnumAllValues<ERowAvailability>().Materialize() : availabilities)) {
                        TString specialHost = GetSampleSpecialHost(source, destiny, availability);
                        result[specialHost] = source;
                    }
                }
            }
            return result;
        }

        int GlobalDecorator(std::function<void(void)> func) {
            try {
                func();
                L_INFO << "Done";
            } catch (...) {
                L_ERROR << CurrentExceptionMessage();
                return EXIT_FAILURE;
            }
            return EXIT_SUCCESS;
        }

    }

    int CheckMercuryUnionTable(int argc, const char* argv[]) {
        return GlobalDecorator([&]() {
            auto reader = GetTableReader<TInternalAnnotationTableFormat>(argc, argv);
            auto expectedHosts = GetSpecialHostMap({ERD_CHANGED, ERD_NEW, ERD_SAME}, {ERA_MERCURY_SEARCHABLE}, /*includeCandidates*/ true);
            THashSet<TString> readedHosts;
            TFieldSplitter<TInternalAnnotationTableFormat> fieldSplitter(TExportTables::GetCanonizedFactorsSplitOptions());
            for (; reader->IsValid(); reader->Next()) {
                auto row = fieldSplitter.Read(TVector<TInternalAnnotationTableFormat>{reader->GetRow()}).GetRef();

                TAnnotationTableFormat factors;
                Y_ENSURE(factors.ParseFromString(row.GetFactors()), "Can't parse TExternalUrldat");

                const auto& host = row.GetHost();
                Y_ENSURE(host == factors.GetHost(), "Host are different in host and factors fields " + host + " " + factors.DebugString());
                auto result = readedHosts.insert(host);
                Y_ENSURE(result.second, MERCURY_UNION_TABLE_ERROR << " host " << host << " isn't unique.");

                auto it = expectedHosts.find(host);
                bool expected = (it != expectedHosts.end());
                Y_ENSURE(expected, MERCURY_UNION_TABLE_ERROR << " host " << host << " isn't expected.");

                bool hasData = it->second->HasData(factors);
                Y_ENSURE(hasData, MERCURY_UNION_TABLE_ERROR << " row with host " << host << " has no data.");
            }
            L_INFO << "Readed " << readedHosts.size() << " Expected " << expectedHosts.size();
            for (const auto& [host, source] : expectedHosts) {
                bool found = readedHosts.contains(host);
                Y_ENSURE(found, MERCURY_UNION_TABLE_ERROR << " expected host " << host << " isn't found.");
            }
        });
    }

    int CheckRecrawlTable(int argc, const char* argv[]) {
        return GlobalDecorator([&]() {
            auto reader = GetTableReader<TRecrawlUrl>(argc, argv);
            auto expectedHosts = GetSpecialHostMap({ERD_CHANGED, ERD_NEW}, {ERA_MERCURY_SEARCHABLE}, /*includeCandidates*/ false);
            THashSet<TString> readedHosts;
            for (; reader->IsValid(); reader->Next()) {
                auto row = reader->GetRow();
                auto host = TString{GetSchemeHostAndPort(row.GetUrl(), false)};
                auto result = readedHosts.insert(host);
                Y_ENSURE(result.second, RECRAWL_TABLE_ERROR << " host " << host << " isn't unique.");

                bool expected = expectedHosts.contains(host);
                Y_ENSURE(expected, RECRAWL_TABLE_ERROR << " host " << host << " isn't expected.");
            }

            for (const auto& [host, source] : expectedHosts) {
                bool found = readedHosts.contains(host);
                Y_ENSURE(found, RECRAWL_TABLE_ERROR << " expected host " << host << " isn't found.");
            }
        });
    }

}
