#include <geobus/channels/signal_v2/signal_v2.hpp>
#include <geobus/channels/signal_v2/signal_v2_generator.hpp>
#include <lowlevel/fb_serialization_test.hpp>
#include "test_traits.hpp"

#include <gtest/gtest.h>

namespace geobus::lowlevel {

namespace signal_v2 {

INSTANTIATE_TYPED_TEST_SUITE_P(SignalV2SerializationTest,
                               FlatbuffersSerializationTest, types::SignalV2);

}
}  // namespace geobus::lowlevel
