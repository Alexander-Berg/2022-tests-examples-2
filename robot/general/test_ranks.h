#pragma once

#include "ranks.h"

namespace NSamovar {

    class TRankFactorsProducers;

    template <>
    class TRankCalcer<R_TEST0>: public TGenericRankCalcer {
    public:
        TRankCalcer(const TRankFactorsProducers& producers);
        static TSlicesMapping CreateSlicesSetup();
        virtual bool UrlFilter(const TUrlRecord&, const NRecord::TUrlRanksState::TRank* prev, const TRanksCalcEnv&) override;

    private:
        static const TDuration FreshTtl;
        static const TDuration OrdinaryTtl;
    };

    template <>
    class TRankCalcer<R_TEST1>: public TGenericRankCalcer {
    public:
        TRankCalcer(const TRankFactorsProducers& producers);
        static TSlicesMapping CreateSlicesSetup();
        virtual bool UrlFilter(const TUrlRecord&, const NRecord::TUrlRanksState::TRank* prev, const TRanksCalcEnv&) override;

    private:
        static const TDuration FreshTtl;
        static const TDuration OrdinaryTtl;
    };

}
