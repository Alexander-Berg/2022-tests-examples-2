#include "httpclient/response.hpp"
#include <gtest/gtest.h>

TEST(Responce, UrlParamHiding) {
  // nothing to hide
  ASSERT_EQ(utils::http::hide_param_value("", ""), "");
  ASSERT_EQ(utils::http::hide_param_value("http://www.website.com/", ""),
            "http://www.website.com/");
  ASSERT_EQ(utils::http::hide_param_value(
                "http://www.website.com/?the_param=nosecret", ""),
            "http://www.website.com/?the_param=nosecret");
  ASSERT_EQ(
      utils::http::hide_param_value(
          "http://www.website.com/directory/?key=val&the_param=nosecret", ""),
      "http://www.website.com/directory/?key=val&the_param=nosecret");
  ASSERT_EQ(
      utils::http::hide_param_value(
          "http://www.website.com/?key=val#anchor&the_param=nosecret", ""),
      "http://www.website.com/?key=val#anchor&the_param=nosecret");

  // secret to hide
  ASSERT_EQ(
      utils::http::hide_param_value("http://www.website.com/", "the_param"),
      "http://www.website.com/");
  ASSERT_EQ(utils::http::hide_param_value("http://www.website.com/directory/",
                                          "the_param"),
            "http://www.website.com/directory/");
  ASSERT_EQ(utils::http::hide_param_value(
                "http://www.website.com/directory/file.filename", "the_param"),
            "http://www.website.com/directory/file.filename");
  ASSERT_EQ(utils::http::hide_param_value("http://www.website.com/?querystring",
                                          "the_param"),
            "http://www.website.com/?querystring");
  ASSERT_EQ(utils::http::hide_param_value(
                "http://www.website.com/?the_param=secret", "the_param"),
            "http://www.website.com/?the_param=HIDDEN");
  ASSERT_EQ(
      utils::http::hide_param_value(
          "http://www.website.com/directory/?the_param=secret", "the_param"),
      "http://www.website.com/directory/?the_param=HIDDEN");
  ASSERT_EQ(utils::http::hide_param_value(
                "http://www.website.com/directory/?key=val&the_param=secret",
                "the_param"),
            "http://www.website.com/directory/?key=val&the_param=HIDDEN");
  ASSERT_EQ(utils::http::hide_param_value(
                "http://www.website.com/?the_param=secret#anchor", "the_param"),
            "http://www.website.com/?the_param=HIDDEN#anchor");
  ASSERT_EQ(utils::http::hide_param_value(
                "http://www.website.com/?key=val&the_param=secret#anchor",
                "the_param"),
            "http://www.website.com/?key=val&the_param=HIDDEN#anchor");
  ASSERT_EQ(utils::http::hide_param_value(
                "http://www.website.com/?key=val#anchor&the_param=secret",
                "the_param"),
            "http://www.website.com/?key=val#anchor&the_param=HIDDEN");
}
