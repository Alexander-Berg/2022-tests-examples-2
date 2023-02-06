#pragma once

#include <blocklist_client/models/blocklist_cache.hpp>

namespace serializer_test_helper {

using CacheType = blocklist_client::models::BlocklistCache;
using BlocksIndex = blocklist_client::models::BlocksIndex;
using Blocks = blocklist_client::models::Blocks;

class SerializerTestHelper {
 public:
  static bool CompareCaches(const CacheType& first, const CacheType& second);
  static bool CompareBlocksIndex(const BlocksIndex& first,
                                 const BlocksIndex& second);
  static bool CompareBlocks(const Blocks& first, const Blocks& second);
  static bool CompareEvaluators(
      const predicate_evaluator::PredicateEvaluator& first,
      const predicate_evaluator::PredicateEvaluator& second);

  // comparison help methods

  static bool Compare(const predicate_evaluator::PredicateCPtr& first_ptr,
                      const predicate_evaluator::PredicateCPtr& second_ptr);

  static bool Compare(const predicate_evaluator::KwargData& first,
                      const predicate_evaluator::KwargData& second);

  static bool Compare(const blocklist_client::models::BlockPtr& first_ptr,
                      const blocklist_client::models::BlockPtr& second_ptr);

  template <typename K, typename V>
  static bool Compare(const std::unordered_map<K, V>& first,
                      const std::unordered_map<K, V>& second) {
    bool result = true;

    UASSERT_MSG(first.size() == second.size(), "different elements number");

    for (const auto& [key, first_value] : first) {
      const auto it = second.find(key);

      UASSERT_MSG(it != second.end(), "different elements");

      result &= Compare(it->second, first_value);
    }

    return result;
  }

  template <typename T>
  static bool Compare(const utils::DummyCow<T>& first,
                      const utils::DummyCow<T>& second) {
    return Compare(*first, *second);
  }
};
}  // namespace serializer_test_helper
