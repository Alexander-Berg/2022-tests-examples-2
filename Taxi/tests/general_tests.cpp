#include "framing/framing.hpp"

#include <userver/dump/test_helpers.hpp>
#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>

#include <fmt/format.h>
#include <google/protobuf/util/message_differencer.h>

#include <tests/test.pb.h>

namespace {
class PackerTest : public testing::TestWithParam<framing::Format> {
 protected:
};
}  // namespace

TEST_P(PackerTest, PackStrings) {
  const std::string expected = [&]() {
    using std::literals::string_literals::operator""s;
    switch (GetParam()) {
      case framing::Format::Auto:
      case framing::Format::Protoseq:
        return fmt::format(
            "\x09\x00\x00\x00"s
            "123456789"
            "{syncword}"
            "\x0b\x00\x00\x00"s
            "not checked"
            "{syncword}",
            fmt::arg("syncword", framing::kSyncWord));
        break;
      case framing::Format::Lenval:
        return fmt::format(
            "\t"
            "123456789"
            "\x0B"
            "not checked");
        break;
    }
  }();

  auto packer = framing::Packer{GetParam()};

  packer.Add("123456789");
  packer.Add("not checked");
  std::string out = packer.Flush();
  EXPECT_EQ(expected, out);
}

INSTANTIATE_TEST_SUITE_P(framing, PackerTest,
                         testing::Values(framing::Format::Protoseq,
                                         framing::Format::Lenval));

namespace {
class UnpackerTestDifferentFormats
    : public testing::TestWithParam<framing::Format> {
 protected:
  TB m1;
  TA m2;
  void SetUp() override {
    m1.mutable_a()->set_i(123);
    m1.mutable_a()->set_s("foobar020");
    m1.add_ff(256);
    m1.add_ff(65537);

    m2.set_i(2);
    m2.set_s("barfu030");
  }
};
}  // namespace

TEST_P(UnpackerTestDifferentFormats, UnpackStrings) {
  const std::string from = [&]() {
    using std::literals::string_literals::operator""s;
    switch (GetParam()) {
      case framing::Format::Auto:
      case framing::Format::Protoseq:
        return fmt::format(
            "\x09\x00\x00\x00"s
            "123456789"
            "{syncword}"
            "\x0b\x00\x00\x00"s
            "not checked"
            "{syncword}",
            fmt::arg("syncword", framing::kSyncWord));
        break;
      case framing::Format::Lenval:
        return fmt::format(
            "\t"
            "123456789"
            "\x0B"
            "not checked");
        break;
    }
  }();

  std::string_view from_view = from;

  auto unpacker = framing::Unpacker{GetParam(), from_view};
  bool parsed = false;
  std::string frame;

  parsed = unpacker.NextFrame(frame);
  ASSERT_TRUE(parsed);
  ASSERT_EQ(frame, "123456789");

  parsed = unpacker.NextFrame(frame);
  ASSERT_TRUE(parsed);
  ASSERT_EQ(frame, "not checked");

  parsed = unpacker.NextFrame(frame);
  ASSERT_FALSE(parsed);
}

TEST_P(UnpackerTestDifferentFormats, UnpackProtobuf) {
  const std::string source = [&] {
    framing::Packer packer{GetParam()};
    packer.Add(m1);
    packer.Add(m2);
    return packer.Flush();
  }();

  auto quasi_stream = std::string_view{source.data(), source.size()};
  framing::Unpacker unpacker(GetParam(), quasi_stream);

  TB frameTb;
  EXPECT_TRUE(unpacker.NextFrame(frameTb));
  EXPECT_TRUE(google::protobuf::util::MessageDifferencer::Equals(frameTb, m1));

  TA frameTa;
  EXPECT_TRUE(unpacker.NextFrame(frameTa));
  EXPECT_TRUE(google::protobuf::util::MessageDifferencer::Equals(frameTa, m2));
}

