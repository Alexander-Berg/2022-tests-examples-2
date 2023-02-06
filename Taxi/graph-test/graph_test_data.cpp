// Dummy file
#include "graph_test_data.h"

namespace NTaxi::NGraph2 {
    namespace {
        using TEdgeDesc = TGraphTestData::TEdgeDesc;
        using TNumeratedDesc = std::pair<TEdgeDesc, size_t>;
        using TNumeratedEdges = TVector<TNumeratedDesc>;
        // Map original sequential edge id to resulting EdgeId from Graph built
        using TEdgeMapping = std::unordered_map<ui32, TEdgeId>;

        /// Numerate original edges to restore original indices.
        /// Needed to build mapping original edge index to RoadGraph EdgeId
        TNumeratedEdges NumerateAndSort(const TVector<TEdgeDesc>& edges) {
            const auto EdgesCount = edges.size();

            TNumeratedEdges ret(EdgesCount);
            for (size_t i = 0; i < EdgesCount; ++i)
                ret[i] = std::make_pair(edges[i], i);

            // Sort edges by source vertex index.
            // RoadGraph builder has this condition to build road graph
            std::stable_sort(ret.begin(), ret.end(),
                             [](const auto& x, const auto& y) { return x.first.source < y.first.source; });

            return ret;
        }

        TEdgeMapping MakeEdgeMapping(const TNumeratedEdges& numeratedEdges) {
            TEdgeMapping ret;
            for (size_t i = 0; i < numeratedEdges.size(); ++i) {
                const auto& elem = numeratedEdges[i];
                const auto& result_id = static_cast<TEdgeId>(i);
                const auto& original_id = elem.second;
                ret[original_id] = result_id;
            }

            return ret;
        }
    }

    TGraph TGraphTestData::CreateRoadGraph(const TVector<TPoint>& vertices,
                                           const TVector<TEdgeDesc>& edges,
                                           const TVector<TTurnInfoDesc>& turnInfos,
                                           TEdgeMapping* edgeMapping) {
        static const constexpr size_t RoadCount = 0;
        const auto edgesCount = edges.size();
        const auto verticesCount = vertices.size();

        const auto& numeratedEdges = NumerateAndSort(edges);
        auto mapping = MakeEdgeMapping(numeratedEdges);

        auto builder = std::make_unique<TRoadGraphDataBuilder>(verticesCount, edgesCount, RoadCount);

        for (size_t i = 0; i < verticesCount; ++i) {
            const auto vertexId = static_cast<TVertexId>(i);
            builder->SetVertexGeometry(vertexId, vertices[i]);
        }

        for (ui32 i = 0; i < edgesCount; ++i) {
            const auto& numeratedEdge = numeratedEdges[i];
            const auto& edge_desc = numeratedEdge.first;
            const auto& source = TVertexId{edge_desc.source};
            const auto& target = TVertexId{edge_desc.target};
            const auto edgeId = TEdgeId{i};

            TEdge edge;
            edge.Id = edgeId;
            edge.Source = source;
            edge.Target = target;
            builder->SetEdge(edge, true);

            auto data = TEdgeData{edge_desc.speed, edge_desc.length};
            data.Category = edge_desc.category;
            data.Speed = edge_desc.speed;

            TPolyline geometry;
            const auto pointFrom = vertices.at(edge_desc.source);
            const auto pointTo = vertices.at(edge_desc.target);
            geometry.AddPoint(pointFrom);
            geometry.AddPoint(pointTo);

            builder->SetEdgeData(edgeId, data, geometry);
        }

        for (const auto& desc : turnInfos) {
            const auto source = mapping.at(desc.source);
            const auto target = mapping.at(desc.target);

            TTurnInfo info;
            info.Weight = 0;
            info.Forbidden = desc.forbidden;
            info.AccessPass = desc.accessPass;
            info.CountryBorder = desc.countryBorder;

            builder->SetTurnInfo(source, target, info);
        }

        builder->Build();

        if (edgeMapping)
            *edgeMapping = std::move(mapping);

        return TGraph(std::move(builder));
    }
}
