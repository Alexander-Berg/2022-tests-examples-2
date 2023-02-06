#pragma once

#include <taxi/graph/libs/search2/dijkstra_edge_searcher.h>

struct TBaseSearchTraits {
    static constexpr size_t HeapReserve = 8;
    static constexpr size_t EdgeInfoStorageReserve = 8;
    static constexpr bool DisableSearchingThroughNonPavedOrPoorConditionRoads = false;
};

struct TTestForwardSearchTraits: TBaseSearchTraits {
    using TDirectionControl = NTaxi::NGraphSearch2::TForwardSearchControl<NTaxi::NGraph2::TGraphFacadeCommon>;
    using EResidentialAreaDriveMode = NTaxi::NGraphSearch2::EResidentialAreaDriveMode;
    using EBoomBarriersAreaDriveMode = NTaxi::NGraphSearch2::EBoomBarriersAreaDriveMode;
    [[maybe_unused]] static constexpr bool TrackPaths = true;
    [[maybe_unused]] static constexpr bool TrackTollRoads = true;
    [[maybe_unused]] static constexpr bool TrackEdgeLeeway = false;
    [[maybe_unused]] static constexpr bool DisableTollRoads = false;
    [[maybe_unused]] static constexpr EResidentialAreaDriveMode ResidentialAreaDriveMode = EResidentialAreaDriveMode::PassThroughProhibited;
    [[maybe_unused]] static constexpr EBoomBarriersAreaDriveMode BoomBarriersAreaDriveMode = EBoomBarriersAreaDriveMode::PassThroughProhibited;
};

struct TTestForwardEntryProhibitedSearchTraits: TBaseSearchTraits {
    using TDirectionControl = NTaxi::NGraphSearch2::TForwardSearchControl<NTaxi::NGraph2::TGraphFacadeCommon>;
    using EResidentialAreaDriveMode = NTaxi::NGraphSearch2::EResidentialAreaDriveMode;
    using EBoomBarriersAreaDriveMode = NTaxi::NGraphSearch2::EBoomBarriersAreaDriveMode;
    [[maybe_unused]] static constexpr bool TrackPaths = true;
    [[maybe_unused]] static constexpr bool TrackTollRoads = true;
    [[maybe_unused]] static constexpr bool TrackEdgeLeeway = false;
    [[maybe_unused]] static constexpr bool DisableTollRoads = false;
    [[maybe_unused]] static constexpr EResidentialAreaDriveMode ResidentialAreaDriveMode = EResidentialAreaDriveMode::EntryProhibited;
    [[maybe_unused]] static constexpr EBoomBarriersAreaDriveMode BoomBarriersAreaDriveMode = EBoomBarriersAreaDriveMode::EntryProhibited;
};

struct TTestReverseSearchTraits: TBaseSearchTraits {
    using TDirectionControl = NTaxi::NGraphSearch2::TReverseSearchControl<NTaxi::NGraph2::TGraphFacadeCommon>;
    using EResidentialAreaDriveMode = NTaxi::NGraphSearch2::EResidentialAreaDriveMode;
    using EBoomBarriersAreaDriveMode = NTaxi::NGraphSearch2::EBoomBarriersAreaDriveMode;
    [[maybe_unused]] static constexpr bool TrackPaths = true;
    [[maybe_unused]] static constexpr bool TrackTollRoads = true;
    [[maybe_unused]] static constexpr bool TrackEdgeLeeway = false;
    [[maybe_unused]] static constexpr bool DisableTollRoads = false;
    [[maybe_unused]] static constexpr EResidentialAreaDriveMode ResidentialAreaDriveMode = EResidentialAreaDriveMode::PassThroughProhibited;
    [[maybe_unused]] static constexpr EBoomBarriersAreaDriveMode BoomBarriersAreaDriveMode = EBoomBarriersAreaDriveMode::PassThroughProhibited;
};

struct TTestReverseSearchTraitsLeewayEnable: TBaseSearchTraits {
    using TDirectionControl = NTaxi::NGraphSearch2::TReverseSearchControl<NTaxi::NGraph2::TGraphFacadeCommon>;
    using EResidentialAreaDriveMode = NTaxi::NGraphSearch2::EResidentialAreaDriveMode;
    using EBoomBarriersAreaDriveMode = NTaxi::NGraphSearch2::EBoomBarriersAreaDriveMode;
    [[maybe_unused]] static constexpr bool TrackPaths = true;
    [[maybe_unused]] static constexpr bool TrackTollRoads = true;
    [[maybe_unused]] static constexpr bool TrackEdgeLeeway = true;
    [[maybe_unused]] static constexpr bool DisableTollRoads = false;
    [[maybe_unused]] static constexpr EResidentialAreaDriveMode ResidentialAreaDriveMode = EResidentialAreaDriveMode::PassThroughProhibited;
    [[maybe_unused]] static constexpr EBoomBarriersAreaDriveMode BoomBarriersAreaDriveMode = EBoomBarriersAreaDriveMode::PassThroughProhibited;
};

