#include <gtest/gtest.h>

#include <pricing-functions/helpers/typed_storage.hpp>

namespace {

struct Statistics {
  size_t constructed = 0;
  size_t move_constructed = 0;
  size_t copy_constructed = 0;
  size_t destructed = 0;
  size_t move_assigned = 0;
  size_t copy_assigned = 0;
};

template <typename T>
Statistics& GetStatistics() {
  static Statistics value;
  return value;
}

struct Base {
  Base() { ++GetStatistics<Base>().constructed; }

  Base(const Base&) { ++GetStatistics<Base>().copy_constructed; }

  Base(Base&&) noexcept { ++GetStatistics<Base>().move_constructed; }

  Base& operator=(const Base&) {
    ++GetStatistics<Base>().copy_assigned;
    return *this;
  }

  Base& operator=(Base&&) noexcept {
    ++GetStatistics<Base>().move_assigned;
    return *this;
  }

  virtual ~Base() { ++GetStatistics<Base>().destructed; }
};

struct Derived : Base {
  Derived() { ++GetStatistics<Derived>().constructed; }

  Derived(const Derived&) { ++GetStatistics<Derived>().copy_constructed; }

  Derived(Derived&&) noexcept { ++GetStatistics<Derived>().move_constructed; }

  Derived& operator=(const Derived&) {
    ++GetStatistics<Derived>().copy_assigned;
    return *this;
  }

  Derived& operator=(Derived&&) noexcept {
    ++GetStatistics<Derived>().move_assigned;
    return *this;
  }

  virtual ~Derived() { ++GetStatistics<Derived>().destructed; }
};

}  // namespace

TEST(TypedStorage, ConstructEmptyStatic) {
  GetStatistics<Base>() = Statistics();
  GetStatistics<Derived>() = Statistics();
  {
    helpers::TypedStorage<helpers::storage_traits::Static<Base>> storage;
    EXPECT_FALSE(!!storage);
  }
  EXPECT_EQ(GetStatistics<Base>().constructed, 0);
  EXPECT_EQ(GetStatistics<Base>().destructed, 0);
}

TEST(TypedStorage, ConstructEmptyDynamic) {
  GetStatistics<Base>() = Statistics();
  GetStatistics<Derived>() = Statistics();
  {
    helpers::TypedStorage<helpers::storage_traits::Dynamic<Base>> storage;
    EXPECT_FALSE(!!storage);
  }
  EXPECT_EQ(GetStatistics<Base>().constructed, 0);
  EXPECT_EQ(GetStatistics<Base>().destructed, 0);
}

TEST(TypedStorage, ConstructDerivedStatic) {
  GetStatistics<Base>() = Statistics();
  GetStatistics<Derived>() = Statistics();
  {
    helpers::TypedStorage<helpers::storage_traits::Static<Base>> storage(
        Derived{});
    EXPECT_TRUE(!!storage);
  }
  EXPECT_EQ(GetStatistics<Base>().constructed, 2);
  EXPECT_EQ(GetStatistics<Base>().move_constructed, 0);
  EXPECT_EQ(GetStatistics<Base>().destructed, 2);
  EXPECT_EQ(GetStatistics<Derived>().move_constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().destructed, 2);
}

TEST(TypedStorage, ConstructDerivedDynamic) {
  GetStatistics<Base>() = Statistics();
  GetStatistics<Derived>() = Statistics();
  {
    helpers::TypedStorage<helpers::storage_traits::Dynamic<Base>> storage(
        Derived{});
    EXPECT_TRUE(!!storage);
  }
  EXPECT_EQ(GetStatistics<Base>().constructed, 2);
  EXPECT_EQ(GetStatistics<Base>().move_constructed, 0);
  EXPECT_EQ(GetStatistics<Base>().destructed, 2);
  EXPECT_EQ(GetStatistics<Derived>().constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().move_constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().destructed, 2);
}

TEST(TypedStorage, CopyConstructDerivedStatic) {
  GetStatistics<Base>() = Statistics();
  GetStatistics<Derived>() = Statistics();
  {
    helpers::TypedStorage<helpers::storage_traits::Static<Base>> storage(
        Derived{});
    helpers::TypedStorage<helpers::storage_traits::Static<Base>> storage2 =
        storage;
    EXPECT_TRUE(!!storage);
    EXPECT_TRUE(!!storage2);
  }
  EXPECT_EQ(GetStatistics<Base>().constructed, 3);
  EXPECT_EQ(GetStatistics<Base>().move_constructed, 0);
  EXPECT_EQ(GetStatistics<Base>().destructed, 3);
  EXPECT_EQ(GetStatistics<Derived>().constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().move_constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().copy_constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().destructed, 3);
}

TEST(TypedStorage, CopyConstructDerivedDynamic) {
  GetStatistics<Base>() = Statistics();
  GetStatistics<Derived>() = Statistics();
  {
    helpers::TypedStorage<helpers::storage_traits::Dynamic<Base>> storage(
        Derived{});
    helpers::TypedStorage<helpers::storage_traits::Dynamic<Base>> storage2 =
        storage;
    EXPECT_TRUE(!!storage);
    EXPECT_TRUE(!!storage2);
  }
  EXPECT_EQ(GetStatistics<Base>().constructed, 3);
  EXPECT_EQ(GetStatistics<Base>().move_constructed, 0);
  EXPECT_EQ(GetStatistics<Base>().destructed, 3);
  EXPECT_EQ(GetStatistics<Derived>().constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().move_constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().copy_constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().destructed, 3);
}

