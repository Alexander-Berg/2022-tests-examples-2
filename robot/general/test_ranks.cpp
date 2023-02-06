#include "test_ranks.h"

#include "slices/producers.h"

using namespace NSamovar;

const TDuration TRankCalcer<R_TEST0>::FreshTtl = TDuration::Hours(1);
const TDuration TRankCalcer<R_TEST0>::OrdinaryTtl = TDuration::Days(3);

TRankCalcer<R_TEST0>::TRankCalcer(const TRankFactorsProducers& producers)
        : TGenericRankCalcer(R_TEST0, CreateSlicesSetup(), producers) {
}

TSlicesMapping TRankCalcer<R_TEST0>::CreateSlicesSetup() {
    return {
            {NFactorSlices::EFactorSlice::ROBOT_PRIMARY, ESamovarFactorSlice::Base},
            {NFactorSlices::EFactorSlice::WEB_PRODUCTION, ESamovarFactorSlice::WebProduction},
            {NFactorSlices::EFactorSlice::ROBOT_SELECTION_RANK, ESamovarFactorSlice::RobotSelectionRank},
            {NFactorSlices::EFactorSlice::ROBOT_INCOMING_LINKS, ESamovarFactorSlice::IncomingLinks},
            {NFactorSlices::EFactorSlice::ROBOT_ZONAL, ESamovarFactorSlice::RobotZonal},
    };
}

bool TRankCalcer<R_TEST0>::UrlFilter(const TUrlRecord& url, const NRecord::TUrlRanksState::TRank* prev, const TRanksCalcEnv& env) {
    if (!url.GetCrawlResult().HasHTTPCode()) {
        return false;
    }
    const auto ttl = env.FreshRanks ? FreshTtl : OrdinaryTtl;
    return !prev || GetNow() > prev->Mtime + ttl;
}

const TDuration TRankCalcer<R_TEST1>::FreshTtl = TDuration::Hours(1);
const TDuration TRankCalcer<R_TEST1>::OrdinaryTtl = TDuration::Days(3);

TRankCalcer<R_TEST1>::TRankCalcer(const TRankFactorsProducers& producers)
        : TGenericRankCalcer(R_TEST1, CreateSlicesSetup(), producers) {
}

TSlicesMapping TRankCalcer<R_TEST1>::CreateSlicesSetup() {
    return {
            {NFactorSlices::EFactorSlice::ROBOT_PRIMARY, ESamovarFactorSlice::Base},
            {NFactorSlices::EFactorSlice::ROBOT_INCOMING_LINKS, ESamovarFactorSlice::IncomingLinks},
    };
}

bool TRankCalcer<R_TEST1>::UrlFilter(const TUrlRecord&, const NRecord::TUrlRanksState::TRank* prev, const TRanksCalcEnv& env) {
    const auto ttl = env.FreshRanks ? FreshTtl : OrdinaryTtl;
    return !prev || GetNow() > prev->Mtime + ttl;
}
