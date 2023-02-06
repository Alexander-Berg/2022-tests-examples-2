#include <gmock/gmock.h>
#include <clients/route_info.hpp>

class MockRouteInfo : public clients::routing::RouteInfoEx {
 public:
  MOCK_CONST_METHOD0(GetTotalTime, double());
  MOCK_CONST_METHOD0(GetTotalDistance, double());
  MOCK_CONST_METHOD0(GetWaypoints, movement_t());
  MOCK_CONST_METHOD0(GetRawPath, path_t());
  MOCK_CONST_METHOD0(GetMovement, movement_t());
  MOCK_CONST_METHOD0(GetExpirations, expirations_t());
};