TEST(TypedStorage, MoveConstructDerivedStatic) {
  GetStatistics<Base>() = Statistics();
  GetStatistics<Derived>() = Statistics();
  {
    helpers::TypedStorage<helpers::storage_traits::Static<Base>> storage(
        Derived{});
    helpers::TypedStorage<helpers::storage_traits::Static<Base>> storage2 =
        std::move(storage);
    EXPECT_TRUE(!!storage);
    EXPECT_TRUE(!!storage2);
  }
  EXPECT_EQ(GetStatistics<Base>().constructed, 3);
  EXPECT_EQ(GetStatistics<Base>().move_constructed, 0);
  EXPECT_EQ(GetStatistics<Base>().destructed, 3);
  EXPECT_EQ(GetStatistics<Derived>().constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().move_constructed, 2);
  EXPECT_EQ(GetStatistics<Derived>().copy_constructed, 0);
  EXPECT_EQ(GetStatistics<Derived>().destructed, 3);
}

TEST(TypedStorage, MoveConstructDerivedDynamic) {
  GetStatistics<Base>() = Statistics();
  GetStatistics<Derived>() = Statistics();
  {
    helpers::TypedStorage<helpers::storage_traits::Dynamic<Base>> storage(
        Derived{});
    helpers::TypedStorage<helpers::storage_traits::Dynamic<Base>> storage2 =
        std::move(storage);
    EXPECT_FALSE(!!storage);
    EXPECT_TRUE(!!storage2);
  }
  EXPECT_EQ(GetStatistics<Base>().constructed, 2);
  EXPECT_EQ(GetStatistics<Base>().move_constructed, 0);
  EXPECT_EQ(GetStatistics<Base>().destructed, 2);
  EXPECT_EQ(GetStatistics<Derived>().constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().move_constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().copy_constructed, 0);
  EXPECT_EQ(GetStatistics<Derived>().destructed, 2);
}

TEST(TypedStorage, CopyAssignDerivedStatic) {
  GetStatistics<Base>() = Statistics();
  GetStatistics<Derived>() = Statistics();
  {
    helpers::TypedStorage<helpers::storage_traits::Static<Base>> storage(
        Derived{});
    helpers::TypedStorage<helpers::storage_traits::Static<Base>> storage2;
    storage2 = storage;
    EXPECT_TRUE(!!storage);
    EXPECT_TRUE(!!storage2);
  }
  EXPECT_EQ(GetStatistics<Base>().constructed, 3);
  EXPECT_EQ(GetStatistics<Base>().move_constructed, 0);
  EXPECT_EQ(GetStatistics<Base>().destructed, 3);
  EXPECT_EQ(GetStatistics<Derived>().constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().move_constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().copy_constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().destructed, 3);
}

TEST(TypedStorage, CopyAssignDerivedDynamic) {
  GetStatistics<Base>() = Statistics();
  GetStatistics<Derived>() = Statistics();
  {
    helpers::TypedStorage<helpers::storage_traits::Dynamic<Base>> storage(
        Derived{});
    helpers::TypedStorage<helpers::storage_traits::Dynamic<Base>> storage2;
    storage2 = storage;
    EXPECT_TRUE(!!storage);
    EXPECT_TRUE(!!storage2);
  }
  EXPECT_EQ(GetStatistics<Base>().constructed, 3);
  EXPECT_EQ(GetStatistics<Base>().move_constructed, 0);
  EXPECT_EQ(GetStatistics<Base>().destructed, 3);
  EXPECT_EQ(GetStatistics<Derived>().constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().move_constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().copy_constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().destructed, 3);
}

TEST(TypedStorage, MoveAssignDerivedStatic) {
  GetStatistics<Base>() = Statistics();
  GetStatistics<Derived>() = Statistics();
  {
    helpers::TypedStorage<helpers::storage_traits::Static<Base>> storage(
        Derived{});
    helpers::TypedStorage<helpers::storage_traits::Static<Base>> storage2;
    storage2 = std::move(storage);
    EXPECT_TRUE(!!storage);
    EXPECT_TRUE(!!storage2);
  }
  EXPECT_EQ(GetStatistics<Base>().constructed, 3);
  EXPECT_EQ(GetStatistics<Base>().move_constructed, 0);
  EXPECT_EQ(GetStatistics<Base>().destructed, 3);
  EXPECT_EQ(GetStatistics<Derived>().constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().move_constructed, 2);
  EXPECT_EQ(GetStatistics<Derived>().copy_constructed, 0);
  EXPECT_EQ(GetStatistics<Derived>().destructed, 3);
}

TEST(TypedStorage, MoveAssignDerivedDynamic) {
  GetStatistics<Base>() = Statistics();
  GetStatistics<Derived>() = Statistics();
  {
    helpers::TypedStorage<helpers::storage_traits::Dynamic<Base>> storage(
        Derived{});
    helpers::TypedStorage<helpers::storage_traits::Dynamic<Base>> storage2;
    storage2 = std::move(storage);
    EXPECT_FALSE(!!storage);
    EXPECT_TRUE(!!storage2);
  }
  EXPECT_EQ(GetStatistics<Base>().constructed, 2);
  EXPECT_EQ(GetStatistics<Base>().move_constructed, 0);
  EXPECT_EQ(GetStatistics<Base>().destructed, 2);
  EXPECT_EQ(GetStatistics<Derived>().constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().move_constructed, 1);
  EXPECT_EQ(GetStatistics<Derived>().copy_constructed, 0);
  EXPECT_EQ(GetStatistics<Derived>().destructed, 2);
}
