#include <gtest/gtest-param-test.h>
#include <gtest/gtest.h>

#include <optional>
#include <tuple>

#include <models/advert_status.hpp>
#include <utils/direct_statuses_mapping.hpp>

namespace testing {
namespace utils = eats_restapp_marketing::utils;
using DirectStatus = eats_restapp_marketing::models::DirectCampaignStatuses;
using DirectState = eats_restapp_marketing::models::DirectCampaignStates;
using eats_restapp_marketing::models::AdvertStatus;
using eats_restapp_marketing::models::CampaignStatus;
struct GenerateCpmTest
    : TestWithParam<std::tuple<DirectStatus, DirectState,
                               std::optional<CampaignStatus>>> {};

INSTANTIATE_TEST_SUITE_P(
    results, GenerateCpmTest,
    Values(
        std::make_tuple(DirectStatus::kDraft, DirectState::kArchived,
                        CampaignStatus::kEnded),
        std::make_tuple(DirectStatus::kDraft, DirectState::kSuspended,
                        CampaignStatus::kSuspended),
        std::make_tuple(DirectStatus::kDraft, DirectState::kEnded,
                        CampaignStatus::kEnded),
        std::make_tuple(DirectStatus::kDraft, DirectState::kOn, std::nullopt),
        std::make_tuple(DirectStatus::kDraft, DirectState::kOff, std::nullopt),
        std::make_tuple(DirectStatus::kModeration, DirectState::kArchived,
                        CampaignStatus::kEnded),
        std::make_tuple(DirectStatus::kModeration, DirectState::kSuspended,
                        CampaignStatus::kSuspended),
        std::make_tuple(DirectStatus::kModeration, DirectState::kEnded,
                        CampaignStatus::kEnded),
        std::make_tuple(DirectStatus::kModeration, DirectState::kOn,
                        std::nullopt),
        std::make_tuple(DirectStatus::kModeration, DirectState::kOff,
                        std::nullopt),
        std::make_tuple(DirectStatus::kAccepted, DirectState::kArchived,
                        CampaignStatus::kEnded),
        std::make_tuple(DirectStatus::kAccepted, DirectState::kSuspended,
                        CampaignStatus::kSuspended),
        std::make_tuple(DirectStatus::kAccepted, DirectState::kEnded,
                        CampaignStatus::kEnded),
        std::make_tuple(DirectStatus::kAccepted, DirectState::kOn,
                        std::nullopt),
        std::make_tuple(DirectStatus::kAccepted, DirectState::kOff,
                        std::nullopt),
        std::make_tuple(DirectStatus::kRejected, DirectState::kArchived,
                        CampaignStatus::kRejected),
        std::make_tuple(DirectStatus::kRejected, DirectState::kSuspended,
                        CampaignStatus::kRejected),
        std::make_tuple(DirectStatus::kRejected, DirectState::kEnded,
                        CampaignStatus::kRejected),
        std::make_tuple(DirectStatus::kRejected, DirectState::kOn,
                        CampaignStatus::kRejected),
        std::make_tuple(DirectStatus::kRejected, DirectState::kOff,
                        CampaignStatus::kRejected)));

TEST_P(GenerateCpmTest, succesfulMappingStatus) {
  const auto [status, state, expected] = GetParam();
  ASSERT_EQ(utils::DirectStatusMappingCpm(status, state), expected);
}

struct GenerateCpcTest
    : TestWithParam<
          std::tuple<DirectStatus, DirectState, std::optional<AdvertStatus>>> {
};

INSTANTIATE_TEST_SUITE_P(
    results, GenerateCpcTest,
    Values(
        std::make_tuple(DirectStatus::kDraft, DirectState::kArchived,
                        AdvertStatus::kPaused),
        std::make_tuple(DirectStatus::kDraft, DirectState::kSuspended,
                        AdvertStatus::kPaused),
        std::make_tuple(DirectStatus::kDraft, DirectState::kEnded,
                        AdvertStatus::kPaused),
        std::make_tuple(DirectStatus::kDraft, DirectState::kOn, std::nullopt),
        std::make_tuple(DirectStatus::kDraft, DirectState::kOff, std::nullopt),
        std::make_tuple(DirectStatus::kModeration, DirectState::kArchived,
                        AdvertStatus::kPaused),
        std::make_tuple(DirectStatus::kModeration, DirectState::kSuspended,
                        AdvertStatus::kPaused),
        std::make_tuple(DirectStatus::kModeration, DirectState::kEnded,
                        AdvertStatus::kPaused),
        std::make_tuple(DirectStatus::kModeration, DirectState::kOn,
                        std::nullopt),
        std::make_tuple(DirectStatus::kModeration, DirectState::kOff,
                        std::nullopt),
        std::make_tuple(DirectStatus::kAccepted, DirectState::kArchived,
                        AdvertStatus::kPaused),
        std::make_tuple(DirectStatus::kAccepted, DirectState::kSuspended,
                        AdvertStatus::kPaused),
        std::make_tuple(DirectStatus::kAccepted, DirectState::kEnded,
                        AdvertStatus::kPaused),
        std::make_tuple(DirectStatus::kAccepted, DirectState::kOn,
                        std::nullopt),
        std::make_tuple(DirectStatus::kAccepted, DirectState::kOff,
                        std::nullopt),
        std::make_tuple(DirectStatus::kRejected, DirectState::kArchived,
                        AdvertStatus::kPaused),
        std::make_tuple(DirectStatus::kRejected, DirectState::kSuspended,
                        AdvertStatus::kPaused),
        std::make_tuple(DirectStatus::kRejected, DirectState::kEnded,
                        AdvertStatus::kPaused),
        std::make_tuple(DirectStatus::kRejected, DirectState::kOn,
                        std::nullopt),
        std::make_tuple(DirectStatus::kRejected, DirectState::kOff,
                        std::nullopt)));

TEST_P(GenerateCpcTest, succesfulMappingStatus) {
  const auto [status, state, expected] = GetParam();
  ASSERT_EQ(utils::DirectStatusMappingCpc(status, state), expected);
}
}  // namespace testing
