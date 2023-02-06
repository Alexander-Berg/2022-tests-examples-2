#include <gtest/gtest.h>

#include <cimg/cimg.hpp>

TEST(CImg, CreateAndIterate) {
  cimg_library::CImg<int8_t> img{4, 4, 1, 1, 100.};
  cimg_for2Y(img, y) {
    cimg_forX(img, x) {
      int8_t value = img(x, y);
      ASSERT_EQ(value, 100);
    }
  }
}

TEST(CImg, Draw) {
  auto kDefaultColor = 100.;
  cimg_library::CImg<int8_t> img{4, 4, 1, 1, kDefaultColor};
  const int8_t line_color[] = {0};
  const int8_t point_color[] = {1};
  img.draw_line(0, 2, 3, 2, line_color);
  img.draw_point(2, 2, point_color);
  cimg_for2Y(img, y) {
    cimg_forX(img, x) {
      int8_t value = img(x, y);
      if (x == 2 && y == 2) {
        ASSERT_EQ(value, *point_color);
      } else if (y == 2) {
        ASSERT_EQ(value, *line_color);
      } else {
        ASSERT_EQ(value, kDefaultColor);
      }
    }
  }
}
