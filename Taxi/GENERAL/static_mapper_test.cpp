#include "static_mapper.hpp"

#include <algorithm>
#include <functional>
#include <thread>
#include <unordered_set>
#include <vector>

#include <gtest/gtest.h>

namespace {

constexpr uint16_t kMapperSize = 2048;

struct Mapper1 : utils::SingletonMapperCRTP<Mapper1, kMapperSize> {
  constexpr static const char* kTag = "ConcurrentFill";
};

struct Mapper2 : utils::SingletonMapperCRTP<Mapper2, kMapperSize> {
  constexpr static const char* kTag = "ImplicitFillViaValue";
};

struct Mapper3 : utils::SingletonMapperCRTP<Mapper3, kMapperSize> {
  constexpr static const char* kTag = "ImplicitFillViaValueByForwardCtor1";
};

struct Mapper4 : utils::SingletonMapperCRTP<Mapper4, kMapperSize> {
  constexpr static const char* kTag = "ImplicitFillViaValueByForwardCtor2";
};

template <typename Mapper>
void FillAndCheckMapper(
    std::function<typename Mapper::Value(const std::string&)> fill_fn) {
  // Prepare data to concurrently insert into mapper
  const size_t workers_cnt = std::max(std::thread::hardware_concurrency(), 4u);
  std::vector<std::vector<std::string>> workers_keys(workers_cnt);
  {
    const size_t key_per_worker = kMapperSize / workers_cnt;
    for (size_t i = 0; i != workers_cnt - 1; ++i) {
      for (size_t j = 0; j != key_per_worker; ++j) {
        workers_keys[i].emplace_back(std::to_string(i * key_per_worker + j));
      }
    }
    for (size_t i = key_per_worker * (workers_cnt - 1); i != kMapperSize; ++i)
      workers_keys.back().emplace_back(std::to_string(i));
  }

  // we are to be insert into mapper its full capacity
  std::unordered_set<std::string> all_keys;
  for (const auto& v : workers_keys) {
    for (const auto& k : v) all_keys.insert(k);
  }
  EXPECT_EQ(all_keys.size(), kMapperSize);

  // insert by workers
  std::vector<std::thread> workers;
  workers.reserve(workers_cnt);
  for (size_t i = 0; i != workers_cnt; ++i) {
    workers.emplace_back([i, &workers_keys, &fill_fn]() {
      for (const auto& k : workers_keys[i]) fill_fn(k);
    });
  }
  for (auto& w : workers) w.join();

  EXPECT_EQ(Mapper::GetSize(), kMapperSize);

  const std::vector<typename Mapper::Value> mapped_vals = Mapper::GetValues();
  EXPECT_EQ(kMapperSize, mapped_vals.size());

  for (const auto& v : mapped_vals) {
    EXPECT_EQ(1u, all_keys.count(v.Get()));
    all_keys.erase(v.Get());

    const std::string another_key = v.Get();
    auto another_val = Mapper::GetOrCreate(another_key);
    EXPECT_EQ(another_val, v);
  }
}

template <typename Mapper>
void CheckMapper(
    std::function<typename Mapper::Value(const std::string&)> fill_fn) {
  // fill empty mapper
  EXPECT_EQ(Mapper::GetSize(), 0);
  FillAndCheckMapper<Mapper>(fill_fn);

  EXPECT_EQ(Mapper::GetSize(), kMapperSize);
  EXPECT_THROW(Mapper::GetOrCreate(std::to_string(kMapperSize + 1)),
               std::length_error);

  // try to fill same values
  EXPECT_NO_THROW(FillAndCheckMapper<Mapper>(fill_fn));
}

}  // namespace

TEST(StaticMapper, ConcurrentFill) {
  CheckMapper<Mapper1>([](const std::string& k) -> Mapper1::Value {
    return Mapper1::GetOrCreate(k);
  });
}

TEST(StaticMapper, ImplicitFillViaValue) {
  CheckMapper<Mapper2>(
      [](const std::string& k) -> Mapper2::Value { return Mapper2::Value{k}; });
}

TEST(StaticMapper, ImplicitFillViaValueByForwardCtor1) {
  CheckMapper<Mapper3>(
      [](const std::string& k) -> Mapper3::Value { return k; });
}

TEST(StaticMapper, ImplicitFillViaValueByForwardCtor2) {
  CheckMapper<Mapper4>(
      [](const std::string& k) -> Mapper4::Value { return k.c_str(); });
}
