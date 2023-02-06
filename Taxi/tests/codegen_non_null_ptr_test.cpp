#include <userver/utest/utest.hpp>

#include <codegen/non_null_ptr.hpp>
#include <defs/definitions/simple_recursive.hpp>

TEST(NonNullPtr, Assignment) {
  ::codegen::NonNullPtr a = std::make_unique<int>(4);
  ::codegen::NonNullPtr b = std::make_unique<int>(5);

  a = b;
  EXPECT_EQ(*a.Get(), 5);
}

TEST(NonNullPtr, UniqueOwnershipA) {
  ::codegen::NonNullPtr a = std::make_unique<int>(4);
  ::codegen::NonNullPtr b = std::make_unique<int>(5);

  a = b;
  b = std::make_unique<int>(6);
  EXPECT_EQ(*a.Get(), 5);
  EXPECT_EQ(*b.Get(), 6);
}

TEST(NonNullPtr, UniqueOwnershipB) {
  ::codegen::NonNullPtr a = std::make_unique<int>(4);
  ::codegen::NonNullPtr b = std::make_unique<int>(5);

  a = b;
  a = std::make_unique<int>(6);
  EXPECT_EQ(*a.Get(), 6);
  EXPECT_EQ(*b.Get(), 5);
}

TEST(NotNullPtr, CodegenAssignment) {
  using Root = handlers::Root;
  using Children = handlers::Children;

  Root a{std::make_unique<Children>(Children{4})};
  Root b{std::make_unique<Children>(Children{5})};

  a = b;
  EXPECT_EQ(a.children->value, 5);
  EXPECT_EQ(a.children->value, b.children->value);
  EXPECT_TRUE(a.children.Get() != b.children.Get());
}
