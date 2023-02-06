#include <userver/utest/utest.hpp>

#include <grocery-shared/types.hpp>

namespace grocery_shared {

namespace {

std::vector<ShelfType> GetAllEnums() {
  std::vector<ShelfType> result;
  bool ok = false;
  const auto enum_item = ShelfType::kStore;
  // Do not forget add enum here
  switch (enum_item) {
    case ShelfType::kStore:
    case ShelfType::kMarkdown:
    case ShelfType::kParcel:
    case ShelfType::kGoalReward:
      ok = true;
  }

  return {ShelfType::kMarkdown, ShelfType::kStore, ShelfType::kParcel,
          ShelfType::kGoalReward};
}

}  // namespace

TEST(ProductKey, CTor) {
  const ProductId id{"abc1234"};

  ProductKey pk(id);
  ASSERT_EQ(pk.id, id);
  ASSERT_EQ(pk.shelf_type, ShelfType::kStore);

  pk = ProductKey(id, ShelfType::kStore);
  ASSERT_EQ(pk.id, id);
  ASSERT_EQ(pk.shelf_type, ShelfType::kStore);

  pk = ProductKey(id, ShelfType::kMarkdown);
  ASSERT_EQ(pk.id, id);
  ASSERT_EQ(pk.shelf_type, ShelfType::kMarkdown);

  pk = ProductKey(id, ShelfType::kParcel);
  ASSERT_EQ(pk.id, id);
  ASSERT_EQ(pk.shelf_type, ShelfType::kParcel);

  pk = ProductKey(id, ShelfType::kGoalReward);
  ASSERT_EQ(pk.id, id);
  ASSERT_EQ(pk.shelf_type, ShelfType::kGoalReward);
}

TEST(ProductKey, Serialization) {
  const std::string id{"abc1234"};
  ProductId pid{id};

  {
    const ProductKey pk = ProductKey::ParseHandlerId(id);
    ASSERT_EQ(pk.id.GetUnderlying(), id);
  }
  {
    const ProductKey pk{pid};
    ASSERT_EQ(pk.ToHandlerId(), id);
  }
  {
    const ProductKey pk{pid, ShelfType::kStore};
    ASSERT_EQ(pk.ToHandlerId(), id);
  }
  {
    const ProductKey pk{pid, ShelfType::kMarkdown};
    ASSERT_NE(pk.ToHandlerId(), id);
  }
  {
    const ProductKey pk{pid, ShelfType::kParcel};
    ASSERT_NE(pk.ToHandlerId(), id);
  }
  {
    const ProductKey pk{pid, ShelfType::kGoalReward};
    ASSERT_NE(pk.ToHandlerId(), id);
  }
  {
    constexpr const auto check = [](const ProductKey& pk) {
      const auto serialized = pk.ToHandlerId();
      const auto parsed = ProductKey::ParseHandlerId(serialized);
      ASSERT_EQ(pk.id, parsed.id);
      ASSERT_EQ(pk.shelf_type, parsed.shelf_type);
      ASSERT_EQ(pk, parsed);
    };

    for (auto shelf_type : GetAllEnums()) {
      check(ProductKey{pid, shelf_type});
    }
    check(ProductKey{pid});
  }
}

}  // namespace grocery_shared
