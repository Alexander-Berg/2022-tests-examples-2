#include <gtest/gtest.h>

#include <ml/eats/places_ranking/api/v2.hpp>
#include <ml/eats/places_ranking/common/catalog_builder.hpp>

#include "common/utils.hpp"

namespace {
namespace ranking_api = ml::eats::places_ranking::api::v2;
}  // namespace

// Make sure that it compiles
void DeduplicateBrands(const ranking_api::Request& ml_request,
                       ranking_api::Response* ml_response) {
  ranking_api::DeduplicateBrands(
      ml_request, ml_response,
      [](const ranking_api::Place& lhs, const ranking_api::Place& rhs) {
        return &lhs < &rhs;
      });
}
