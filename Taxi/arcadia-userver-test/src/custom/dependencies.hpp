#pragma once

#include <memory>

#include <userver/components/component_fwd.hpp>
#include <ytlib/ytlib_component.hpp>

namespace custom {

class Dependencies {
 public:
  Dependencies(const components::ComponentConfig&,
               const components::ComponentContext&);

  struct Extra {
    // Add your data here
    ytlib::component::YtLib& ytlib;
  };

  Extra GetExtra() const;

 private:
  ytlib::component::YtLib& ytlib_;
};

}  // namespace custom
