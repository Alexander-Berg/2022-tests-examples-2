#pragma once

#include <portal/morda/blocks/services/geobase/geobase.h>
#include <portal/morda/blocks/request_context/request_context.pb.h>

#include <util/generic/map.h>
#include <util/generic/string.h>
#include <util/generic/vector.h>

#include <utility>

namespace NMordaBlocks {

    class TTestGeoBase : public IGeoBase {
    public:
        struct TRegionInfo {
            ERegion Parent = ERegion::REGION_INVALID;
            ERegion Capital = ERegion::REGION_INVALID;
            ERegion City = ERegion::REGION_INVALID;
            ERegionType Type = ERegionType::OTHER;
            TMap<ELinguisticsCase, TString> Names;
            TGeoPoint Location;
            TZoom Zoom = INVALID_ZOOM;

            TRegionInfo& SetParent(ERegion parent) {
                Parent = parent;
                return *this;
            }

            TRegionInfo& SetCapital(ERegion capital) {
                Capital = capital;
                return *this;
            }

            TRegionInfo& SetCity(ERegion city) {
                City = city;
                return *this;
            }

            TRegionInfo& SetType(ERegionType type) {
                Type = type;
                return *this;
            }

            TRegionInfo& SetName(ELinguisticsCase lCase, const TString& name) {
                Names[lCase] = name;
                return *this;
            }

            TRegionInfo& SetLocation(TGeoPoint location) {
                Location = location;
                return *this;
            }

            TRegionInfo& SetZoom(TZoom zoom) {
                Zoom = zoom;
                return *this;
            }
        };

        TTestGeoBase();
        ~TTestGeoBase() override;

        ERegion GetRegionByIp(TStringBuf ip) const override;
        ERegion GetRegionByLocation(const TGeoPoint& location) const override;
        ERegion GetParentId(ERegion id) const override;
        TVector<ERegion> GetRegionWithParents(ERegion region) const override;
        TVector<ERegion> GetOnlyParents(ERegion id) const override;
        TVector<ERegion> GetRegionWithParentsAndCapitals(ERegion region) const override;
        TVector<ERegion> GetOnlyParentsAndCapitals(ERegion id) const override;
        TVector<ERegion> GetRegionWithParentsAndRegionalCapitals(ERegion id) const override;
        TVector<ERegion> GetOnlyParentsAndRegionalCapitals(ERegion id) const override;
        ERegion GetCapitalId(ERegion id) const override;
        ERegion GetCountryId(ERegion id) const override;
        ERegion GetParentIdWithType(ERegion id, ERegionType searchType) const override;
        ERegionType GetRegionType(ERegion id) const override;
        bool GetRegionNode(ERegion id,
                           TRegionNode* outNode) const override;
        TVector<TRegionNode> GetRegionAndParentsNodes(ERegion id) const override;
        TString GetRegionName(ERegion id) const override;
        TString GetRegionAliasName(ERegion id) const override;
        TString GetRegionNameWithCase(ERegion id, ELinguisticsCase lCase) const override;
        TZoom GetZoomForRegion(ERegion id) const override;
        TGeoPoint GetCentralGeoPointForRegion(ERegion id) const override;
        NDatetime::TTimeZone GetTimeZone(ERegion id) const override;
        std::unique_ptr<TGeoLocationProto> MakeLaasResponse(const TString& ip, const TString* yp, const TString* ys) const override;

        TRegionInfo& GetOrMakeRegion(ERegion id);
        void FillParents(const TVector<int>& regions);

        void Clear();

        // IService overrides:
        bool IsReady() const override;
        void Start() override;
        void BeforeShutDown() override;
        void ShutDown() override;
        TString GetServiceName() const override;

    private:
        void AddAllParents(ERegion id, TVector<ERegion>* regions) const;
        void AddAllParentsAndCapitals(ERegion id, TVector<ERegion>* regions) const;
        void AddAllParentsAndRegionalCapitals(ERegion region, TVector<ERegion>* regions) const;

    private:
        const TRegionInfo* GetRegion(ERegion id) const;
        TMap<ERegion, TRegionInfo> Regions_;

        TGeoLocationProto laasResponse_;
    };

} // namespace NMordaBlocks
