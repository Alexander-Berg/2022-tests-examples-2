#include <unordered_set>

#include <userver/utest/utest.hpp>

#include <segmented_dict/segmented_dict.hpp>

namespace {

using Dict = segmented_dict::SegmentedDict<std::string, int>;

constexpr size_t kDefaultWorkerThreads = 4;

void Find(const std::unordered_map<std::string, int>& map,
          const std::unordered_set<std::string>& keys) {
  Dict dict;
  for (const auto& [key, value] : map) dict.Upsert(key, value);

  for (const auto& key : keys) {
    size_t times_called{0};
    const bool has_key = map.count(key);
    ASSERT_EQ(dict.Find(key, [&times_called](const auto&) { times_called++; }),
              has_key);
    ASSERT_TRUE(has_key ? times_called == 1 : times_called == 0);
  }
}

void ContainsKey(const std::unordered_map<std::string, int>& map,
                 const std::unordered_set<std::string>& keys) {
  Dict dict;
  for (const auto& [key, value] : map) dict.Upsert(key, value);

  for (const auto& key : keys) {
    ASSERT_EQ(dict.ContainsKey(key), map.count(key));
  }
}

void Update(const std::unordered_map<std::string, int>& a,
            std::unordered_map<std::string, int> b) {
  Dict dict;
  for (const auto& [key, value] : a) dict.Upsert(key, value);

  for (const auto& [key, value] : b) {
    size_t times_called{0};
    const bool has_key = a.count(key);
    ASSERT_EQ(dict.Update(key,
                          [&times_called, value(value)](auto& val) {
                            val = value;
                            times_called++;
                          }),
              has_key);
    ASSERT_TRUE(has_key ? times_called == 1 : times_called == 0);
  }

  ASSERT_EQ(dict.GetSizeApprox(), a.size());

  for (const auto& [key, value] : a)
    dict.Find(key, [value(b.count(key) ? b[key] : value)](const auto& val) {
      ASSERT_EQ(value, val);
    });
}

void InsertThenUpdate(std::unordered_map<std::string, int> a,
                      const std::unordered_map<std::string, int>& b) {
  Dict dict;
  for (const auto& [key, value] : a) dict.Upsert(key, value);

  size_t times_called{0};

  for (const auto& [key, value] : b) {
    const bool should_insert = !a.count(key);
    ASSERT_EQ(dict.InsertThenUpdate(key,
                                    [value(value), should_insert,
                                     &times_called](bool inserted, int& val) {
                                      ASSERT_EQ(inserted, should_insert);
                                      val = value;
                                      times_called++;
                                    }),
              should_insert);
  }

  ASSERT_EQ(times_called, b.size());

  for (const auto& [key, value] : b) a[key] = value;

  ASSERT_EQ(dict.GetSizeApprox(), a.size());

  for (const auto& [key, value] : a)
    ASSERT_EQ(dict.Find(key, [value(value)](
                                 const auto& val) { ASSERT_EQ(val, value); }),
              true);
}

void Insert(std::unordered_map<std::string, int> a,
            std::unordered_map<std::string, int> b) {
  Dict dict;
  for (const auto& [key, value] : a) dict.Upsert(key, value);

  for (const auto& [key, value] : b)
    ASSERT_EQ(dict.Insert(key, value), !a.count(key));

  a.merge(b);

  ASSERT_EQ(dict.GetSizeApprox(), a.size());

  for (const auto& [key, value] : a)
    ASSERT_EQ(dict.Find(key, [value(value)](
                                 const auto& val) { ASSERT_EQ(val, value); }),
              true);
}

void Upsert(const std::vector<std::pair<std::string, int>>& values) {
  Dict dict;
  std::unordered_map<std::string, int> tmp;
  for (const auto& [key, value] : values) {
    tmp[key] = value;
    dict.Upsert(key, value);
  }
  for (const auto& [key, value] : tmp)
    ASSERT_TRUE(dict.Find(
        key, [& value = value](const auto& item) { ASSERT_EQ(item, value); }));
}

void UpsertMany(const std::vector<std::pair<std::string, int>>& values) {
  Dict dict;
  std::unordered_map<std::string, int> tmp;
  for (const auto& [key, value] : values) tmp[key] = value;

  size_t ret = dict.UpsertMany(tmp);

  ASSERT_EQ(ret, dict.GetSizeApprox());

  for (const auto& [key, value] : tmp)
    ASSERT_TRUE(dict.Find(
        key, [& value = value](const auto& item) { ASSERT_EQ(item, value); }));
}

void GetSizeApprox(std::vector<std::string> keys, size_t size) {
  Dict dict;
  ASSERT_EQ(dict.GetSizeApprox(), 0);
  for (const auto& key : keys) dict.Upsert(key, 0);
  ASSERT_EQ(dict.GetSizeApprox(), size);
  dict.Clear();
  ASSERT_EQ(dict.GetSizeApprox(), 0);
}

void Erase(std::unordered_set<std::string> keys) {
  Dict dict;
  for (const auto& key : keys) dict.Upsert(key, 0);

  ASSERT_EQ(keys.size(), dict.GetSizeApprox());

  for (const auto& key : keys) {
    ASSERT_TRUE(dict.Find(key, [](const auto&) {}));
    dict.Erase(key);
    ASSERT_FALSE(dict.Find(key, [](const auto&) {}));
  }

  ASSERT_EQ(dict.GetSizeApprox(), 0);
}

void ForEach(const std::unordered_map<std::string, int>& a,
             const std::unordered_map<std::string, int>& b) {
  Dict dict;
  for (const auto& [key, value] : a) dict.Upsert(key, value);

  dict.ForEach([&b](auto& item) {
    if (const auto it = b.find(item.first); it != b.end())
      item.second = it->second;
  });

  for (const auto& [key, value] : a) {
    const auto it = b.find(key);
    auto expected = it == b.end() ? value : it->second;
    dict.Find(key,
              [expected](const auto& value) { ASSERT_EQ(expected, value); });
  }
}

void ForEachConst(const std::unordered_map<std::string, int>& map) {
  Dict dict;
  for (const auto& [key, value] : map) dict.Upsert(key, value);

  std::unordered_map<std::string, int> tmp;
  static_cast<const Dict&>(dict).ForEach(
      [&tmp](const auto& item) { tmp.emplace(item.first, item.second); });

  ASSERT_EQ(tmp, map);
}

template <typename Func>
void EraseIf(std::unordered_map<std::string, int> map, Func func) {
  Dict dict;
  for (const auto& [key, value] : map) dict.Upsert(key, value);

  for (auto it = map.begin(); it != map.end();)
    if (func(*it))
      it = map.erase(it);
    else
      ++it;

  dict.EraseIf(func);

  ASSERT_EQ(map.size(), dict.GetSizeApprox());

  for (const auto& [key, value] : map)
    ASSERT_TRUE(dict.Find(key, [](const auto&) {}));
}

}  // namespace