TEST_P(UnpackerTestDifferentFormats, CheckEndOfStream) {
  const std::string source = [&] {
    framing::Packer packer{GetParam()};
    packer.Add("foo");
    packer.Add("bar");
    return packer.Flush();
  }();

  auto quasi_stream = std::string_view{source.data(), source.size()};
  framing::Unpacker unpacker(GetParam(), quasi_stream);

  std::string foo;
  EXPECT_TRUE(unpacker.NextFrame(foo));
  EXPECT_EQ(foo, "foo");

  std::string bar;
  EXPECT_TRUE(unpacker.NextFrame(bar));
  EXPECT_EQ(bar, "bar");

  std::string something;
  EXPECT_FALSE(unpacker.NextFrame(something));

  quasi_stream = std::string_view{};
  auto unpacker2 = framing::Unpacker(GetParam(), quasi_stream);
  EXPECT_FALSE(unpacker2.NextFrame(something));
}

INSTANTIATE_TEST_SUITE_P(framing, UnpackerTestDifferentFormats,
                         testing::Values(framing::Format::Auto,
                                         framing::Format::Protoseq));

namespace {
class UnpackerTestCorruptions : public testing::TestWithParam<framing::Format> {
 protected:
  TB m1;
  TA m2;

  void SetUp() override {
    m1.mutable_a()->set_i(123);
    m1.mutable_a()->set_s("foobar020");
    m1.add_ff(256);
    m1.add_ff(65537);

    m2.set_i(2);
    m2.set_s("barfu030");
  }
};
}  // namespace

TEST_P(UnpackerTestCorruptions, FirstMessageHasLesserLength) {
  const std::string source = [&] {
    framing::Packer packer{framing::Format::Protoseq};
    packer.Add(m1);
    packer.Add(m2);
    auto message = packer.Flush();
    message[0] -= 1;
    return message;
  }();

  auto quasi_stream = std::string_view{source.data(), source.size()};
  framing::Unpacker unpacker(GetParam(), quasi_stream);

  TB frameTb;
  EXPECT_FALSE(unpacker.NextFrame(frameTb));

  TA frameTa;
  EXPECT_TRUE(unpacker.NextFrame(frameTa));
  EXPECT_TRUE(google::protobuf::util::MessageDifferencer::Equals(frameTa, m2));
}

TEST_P(UnpackerTestCorruptions, FirstMessageHasCorruptedSyncWord) {
  const std::string source = [&] {
    framing::Packer packer{framing::Format::Protoseq};
    packer.Add(m1);
    auto first_message = packer.Flush();
    first_message.back() = 0xFF;
    packer.Add(m2);
    auto second_message = packer.Flush();
    packer.Add(m1);
    auto third_message = packer.Flush();
    return first_message + second_message + third_message;
  }();

  auto quasi_stream = std::string_view{source.data(), source.size()};
  framing::Unpacker unpacker(GetParam(), quasi_stream);

  TB frameTb;
  EXPECT_FALSE(unpacker.NextFrame(frameTb));

  // the second message is skipped because its syncword found instead of the
  // corrupted first one

  EXPECT_TRUE(unpacker.NextFrame(frameTb));
  EXPECT_TRUE(google::protobuf::util::MessageDifferencer::Equals(frameTb, m1));
}

TEST_P(UnpackerTestCorruptions, FirstMessageHasGreaterLength) {
  const std::string source = [&] {
    framing::Packer packer{framing::Format::Protoseq};
    packer.Add(m1);
    auto first_message = packer.Flush();
    first_message.front() = 0xFF;
    packer.Add(m2);
    auto second_message = packer.Flush();
    packer.Add(m1);
    auto third_message = packer.Flush();
    return first_message + second_message + third_message;
  }();

  auto quasi_stream = std::string_view{source.data(), source.size()};
  framing::Unpacker unpacker(GetParam(), quasi_stream);

  TB frameTb;
  EXPECT_FALSE(unpacker.NextFrame(frameTb));

  TA frameTa;
  EXPECT_TRUE(unpacker.NextFrame(frameTa));
  EXPECT_TRUE(google::protobuf::util::MessageDifferencer::Equals(frameTa, m2));

  EXPECT_TRUE(unpacker.NextFrame(frameTb));
  EXPECT_TRUE(google::protobuf::util::MessageDifferencer::Equals(frameTb, m1));
}

INSTANTIATE_TEST_SUITE_P(framing, UnpackerTestCorruptions,
                         testing::Values(framing::Format::Protoseq));
