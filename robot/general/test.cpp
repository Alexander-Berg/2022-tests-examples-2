#include "test.h"

namespace NSamovar {
    namespace {
        void ProduceZoneFactors(
            const ESamovarFactorSlice factorProducerId,
            const TRobotZoneCode zone,
            const TUrlRecord& url,
            const size_t factorCount,
            TVector<float>& ret
        ) {
            static const ESamovarFactorSlice MinFactorProducerId = ESamovarFactorSlice::Test1Zoned0;
            const size_t urlIdx = url.GetDebugCounter();
            const size_t factorProducerIdx = (int)factorProducerId - (int)MinFactorProducerId;

            for (size_t factorIdx = 0; factorIdx < factorCount; ++factorIdx) {
                ret[factorIdx] = (((factorProducerIdx + 1) * 10 + (size_t)zone) * 100 + urlIdx) * 100 + factorIdx;
            }
        }

        void ProduceAllZoneFactors(
            const ESamovarFactorSlice factorProducerId,
            const TUrlRecord& url,
            const size_t factorCount,
            TVector<TVector<float>>& ret
        ) {
            for (TRobotZoneCode zone = 0; zone < ret.size(); ++zone) {
                if (ret[zone]) {
                    ProduceZoneFactors(factorProducerId, zone, url, factorCount, ret[zone]);
                }
            }
        }
    }

    void TRankFactorsProducer<ESamovarFactorSlice::Test1Zoned0>::ProduceFactors(const TUrlRecord& url, TVector<TVector<float>>& factors) const {
        ProduceAllZoneFactors(ESamovarFactorSlice::Test1Zoned0, url, FeatureVectorSize, factors);
    }

    void TRankFactorsProducer<ESamovarFactorSlice::Test2Zoned1>::ProduceFactors(const TUrlRecord& url, TVector<TVector<float>>& factors) const {
        ProduceAllZoneFactors(ESamovarFactorSlice::Test2Zoned1, url, FeatureVectorSize, factors);
    }

    void TRankFactorsProducer<ESamovarFactorSlice::Test3NonZoned0>::ProduceFactors(const TUrlRecord& url, TVector<float>& factors) const {
        ProduceZoneFactors(ESamovarFactorSlice::Test3NonZoned0, 0, url, FeatureVectorSize, factors);
    }

    void TRankFactorsProducer<ESamovarFactorSlice::Test4NonZoned1>::ProduceFactors(const TUrlRecord& url, TVector<float>& factors) const {
        ProduceZoneFactors(ESamovarFactorSlice::Test4NonZoned1, 0, url, FeatureVectorSize, factors);
    }

    //TMaybe<EFactorAggrSetup> TRankFactorsProducer<ESamovarFactorSlice::Test1Zoned0>::AggrFactorsSetup;
    //TMaybe<EFactorAggrSetup> TRankFactorsProducer<ESamovarFactorSlice::Test2Zoned1>::AggrFactorsSetup;
    //TMaybe<EFactorAggrSetup> TRankFactorsProducer<ESamovarFactorSlice::Test3NonZoned0>::AggrFactorsSetup;
    //TMaybe<EFactorAggrSetup> TRankFactorsProducer<ESamovarFactorSlice::Test4NonZoned1>::AggrFactorsSetup;
}
