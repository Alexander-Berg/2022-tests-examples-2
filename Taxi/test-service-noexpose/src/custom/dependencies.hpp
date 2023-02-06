#pragma once

#include <memory>

#include <userver/components/component_fwd.hpp>

namespace custom {

class Dependencies {
 public:
  Dependencies(const components::ComponentConfig&,
               const components::ComponentContext&);

  struct Extra {
    // Add your data here
  };

  Extra GetExtra() const;

 private:
};

}  // namespace custom
