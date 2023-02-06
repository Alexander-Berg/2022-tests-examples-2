#include <gtest/gtest.h>

#include <common/include/leaky_bucket.h>

using namespace maps::rate_limiter2;

using std::chrono::system_clock;

TEST(LeakyBucket, Ctor) {
  {
    LimitInfo info(0, 0);
    EXPECT_EQ(info.rate(), 0);
    EXPECT_EQ(info.burst(), 0);
    EXPECT_EQ(info.unit(), 1);
    EXPECT_TRUE(info.isForbidden());
  }
  {
    LimitInfo info(100, 200, 153);
    EXPECT_EQ(info.rate(), 100);
    EXPECT_EQ(info.burst(), 200);
    EXPECT_EQ(info.unit(), 153);
    EXPECT_FALSE(info.isForbidden());
  }

  // default is not forbidding
  EXPECT_FALSE(LimitInfo::UNDEFINED.isForbidden());
}

// Leaky Bucket algorithm tests

TEST(LeakyBucket, Rps) {
  auto limit = LimitInfo(2, 5);  // 2 requests per second, burst 5

  int64_t counter = 0;
  int64_t bucket = 0;  // bucket bottom

  system_clock::time_point now;

  for (int i = 0; i < 100; ++i) {  // 100 request attempts
    passLeakyBucket(limit, now, 1, counter, bucket);
  }
  EXPECT_EQ(counter, 5);  // expect +burst success

  now += std::chrono::seconds(1);

  for (int i = 0; i < 100; ++i) {  // 100 request attempts
    passLeakyBucket(limit, now, 1, counter, bucket);
  }
  EXPECT_EQ(counter, 7);

  now += std::chrono::seconds(1);

  for (int i = 0; i < 100; ++i) {  // 100 request attempts
    passLeakyBucket(limit, now, 1, counter, bucket);
  }
  EXPECT_EQ(counter, 9);  // 2 more success attempts

  now += std::chrono::seconds(10);  // meaning there where no requests for 10
                                    // sec - expect burst after that

  for (int i = 0; i < 100; ++i) {  // 100 request attempts
    passLeakyBucket(limit, now, 1, counter, bucket);
  }
  EXPECT_EQ(counter, 14);  // +burst
}

TEST(LeakyBucket, Rpm) {
  // 100 requests per minute, burst 20
  auto limit = LimitInfo(100, 20, 60);

  int64_t counter = 0;
  int64_t bucket = 0;  // bucket bottom

  system_clock::time_point now;

  for (int i = 0; i < 100; ++i) {  // 100 request attempts
    passLeakyBucket(limit, now, 1, counter, bucket);
  }
  EXPECT_EQ(counter, 20);  // expect burst success at start

  now += std::chrono::seconds(5);
  for (int i = 0; i < 100; ++i) {  // 100 request attempts
    passLeakyBucket(limit, now, 1, counter, bucket);
  }
  EXPECT_TRUE(counter > 20 && counter < 30);  // + 1/12 of limit

  now += std::chrono::seconds(15);
  for (int i = 0; i < 100; ++i) {  // 100 request attempts
    passLeakyBucket(limit, now, 1, counter, bucket);
  }
  EXPECT_TRUE(counter > 40 && counter < 50);  // + burst

  // constant load for 60sec
  for (auto start = now;
       std::chrono::duration_cast<std::chrono::seconds>(now - start).count() <
       60;
       now += std::chrono::seconds(1)) {
    for (int i = 0; i < 100; ++i) {  // 100 attempts
      passLeakyBucket(limit, now, 1, counter, bucket);
    }
  }
  EXPECT_TRUE(counter > 140 && counter < 150);

  now += std::chrono::seconds(30);
  auto nkeep = counter;
  for (int i = 0; i < 100; ++i) {  // 100 request attempts
    counter += passLeakyBucket(limit, now, 1, counter, bucket);
  }
  EXPECT_EQ(counter, nkeep + 20);  // +burst

  // constant load for 30sec
  for (auto start = now;
       std::chrono::duration_cast<std::chrono::seconds>(now - start).count() <
       30;
       now += std::chrono::seconds(1)) {
    for (int i = 0; i < 100; ++i) {  // 100 attempts
      passLeakyBucket(limit, now, 1, counter, bucket);
    }
  }
  EXPECT_TRUE(counter > 210 && counter < 220);  // gradual success count grow
}

