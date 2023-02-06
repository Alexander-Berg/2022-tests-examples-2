#include <gtest/gtest.h>

#include <forward_list>
#include <string>

#include <utils/hex.hpp>

namespace geobus::utils {

namespace {
template <typename T>
auto GetEndPtr(const T& data) {
  return data.data() + data.size();
};

inline void ResizeByLastPtr(std::string& object, const char* ptr) {
  object.resize(ptr - object.data());
}

}  // namespace

TEST(Hex, LengthInHexForm) {
  std::string empty;
  EXPECT_EQ(0, LengthInHexForm(empty));

  std::string data{"_+=156"};
  EXPECT_EQ(12, LengthInHexForm(data));

  EXPECT_EQ(6, LengthInHexForm(3));
}

TEST(Hex, FromHexUpperBound) {
  EXPECT_EQ(0, FromHexUpperBound(0));
  EXPECT_EQ(3, FromHexUpperBound(6));
  EXPECT_EQ(3, FromHexUpperBound(7));
}

TEST(Hex, ToHex) {
  std::string data{"_+=156"};
  std::string reference{"5f2b3d313536"};
  std::string result = ToHex(data);
  EXPECT_EQ(reference, result);
}

TEST(Hex, FromHex) {
  // Test simple case - everything is correct
  {
    std::string data{"5f2b3d313536"};
    EXPECT_TRUE(IsHexData(data));
    std::string reference{"_+=156"};
    std::string result;
    result.resize(FromHexUpperBound(data.size()), 'x');
    auto [input_last, output_last] = FromHex(data, result.data());
    EXPECT_EQ(GetEndPtr(result), output_last);
    EXPECT_EQ(GetEndPtr(data), input_last);
    EXPECT_EQ(reference, result);
  }
  // Test missing symbol
  {
    // True data is : std::string data{"5f2b3d313536"};
    // Remove one symbol
    std::string data{"5f2b3d31353"};
    std::string reference{"_+=15"};
    std::string result;
    EXPECT_FALSE(IsHexData(data));  // no, because one symbol is missing
    // Add extra 2 elements to better check where output_last wil be
    result.resize(FromHexUpperBound(data.size()) + 2, 'x');
    auto [input_last, output_last] = FromHex(data, result.data());
    // All input except last char should have been read
    EXPECT_EQ(GetEndPtr(data) - 1, input_last);
    EXPECT_EQ(reference.size(), std::distance(result.data(), output_last));
    // now, resize result to real limit
    ResizeByLastPtr(result, output_last);
    EXPECT_EQ(reference, result);
  }
  // Test wrong symbol at even position
  {
    // True data is : std::string data{"5f2b3d313536"};
    // Place wrong symbol
    std::string data{"5f2b!3d313536"};
    EXPECT_FALSE(IsHexData(data));  // no, because one symbol is not hex
    std::string reference{"_+"};
    std::string result;
    result.resize(FromHexUpperBound(data.size()));
    auto [input_last, output_last] = FromHex(data, result.data());
    // Should have stopped at '!'
    EXPECT_NE(GetEndPtr(data), input_last);
    EXPECT_EQ('!', *input_last);
    ResizeByLastPtr(result, output_last);
    EXPECT_EQ(reference, result);
  }
  // Test wrong symbol at odd position
  {
    // True data is : std::string data{"5f2b3d313536"};
    // Place wrong symbol
    std::string data{"5f2b3!d313536"};
    EXPECT_FALSE(IsHexData(data));  // no, because one symbol is not hex
    std::string reference{"_+"};
    std::string result;
    result.resize(FromHexUpperBound(data.size()));
    auto [input_last, output_last] = FromHex(data, result.data());
    // Should have stopped at '3', right before '!'
    EXPECT_NE(GetEndPtr(data), input_last);
    EXPECT_EQ('3', *input_last);
    ResizeByLastPtr(result, output_last);
    EXPECT_EQ(reference, result);
  }

  // Test all supported hex chars
  {
    std::string data{"0123456789abcdef"};
    EXPECT_TRUE(IsHexData(data));
  }
}

TEST(Hex, FromHexInplace) {
  // Test simple case - everything is correct
  {
    std::string data{"5f2b3d313536"};
    EXPECT_TRUE(IsHexData(data));
    std::string reference{"_+=156"};
    auto [input_last, output_last] = FromHex(data, data.data());
    EXPECT_EQ(reference.size(), std::distance(data.data(), output_last));
    EXPECT_EQ(GetEndPtr(data), input_last);

    // Clean up leftover data
    ResizeByLastPtr(data, output_last);
    EXPECT_EQ(reference, data);
  }
  // Test missing symbol
  {
    // True data is : std::string data{"5f2b3d313536"};
    // Remove one symbol
    std::string data{"5f2b3d31353"};
    std::string reference{"_+=15"};
    auto [input_last, output_last] = FromHex(data, data.data());
    ResizeByLastPtr(data, output_last);
    EXPECT_EQ(reference, data);
  }
  // Test wrong symbol at even position
  {
    // True data is : std::string data{"5f2b3d313536"};
    // Place wrong symbol
    std::string data{"5f2b!3d313536"};
    EXPECT_FALSE(IsHexData(data));  // no, because one symbol is not hex
    std::string reference{"_+"};
    std::string result;
    auto [input_last, output_last] = FromHex(data, data.data());
    ResizeByLastPtr(data, output_last);
    EXPECT_EQ(reference, data);
  }
  // Test wrong symbol at odd position
  {
    // True data is : std::string data{"5f2b3d313536"};
    // Place wrong symbol
    std::string data{"5f2b3!d313536"};
    EXPECT_FALSE(IsHexData(data));  // no, because one symbol is not hex
    std::string reference{"_+"};
    std::string result;
    auto [input_last, output_last] = FromHex(data, data.data());
    ResizeByLastPtr(data, output_last);
    EXPECT_EQ(reference, data);
  }
}

TEST(Hex, GetHexPart) {
  // Test simple case - everything is correct
  {
    std::string data{"5f2b3d313536"};
    EXPECT_TRUE(IsHexData(data));
    EXPECT_EQ(data.data() + data.size(), GetHexPart(data));
  }
  // Test missing symbol
  {
    // True data is : std::string data{"5f2b3d313536"};
    // Remove one symbol
    std::string data{"5f2b3d31353"};
    EXPECT_FALSE(IsHexData(data));  // no, because one symbol is missing
    EXPECT_EQ(data.data() + data.size() - 1, GetHexPart(data));
  }
  // Test wrong symbol at even position
  {
    // True data is : std::string data{"5f2b3d313536"};
    // Place wrong symbol
    std::string data{"5f2b!3d313536"};
    EXPECT_FALSE(IsHexData(data));  // no, because one symbol is not hex
    // Should have stopped at '!'
    EXPECT_EQ(data.data() + 4, GetHexPart(data));
  }
  // Test wrong symbol at odd position
  {
    // True data is : std::string data{"5f2b3d313536"};
    // Place wrong symbol
    std::string data{"5f2b3!d313536"};
    EXPECT_EQ(data.data() + 4, GetHexPart(data));
    EXPECT_FALSE(IsHexData(data));  // no, because one symbol is not hex
  }
}

}  // namespace geobus::utils
