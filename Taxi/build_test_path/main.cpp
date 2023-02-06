#include <iomanip>
#include <iostream>
#include <vector>

#include <yandex/taxi/graph2/container.h>
#include <yandex/taxi/graph2/graph_builder.h>
#include <yandex/taxi/graph2/graph.h>
#include <yandex/taxi/graph2/routing/leptidea.h>

#include <maps/libs/geolib/include/distance.h>

using NTaxiExternal::NGraph2::TRoadGraphFileLoader;
using TaxiGraph = NTaxiExternal::NGraph2::TGraph;
using NTaxiExternal::NGraph2::TContainer;
using NTaxiExternal::NGraph2::TLeptidea;
using NTaxiExternal::NGraph2::TPoint;
using NTaxiExternal::NGraph2::TRouterConfig;

enum class EOutputFormat {
    EasyView,
    Raw
};

TString GraphPath(const TStringBuf& path, const TStringBuf& file) {
    return path + TString("/") + file;
}

int main(int argc, char* argv[]) {
    if (argc < 2 || argc > 3) {
        std::cerr << "Usage: taxi-graph-tool-path <path to graph directory> [output format: easyview|raw (default)]." << std::endl;
        return 1;
    }

    EOutputFormat output_format = EOutputFormat::Raw;
    if (argc == 3) {
        if (std::string(argv[2]) == "easyview") {
            output_format = EOutputFormat::EasyView;
        } else if (std::string(argv[2]) == "raw") {
            output_format = EOutputFormat::Raw;
        } else {
            std::cerr << "Unknown output format: " << argv[2] << "." << std::endl;
            return 2;
        }
    }

    TaxiGraph graph(
        TRoadGraphFileLoader::Create(
            GraphPath(argv[1], "road_graph.fb").c_str(),
            GraphPath(argv[1], "rtree.fb").c_str()
        )
    );
    TLeptidea leptidea(
        graph,
        GraphPath(argv[1], "l6a_topology.fb.7").c_str(),
        GraphPath(argv[1], "l6a_data.fb.7").c_str()
    );
    leptidea.Init(1);

    const auto& paths = leptidea.CalcRoute(
        // threadId
        0,

        // from
        TPoint{37.533547, 55.700951},

        // to
        TPoint{37.548664, 55.697747});
    if (!paths.isInitialized || paths.value.Empty()) {
        std::cerr << "No paths." << std::endl;
        return 3;
    }

    if (output_format == EOutputFormat::EasyView) {
        // Formatted output for https://wiki.yandex-team.ru/users/idg/yandex-maps-easyview/
        // Usage:
        // $ ./taxi-graph-tool-path <path> > map.txt
        // $ cat map.txt | easyview
        const std::vector<TString> colors = {
            "black",
            "red",
            "lime",
            "blue",
            "yellow",
            "magenta",
            "cyan",
            "gray",
            "silver",
            "maroon",
            "green",
            "navy",
            "olive",
            "purple",
            "teal"};

        std::cout.setf(std::ios::fixed, std::ios::floatfield);
        std::cout.precision(6);

        size_t color_idx = 0;
        for (size_t i = 0; i < paths.value.Size(); i++) {
            const auto& path = paths.value[i];

            assert(!path.Path.Empty());
            const auto firstPoint = path.Path[0].Point;
            const auto lastPoint = path.Path[path.Path.Size() - 1].Point;

            std::cout << "!pointstyle=red:red:6" << std::endl;
            std::cout << firstPoint.Lon << " " << firstPoint.Lat << std::endl;
            std::cout << "!pointstyle=blue:blue:6" << std::endl;
            std::cout << lastPoint.Lon << " " << lastPoint.Lat << std::endl;

            std::cout << "!linestyle=" << colors[color_idx++ % colors.size()] << ":3" << std::endl;
            for (size_t p = 0; p < path.Path.Size(); p++) {
                const auto& point = path.Path[p];
                std::cout << point.Point.Lon << " " << point.Point.Lat << " ";
            }
            std::cout << std::endl;
        }

        return 0;
    }

    for (size_t i = 0; i < paths.value.Size(); i++) {
        std::cout << "Path #" << i << std::endl;

        const auto& path = paths.value[i];
        for (size_t p = 0; p < path.Path.Size(); p++) {
            const auto& point = path.Path[p];
            std::cout << std::fixed << std::setprecision(6)
                      << point.Point.Lon << " " << point.Point.Lat
                      << std::setprecision(3)
                      << " edgeId: " << point.EdgeId
                      << " time: " << point.Duration.value
                      << " length: " << point.Length.value << std::endl;
        }
        std::cout << std::endl;
    }
}
