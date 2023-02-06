#include "tracker_requirements.hpp"

#include <gtest/gtest.h>

TEST(requirements, childchair_multi) {
  std::vector<models::ChildChairClassesSet> driver_childchair = {
      {2, 3}, {1}, {1, 2}};
  models::DriverRequirements drv_requirements;
  drv_requirements.AddChildChairs(driver_childchair);

  models::ClientRequirements c1;
  c1.Add("childchair", (short)1);
  c1.Add("childchair", (short)1);

  auto c2 = c1;
  c1.Add("childchair", (short)3);

  ASSERT_TRUE(drv_requirements.Provides(c1));
  c1.Add("childchair", (short)2);

  ASSERT_FALSE(drv_requirements.Provides(c1));

  c2.Add("childchair", (short)1);
  ASSERT_FALSE(drv_requirements.Provides(c2));

  models::ClientRequirements c3;
  c3.Add("childchair", (short)2);
  c3.Add("childchair", (short)3);
  ASSERT_TRUE(drv_requirements.Provides(c3));
  c3.Add("childchair", (short)1);
  ASSERT_TRUE(drv_requirements.Provides(c3));

  models::ClientRequirements c4;
  c4.Add("childchair", (short)3);
  c4.Add("childchair", (short)2);
  ASSERT_TRUE(drv_requirements.Provides(c4));
}
