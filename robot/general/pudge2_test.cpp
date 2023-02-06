#include "pudge2.h"

#include "tier_config.h"

#include <robot/jupiter/library/pudge/minipudge/protos/pudge_chunk_stats.pb.h>

#include <library/cpp/testing/gtest/gtest.h>

#include <util/generic/hash_set.h>

#include <random>


using NJupiter::TPudgeChunkStats;
using NJupiter::TTierConfig;

namespace NPlutonium::NChunkler {

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

struct TSolutionStats {
    ui64 AddedDocs = 0;
    ui64 AliveDocs = 0;
    ui64 Holes = 0;
    ui64 TouchedDocs = 0;

    double JunkRate() const {
        return double(Holes) / (AliveDocs + AddedDocs + Holes);
    }
};

TSolutionStats CalcSolutionStats(const TVector<TPudgeChunkStats>& chunks, const TVector<ui32>& replacedChunks) {
    THashSet<ui32> chunkSet{replacedChunks.begin(), replacedChunks.end()};
    TSolutionStats stats;
    for (ui32 i = 0; i < chunks.size(); ++i) {
        const TPudgeChunkStats& chunk = chunks[i];
        stats.AliveDocs += chunk.GetNumAliveDocs();
        stats.AddedDocs += chunk.GetNumAddedDocs();
        if (!chunkSet.contains(i)) {
            stats.Holes += chunk.GetMaxLocalIdPlusOne() - chunk.GetNumAliveDocs();
        } else {
            stats.TouchedDocs += chunk.GetNumAliveDocs();
        }
    }
    return stats;
}

bool CheckSolutionStats(
    const TVector<TPudgeChunkStats>& chunks,
    const TVector<ui32>& replacedChunks,
    double expectedJunkRate,
    double error
) {
    TSolutionStats stats = CalcSolutionStats(chunks, replacedChunks);
    EXPECT_LE(stats.JunkRate(), expectedJunkRate + error);
    return stats.JunkRate() <= expectedJunkRate + error;
}

TVector<TPudgeChunkStats> ToPudgeStats(const TVector<TTestChunk>& chunks) {
    TVector<TPudgeChunkStats> statsByChunk(Reserve(chunks.size()));
    for (auto& chunk : chunks) {
        statsByChunk.push_back(chunk.Stats());
    }
    return statsByChunk;
}

void DoTestExact(const TTierConfig& tierConfig, const TVector<ui32>& expectedChunks, const TVector<TTestChunk>& chunks) {
    const TVector<TPudgeChunkStats> statsByChunk = ToPudgeStats(chunks);
    const TVector<ui32> chunksToReplace = SelectDeltaChunks2(statsByChunk, tierConfig, "test_shard");
    ASSERT_EQ(chunksToReplace, expectedChunks);
}

bool DoTest(const TTierConfig& tierConfig, const TVector<TTestChunk>& chunks) {
    const TVector<TPudgeChunkStats> statsByChunk = ToPudgeStats(chunks);
    const TVector<ui32> chunksToReplace = SelectDeltaChunks2(statsByChunk, tierConfig, "test_shard");
    return CheckSolutionStats(statsByChunk, chunksToReplace, tierConfig.GetMaxAdditionalSpace(), 0.01);
}

TEST(SelectDeltaChunks2, Simple) {
    DoTestExact(TTierConfig(5, 1, 0.1, 0, true, 0.01), {3}, {
        TTestChunk{.Total = 100, .Alive = 90, .Added = 50},
        TTestChunk{.Total = 123, .Alive = 120},
        TTestChunk{.Total = 61, .Alive = 40},
        TTestChunk{.Total = 142, .Alive = 80},
        TTestChunk{.Total = 50, .Alive = 50}
    });
    DoTestExact(TTierConfig(5, 1, 0.19, 0, true, 0.01), {4}, {
        TTestChunk{.Total = 100, .Alive = 90, .Added = 50},
        TTestChunk{.Total = 123, .Alive = 120},
        TTestChunk{.Total = 61, .Alive = 40},
        TTestChunk{.Total = 142, .Alive = 80},
        TTestChunk{.Total = 95, .Alive = 50}
    });
}

struct TChunkGenerator {
    TChunkGenerator(ui32 seed = 0)
        : Gen_(seed)
        , SizeDistrib_(1000, 10000)
        , AddedDistrib_(10, 20000)
    {
    }

    TTestChunk GenChunk(bool first, ui32 holeyness) {
        std::uniform_int_distribution<ui32> holesDistrib(0, std::min<ui32>(holeyness, 99));
        TTestChunk chunk;
        chunk.Total = SizeDistrib_(Gen_);
        chunk.Alive = chunk.Total * double(holesDistrib(Gen_)) / 100;
        chunk.Added = first ? AddedDistrib_(Gen_) : 0;
        return chunk;
    }

private:
    std::mt19937 Gen_;
    std::uniform_int_distribution<ui32> SizeDistrib_;
    std::uniform_int_distribution<ui32> AddedDistrib_;
};

TEST(SelectDeltaChunks2, NotExact) {
    TChunkGenerator gen;

    for (ui32 nChunks : {10, 20, 40, 100, 2000}) {
        for (ui32 allowedJunk : {1, 5, 10, 20, 40}) {
            for (ui32 maxHoleyness : {1, 5, 15, 40}) {
                TVector<TTestChunk> chunks(Reserve(nChunks));
                for (size_t i = 0; i < nChunks; ++i) {
                    chunks.push_back(gen.GenChunk(i == 0, maxHoleyness));
                }
                bool res = DoTest(TTierConfig(nChunks, 1, 0.01 * allowedJunk, 0, true, 0.01), chunks);
                Y_ENSURE(res, "failed: nChunks=" << nChunks << ", allowedJunk=" << allowedJunk << ", maxHoleyness=" << maxHoleyness);
            }
        }
    }
}

TEST(SelectDeltaChunks2, EmptyChunks) {
    const TVector<TTestChunk> testChunks{
        TTestChunk{.Total = 100, .Alive = 90, .Added = 70},
        TTestChunk{.Total = 0, .Alive = 0},
        TTestChunk{.Total = 60, .Alive = 40},
        TTestChunk{.Total = 140, .Alive = 80},
        TTestChunk{.Total = 0, .Alive = 0}
    };
    const TVector<TPudgeChunkStats> statsByChunk = ToPudgeStats(testChunks);

    {
        const TVector<ui32> chunksToReplace = SelectDeltaChunks2(statsByChunk, TTierConfig(5, 1, 0.1, 0, true, 0.01), "test_shard");
        const TVector<ui32> expectedChunks{1, 3};
        ASSERT_EQ(chunksToReplace, expectedChunks);
    }
    {
        const TVector<ui32> chunksToReplace = SelectDeltaChunks2(statsByChunk, TTierConfig(5, 3, 0.1, 0, true, 0.01), "test_shard");
        const TVector<ui32> expectedChunks{1, 3, 4};
        ASSERT_EQ(chunksToReplace, expectedChunks);
    }
}

}
