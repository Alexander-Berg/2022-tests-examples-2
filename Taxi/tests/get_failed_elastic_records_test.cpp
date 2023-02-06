#include "elastic/get_failed_records.hpp"

#include <gtest/gtest.h>

namespace {

constexpr char insert_data[] =
    R"({"index":{"_index":"test","_type":"_doc","_id":"1"}})"
    "\n"
    R"({"field1":"value1"})"
    "\n"

    R"({"index":{"_index":"test","_type":"_doc","_id":"2"}})"
    "\n"
    R"({"field22":"value22"})"
    "\n"

    R"({"index":{"_index":"test","_type":"_doc","_id":"3"}})"
    "\n"
    R"({"field333":"value333"})"
    "\n"

    R"({"index":{"_index":"test","_type":"_doc","_id":"4"}})"
    "\n"
    R"({"field4444":"value4444"})"
    "\n"

    R"({"index":{"_index":"test","_type":"_doc","_id":"5"}})"
    "\n"
    R"({"field55555":"value55555"})"
    "\n";

const char success_record[] = R"(
    "_index":"testing-pilorama",
    "_type":"log",
    "_id":"AWc7qdDTnHgqRqNatypN",
    "_version":1,
    "_shards":{"total":1,"successful":1,"failed":0},
    "status":201
)";

const char failure_record[] = R"(
    "_index":"test",
    "_type":"log",
    "_id":"AWc7qwqonHgqRqNavhCm",
    "status":429,
    "error":{
      "type":"es_rejected_execution_exception",
      "reason":"rejected execution"
    }
)";

std::string MakeElasticRecords(std::initializer_list<bool> successes,
                               const std::string& entry_type = "create") {
  std::string result;

  const bool failed_at_least_one = std::any_of(
      successes.begin(), successes.end(), [](bool suc) { return !suc; });
  if (failed_at_least_one) {
    result += R"({"took":696,"errors":true,"items":[)";
  }  // namespace
  else {
    result += R"({"took":696,"errors":false,"items":[)";
  }

  bool first_entry = true;
  for (bool b : successes) {
    if (first_entry) {
      first_entry = false;
    } else {
      result += ',';
    }

    result += "{\"" + entry_type + "\":{";
    if (b) {
      result += success_record;
    } else {
      result += failure_record;
    }
    result += "}}";
  }

  result += "]}";
  return result;
}

struct data_t {
  const char* const name;
  const std::string elastic_answer;
  const char* const ethalon;
};

inline std::string PrintToString(const data_t& d) { return d.name; }

using TestData = std::initializer_list<data_t>;

}  // namespace

////////////////////////////////////////////////////////////////////////////////

class FailedElasticRecords : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, FailedElasticRecords,
    ::testing::ValuesIn(TestData{
        {"failed_none", MakeElasticRecords({true, true, true, true, true}), ""},

        {"failed_1",

         MakeElasticRecords({false, true, true, true, true}),

         R"({"index":{"_index":"test","_type":"_doc","_id":"1"}})"
         "\n"
         R"({"field1":"value1"})"
         "\n"},

        {"failed_2_index",

         MakeElasticRecords({true, false, true, true, true}, "index"),

         R"({"index":{"_index":"test","_type":"_doc","_id":"2"}})"
         "\n"
         R"({"field22":"value22"})"
         "\n"},

        {"failed_2",

         MakeElasticRecords({true, false, true, true, true}),

         R"({"index":{"_index":"test","_type":"_doc","_id":"2"}})"
         "\n"
         R"({"field22":"value22"})"
         "\n"},

        {"failed_5",

         MakeElasticRecords({true, true, true, true, false}),

         R"({"index":{"_index":"test","_type":"_doc","_id":"5"}})"
         "\n"
         R"({"field55555":"value55555"})"
         "\n"},

        {"failed_1_5",

         MakeElasticRecords({false, true, true, true, false}),

         R"({"index":{"_index":"test","_type":"_doc","_id":"1"}})"
         "\n"
         R"({"field1":"value1"})"
         "\n"
         R"({"index":{"_index":"test","_type":"_doc","_id":"5"}})"
         "\n"
         R"({"field55555":"value55555"})"
         "\n"},

        {"failed_1_2",

         MakeElasticRecords({false, false, true, true, true}),

         R"({"index":{"_index":"test","_type":"_doc","_id":"1"}})"
         "\n"
         R"({"field1":"value1"})"
         "\n"
         R"({"index":{"_index":"test","_type":"_doc","_id":"2"}})"
         "\n"
         R"({"field22":"value22"})"
         "\n"},

        {"failed_4_5",

         MakeElasticRecords({true, true, true, false, false}),

         R"({"index":{"_index":"test","_type":"_doc","_id":"4"}})"
         "\n"
         R"({"field4444":"value4444"})"
         "\n"
         R"({"index":{"_index":"test","_type":"_doc","_id":"5"}})"
         "\n"
         R"({"field55555":"value55555"})"
         "\n"},

        {"failed_all", MakeElasticRecords({false, false, false, false, false}),
         insert_data},

        {"failed_empty_elastic_record", "", insert_data},

        {"failed_broken_elastic_record", MakeElasticRecords({}), insert_data},

        {"failed_missing_last_elastic_record",
         MakeElasticRecords({true, true, true, true}),
         R"({"index":{"_index":"test","_type":"_doc","_id":"5"}})"
         "\n"
         R"({"field55555":"value55555"})"
         "\n"},

        {"failed_too_many_elastic_records",
         MakeElasticRecords({true, true, true, true, true, true}), ""},

        {"failed_json_broken",
         "BREAKING{JSON}}" + MakeElasticRecords({true, true, true, true, true}),
         insert_data},
    }),
    ::testing::PrintToStringParamName());

TEST_P(FailedElasticRecords, Basic) {
  auto d = GetParam();
  std::string data = insert_data;
  data = pilorama::elastic::GetFailedRecords(std::move(data), d.elastic_answer);
  EXPECT_EQ(data, d.ethalon);
}

TEST(FailedElastic, EmptyResponse) {
  std::string data = insert_data;
  data = pilorama::elastic::GetFailedRecords(std::move(data), "");
  EXPECT_EQ(data, insert_data);
}

TEST(FailedElastic, NonJsonResponse) {
  std::string data = insert_data;
  data = pilorama::elastic::GetFailedRecords(std::move(data), "Internal error");
  EXPECT_EQ(data, insert_data);
}
