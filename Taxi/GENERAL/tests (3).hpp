#include <defs/all_definitions.hpp>
#include <handlers/dependencies.hpp>
#include <optional>

namespace persey_labs::utils {

std::optional<handlers::TestType> GetTestById(
    const std::string& id, const handlers::Dependencies& deps);

std::optional<handlers::TestPrice> GetTestPrice(
    const std::string& id, const std::string& lab_entity_id,
    std::int32_t locality_id, const handlers::Dependencies& deps);

std::vector<handlers::TestType> GetTests(const handlers::Dependencies& deps);

}  // namespace persey_labs::utils
