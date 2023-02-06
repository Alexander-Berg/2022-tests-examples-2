#include <userver/utest/utest.hpp>

#include <optional>

#include <models/double_with_payload.hpp>

using Type = models::DoubleWithPayload;

TEST(DoubleWithPayload, Ctor) {
  const Type default_constructed{};
  ASSERT_EQ(default_constructed, 0.);
  ASSERT_EQ(default_constructed.GetPayload(), std::nullopt);

  const Type double_constructed(1.5);
  ASSERT_EQ(double_constructed, 1.5);
  ASSERT_EQ(double_constructed.GetPayload(), std::nullopt);

  const Type constructed(1.7, "str");
  ASSERT_EQ(constructed, 1.7);
  ASSERT_EQ(constructed.GetPayload(), "str");

  Type to_assign(5.5, "string");
  to_assign = 2.5;
  ASSERT_EQ(to_assign, 2.5);
  ASSERT_EQ(to_assign.GetPayload(), "string");

  const Type invalid(5.5, "INVALID");
  ASSERT_EQ(invalid, 5.5);
  ASSERT_EQ(invalid.GetPayload(), std::nullopt);
};

TEST(DoubleWithPayload, Payload) {
  Type a(5.5);
  ASSERT_EQ(a.GetPayload(), std::nullopt);

  a.SetPayload("strstr");
  ASSERT_EQ(a.GetPayload(), "strstr");

  a.SetPayload("123");
  ASSERT_EQ(a.GetPayload(), "123");
}

TEST(DoubleWithPayload, Conversion) {
  {
    double a = 3.5;
    double b = a + Type(1.5);
    ASSERT_EQ(b, 5.);
  }

  {
    Type a(3.5);
    double& b = a;
    b += 2.5;
    ASSERT_EQ(a, 6.);
  }

  {
    Type a(3.5);
    a += 4.5;
    ASSERT_EQ(a, 8.);
  }
}

TEST(DoubleWithPayload, Specific) {
  Type a(3.5);
  a += Type(1.5);
  ASSERT_EQ(a, 5.);
  ASSERT_EQ(a.GetPayload(), std::nullopt);

  a += Type(1, "payload");
  ASSERT_EQ(a, 6.);
  ASSERT_EQ(a.GetPayload(), "payload");

  a += Type(0.5, "payload");
  ASSERT_EQ(a, 6.5);
  ASSERT_EQ(a.GetPayload(), "payload");

  a += Type(1.);
  ASSERT_EQ(a, 7.5);
  ASSERT_EQ(a.GetPayload(), "payload");

  a += Type(2.3, "other");
  ASSERT_EQ(a, 9.8);
  ASSERT_EQ(a.GetPayload(), std::nullopt);

  a += Type(1.2, "another");
  ASSERT_EQ(a, 11.0);
  ASSERT_EQ(a.GetPayload(), std::nullopt);
}
