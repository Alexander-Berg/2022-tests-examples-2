#include <chrono>
#include <string>
#include <vector>

#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

#include <models/yt_feedback.hpp>

namespace eprm = eats_place_rating::models;

namespace eats_place_rating::models::feedback_report {
std::vector<std::string> GetTableNames(const std::string& start,
                                       const std::string& finish);

bool CheckFilter(
    const Feedback& feedback,
    const std::unordered_set<std::int32_t>& predefined_comments_set,
    const std::unordered_set<std::int32_t>& ratings_set,
    const std::unordered_set<std::int32_t>& place_ids_set);

std::chrono::system_clock::time_point DateTimeFromYt(
    const std::string& datetime);
}  // namespace eats_place_rating::models::feedback_report

namespace {
//содержимое поля doc
std::string doc = {R"({
    "comment": null,
    "comment_status": null,
    "contact_requested": false,
    "created_at": {
      "$attributes": {
        "raw_type": "datetime"
      },
      "$value": "2021-01-01T02:25:29"
    },
    "ext_info": "wpe",
    "feedback_filled_at": {
      "$attributes": {
        "raw_type": "datetime"
      },
      "$value": "2021-01-01T03:17:25"
    },
    "fraud_skip": false,
    "id": 310017530,
    "manual_skip": false,
    "notification_sent_at": null,
    "order_nr": "210101-192600",
    "place_id": "327325",
    "predefined_comment_ids": [
    13,
    15,
    17,
    19
    ],
    "predefined_comments_skip": false,
    "rating": 5,
    "status": 5,
    "updated_at": {
      "$attributes": {
        "raw_type": "datetime"
      },
      "$value": "2021-04-22T18:08:26.967184"
    }
})"};

//поля в json с нужными данными
const std::string kPredefinedCommentsIds = "predefined_comment_ids";
const std::string kRating = "rating";
const std::string kPlaceId = "place_id";
const std::string kOrderNr = "order_nr";
const std::string kCustomComment = "comment";

const std::string kDateFormat = "%Y-%m-%d";
const std::string kDefaultTimezone = "UTC";

std::string TimePointAsString(std::chrono::system_clock::time_point time) {
  std::time_t now_c = std::chrono::system_clock::to_time_t(time);
  auto tm = std::gmtime(&now_c);
  char buffer[32];
  std::strftime(buffer, 32, "%Y-%m-%d %H:%M:%S", tm);
  return std::string(buffer);
}

std::chrono::system_clock::time_point StringToDateTime(const std::string& s) {
  return ::utils::datetime::Stringtime(s, kDefaultTimezone,
                                       "%Y-%m-%d %H:%M:%S");
}

void InnerHandle(
    const formats::json::Value& info,
    const std::unordered_set<std::int32_t>& predefined_comments_set,
    const std::unordered_set<std::int32_t>& ratings_set,
    const std::unordered_set<std::int32_t>& place_ids_set,
    std::vector<eats_place_rating::models::feedback_report::Feedback>&
        feedbacks) {
  //для перевода строки в std::chrono::system_clock::time_point
  auto StringToTimePoint = [](const std::string s) {
    return ::utils::datetime::Stringtime(s, "UTC", "%Y-%m-%d %H:%M:%S");
  };
  auto comments_ids =
      info[kPredefinedCommentsIds].As<std::vector<std::int32_t>>();
  auto rating = info[kRating].As<std::int32_t>();
  std::int32_t place_id = std::stoul(info[kPlaceId].As<std::string>());
  auto comment = info[kCustomComment].IsString()
                     ? info[kCustomComment].As<std::string>()
                     : "";
  auto order =
      info[kOrderNr].IsString() ? info[kOrderNr].As<std::string>() : "";
  eats_place_rating::models::feedback_report::Feedback feedback = {
      place_id,
      std::move(order),
      rating,
      std::move(comment),
      StringToTimePoint("2020-12-09 12:35:34"),
      std::move(comments_ids)};
  if (eprm::feedback_report::CheckFilter(feedback, predefined_comments_set,
                                         ratings_set, place_ids_set))
    feedbacks.push_back(std::move(feedback));
}
eats_place_rating::models::feedback_report::FeedbacksReportFilter test_filter{
    std::vector<std::int32_t>{12, 13, 14, 15, 16, 17, 18, 19},
    std::vector<std::int32_t>{1, 2, 3, 4, 5}, std::vector<std::int32_t>{327325},
    utils::datetime::Stringtime("2020-12-30 00:00:00", "UTC",
                                "%Y-%m-%d %H:%M:%S"),
    utils::datetime::Stringtime("2021-02-01 00:00:00", "UTC",
                                "%Y-%m-%d %H:%M:%S")};
}  // namespace

