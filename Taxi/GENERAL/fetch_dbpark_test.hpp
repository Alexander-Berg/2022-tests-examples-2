#pragma once

#include "fetch_dbpark.hpp"

namespace candidates::filters::infrastructure::test {

inline void SetClid(Context& context, std::string clid) {
  auto park = std::make_shared<::models::DbPark>();
  park->dbid = "dbid";
  park->clid = std::move(clid);
  park->city = "city";
  FetchDbPark::Set(context, std::move(park));
}

}  // namespace candidates::filters::infrastructure::test