TEST(SegmentedDict, Find) {
  RunInCoro(
      [] {
        Find({}, {"1", "2", "3"});
        Find({{"1", 1}}, {"1", "2"});
        Find({{"1", 1}}, {"2", "3"});
        Find({{"1", 1}, {"2", 2}}, {"2", "3"});
        Find({{"1", 1}, {"2", 2}}, {"3", "4"});
      },
      kDefaultWorkerThreads);
}

TEST(SegmentedDict, ContainsKey) {
  RunInCoro(
      [] {
        ContainsKey({}, {"1", "2", "3"});
        ContainsKey({{"1", 1}}, {"1", "2"});
        ContainsKey({{"1", 1}}, {"2", "3"});
        ContainsKey({{"1", 1}, {"2", 2}}, {"2", "3"});
        ContainsKey({{"1", 1}, {"2", 2}}, {"3", "4"});
      },
      kDefaultWorkerThreads);
}

TEST(SegmentedDict, Update) {
  RunInCoro(
      [] {
        Update({}, {{"1", 1}, {"2", 2}, {"3", 3}});
        Update({{"1", 1}}, {{"1", 2}, {"2", 3}});
        Update({{"1", 1}}, {{"2", 2}, {"3", 3}});
        Update({{"1", 1}, {"2", 2}}, {{"2", 3}, {"3", 4}});
        Update({{"1", 1}, {"2", 2}}, {{"3", 3}, {"4", 4}});
      },
      kDefaultWorkerThreads);
}

