#include "serializer_test_helper.hpp"

namespace serializer_test_helper {

bool SerializerTestHelper::Compare(
    const predicate_evaluator::PredicateCPtr& first_ptr,
    const predicate_evaluator::PredicateCPtr& second_ptr) {
  UASSERT_MSG(*first_ptr == *second_ptr, "different predicates");
  return true;
};

bool SerializerTestHelper::Compare(
    const predicate_evaluator::KwargData& first,
    const predicate_evaluator::KwargData& second) {
  UASSERT_MSG(first.value == second.value, "different kwarg's values");
  UASSERT_MSG(first.index == second.index, "different kwarg's indexable flags");
  return true;
};

bool SerializerTestHelper::Compare(
    const blocklist_client::models::BlockPtr& first_ptr,
    const blocklist_client::models::BlockPtr& second_ptr) {
  bool result = true;
  const auto& first_block = *first_ptr;
  const auto& second_block = *second_ptr;
  // compare blocks
  UASSERT_MSG(first_block.predicate_id == second_block.predicate_id,
              "different predicate_ids");
  UASSERT_MSG(first_block.id == second_block.id, "different block_ids");

  // compare blocks kwargs
  const auto& first_kwargs = first_block.kwargs;
  const auto& second_kwargs = second_block.kwargs;
  result &= Compare(first_kwargs, second_kwargs);

  return result;
};

bool SerializerTestHelper::CompareCaches(const CacheType& first,
                                         const CacheType& second) {
  bool result = true;
  result &= first.last_known_revision_ == second.last_known_revision_;
  result &= CompareEvaluators(first.predicate_evaluator_,
                              second.predicate_evaluator_);
  result &= CompareBlocksIndex(first.blocks_index_, second.blocks_index_);
  result &= CompareBlocks(first.blocks_, second.blocks_);

  return result;
}

bool SerializerTestHelper::CompareEvaluators(
    const predicate_evaluator::PredicateEvaluator& first,
    const predicate_evaluator::PredicateEvaluator& second) {
  bool result = true;
  result &= Compare(first.predicates_, second.predicates_);
  return result;
}

bool SerializerTestHelper::CompareBlocksIndex(const BlocksIndex& first,
                                              const BlocksIndex& second) {
  bool result = true;
  result &= Compare(first, second);
  return result;
}

bool SerializerTestHelper::CompareBlocks(const Blocks& first,
                                         const Blocks& second) {
  bool result = true;
  result &= Compare(first, second);
  return result;
}

}  // namespace serializer_test_helper
