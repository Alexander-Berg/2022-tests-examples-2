#include "gziphelper.hpp"

#include <gtest/gtest.h>

TEST(GzipHelper, Old) {
  std::string buf;
  for (int i = 0; i < 1000; ++i) buf.append(std::to_string(i));

  const std::string& comp = gzip::compress(buf);
  EXPECT_GT(buf.size(), comp.size());

  gzip::Buffer out;
  gzip::decompress(comp, out);
  EXPECT_EQ(buf, std::string(out.begin(), out.end()));
}

TEST(GzipHelper, New) {
  std::string buf;
  for (int i = 0; i < 1000; ++i) buf.append(std::to_string(i));

  const std::string& comp = gzip::Compress(buf);
  EXPECT_GT(buf.size(), comp.size());

  EXPECT_EQ(buf, gzip::Decompress(comp));
}