TEST(LeakyBucket, Resize) {
  system_clock::time_point now = std::chrono::system_clock::now();

  int64_t counter = 0;
  int64_t bucket = 0;  // bucket bottom

  auto limit = LimitInfo(5, 5, 1);

  EXPECT_TRUE(passLeakyBucket(limit, now, 5, counter, bucket));
  EXPECT_FALSE(passLeakyBucket(limit, now, 5, counter, bucket));  // exceeded

  // increase limit
  auto oldLimit = limit;
  limit = LimitInfo(10, 10, 1);
  resizeLeakyBucket(oldLimit, limit, now, bucket);

  EXPECT_TRUE(passLeakyBucket(limit, now, 5, counter, bucket));
  EXPECT_FALSE(passLeakyBucket(limit, now, 5, counter, bucket));  // exceeded
  now += std::chrono::seconds(1);
  EXPECT_TRUE(passLeakyBucket(limit, now, 10, counter, bucket));
  EXPECT_FALSE(passLeakyBucket(limit, now, 1, counter, bucket));  // exceeded
  now += std::chrono::seconds(1);
  EXPECT_TRUE(passLeakyBucket(limit, now, 5, counter, bucket));

  // decrease limit
  oldLimit = limit;
  limit = LimitInfo(2, 2, 1);
  resizeLeakyBucket(oldLimit, limit, now, bucket);

  // exceeded for now + 2secs
  EXPECT_FALSE(passLeakyBucket(limit, now, 2, counter, bucket));  // exceeded
  now += std::chrono::seconds(1);
  EXPECT_FALSE(passLeakyBucket(limit, now, 2, counter, bucket));
  now += std::chrono::seconds(1);
  EXPECT_FALSE(passLeakyBucket(limit, now, 2, counter, bucket));

  // now ok
  now += std::chrono::seconds(1);
  EXPECT_TRUE(passLeakyBucket(limit, now, 2, counter, bucket));
}

TEST(LeakyBucket, DefaultLimitToSpecific) {
  int64_t counter = 0;
  int64_t bucket = 0;  // bucket bottom
  system_clock::time_point now = std::chrono::system_clock::now();

  EXPECT_TRUE(passLeakyBucket(LimitInfo::UNDEFINED, now, 100, counter, bucket));
  EXPECT_TRUE(passLeakyBucket(LimitInfo::UNDEFINED, now, 10, counter, bucket));

  // resize from default limit
  auto limitRPS = LimitInfo(100, 100, 1);
  resizeLeakyBucket(LimitInfo::UNDEFINED, limitRPS, now, bucket);
  // oops exceeded
  EXPECT_FALSE(passLeakyBucket(limitRPS, now, 1, counter, bucket));  // exceeded

  // but time passes and we good again
  now += std::chrono::seconds(1);
  EXPECT_TRUE(passLeakyBucket(limitRPS, now, 90, counter, bucket));
  // exceed
  EXPECT_FALSE(passLeakyBucket(limitRPS, now, 1, counter, bucket));
}

TEST(LeakyBucket, ToDefaultAndBack) {
  int64_t counter = 0;
  int64_t bucket = 0;  // bucket bottom
  system_clock::time_point now = std::chrono::system_clock::now();

  auto limitRPS = LimitInfo(100, 100, 1);
  EXPECT_TRUE(passLeakyBucket(limitRPS, now, 10, counter, bucket));
  counter += 1000000;  // huge delta out of the blue
  EXPECT_FALSE(passLeakyBucket(limitRPS, now, 1, counter, bucket));

  // resize to default limit
  resizeLeakyBucket(limitRPS, LimitInfo::UNDEFINED, now, bucket);
  // not exceeded now
  EXPECT_TRUE(passLeakyBucket(LimitInfo::UNDEFINED, now, 100, counter, bucket));

  // time passed
  now += std::chrono::seconds(1);
  EXPECT_TRUE(passLeakyBucket(LimitInfo::UNDEFINED, now, 10, counter, bucket));

  // resize back from default
  resizeLeakyBucket(LimitInfo::UNDEFINED, limitRPS, now, bucket);
  // expect not exceeded
  EXPECT_TRUE(passLeakyBucket(limitRPS, now, 80, counter, bucket));
}

