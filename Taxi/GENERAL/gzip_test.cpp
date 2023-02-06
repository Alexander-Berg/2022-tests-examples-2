#include <gtest/gtest.h>

#include <sstream>

#include <gzip/gzip.hpp>

TEST(GzipHelper, Stream) {
  std::stringstream is;
  for (int i = 0; i < 1000; ++i) is << i;
  std::string orig = is.str();
  std::stringstream os;
  gzip::Compress(is, os);
  std::string comp = os.str();
  EXPECT_GT(orig.size(), comp.size());

  is.str("");
  gzip::Decompress(os, is);
  std::string decomp = is.str();
  EXPECT_EQ(orig, decomp);
}

TEST(GzipHelper, Buffer) {
  std::string buf;
  for (int i = 0; i < 1000; ++i) buf.append(std::to_string(i));

  const std::string& comp = gzip::Compress(buf);
  EXPECT_GT(buf.size(), comp.size());

  EXPECT_EQ(buf, gzip::Decompress(comp));
}