TEST(SegmentedDict, InsertThenUpdate) {
  RunInCoro(
      [] {
        InsertThenUpdate({}, {{"1", 1}, {"2", 2}});
        InsertThenUpdate({{"1", 1}, {"2", 2}}, {{"3", 3}, {"4", 4}});
        InsertThenUpdate({{"1", 1}, {"2", 2}}, {{"2", 3}, {"3", 4}});
        InsertThenUpdate({{"1", 1}, {"2", 2}}, {{"1", 3}, {"2", 4}});
      },
      kDefaultWorkerThreads);
}

TEST(SegmentedDict, Insert) {
  RunInCoro(
      [] {
        Insert({}, {{"1", 1}, {"2", 2}});
        Insert({{"1", 1}, {"2", 2}}, {{"3", 3}, {"4", 4}});
        Insert({{"1", 1}, {"2", 2}}, {{"2", 3}, {"3", 4}});
        Insert({{"1", 1}, {"2", 2}}, {{"1", 3}, {"2", 4}});
      },
      kDefaultWorkerThreads);
}

TEST(SegmentedDict, Upsert) {
  RunInCoro(
      [] {
        Upsert({});
        Upsert({{"1", 1}});
        Upsert({{"1", 1}, {"1", 2}});
        Upsert({{"1", 1}, {"1", 2}, {"2", 1}});
        Upsert({{"1", 1}, {"2", 1}, {"2", 1}});
        Upsert({{"1", 1}, {"2", 1}, {"3", 1}});
      },
      kDefaultWorkerThreads);
}

TEST(SegmentedDict, UpsertMany) {
  RunInCoro(
      [] {
        UpsertMany({});
        UpsertMany({{"1", 1}});
        UpsertMany({{"1", 1}, {"1", 2}});
        UpsertMany({{"1", 1}, {"1", 2}, {"2", 1}});
        UpsertMany({{"1", 1}, {"2", 1}, {"2", 1}});
        UpsertMany({{"1", 1}, {"2", 1}, {"3", 1}});
      },
      kDefaultWorkerThreads);
}

TEST(SegmentedDict, GetSize) {
  RunInCoro(
      [] {
        GetSizeApprox({}, 0);
        GetSizeApprox({"1"}, 1);
        GetSizeApprox({"1", "1"}, 1);
        GetSizeApprox({"1", "1", "2"}, 2);
        GetSizeApprox({"1", "2", "2"}, 2);
        GetSizeApprox({"1", "1", "3"}, 2);
      },
      kDefaultWorkerThreads);
}

TEST(SegmentedDict, Erase) {
  RunInCoro(
      [] {
        Erase({"1"});
        Erase({"1", "2"});
        Erase({"1", "2", "3"});
      },
      kDefaultWorkerThreads);
}

TEST(SegmentedDict, ForEach) {
  RunInCoro(
      [] {
        ForEach({}, {});
        ForEach({{"1", 1}}, {});
        ForEach({{"1", 1}, {"2", 2}}, {{"1", 3}});
        ForEach({{"1", 1}, {"2", 2}, {"3", 3}}, {{"1", 4}, {"2", 5}, {"3", 6}});
      },
      kDefaultWorkerThreads);
}

TEST(SegmentedDict, ForEachConst) {
  RunInCoro(
      [] {
        ForEachConst({});
        ForEachConst({{"1", 1}});
        ForEachConst({{"1", 1}, {"1", 2}});
        ForEachConst({{"1", 1}, {"1", 2}, {"2", 1}});
        ForEachConst({{"1", 1}, {"2", 1}, {"2", 1}});
        ForEachConst({{"1", 1}, {"2", 1}, {"3", 1}});
      },
      kDefaultWorkerThreads);
}

TEST(SegmentedDict, EraseIf) {
  RunInCoro(
      [] {
        EraseIf({{"1", 15}, {"2", 20}, {"3", 25}},
                [](const auto& x) { return x.second < 20; });

        EraseIf({{"1", 15}, {"2", 20}, {"3", 25}},
                [](const auto& x) { return x.second < 15; });

        EraseIf({{"1", 15}, {"2", 20}, {"3", 25}},
                [](const auto& x) { return x.second > 25; });
      },
      kDefaultWorkerThreads);
}
