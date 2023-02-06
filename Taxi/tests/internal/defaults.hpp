#pragma once

#include "models_test.hpp"

namespace sweet_home {

const subscription::PlusSubscription kAvailableSubscription =
    tests::MakePlusSubscription("sub_id",
                                subscription::PurchaseStatus::kAvailable, true);

const subscription::PlusSubscription kActiveSubscription =
    tests::MakePlusSubscription("sub_id", subscription::PurchaseStatus::kActive,
                                true);

}  // namespace sweet_home