struct TTestReverseSearchTraitsDisableDriveThroughNonPaved: TBaseSearchTraits {
    using TDirectionControl = NTaxi::NGraphSearch2::TReverseSearchControl<NTaxi::NGraph2::TGraphFacadeCommon>;
    using EResidentialAreaDriveMode = NTaxi::NGraphSearch2::EResidentialAreaDriveMode;
    using EBoomBarriersAreaDriveMode = NTaxi::NGraphSearch2::EBoomBarriersAreaDriveMode;
    [[maybe_unused]] static constexpr bool TrackPaths = true;
    [[maybe_unused]] static constexpr bool TrackTollRoads = true;
    [[maybe_unused]] static constexpr bool TrackEdgeLeeway = false;
    [[maybe_unused]] static constexpr bool DisableTollRoads = false;
    [[maybe_unused]] static constexpr EResidentialAreaDriveMode ResidentialAreaDriveMode = EResidentialAreaDriveMode::PassThroughProhibited;
    [[maybe_unused]] static constexpr EBoomBarriersAreaDriveMode BoomBarriersAreaDriveMode = EBoomBarriersAreaDriveMode::PassThroughProhibited;
    [[maybe_unused]] static constexpr bool DisableSearchingThroughNonPavedOrPoorConditionRoads = true;
};

struct TTestReverseSearchTraitsDisabledTollRoads: TBaseSearchTraits {
    using TDirectionControl = NTaxi::NGraphSearch2::TReverseSearchControl<NTaxi::NGraph2::TGraphFacadeCommon>;
    using EResidentialAreaDriveMode = NTaxi::NGraphSearch2::EResidentialAreaDriveMode;
    using EBoomBarriersAreaDriveMode = NTaxi::NGraphSearch2::EBoomBarriersAreaDriveMode;
    [[maybe_unused]] static constexpr bool TrackPaths = true;
    [[maybe_unused]] static constexpr bool TrackTollRoads = true;
    [[maybe_unused]] static constexpr bool TrackEdgeLeeway = false;
    [[maybe_unused]] static constexpr bool DisableTollRoads = true;
    [[maybe_unused]] static constexpr EResidentialAreaDriveMode ResidentialAreaDriveMode = EResidentialAreaDriveMode::EntryProhibited;
    [[maybe_unused]] static constexpr EBoomBarriersAreaDriveMode BoomBarriersAreaDriveMode = EBoomBarriersAreaDriveMode::EntryProhibited;
};

/// Search traits flags for transformator
enum struct TTestSearchTraitsFlags: unsigned char {
    kTrackPaths = 1,
    kTrackEdgeLeeway = 2,
    // kSomeOtherElement = 16,
    // keep kMaxElem pointing to the last element
    kMaxElem = kTrackEdgeLeeway,
    kAllFlagsSet = 2 * kMaxElem - 1
};

/// Contractor Search Traits for creating searcher using transformator
template <unsigned char Flags>
struct TTestSearchTraitsWithFlags: TBaseSearchTraits {
    using TDirectionControl = NTaxi::NGraphSearch2::TReverseSearchControl<NTaxi::NGraph2::TGraphFacadeCommon>;
    using EResidentialAreaDriveMode = NTaxi::NGraphSearch2::EResidentialAreaDriveMode;
    using EBoomBarriersAreaDriveMode = NTaxi::NGraphSearch2::EBoomBarriersAreaDriveMode;
    static constexpr unsigned char MyFlags = Flags;
    static constexpr bool TrackPaths = MyFlags & static_cast<unsigned char>(TTestSearchTraitsFlags::kTrackPaths);
    static constexpr bool TrackEdgeLeeway = MyFlags & static_cast<unsigned char>(TTestSearchTraitsFlags::kTrackEdgeLeeway);
    static constexpr bool TrackTollRoads = true;
    [[maybe_unused]] static constexpr bool DisableTollRoads = true;
    [[maybe_unused]] static constexpr EResidentialAreaDriveMode ResidentialAreaDriveMode = EResidentialAreaDriveMode::EntryProhibited;
    [[maybe_unused]] static constexpr EBoomBarriersAreaDriveMode BoomBarriersAreaDriveMode = EBoomBarriersAreaDriveMode::EntryProhibited;
};

struct TTestSettings {
    bool TrackPaths = true;
    bool TrackEdgeLeeway = true;
};

struct TTestSearchTraitsToFlagsConverter {
    static unsigned char GetFlags(const TTestSettings& settings) {
        unsigned char result{0};
        if (settings.TrackPaths) {
            result |= static_cast<unsigned char>(TTestSearchTraitsFlags::kTrackPaths);
        }

        if (settings.TrackEdgeLeeway) {
            result |= static_cast<unsigned char>(TTestSearchTraitsFlags::kTrackEdgeLeeway);
        }

        return result;
    }

    static NTaxi::NGraphSearch2::TFastSearchSettings GetSearchSettings(const TTestSettings& settings) {
        NTaxi::NGraphSearch2::TFastSearchSettings result;
        result.MaxVisitedEdgesCount = 10'000u;
        return result;
    }
};

[[maybe_unused]] inline double ToTestDouble(const std::optional<NTaxi::NGraphSearch2::TPathGeolength>& value) {
    Y_VERIFY(value);
    return value->value();
}

[[maybe_unused]] inline double ToTestDouble(const std::optional<double>& value) {
    Y_VERIFY(value);
    return *value;
}

[[maybe_unused]] inline double ToTestDouble(double value) {
    return value;
}

[[maybe_unused]] inline double ToTestDouble(NTaxi::NGraphSearch2::TPathGeolength value) {
    return value.value();
}
