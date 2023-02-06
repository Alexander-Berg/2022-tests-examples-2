#include <gtest/gtest.h>
#include <stdint.h>
#include <limits>
#include <ytlib/yson/yson.hpp>

using ytlib::yson::MakeArray;
using ytlib::yson::MakeObject;
using ytlib::yson::Yson;

#define VALUES(XX)                                        \
  XX("char", int64_t, '\x01')                             \
  XX("uchar", uint64_t, static_cast<unsigned char>(2u))   \
  XX("short", int64_t, static_cast<short>(3))             \
  XX("ushort", uint64_t, static_cast<unsigned short>(4u)) \
  XX("int", int64_t, 5)                                   \
  XX("uint", uint64_t, 6u)                                \
  XX("long", int64_t, 7l)                                 \
  XX("ulong", uint64_t, 8ul)                              \
  XX("llong", int64_t, 9ll)                               \
  XX("ullong", uint64_t, 10ull)                           \
  XX("float", double, 36.6f)                              \
  XX("double", double, 37.7)                              \
  XX("string", std::string, "str_val")                    \
  XX("string_view", std::string_view, "sview_val")

namespace {
template <typename T>
T As(const Yson&) {
  static_assert(sizeof(T) != sizeof(T), "Unsupported As<T>");
}
template <>
bool As(const Yson& yson) {
  return yson.AsBool();
}
template <>
int64_t As(const Yson& yson) {
  return yson.AsInt64();
}
template <>
uint64_t As(const Yson& yson) {
  return yson.AsUint64();
}
template <>
double As(const Yson& yson) {
  return yson.AsDouble();
}
template <>
std::string As(const Yson& yson) {
  return yson.AsString();
}
template <>
std::string_view As(const Yson& yson) {
  return yson.AsStringView();
}

template <typename T>
void CheckTypeMismatch(const Yson& yson) {
#define CHECK(type)                       \
  if constexpr (!std::is_same_v<T, type>) \
  EXPECT_THROW(As<type>(yson), ytlib::yson::TypeMismatchException)
  CHECK(bool);
  CHECK(int64_t);
  CHECK(uint64_t);
  CHECK(double);
  if constexpr (!std::is_same_v<T, std::string> &&
                !std::is_same_v<T, std::string_view>) {
    EXPECT_THROW(As<std::string>(yson), ytlib::yson::TypeMismatchException);
    EXPECT_THROW(As<std::string_view>(yson),
                 ytlib::yson::TypeMismatchException);
  }
}
}  // namespace

TEST(YsonValue, Primitive) {
#define XX(key, y_type, val)             \
  EXPECT_EQ(As<y_type>(Yson(val)), val); \
  CheckTypeMismatch<y_type>(Yson(val));
  VALUES(XX);
#undef XX
}

TEST(YsonValue, Array) {
  Yson yson = MakeArray(
#define XX(key, y_type, val) val,
      VALUES(XX)
#undef XX
      - 1);
  int index = 0;
#define XX(key, y_type, val)                       \
  EXPECT_EQ(As<y_type>(yson[index]), val);         \
  EXPECT_EQ(&yson[index], &yson.AsArray()[index]); \
  index++;
  VALUES(XX);
#undef XX
  EXPECT_THROW(yson[index + 1], ytlib::yson::OutOfBoundsException);
  CheckTypeMismatch<Yson::array_ptr_t>(yson);
}

TEST(YsonValue, Object) {
  Yson yson = MakeObject(
#define XX(key, y_type, val) key, val,
      VALUES(XX)
#undef XX
          "sentinel",
      Yson());
#define XX(key, y_type, val)             \
  EXPECT_EQ(As<y_type>(yson[key]), val); \
  EXPECT_EQ(&yson.AsObject()[key], &yson[key]);
  VALUES(XX);
#undef XX
  EXPECT_THROW(yson["nonexistent"], ytlib::yson::MemberMissingException);
  CheckTypeMismatch<Yson::object_ptr_t>(yson);
}

TEST(YsonValue, ObjectOfArrays) {
  Yson yson = MakeObject(
#define XX(key, y_type, val) key, MakeArray(val),
      VALUES(XX)
#undef XX
          "sentinel",
      Yson());
#define XX(key, y_type, val) EXPECT_EQ(As<y_type>(yson[key][0]), val);
  VALUES(XX)
#undef XX
}

TEST(YsonValue, ArrayOfObjects) {
  Yson yson = MakeArray(
#define XX(key, y_type, val) MakeObject(key, val),
      VALUES(XX)
#undef XX
          Yson());
  int index = 0;
#define XX(key, y_type, val)                    \
  EXPECT_EQ(As<y_type>(yson[index][key]), val); \
  index++;
  VALUES(XX)
#undef XX
}
