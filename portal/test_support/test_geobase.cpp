#include "test_geobase.h"

#include <util/generic/hash_set.h>
#include <util/generic/set.h>
#include <util/generic/strbuf.h>
#include <util/string/cast.h>

namespace NMordaBlocks {

    TTestGeoBase::TTestGeoBase() {
    }

    TTestGeoBase::~TTestGeoBase() {
    }

    ERegion TTestGeoBase::GetRegionByIp(TStringBuf ip) const {
        Y_UNUSED(ip);
        return ERegion::REGION_EARTH;
    }

    ERegion TTestGeoBase::GetRegionByLocation(const TGeoPoint& location) const {
        if (!location)
            return ERegion::REGION_INVALID;

        for (const auto& it : Regions_) {
            const double lat = it.second.Location.Lat();
            const double lon = it.second.Location.Lon();
            if (lat - 10 < location.Lat() && location.Lat() < lat + 10 &&
                lon - 10 < location.Lon() && location.Lon() < lon + 10) {
                return it.first;
            }
        }
        return ERegion::REGION_INVALID;
    }

    ERegion TTestGeoBase::GetParentId(ERegion id) const {
        TRegionNode node;
        if(!GetRegionNode(id, &node))
            return ERegion::REGION_INVALID;

        if (node.ParentId != id)
            return node.ParentId;
        return ERegion::REGION_INVALID;
    }

    void TTestGeoBase::AddAllParents(ERegion region,
        TVector<ERegion>* regions) const
    {
        int depth = 0;
        ERegion currentRegion = region;
        while (currentRegion != ERegion::REGION_INVALID) {
            if (++depth > DEPTH_LIMIT) {
                break;
            }
            currentRegion = GetParentId(currentRegion);
            regions->push_back(currentRegion);
        }
    }

    TVector<ERegion> TTestGeoBase::GetOnlyParents(ERegion region) const {
        TVector<ERegion> result;
        AddAllParents(region, &result);
        return result;
    }

    TVector<ERegion> TTestGeoBase::GetRegionWithParents(ERegion region) const
    {
        TVector<ERegion> result;
        result.push_back(region);
        AddAllParents(region, &result);
        return result;
    }

    void TTestGeoBase::AddAllParentsAndCapitals(ERegion region,
        TVector<ERegion>* regions) const
    {
        if (region == REGION_INVALID)
            return;

        THashSet<ERegion> addedCapitals{region};
        const TVector<ERegion> parents = GetRegionWithParents(region);
        for (const auto& parent : parents) {
            if (parent != region) {
                regions->push_back(parent);
            }
            const ERegion capital = GetCapitalId(parent);
            if (capital != ERegion::REGION_INVALID && addedCapitals.insert(capital).second) {
                regions->push_back(capital);
            }
        }
    }

     void TTestGeoBase::AddAllParentsAndRegionalCapitals(ERegion region, TVector<ERegion>* regions) const {
        if (region == REGION_INVALID)
            return;

        TSet<ERegion> addedRegions;
        addedRegions.insert(region);
        TRegionNode currentNode;
        ERegion currentRegion = region;
        while (GetRegionNode(currentRegion, &currentNode)) {
            currentRegion = currentNode.ParentId;
            if (addedRegions.insert(currentNode.ParentId).second) {
                regions->push_back(currentNode.ParentId);
            }

            if (currentNode.Type < ERegionType::REGION ||
                currentNode.CapitalId == ERegion::REGION_INVALID) {
                continue;
            }

            if (addedRegions.insert(currentNode.CapitalId).second) {
                regions->push_back(currentNode.CapitalId);
            }
        }
    }

    TVector<ERegion> TTestGeoBase::GetOnlyParentsAndCapitals(ERegion region) const {
        TVector<ERegion> result;
        AddAllParentsAndCapitals(region, &result);
        return result;
    }

    TVector<ERegion> TTestGeoBase::GetRegionWithParentsAndCapitals(ERegion region) const
    {
        TVector<ERegion> result;
        result.push_back(region);
        AddAllParentsAndCapitals(region, &result);
        return result;
    }

    TVector<ERegion> TTestGeoBase::GetRegionWithParentsAndRegionalCapitals(ERegion region) const {
        TVector<ERegion> result;
        result.push_back(region);
        AddAllParentsAndRegionalCapitals(region, &result);
        return result;
    }

    TVector<ERegion> TTestGeoBase::GetOnlyParentsAndRegionalCapitals(ERegion region) const {
        TVector<ERegion> result;
        AddAllParentsAndRegionalCapitals(region, &result);
        return result;
    }

    ERegion TTestGeoBase::GetCapitalId(ERegion id) const {
        TRegionNode node;
        if (!GetRegionNode(id, &node))
            return ERegion::REGION_INVALID;

        return node.CapitalId;
    }