TEST(TimePointAsString, Check) {
  std::chrono::system_clock::time_point tp =
      StringToDateTime("2020-12-09 12:35:34");
  ASSERT_EQ(TimePointAsString(tp), "2020-12-09 12:35:34");
}

TEST(GetTableNames, OneYear) {
  auto start = "2020-12-09 12:35:34", finish = "2020-12-25 12:35:34";
  std::vector<std::string> correct_answer{"2020"};
  std::vector<std::string> check =
      eprm::feedback_report::GetTableNames(start, finish);
  ASSERT_EQ(check.size(), correct_answer.size());
  for (unsigned long i = 0; i < check.size(); ++i)
    ASSERT_EQ(check[i], correct_answer[i]);
}

TEST(GetTableNames, TwoYear) {
  auto start = "2020-12-09 12:35:34", finish = "2021-12-25 12:35:34";
  std::vector<std::string> correct_answer{"2020", "2021"};
  std::vector<std::string> check =
      eprm::feedback_report::GetTableNames(start, finish);
  ASSERT_EQ(check.size(), correct_answer.size());
  for (unsigned long i = 0; i < check.size(); ++i)
    ASSERT_EQ(check[i], correct_answer[i]);
}

TEST(GetTableNames, ThreeYear) {
  auto start = "2020-12-09 12:35:34", finish = "2022-12-25 12:35:34";
  std::vector<std::string> correct_answer{"2020", "2021", "2022"};
  std::vector<std::string> check =
      eprm::feedback_report::GetTableNames(start, finish);
  ASSERT_EQ(check.size(), correct_answer.size());
  for (unsigned long i = 0; i < check.size(); ++i)
    ASSERT_EQ(check[i], correct_answer[i]);
}

TEST(GetFieldsFromJson, ParseJsonArray) {
  auto info = formats::json::FromString(doc);
  ASSERT_TRUE(info["predefined_comment_ids"].IsArray());
  auto comments =
      info["predefined_comment_ids"].As<std::vector<std::int32_t>>();
  ASSERT_EQ(comments[0], 13);
}

TEST(GetFieldsFromJson, ParseJsonString) {
  auto info = formats::json::FromString(doc);
  ASSERT_TRUE(info[kPlaceId].IsString());
  auto s = std::stoul(info[kPlaceId].As<std::string>());
  ASSERT_EQ(s, 327325);
}

TEST(Handle, HandlingTableValues) {
  std::vector<eats_place_rating::models::feedback_report::Feedback> feedbacks;
  std::unordered_set<std::int32_t> predefined_comments_set(
      test_filter.predefined_comment_ids.begin(),
      test_filter.predefined_comment_ids.end()),
      ratings_set(test_filter.ratings.begin(), test_filter.ratings.end()),
      place_ids_set(test_filter.place_ids.begin(), test_filter.place_ids.end());
  InnerHandle(formats::json::FromString(doc), predefined_comments_set,
              ratings_set, place_ids_set, feedbacks);
  ASSERT_EQ(feedbacks[0].place_id, 327325);
}

TEST(TimeFormats, StringToDate) {
  auto date = eprm::feedback_report::DateTimeFromYt("2022-12-25 12:35:34");
  ASSERT_EQ(::utils::datetime::Timestring(date, kDefaultTimezone, kDateFormat),
            "2022-12-25");

  date = eprm::feedback_report::DateTimeFromYt("2022-12-25T12:35:34");
  ASSERT_EQ(::utils::datetime::Timestring(date, kDefaultTimezone, kDateFormat),
            "2022-12-25");

  date = eprm::feedback_report::DateTimeFromYt("2022-12-25T12:35:34.203870");
  ASSERT_EQ(::utils::datetime::Timestring(date, kDefaultTimezone, kDateFormat),
            "2022-12-25");
}
