#include <userver/utest/utest.hpp>

#include <utils/get_ids_chunk.hpp>

namespace eats_restapp_places::utils {

std::vector<int64_t> place_ids = {6, 3, 2, 5, 1};

TEST(GetIdsChunk, return_ids_from_beginning_of_place_ids) {
  auto [place_begin, place_end] = GetIdsChunk(place_ids, 0, 2);
  std::vector<int64_t> result_place_ids(place_begin, place_end);
  std::vector<int64_t> expected_place_ids = {1, 2};
  ASSERT_EQ(result_place_ids, expected_place_ids);
}

TEST(GetIdsChunk, return_all_ids_if_limit_is_more_than_number_of_place_ids) {
  auto [place_begin, place_end] = GetIdsChunk(place_ids, 0, 10);
  std::vector<int64_t> result_place_ids(place_begin, place_end);
  std::vector<int64_t> expected_place_ids = {1, 2, 3, 5, 6};
  ASSERT_EQ(result_place_ids, expected_place_ids);
}

TEST(GetIdsChunk, return_ids_from_middle_of_place_ids) {
  auto [place_begin, place_end] = GetIdsChunk(place_ids, 3, 2);
  std::vector<int64_t> result_place_ids(place_begin, place_end);
  std::vector<int64_t> expected_place_ids = {5, 6};
  ASSERT_EQ(result_place_ids, expected_place_ids);
}

TEST(GetIdsChunk, return_fewer_ids_if_limit_is_out_of_place_ids) {
  auto [place_begin, place_end] = GetIdsChunk(place_ids, 3, 3);
  std::vector<int64_t> result_place_ids(place_begin, place_end);
  std::vector<int64_t> expected_place_ids = {5, 6};
  ASSERT_EQ(result_place_ids, expected_place_ids);
}

TEST(GetIdsChunk, throw_exception_for_invalid_cursor) {
  EXPECT_THROW(GetIdsChunk(place_ids, 6, 1), InvalidCursorError);
}

TEST(GetIdsChunk, return_empty_list_for_zero_limit) {
  auto [place_begin, place_end] = GetIdsChunk(place_ids, 4, 0);
  std::vector<int64_t> result_place_ids(place_begin, place_end);
  ASSERT_EQ(result_place_ids.empty(), true);
}

}  // namespace eats_restapp_places::utils
