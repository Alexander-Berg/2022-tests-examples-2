#include <memory>
#include <string>

#include <incremental-unordered-map/incremental_unordered_map.hpp>

#include <userver/utest/utest.hpp>

#include <userver/engine/run_standalone.hpp>
#include <userver/rcu/rcu.hpp>

namespace incremental_unordered_map::tests {

namespace {

struct Config final {
  static constexpr auto kMaxIncrements = 5;
  static constexpr auto kIncrementFreezeThreshold = 1;
};

using Container =
    incremental_unordered_map::IncrementalUnorderedMap<Config, std::string,
                                                       std::string>;

struct IncrementCompactConfig final {
  static constexpr auto kMaxIncrements = 5;
  static constexpr auto kIncrementFreezeThreshold = 2;
};

using CompactingIncrementsContainer =
    incremental_unordered_map::IncrementalUnorderedMap<
        IncrementCompactConfig, std::string, std::string>;

void AddSomeData(Container& container) {
  container.insert_or_assign("a", "a");
  container.OnWritesDone();
}

}  // namespace

TEST(ContainerIteration, empty_container) {
  Container container;

  size_t sz = 0;
  for ([[maybe_unused]] const auto& [k, v] : container) {
    ++sz;
  }

  ASSERT_EQ(sz, 0);
}

TEST(ContainerIteration, only_full_update) {
  Container container;
  AddSomeData(container);

  size_t sz = 0;
  for ([[maybe_unused]] const auto& [k, v] : container) {
    ++sz;
  }

  ASSERT_EQ(sz, 1);
}

TEST(ContainerIteration, has_increments_same_key) {
  Container container;
  AddSomeData(container);
  AddSomeData(container);
  AddSomeData(container);

  size_t sz = 0;
  for ([[maybe_unused]] const auto& [k, v] : container) {
    ++sz;
  }

  ASSERT_EQ(sz, 1);
}

TEST(ContainerIteration, has_increments_different_keys) {
  Container container;

  const auto add = [&container](std::string key, std::string value) {
    container.insert_or_assign(std::move(key), std::move(value));
    container.OnWritesDone();
  };

  add("first", "first_v");
  add("second", "second_v");
  add("third", "third_v");

  std::vector<std::pair<std::string, std::string>> items;
  for (const auto& [k, v] : container) items.push_back({k.GetKey(), v});
  std::sort(items.begin(), items.end());

  ASSERT_EQ(items.size(), 3);

  ASSERT_EQ(items[0].first, "first");
  ASSERT_EQ(items[0].second, "first_v");
  ASSERT_EQ(items[1].first, "second");
  ASSERT_EQ(items[1].second, "second_v");
  ASSERT_EQ(items[2].first, "third");
  ASSERT_EQ(items[2].second, "third_v");
}

TEST(ContainerFind, basic_find) {
  Container container;
  container.insert_or_assign("68a62d07-cb90-43ba-b8b4-73ffbf8c80fe",
                             "68a62d07-cb90-43ba-b8b4-73ffbf8c80fe");
  container.OnWritesDone();

  auto it = container.find("68a62d07-cb90-43ba-b8b4-73ffbf8c80fe");
  ASSERT_TRUE(it != container.end());
  ASSERT_EQ(it->first.GetKey(), "68a62d07-cb90-43ba-b8b4-73ffbf8c80fe");
  ASSERT_EQ(it->second, "68a62d07-cb90-43ba-b8b4-73ffbf8c80fe");
}

TEST(ContainerFind, not_found) {
  Container container;
  AddSomeData(container);
  // ASSERT_EQ(container.parts_count(), 2);

  const auto it = container.find("asdasd");
  ASSERT_TRUE(it == container.end());
}

TEST(ContainerFind, found_in_increment) {
  Container container;
  const std::string key = "some-random-string-key";

  container.insert_or_assign(std::string{key}, "1");
  container.OnWritesDone();

  container.insert_or_assign(std::string{key}, "2");
  container.OnWritesDone();

  const auto it = container.find(key);
  ASSERT_TRUE(it != container.end());

  ASSERT_EQ(it->first.GetKey(), key);
  ASSERT_EQ(it->second, "2");
}

TEST(ContainerCompact, test_basic) {
  engine::RunStandalone([] {
    Container container;

    const auto add = [&container](int kv) {
      auto k_str = std::to_string(kv);
      auto v_str = std::to_string(kv);
      container.insert_or_assign(std::move(k_str), std::move(v_str));
      container.OnWritesDone();
    };

    const auto check_keys = [&container](int to) {
      std::vector<std::pair<std::string, std::string>> items;
      for (const auto& [k, v] : container) items.push_back({k.GetKey(), v});
      ASSERT_EQ(items.size(), to + 1);

      std::sort(items.begin(), items.end());
      for (int i = 0; i <= to; ++i) {
        const auto v = std::to_string(i);
        ASSERT_EQ(items[i].first, v);
        ASSERT_EQ(items[i].second, v);
      }
    };

    add(0);
    ASSERT_EQ(container.IncrementsCount(), 0);

    for (int i = 1; i <= Config::kMaxIncrements; ++i) add(i);
    ASSERT_EQ(container.IncrementsCount(), Config::kMaxIncrements);
    check_keys(Config::kMaxIncrements);

    add(Config::kMaxIncrements);
    ASSERT_EQ(container.IncrementsCount(), 0);
    check_keys(Config::kMaxIncrements);
  });
}

TEST(ContainerCompact, increment_compaction) {
  engine::RunStandalone([] {
    CompactingIncrementsContainer container;
    for (size_t i = 0; i < 10; ++i) {
      container.insert_or_assign(std::to_string(i), std::to_string(i));
    }
    container.OnWritesDone();
    ASSERT_EQ(container.IncrementsCount(), 0);
    ASSERT_EQ(container.size(), 10);
    ASSERT_EQ(container.TotalSize(), 10);

    container.insert_or_assign("5", "_5");
    container.OnWritesDone();
    ASSERT_EQ(container.IncrementsCount(), 1);
    ASSERT_EQ(container.size(), 10);
    ASSERT_EQ(container.TotalSize(), 11);

    container.insert_or_assign("5", "__5");
    container.insert_or_assign("6", "_6");
    container.insert_or_assign("10", "10");
    container.OnWritesDone();
    ASSERT_EQ(container.find("5")->second, "__5");
    ASSERT_EQ(container.find("6")->second, "_6");
    ASSERT_EQ(container.find("10")->second, "10");
    ASSERT_EQ(container.IncrementsCount(), 1);
    ASSERT_EQ(container.size(), 11);
    ASSERT_EQ(container.TotalSize(), 13);
  });
}

TEST(ContainerCompact, size) {
  engine::RunStandalone([] {
    Container container;

    const auto add = [&container](int kv) {
      container.insert_or_assign(std::to_string(kv), std::to_string(kv));
      container.OnWritesDone();
    };

    ASSERT_EQ(container.size(), 0);
    ASSERT_EQ(container.TotalSize(), 0);

    for (size_t i = 0; i <= Config::kMaxIncrements; ++i) add(i);
    ASSERT_EQ(container.size(), Config::kMaxIncrements + 1);
    ASSERT_EQ(container.TotalSize(), Config::kMaxIncrements + 1);
    ASSERT_EQ(container.IncrementsCount(), Config::kMaxIncrements);

    add(0);
    ASSERT_EQ(container.size(), Config::kMaxIncrements + 1);
    ASSERT_EQ(container.TotalSize(), Config::kMaxIncrements + 1);
    ASSERT_EQ(container.IncrementsCount(), 0);

    for (size_t i = 0; i < Config::kMaxIncrements; ++i) add(0);
    ASSERT_EQ(container.size(), Config::kMaxIncrements + 1);
    ASSERT_EQ(container.TotalSize(), Config::kMaxIncrements * 2 + 1);
    ASSERT_EQ(container.IncrementsCount(), Config::kMaxIncrements);
  });
}

TEST(ContainerInRCU, test_basic) {
  engine::RunStandalone([] {
    rcu::Variable<std::shared_ptr<const Container>> rcu;

    const auto upd_rcu = [&rcu](Container&& map) {
      rcu.Assign(std::make_shared<const Container>(std::move(map)));
    };
    upd_rcu(Container{});

    const auto& last_version = *rcu.ReadCopy();
    ASSERT_EQ(last_version.size(), 0);

    Container new_version{last_version};
    new_version.insert_or_assign("1", "1");
    new_version.OnWritesDone();
    upd_rcu(std::move(new_version));

    const auto& latest_version = *rcu.ReadCopy();
    ASSERT_TRUE(latest_version.begin() != latest_version.end());
    ASSERT_EQ(latest_version.size(), 1);
  });
}

}  // namespace incremental_unordered_map::tests
