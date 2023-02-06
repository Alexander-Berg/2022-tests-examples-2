#include <gtest/gtest.h>

#include <chrono>
#include <userver/utils/datetime.hpp>

#include "entity.hpp"

namespace eats_rest_menu_storage::utils {

namespace {

struct TestEntity {
  std::optional<std::chrono::system_clock::time_point> updated_at;
  std::optional<std::chrono::system_clock::time_point> deleted_at;
};

const auto kTimePoint =
    ::utils::datetime::Stringtime("2022-06-05T12:00:00.000+0000");

}  // namespace

TEST(CompareEntityByUpdatedAt, BothActive) {
  // Проверяем, что если deleted_at не задан
  // то идет сравнение по updated_at
  TestEntity lhs{
      kTimePoint,    // updated_at
      std::nullopt,  // deleted_at
  };
  TestEntity rhs{
      kTimePoint + std::chrono::minutes{30},  // updated_at
      std::nullopt,                           // deleted_at
  };

  ASSERT_TRUE(CompareEntityByUpdatedAt(lhs, rhs));
  ASSERT_FALSE(CompareEntityByUpdatedAt(rhs, lhs));
}

TEST(CompareEntityByUpdatedAt, ActiveVsDeleted) {
  // Проверяем, если пришли две сущности
  // и у удаленной время обновления больше,
  // чем у второй
  // Но при это врям удаления меньше, возьмется
  // активная сущность
  TestEntity lhs{
      kTimePoint,
      std::nullopt,
  };
  TestEntity rhs{
      kTimePoint + std::chrono::minutes{30},  // updated_at
      kTimePoint - std::chrono::minutes{30},  // deleted_at
  };

  ASSERT_FALSE(CompareEntityByUpdatedAt(lhs, rhs));
  ASSERT_TRUE(CompareEntityByUpdatedAt(rhs, lhs));
}

TEST(CompareEntityByUpdatedAt, ActiveVsDeletedEqual) {
  // Проверяем, если пришли две сущности
  // с одниковыми временам, но одна из них
  // не удалена, то выбирается не удаленная
  TestEntity lhs{
      kTimePoint,
      std::nullopt,
  };
  TestEntity rhs{
      kTimePoint,  // updated_at
      kTimePoint,  // deleted_at
  };

  ASSERT_FALSE(CompareEntityByUpdatedAt(lhs, rhs));
  ASSERT_TRUE(CompareEntityByUpdatedAt(rhs, lhs));
}

TEST(CompareEntityByUpdatedAt, BothDeleted) {
  // Проверяем, что если обе удалены,
  // то выбереться та что с большим updated_at
  TestEntity lhs{
      kTimePoint + std::chrono::minutes{1},   // updated_at
      kTimePoint + std::chrono::minutes{10},  // deleted_at
  };
  TestEntity rhs{
      kTimePoint + std::chrono::minutes{2},  // updated_at
      kTimePoint + std::chrono::minutes{5},  // deleted_at
  };

  ASSERT_TRUE(CompareEntityByUpdatedAt(lhs, rhs));
  ASSERT_FALSE(CompareEntityByUpdatedAt(rhs, lhs));
}

}  // namespace eats_rest_menu_storage::utils