    ERegion TTestGeoBase::GetCountryId(ERegion id) const {
        return GetParentIdWithType(id, ERegionType::COUNTRY);
    }

    ERegion TTestGeoBase::GetParentIdWithType(ERegion id, ERegionType searchType) const {
        TRegionNode node;
        if(!GetRegionNode(id, &node))
            return ERegion::REGION_INVALID;

        while (node.Type > searchType) {
            id = node.ParentId;
            if (!GetRegionNode(node.ParentId, &node))
                return ERegion::REGION_INVALID;
        }
        if (node.Type != searchType) {
            return ERegion::REGION_INVALID;
        }
        return id;
    }

    TTestGeoBase::ERegionType TTestGeoBase::GetRegionType(ERegion id) const {
        TRegionNode node;
        if(!GetRegionNode(id, &node))
            return ERegionType::REMOVED;
        return node.Type;
    }

    bool TTestGeoBase::GetRegionNode(ERegion id,
                                     TRegionNode* outNode) const {
        Y_ASSERT(outNode);
        const TRegionInfo* region = GetRegion(id);
        if (!region)
            return false;

        outNode->ParentId = region->Parent;
        outNode->CapitalId = region->Capital;
        outNode->CityId = region->City;
        outNode->Type = region->Type;
        outNode->Location = region->Location;
        return true;
    }

    TVector<TTestGeoBase::TRegionNode> TTestGeoBase::GetRegionAndParentsNodes(ERegion region) const {
        if (region == REGION_INVALID)
            return {};

        TVector<TRegionNode> result(1);
        int depth = 0;
        ERegion currentRegion = region;
        while (depth < DEPTH_LIMIT && GetRegionNode(currentRegion, &result.back())) {
            ++depth;
            currentRegion = result.back().ParentId;
            result.emplace_back();
        }
        result.resize(result.size() - 1);
        return result;
    }

    TString TTestGeoBase::GetRegionName(ERegion id) const {
        return GetRegionNameWithCase(id, ELinguisticsCase::Nominative);
    }

    TString TTestGeoBase::GetRegionAliasName(ERegion id) const {
        return GetRegionName(id);
    }

    TString TTestGeoBase::GetRegionNameWithCase(ERegion id, ELinguisticsCase lCase) const {
        const TRegionInfo* region = GetRegion(id);
        if (!region)
            return {};

        const auto it = region->Names.find(lCase);
        if (it == region->Names.end()) {
            throw std::runtime_error(
                ("No suitable name for region with id " + ToString(static_cast<int>(id)) + ".")
                    .c_str());
        }
        return it->second;
    }

    IGeoBase::TZoom TTestGeoBase::GetZoomForRegion(ERegion id) const
    {
        const TRegionInfo* region = GetRegion(id);
        if (!region)
            return INVALID_ZOOM;
        return region->Zoom;
    }

    TGeoPoint TTestGeoBase::GetCentralGeoPointForRegion(ERegion id) const {
        const TRegionInfo* region = GetRegion(id);
        if (!region)
            return TGeoPoint();
        return region->Location;
    }

    NDatetime::TTimeZone TTestGeoBase::GetTimeZone(ERegion id) const {
        Y_UNUSED(id);
        return NDatetime::GetTimeZone("Europe/Moscow");
    }

    TTestGeoBase::TRegionInfo& TTestGeoBase::GetOrMakeRegion(ERegion id) {
        return Regions_[id];
    }

    void TTestGeoBase::FillParents(const TVector<int>& regions) {
        for (size_t i = 0; i + 1 < regions.size(); ++i) {
            auto& regionInfo = GetOrMakeRegion(static_cast<ERegion>(regions[i]));
            regionInfo.SetParent(static_cast<ERegion>(regions[i + 1]));
        }
    }

    const TTestGeoBase::TRegionInfo* TTestGeoBase::GetRegion(ERegion id) const {
        const auto it = Regions_.find(id);
        if (it == Regions_.end()) {
            return nullptr;
        }
        return &(it->second);
    }

    void TTestGeoBase::Clear() {
        Regions_.clear();
    }

    bool TTestGeoBase::IsReady() const {
        return true;
    }

    void TTestGeoBase::Start() {
    }

    void TTestGeoBase::BeforeShutDown() {
    }

    void TTestGeoBase::ShutDown() {
    }

    TString TTestGeoBase::GetServiceName() const {
        return "TestGoebase";
    }

    std::unique_ptr<TGeoLocationProto> TTestGeoBase::MakeLaasResponse(const TString& ip, const TString* yp, const TString* ys) const {
        Y_UNUSED(ip);
        Y_UNUSED(ys);
        Y_UNUSED(yp);
        auto result = std::make_unique<TGeoLocationProto>();
        *result = laasResponse_;
        return result;
    }

} // namespace NMordaBlocks
