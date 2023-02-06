#pragma once

#include <robot/samovar/algo/ranks/slices/producers.h>

#include <util/generic/vector.h>
#include <util/generic/maybe.h>
#include <util/generic/string.h>

namespace NSamovar {

#define DEFINE_TEST_PRODUCER(id, zoned, feature_count, ret) \
    template <> \
    class TRankFactorsProducer<ESamovarFactorSlice::id>: public IFactorsProducer<zoned> { \
    public: \
        size_t GetFactorCount() const final override { \
            return FeatureCount; \
        } \
        const TString GetFactorName(size_t) const final override { \
            Y_FAIL(); \
            static const TString name; \
            return name; \
        } \
 \
        static const size_t FeatureCount = feature_count; \
        static const size_t FeatureVectorSize = FeatureCount - 3; \
 \
        void ProduceFactors(const TUrlRecord&, ret&) const final override; \
    };

    DEFINE_TEST_PRODUCER(Test1Zoned0, true, 27, TVector<TVector<float>>)
    DEFINE_TEST_PRODUCER(Test2Zoned1, true, 25, TVector<TVector<float>>)
    DEFINE_TEST_PRODUCER(Test3NonZoned0, false, 23, TVector<float>)
    DEFINE_TEST_PRODUCER(Test4NonZoned1, false, 19, TVector<float>)

#undef DEFINE_TEST_PRODUCER
}
