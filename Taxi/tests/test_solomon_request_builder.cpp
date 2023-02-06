#include <gtest/gtest.h>

#include <clients/solomon/utils/solomon_program_builder.hpp>
#include <clients/solomon/utils/solomon_selector_builder.hpp>

#include <set>

namespace hejmdal {

TEST(SolomonSelectorBuilder, TestSolomonRequest) {
  auto builder = clients::utils::SolomonSelectorBuilder();
  EXPECT_EQ(builder.Get(), "{}");

  builder.Cluster("MyCluster");
  EXPECT_FALSE(builder.IsRawProgram());
  EXPECT_EQ(builder.Get(), "{cluster='MyCluster'}");

  builder.Service("MyService").Host("MyHost").ExcludeLabel("excluded");
  EXPECT_FALSE(builder.IsRawProgram());
  EXPECT_EQ(
      builder.Get(),
      "{cluster='MyCluster',host='MyHost',service='MyService',excluded=-}");
  std::set<std::string> sensors = {"MySensor1", "MySensor2", "MySensor3"};
  for (const auto& sensor : sensors) {
    builder.Sensor(sensor);
  }
  EXPECT_FALSE(builder.IsRawProgram());
  EXPECT_EQ(builder.Get(),
            "{cluster='MyCluster',host='MyHost',sensor='MySensor1|MySensor2|"
            "MySensor3',service='MyService',excluded=-}");
  builder.Clear();
  EXPECT_FALSE(builder.IsRawProgram());
  EXPECT_EQ(builder.Get(), "{}");

  std::set<std::string> excl = {"Vla", "Sas"};
  builder.Clear();
  for (const auto& label : excl) {
    builder.ExcludeLabelValue("host", label);
  }
  EXPECT_FALSE(builder.IsRawProgram());
  EXPECT_EQ(builder.Get(), "{host!='Sas|Vla'}");
}

TEST(SolomonSelectorBuilder, TestSolomonRawProgramRequest) {
  auto builder = clients::utils::SolomonSelectorBuilder();
  EXPECT_FALSE(builder.IsRawProgram());
  EXPECT_EQ(builder.Get(), "{}");

  builder.RawProgram("MyVeryRawProgram({some_data_selector})");
  EXPECT_TRUE(builder.IsRawProgram());
  EXPECT_EQ(builder.Get(), "MyVeryRawProgram({some_data_selector})");

  builder.Clear();
  EXPECT_FALSE(builder.IsRawProgram());
  EXPECT_EQ(builder.Get(), "{}");

  builder.RawProgram("MyVeryRawProgram({another_data_selector})");

  EXPECT_ANY_THROW(builder.Cluster("SomeCluster"));
  EXPECT_ANY_THROW(builder.Service("SomeService"));
  EXPECT_ANY_THROW(builder.Application("SomeApplication"));
  EXPECT_ANY_THROW(builder.Host("SomeHost"));
  EXPECT_ANY_THROW(builder.Sensor("SomeSensor"));
  EXPECT_ANY_THROW(builder.AddKeyValue("SomeKey", "SomeValue"));
  EXPECT_ANY_THROW(builder.ExcludeLabel("SomeLabel"));
  EXPECT_ANY_THROW(builder.ExcludeLabelValue("SomeLabel", "SomeValue"));
}

TEST(SolomonProgramBuilder, TestSolomonProgramBuilder) {
  auto selector =
      clients::utils::SolomonSelectorBuilder().Cluster("c").Host("h");

  auto program = clients::utils::SolomonProgramBuilder().SumLines(selector);

  EXPECT_EQ(program.Extract(), "group_lines('sum',{cluster='c',host='h'})");
}

void TestMatchAsterisk(const std::string& needle, const std::string& haystack,
                       bool expected) {
  constexpr auto MatchAsterisk = &hejmdal::clients::utils::MatchAsterisk;

  auto result = MatchAsterisk(needle.begin(), needle.end(), haystack.begin(),
                              haystack.end());
  EXPECT_EQ(expected, result)
      << "needle: " << needle << ", hayastack: " << haystack;
}

TEST(SolomonSelectorBuilder, TestMatchAsterisk) {
  TestMatchAsterisk("a", "a", true);
  TestMatchAsterisk("a", "b", false);
  TestMatchAsterisk("a*", "a", true);
  TestMatchAsterisk("a*", "adbf", true);
  TestMatchAsterisk("*a", "a", true);
  TestMatchAsterisk("*a", "bcda", true);
  TestMatchAsterisk("a*b", "ab", true);
  TestMatchAsterisk("a*b", "acdfb", true);
  TestMatchAsterisk("a*b", "abc", false);
}

TEST(SolomonSelectorBuilder, TestMatch) {
  auto builder = clients::utils::SolomonSelectorBuilder();
  builder.Service("service1");
  builder.Sensor("sensor1");
  builder.AddKeyValue("some_key", "*some_value");

  std::unordered_map<std::string, std::string> some_labels1{
      {"service", "service1"},
      {"sensor", "sensor1"},
      {"some_key", "1some_value"}};

  EXPECT_TRUE(builder.Match(some_labels1));

  builder.ExcludeLabelValue("some_key", "2some_value");

  std::unordered_map<std::string, std::string> some_labels2{
      {"service", "service1"},
      {"sensor", "sensor1"},
      {"some_key", "2some_value"}};

  EXPECT_FALSE(builder.Match(some_labels2));

  std::unordered_map<std::string, std::string> some_labels3{
      {"service", "service1"},
      {"sensor", "another_sensor"},
      {"some_key", "1some_value"}};

  EXPECT_FALSE(builder.Match(some_labels3));
}

TEST(SolomonSelectorBuilder, TestReplaceKeyValueInRawProgram) {
  auto builder = clients::utils::SolomonSelectorBuilder();
  EXPECT_ANY_THROW(builder.ReplaceKeyValueInRawProgram("host", "Man"));

  builder.RawProgram("{project='taxi'}");
  EXPECT_ANY_THROW(builder.ReplaceKeyValueInRawProgram("host", "Man"));

  builder.RawProgram("{project='taxi', host='Sas|Vla}");
  EXPECT_ANY_THROW(builder.ReplaceKeyValueInRawProgram("host", "Man"));

  builder.RawProgram("{project='taxi', host=Sas|Vla'}");
  EXPECT_ANY_THROW(builder.ReplaceKeyValueInRawProgram("host", "Man"));

  builder.RawProgram("{project='taxi', host!='Sas|Vla'}");
  builder.ReplaceKeyValueInRawProgram("host", "Man");
  EXPECT_EQ(builder.Get(), "{project='taxi', host='Man'}");

  builder.RawProgram("{project='taxi', host='Sas|Vla'}");
  builder.ReplaceKeyValueInRawProgram("host", "Man");
  EXPECT_EQ(builder.Get(), "{project='taxi', host='Man'}");

  builder.RawProgram("{project=\"taxi\", host=\"Sas|Vla\"}");
  builder.ReplaceKeyValueInRawProgram("host", "Man");
  EXPECT_EQ(builder.Get(), "{project=\"taxi\", host=\"Man\"}");

  builder.RawProgram("{project='taxi', host='*'}");
  builder.ReplaceKeyValueInRawProgram("host", "Man");
  EXPECT_EQ(builder.Get(), "{project='taxi', host='Man'}");

  builder.RawProgram("{project='taxi', host=''}");
  builder.ReplaceKeyValueInRawProgram("host", "Man");
  EXPECT_EQ(builder.Get(), "{project='taxi', host='Man'}");

  builder.RawProgram(
      "{project='taxi', host='*', cluster='production', host='Sas|Vla'}");
  builder.ReplaceKeyValueInRawProgram("host", "Man");
  EXPECT_EQ(builder.Get(),
            "{project='taxi', host='Man', cluster='production', host='Man'}");

  builder.RawProgram(
      "{project='taxi', host!='*', cluster='production', host!='Sas|Vla'}");
  builder.ReplaceKeyValueInRawProgram("host", "Man");
  EXPECT_EQ(builder.Get(),
            "{project='taxi', host='Man', cluster='production', host='Man'}");
}

}  // namespace hejmdal