TEST(LeakyBucket, SwitchRpsToRph) {
  int64_t counter = 0;
  int64_t bucket = 0;  // bucket bottom
  system_clock::time_point now(std::chrono::seconds(100500));

  auto limitRPS = LimitInfo(10, 10, 1);        // limit requests per second
  auto limitRPH = LimitInfo(10, 10, 60 * 60);  // limit requests per hour
  // start with RPS
  EXPECT_TRUE(passLeakyBucket(limitRPS, now, 10, counter, bucket));
  EXPECT_FALSE(passLeakyBucket(limitRPS, now, 1, counter, bucket));

  now += std::chrono::seconds(1);

  EXPECT_TRUE(passLeakyBucket(limitRPS, now, 10, counter, bucket));
  EXPECT_FALSE(passLeakyBucket(limitRPS, now, 1, counter, bucket));

  // switch to RPH
  resizeLeakyBucket(limitRPS, limitRPH, now, bucket);

  // reject since current rate exceeds new limit
  EXPECT_FALSE(passLeakyBucket(limitRPH, now, 1, counter, bucket));
  now += std::chrono::seconds(10);
  // reject - not enough time passed
  EXPECT_FALSE(passLeakyBucket(limitRPH, now, 1, counter, bucket));

  now += std::chrono::seconds(30 * 60);  // 1/2 of hour passed

  EXPECT_TRUE(passLeakyBucket(limitRPH, now, 5, counter, bucket));
  EXPECT_FALSE(passLeakyBucket(limitRPH, now, 1, counter, bucket));

  now += std::chrono::seconds(60 * 60);  // full hour passed

  EXPECT_TRUE(passLeakyBucket(limitRPH, now, 10, counter, bucket));
  EXPECT_FALSE(passLeakyBucket(limitRPH, now, 1, counter, bucket));

  // back to RPS
  resizeLeakyBucket(limitRPH, limitRPS, now, counter);

  // reject since current rate exceeds new limit
  EXPECT_FALSE(passLeakyBucket(limitRPS, now, 1, counter, bucket));

  now += std::chrono::seconds(1);

  EXPECT_TRUE(passLeakyBucket(limitRPS, now, 10, counter, bucket));
  EXPECT_FALSE(passLeakyBucket(limitRPS, now, 1, counter, bucket));

  now += std::chrono::seconds(1);

  EXPECT_TRUE(passLeakyBucket(limitRPS, now, 10, counter, bucket));
  EXPECT_FALSE(passLeakyBucket(limitRPS, now, 1, counter, bucket));
}

// limit selection tests

TEST(LeakyBucket, AccessLimiterSelectLimit) {
  LimitsRegistry registry(
      {{
           "super.client.1",
           {{"", LimitInfo(50000, 1000, 1)}},  // super-limit for client1
       },
       {"client.2",
        {{"resource.1", LimitInfo(1000, 1000, 1 * 60 * 60)},
         {"resource.2", LimitInfo(300, 300, 24 * 60 * 60)}}},
       {"client.3",
        {{"resource.2", LimitInfo(500, 500, 1)},
         {"resource.3", LimitInfo(555, 333, 60)}}},
       {"",
        {// 'anybody' limit
         {"resource.3", LimitInfo(100, 500, 1)}}}});

  {  // invalid case
    const auto& lim = registry.select("", "");
    EXPECT_TRUE(lim == LimitInfo::UNDEFINED);
  }

  {  // 'anybody' limit
    const auto& lim = registry.select("nonspecific.client", "resource.3");
    EXPECT_TRUE(lim == LimitInfo(100, 500, 1));
  }
  {  // limit not found
    const auto& lim = registry.select("nonspecific.client", "resource.2");
    EXPECT_TRUE(lim == LimitInfo::UNDEFINED);
  }
  {  // super limit
    const auto& limit = registry.select("super.client.1", "");
    EXPECT_TRUE(limit == LimitInfo(50000, 1000, 1));
  }
  {  // specific limit
    const auto& lim = registry.select("client.2", "resource.2");
    EXPECT_TRUE(lim == LimitInfo(300, 300, 24 * 60 * 60));
  }
  {  // specific limit priority
    const auto& lim = registry.select("client.3", "resource.3");
    EXPECT_TRUE(lim == LimitInfo(555, 333, 60));
  }
}
