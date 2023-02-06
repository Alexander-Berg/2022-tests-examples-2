#include <helpers/validator_constraints.hpp>

#include <gtest/gtest.h>

namespace helpers::validator_constraints {

std::vector<std::string> SortedLoosing(
    const models::ValidatorConstraints& old,
    const models::ValidatorConstraints& current) {
  auto loosing = FindLoosing(old, current);
  std::sort(loosing.begin(), loosing.end());
  return loosing;
}

}  // namespace helpers::validator_constraints

TEST(ValidatorConstraints, EmptyAnswer) {
  using helpers::validator_constraints::SortedLoosing;
  using models::Constraint;
  using models::ValidatorConstraints;
  ValidatorConstraints old;
  ValidatorConstraints current;

  ASSERT_EQ(SortedLoosing(old, current).size(), 0);

  current.push_back(Constraint{"any", 1., 4.});
  ASSERT_EQ(SortedLoosing(old, current).size(), 0);

  old.push_back(Constraint{"any", 0., 7.});
  ASSERT_EQ(SortedLoosing(old, current).size(), 0);

  current.push_back(Constraint{"another", 0., std::nullopt});
  ASSERT_EQ(SortedLoosing(old, current).size(), 0);

  old.push_back(Constraint{"another", std::nullopt, std::nullopt});
  ASSERT_EQ(SortedLoosing(old, current).size(), 0);
}

TEST(ValidatorConstraints, CommonCase) {
  using helpers::validator_constraints::SortedLoosing;
  using models::Constraint;
  using models::ValidatorConstraints;
  ValidatorConstraints old;
  ValidatorConstraints current;
  const double kEpsilon = 1e-8;

  old.push_back(Constraint{"empty", std::nullopt, std::nullopt});
  old.push_back(Constraint{"not_changed_1", 0., 1.});
  old.push_back(Constraint{"not_changed_2", 0., std::nullopt});
  old.push_back(Constraint{"not_changed_3", std::nullopt, 1.});
  old.push_back(Constraint{"not_changed_4", 0., 1.});
  old.push_back(Constraint{"not_changed_5", 0., 1.});
  old.push_back(Constraint{"lost", 0., 1.});

  old.push_back(Constraint{"tight_changed_1", 0., 10.});
  old.push_back(Constraint{"tight_changed_2", 0., std::nullopt});
  old.push_back(Constraint{"tight_changed_3", 0., std::nullopt});
  old.push_back(Constraint{"tight_changed_4", std::nullopt, 10.});
  old.push_back(Constraint{"tight_changed_5", std::nullopt, 10.});

  old.push_back(Constraint{"loose_changed_1", 0., 10.});
  old.push_back(Constraint{"loose_changed_2", 0., 10.});
  old.push_back(Constraint{"loose_changed_3", 0., 10.});
  old.push_back(Constraint{"loose_changed_4", 0., std::nullopt});
  old.push_back(Constraint{"loose_changed_5", std::nullopt, 10.});
  old.push_back(Constraint{"loose_changed_6", 0., 10.0});
  old.push_back(Constraint{"loose_changed_7", 0., 10.0});

  current.push_back(Constraint{"not_changed_1", 0., 1.});
  current.push_back(Constraint{"not_changed_2", 0., std::nullopt});
  current.push_back(Constraint{"not_changed_3", std::nullopt, 1.});
  current.push_back(Constraint{"not_changed_4", 0. - kEpsilon / 2.0, 1.});
  current.push_back(Constraint{"not_changed_5", 0., 1. + kEpsilon / 2.0});

  current.push_back(Constraint{"tight_changed_1", 0., 10.});
  current.push_back(Constraint{"tight_changed_2", 1., std::nullopt});
  current.push_back(Constraint{"tight_changed_3", 0., 1000000.});
  current.push_back(Constraint{"tight_changed_4", std::nullopt, 9.});
  current.push_back(Constraint{"tight_changed_5", 7., 10.});

  current.push_back(Constraint{"loose_changed_1", -1., 10.});
  current.push_back(Constraint{"loose_changed_2", std::nullopt, 9.});
  current.push_back(Constraint{"loose_changed_3", 3., std::nullopt});
  current.push_back(Constraint{"loose_changed_4", -1., std::nullopt});
  current.push_back(Constraint{"loose_changed_5", std::nullopt, 12.});
  current.push_back(Constraint{"loose_changed_6", 0. - kEpsilon * 2, 10.0});
  current.push_back(Constraint{"loose_changed_7", 0., 10.0 + kEpsilon * 2});

  auto result = SortedLoosing(old, current);
  ASSERT_EQ(result.size(), 8);
  ASSERT_EQ(result[0], "loose_changed_1");
  ASSERT_EQ(result[1], "loose_changed_2");
  ASSERT_EQ(result[2], "loose_changed_3");
  ASSERT_EQ(result[3], "loose_changed_4");
  ASSERT_EQ(result[4], "loose_changed_5");
  ASSERT_EQ(result[5], "loose_changed_6");
  ASSERT_EQ(result[6], "loose_changed_7");
  ASSERT_EQ(result[7], "lost");
}
