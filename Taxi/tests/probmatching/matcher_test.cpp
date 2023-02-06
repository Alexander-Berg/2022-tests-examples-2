#include <taxi/graph/libs/probmatching/best_heads.h>

#include <library/cpp/testing/unittest/registar.h>
#include <library/cpp/testing/unittest/gtest.h>
#include <library/cpp/testing/unittest/env.h>

#include <random>
#include <iostream>
#include <climits>

namespace mapmatching = maps::analyzer::mapmatching;

namespace {
    std::default_random_engine randomEngine;
    std::uniform_real_distribution<double> randomLikelihood(-5.0, 0.0);
    std::uniform_int_distribution<std::size_t> randomCandidatesCount(1, 5);
    constexpr double SKIP_LOG_LIKELIHOOD = -3.0;
}

struct CandidateState {
    std::size_t id = 0;
    std::size_t time = 0;
};

inline bool operator==(const CandidateState& lhs, const CandidateState& rhs) {
    return lhs.id == rhs.id;
}

inline bool operator!=(const CandidateState& lhs, const CandidateState& rhs) {
    return !(lhs == rhs);
}

std::ostream& operator<<(std::ostream& out, const CandidateState& st) {
    return out << st.id << "[" << st.time << "]";
}

struct Offset {
    Offset& operator+=(const Offset& other) {
        offset += other.offset;
        return *this;
    }
    std::size_t offset = 0;
};

struct Signal {
    std::size_t time = 0;
};

struct NullType {};

using Matcher = mapmatching::Matcher<CandidateState, Signal, Offset>;

Y_UNIT_TEST_SUITE(TestProbMatcher) {
    Y_UNIT_TEST(TestBestHeads) {
        using mapmatching::Weighted;

        Cerr << "=== random candidates ===" << Endl;

        constexpr ui64 LAYERS_COUNT = 40;
        constexpr ui64 BEST_HEAD_LAYERS_COUNT = 7;
        constexpr ui64 BEST_HEADS_COUNT = 10;

        const auto onMatch = [&](const Signal&, const Signal&, const CandidateState&, const CandidateState&, ui64, ui64) {
        };

        std::size_t currentId = 0;
        Matcher matcher{
            2,
            {}, // no candidates limits
            // generate candidates
            [&](const Signal& s, const Offset&) {
                const std::size_t candidatesCount = randomCandidatesCount(randomEngine);
                std::vector<CandidateState> candidates;
                for (std::size_t i = 0; i < candidatesCount; ++i) {
                    candidates.push_back({currentId++, s.time});
                }
                return candidates;
            },
            // weigh candidate
            [&](const Signal&, const Offset&, const CandidateState&) {
                return randomLikelihood(randomEngine);
            },
            // weigh transition
            [&](const Signal&, const Signal&, const Offset& o, const CandidateState&, const CandidateState& to) {
                const auto skippedLikelihood = SKIP_LOG_LIKELIHOOD * static_cast<double>(o.offset - 1);
                const auto logLikelihood = randomLikelihood(randomEngine) + skippedLikelihood;
                return Weighted{logLikelihood, to};
            },
            // weigh head
            [&](const Signal&, const Offset& o, const CandidateState&) {
                return SKIP_LOG_LIKELIHOOD * static_cast<double>(o.offset);
            },
            onMatch};

        for (ui64 i = 0; i < LAYERS_COUNT; ++i) {
            Cerr << "--- --- ---" << Endl;
            Cerr << "adding layer " << i << " ..." << Endl;
            matcher.add({i}, {1});
        }

        // create a reference result for BestHeadsFromLayers
        std::vector<Matcher::WeightedHead> referenceBestHeads;

        UNIT_ASSERT(BEST_HEAD_LAYERS_COUNT < LAYERS_COUNT);

        for (auto lit = matcher.cgraph.layers.begin(); lit != matcher.cgraph.layers.begin() + BEST_HEAD_LAYERS_COUNT; ++lit) {
            const auto& l = *lit;
            for (const auto& c : l.candidates) {
                auto headWeight = matcher.weighHead(l.signal, l.measurement, c.head.value().state);
                referenceBestHeads.push_back(Weighted{
                    c.logLikelihood + headWeight,
                    c.head});
            }
        }
        std::sort(referenceBestHeads.begin(), referenceBestHeads.end(), std::greater<Matcher::WeightedHead>{});
        if (referenceBestHeads.size() > BEST_HEADS_COUNT) {
            referenceBestHeads.resize(BEST_HEADS_COUNT);
        }

        auto result = NTaxi::NMapMatching::BestHeadsFromLayers(matcher, BEST_HEADS_COUNT, BEST_HEAD_LAYERS_COUNT);
        std::sort(result.begin(), result.end(), std::greater<Matcher::WeightedHead>{});

        UNIT_ASSERT(referenceBestHeads.size() <= result.size());

        for (size_t i = 0; i < result.size(); ++i) {
            ASSERT_EQ(result[i].logLikelihood, referenceBestHeads[i].logLikelihood);
        }

        const auto& pool = matcher.root->nodePool();
        Cerr << "Node pool: creations=" << pool.creations() << ", allocations=" << pool.allocations() << Endl;
    }
    Y_UNIT_TEST(TestBestHeadsEmpty) {
        using mapmatching::Weighted;

        Cerr << "=== random candidates ===" << Endl;

        const auto onMatch = [&](const Signal&, const Signal&, const CandidateState&, const CandidateState&, ui64, ui64) {
        };

        std::size_t currentId = 0;
        Matcher matcher{
            2,
            {}, // no candidates limits
            // generate candidates
            [&](const Signal& s, const Offset&) {
                const std::size_t candidatesCount = randomCandidatesCount(randomEngine);
                std::vector<CandidateState> candidates;
                for (std::size_t i = 0; i < candidatesCount; ++i) {
                    candidates.push_back({currentId++, s.time});
                }
                return candidates;
            },
            // weigh candidate
            [&](const Signal&, const Offset&, const CandidateState&) {
                return randomLikelihood(randomEngine);
            },
            // weigh transition
            [&](const Signal&, const Signal&, const Offset& o, const CandidateState&, const CandidateState& to) {
                const auto skippedLikelihood = SKIP_LOG_LIKELIHOOD * static_cast<double>(o.offset - 1);
                const auto logLikelihood = randomLikelihood(randomEngine) + skippedLikelihood;
                return Weighted{logLikelihood, to};
            },
            // weigh head
            [&](const Signal&, const Offset& o, const CandidateState&) {
                return SKIP_LOG_LIKELIHOOD * static_cast<double>(o.offset);
            },
            onMatch};

        auto result = NTaxi::NMapMatching::BestHeadsFromLayers(matcher, 10, 10);
        ASSERT_EQ(0, result.size());
    }
}
