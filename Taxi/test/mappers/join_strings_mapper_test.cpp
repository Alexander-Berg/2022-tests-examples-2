#include <userver/utest/utest.hpp>

#include <test/common.hpp>

#include <eventus/mappers/join_strings_mapper.hpp>

TEST(MappersSuite, JoinStringsBasicTest) {
  using namespace test::common;
  auto mapper =
      MakeOperation<eventus::mappers::JoinStringsMapper>(OperationArgsV{
          {"dst_key", "joined_key"},
          {"src_keys", StringV{"first_key", "second_key", "third_key"}},
          {"separator", "__"},
          {"debug", "yes"},
      });

  {
    eventus::mappers::Event event({});
    event.Set("first_key", "first-value");
    event.Set("second_key", "second-value");
    event.Set("third_key", "third-value");
    mapper->Map(event);

    ASSERT_TRUE(event.HasKey("joined_key"));
    ASSERT_EQ(event.Get<std::string>("joined_key"),
              "first-value__second-value__third-value");
  }

  {
    eventus::mappers::Event event({});
    event.Set("second_key", "second-value");
    event.Set("third_key", "third-value");
    mapper->Map(event);

    ASSERT_TRUE(event.HasKey("joined_key"));
    ASSERT_EQ(event.Get<std::string>("joined_key"),
              "second-value__third-value");
  }

  {
    eventus::mappers::Event event({});
    event.Set("first_key", "first-value");
    mapper->Map(event);

    ASSERT_TRUE(event.HasKey("joined_key"));
    ASSERT_EQ(event.Get<std::string>("joined_key"), "first-value");
  }
}

TEST(MappersSuite, JoinStringsTakeNoneTest) {
  using namespace test::common;
  auto mapper =
      MakeOperation<eventus::mappers::JoinStringsMapper>(OperationArgsV{
          {"dst_key", "joined_key"},
          {"src_keys", StringV{"first_key", "second_key", "third_key"}},
          {"separator", "__"},
          {"take_none_as_empty", "yes"},
          {"debug", "yes"},
      });

  {
    eventus::mappers::Event event({});
    event.Set("first_key", "first-value");
    event.Set("second_key", "second-value");
    event.Set("third_key", "third-value");
    mapper->Map(event);

    ASSERT_TRUE(event.HasKey("joined_key"));
    ASSERT_EQ(event.Get<std::string>("joined_key"),
              "first-value__second-value__third-value");
  }

  {
    eventus::mappers::Event event({});
    event.Set("second_key", "second-value");
    event.Set("third_key", "third-value");
    mapper->Map(event);

    ASSERT_TRUE(event.HasKey("joined_key"));
    ASSERT_EQ(event.Get<std::string>("joined_key"),
              "__second-value__third-value");
  }

  {
    eventus::mappers::Event event({});
    event.Set("first_key", "first-value");
    mapper->Map(event);

    ASSERT_TRUE(event.HasKey("joined_key"));
    ASSERT_EQ(event.Get<std::string>("joined_key"), "first-value____");
  }
}

TEST(MappersSuite, JoinStringsRequiredAllTest) {
  using namespace test::common;
  auto mapper =
      MakeOperation<eventus::mappers::JoinStringsMapper>(OperationArgsV{
          {"dst_key", "joined_key"},
          {"src_keys", StringV{"first_key", "second_key", "third_key"}},
          {"separator", "__"},
          {"required_all", "yes"},
          {"debug", "yes"},
      });

  {
    eventus::mappers::Event event({});
    event.Set("first_key", "first-value");
    event.Set("second_key", "second-value");
    event.Set("third_key", "third-value");
    mapper->Map(event);

    ASSERT_TRUE(event.HasKey("joined_key"));
    ASSERT_EQ(event.Get<std::string>("joined_key"),
              "first-value__second-value__third-value");
  }

  {
    eventus::mappers::Event event({});
    event.Set("second_key", "second-value");
    event.Set("third_key", "third-value");
    EXPECT_THROW(mapper->Map(event), std::exception);

    ASSERT_FALSE(event.HasKey("joined_key"));
  }

  {
    eventus::mappers::Event event({});
    event.Set("first_key", "first-value");
    EXPECT_THROW(mapper->Map(event), std::exception);

    ASSERT_FALSE(event.HasKey("joined_key"));
  }
}
