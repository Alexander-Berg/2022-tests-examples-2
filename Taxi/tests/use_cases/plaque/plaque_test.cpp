#include <gtest/gtest.h>

#include "use_cases/plaque/plaque.hpp"

#include "tests/core/models_test.hpp"
#include "tests/internal/defaults.hpp"
#include "tests/internal/plaque/models_test.hpp"
#include "tests/mocks/plaque_repository_mock.hpp"

namespace sweet_home::plaque {

namespace {
const std::string kYandexUid = "some_id";
}

namespace {

struct DepsMocks {
  std::shared_ptr<mocks::PlaqueRepositoryMock> plaque_repo;

  Deps Compile() const { return {plaque_repo}; }
};

DepsMocks PrepareDeps() {
  auto plaque_repo = std::make_shared<mocks::PlaqueRepositoryMock>();
  return {plaque_repo};
}

Context PrepareContext(bool add_wallet = true, bool wallet_visible = true,
                       bool plaque_exp_enabled = true) {
  std::optional<core::Wallet> wallet{};
  if (add_wallet) wallet = tests::MakeWallet(kYandexUid, "140");

  auto exp_value = (plaque_exp_enabled) ? kExpEnabled : kExpDisabled;
  auto experiments = tests::MakeExperiments(
      {{"sweet-home:feature:plaque", std::move(exp_value)}});

  return {std::move(experiments), kActiveSubscription,
          core::HideableWallet{wallet, wallet_visible}, tests::MakeSDKClient()};
}

}  // namespace

TEST(TestPlaque, ExpDisabled) {
  auto widgets = plaque::PrepareWidgets();
  auto plaques = plaque::PreparePlaques(widgets);

  auto deps = PrepareDeps();
  deps.plaque_repo->SetupGetPlaques(
      [&plaques](const std::string&) -> std::vector<Plaque> {
        return {plaques["plaque:global:buy_plus"],
                plaques["plaque:taxi:composite_payment"]};
      });

  const bool plaque_exp_enabled = false;
  auto context = PrepareContext(true, plaque_exp_enabled);

  const auto result = GetPlaquesForUser(context, deps.Compile(), kYandexUid);
  ASSERT_EQ(result.size(), 0);
}

TEST(TestPlaque, HappyPath) {
  auto widgets = plaque::PrepareWidgets();
  auto plaques = plaque::PreparePlaques(widgets);

  auto deps = PrepareDeps();
  deps.plaque_repo->SetupGetPlaques(
      [&plaques](const std::string&) -> std::vector<Plaque> {
        return {plaques["plaque:global:buy_plus"],
                plaques["plaque:taxi:composite_payment"]};
      });

  {
    SCOPED_TRACE("Plaque: composite_payment");
    auto context = PrepareContext(true);

    const auto result = GetPlaquesForUser(context, deps.Compile(), kYandexUid);

    ASSERT_EQ(result.size(), 1);
    const auto& plaque = result[0];
    AssertPlaque(plaque, plaques["plaque:taxi:composite_payment"]);
  }

  {
    SCOPED_TRACE("Plaque: buy_plus");
    auto context = PrepareContext(true);
    context.user_subscription = kAvailableSubscription;

    const auto result = GetPlaquesForUser(context, deps.Compile(), kYandexUid);

    ASSERT_EQ(result.size(), 1);
    const auto& plaque = result[0];
    AssertPlaque(plaque, plaques["plaque:global:buy_plus"]);
  }
}

TEST(TestPlaque, WalletHidden) {
  auto widgets = plaque::PrepareWidgets();
  auto plaques = plaque::PreparePlaques(widgets);

  auto deps = PrepareDeps();
  deps.plaque_repo->SetupGetPlaques(
      [&plaques](const std::string&) -> std::vector<Plaque> {
        return {plaques["plaque:global:buy_plus"],
                plaques["plaque:taxi:composite_payment"]};
      });

  const bool wallet_visible = false;

  {
    SCOPED_TRACE("Plaque: composite_payment");
    auto context = PrepareContext(true, wallet_visible);

    const auto result = GetPlaquesForUser(context, deps.Compile(), kYandexUid);

    ASSERT_EQ(result.size(), 0);
  }

  {
    SCOPED_TRACE("Plaque: buy_plus");
    auto context = PrepareContext(true, wallet_visible);
    context.user_subscription = kAvailableSubscription;

    const auto result = GetPlaquesForUser(context, deps.Compile(), kYandexUid);

    ASSERT_EQ(result.size(), 1);
    const auto& plaque = result[0];
    AssertPlaque(plaque, plaques["plaque:global:buy_plus"]);
  }
}

}  // namespace sweet_home::plaque
