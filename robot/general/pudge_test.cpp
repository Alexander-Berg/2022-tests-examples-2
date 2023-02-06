#include "pudge.h"

#include "tier_config.h"

#include <robot/jupiter/library/pudge/minipudge/protos/pudge_chunk_stats.pb.h>

#include <library/cpp/testing/gtest/gtest.h>

#include <util/generic/hash_set.h>


namespace NJupiter {

struct TTestChunk {
    ui32 Total = 0;
    ui32 Alive = 0;
    ui32 Added = 0;

    TPudgeChunkStats Stats() const {
        TPudgeChunkStats stats;
        stats.SetMaxLocalIdPlusOne(Total);
        stats.SetNumAliveDocs(Alive);
        stats.SetNumAddedDocs(Added);
        return stats;
    }
};

void DoTest(const TVector<TTestChunk>& chunks, bool incremental, const TTierConfig* tierConfig, const TVector<ui32>& expectedDeltaIndices) {
    // SelectPudgeDeltaChunks uses an unstable algorithm to sort chunks by number of alive docs
    // therefore it's difficult to achieve stable test results if some chunks have equal number of alive docs
    THashSet<ui32> differentAliveDocs;
    TVector<TPudgeChunkStats> statsByChunk(Reserve(chunks.size()));
    for (auto& chunk : chunks) {
        statsByChunk.push_back(chunk.Stats());
        auto inserted = differentAliveDocs.insert(chunk.Alive);
        ASSERT_TRUE(inserted.second);
    }
    TVector<ui32> actualIndices = SelectPudgeDeltaChunks(statsByChunk, incremental, "test_shard", tierConfig);

    ASSERT_EQ(actualIndices, expectedDeltaIndices);
}

TEST(SelectPudgeDeltaChunks, Simple) {
    TTierConfig tierConfig(
        5,  /* chunks */
        1,  /* minChunksToRebuild */
        1,  /* maxAdditionalSpace */
        0); /* maxLargestToSmallestChunkRatio */

    const TVector<TTestChunk> inputChunks{
        TTestChunk{.Total = 100, .Alive = 90, .Added = 50},
        TTestChunk{.Total = 123, .Alive = 120},
        TTestChunk{.Total = 61, .Alive = 40},
        TTestChunk{.Total = 142, .Alive = 80}
    };
    DoTest(inputChunks, true, &tierConfig, {4});
    DoTest(inputChunks, false, &tierConfig, {0, 1, 2, 3, 4});

    const TVector<TTestChunk> inputChunks2{
        TTestChunk{.Total = 100, .Alive = 90, .Added = 50},
        TTestChunk{.Total = 123, .Alive = 120},
        TTestChunk{.Total = 61, .Alive = 40},
        TTestChunk{.Total = 142, .Alive = 80},
        TTestChunk{.Total = 50, .Alive = 50}
    };
    DoTest(inputChunks, true, &tierConfig, {4});
}

TEST(SelectPudgeDeltaChunks, Empty) {
    TTierConfig tierConfig(10, 1, 1, 0);
     const TVector<TTestChunk> inputChunks{
        TTestChunk{.Total = 100, .Alive = 0, .Added = 0}
    };
    DoTest(inputChunks, false, &tierConfig, {});
}

TEST(SelectPudgeDeltaChunks, NoTierConfig) {
     const TVector<TTestChunk> inputChunks{
        TTestChunk{.Total = 100, .Alive = 70, .Added = 50},
        TTestChunk{.Total = 10, .Alive = 10}
    };
    DoTest(inputChunks, true, nullptr, {0});
}

TEST(SelectPudgeDeltaChunks, ZeroChunksToRebuild) {
    TTierConfig tierConfig(
        2,  /* chunks */
        0,  /* minChunksToRebuild */
        1,  /* maxAdditionalSpace */
        0); /* maxLargestToSmallestChunkRatio */

    const TVector<TTestChunk> inputChunks{
        TTestChunk{.Total = 100, .Alive = 90, .Added = 50},
        TTestChunk{.Total = 123, .Alive = 120}
    };
    DoTest(inputChunks, true, &tierConfig, {0});
}

TEST(SelectPudgeDeltaChunks, ForceFullRebuild) {
    TTierConfig tierConfig(
        2,  /* chunks */
        0,  /* minChunksToRebuild */
        1,  /* maxAdditionalSpace */
        0); /* maxLargestToSmallestChunkRatio */

    const TVector<TTestChunk> inputChunks{
        TTestChunk{.Total = 100, .Alive = 90, .Added = 50}
    };
    DoTest(inputChunks, true, &tierConfig, {0, 1});
}

TEST(SelectPudgeDeltaChunks, MaxAdditionalSpace) {
    TTierConfig tierConfig(
        5,  /* chunks */
        1,  /* minChunksToRebuild */
        0.1,  /* maxAdditionalSpace */
        0); /* maxLargestToSmallestChunkRatio */

    const TVector<TTestChunk> inputChunks{
        TTestChunk{.Total = 100, .Alive = 90, .Added = 50},
        TTestChunk{.Total = 123, .Alive = 120},
        TTestChunk{.Total = 61, .Alive = 40},
        TTestChunk{.Total = 142, .Alive = 80},
        TTestChunk{.Total = 50, .Alive = 50}
    };
    DoTest(inputChunks, true, &tierConfig, {2, 3, 4});

    const TVector<TTestChunk> inputChunks2{
        TTestChunk{.Total = 100, .Alive = 90, .Added = 50},
        TTestChunk{.Total = 123, .Alive = 120},
        TTestChunk{.Total = 61, .Alive = 40},
        TTestChunk{.Total = 192, .Alive = 130},
        TTestChunk{.Total = 50, .Alive = 50}
    };
    DoTest(inputChunks2, true, &tierConfig, {0, 1, 2, 3, 4});
}

TEST(SelectPudgeDeltaChunks, MaxLargestToSmallestChunkRatio) {
    TTierConfig tierConfig(
        5,  /* chunks */
        1,  /* minChunksToRebuild */
        1,  /* maxAdditionalSpace */
        2); /* maxLargestToSmallestChunkRatio */

    const TVector<TTestChunk> inputChunks{
        TTestChunk{.Total = 100, .Alive = 90, .Added = 50},
        TTestChunk{.Total = 123, .Alive = 120},
        TTestChunk{.Total = 61, .Alive = 40},
        TTestChunk{.Total = 142, .Alive = 80},
        TTestChunk{.Total = 50, .Alive = 50}
    };
    DoTest(inputChunks, true, &tierConfig, {2, 3, 4});
}

}
