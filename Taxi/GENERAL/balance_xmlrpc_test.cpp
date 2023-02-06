#include <gtest/gtest.h>

#include "balance_xmlrpc.hpp"

#include <optional>
#include <string>

struct A {
  int i;
  std::string str;
  std::vector<std::string> str_v;
  std::vector<int> int_v;
  std::optional<int> o_i;
  std::optional<std::string> o_str;
  std::optional<std::vector<std::string>> o_str_v;
  std::optional<std::vector<int>> o_int_v;
  std::optional<int> null_opt;
};

struct Contract {
  std::vector<int> services;
  int contract_id;
};

struct PersonFault {
  int fault_code;
  std::string fault_string;
};

namespace pugi {

void Fill(const xml_node& member, Contract& data) {
  if (member.child("name").child_value() == std::string("ID")) {
    data.contract_id =
        std::stoi(member.child("value").first_child().child_value());
    return;
  }
  if (member.child("name").child_value() == std::string("SERVICES")) {
    data.services = xmlrpc::response::Wrapper<std::vector<int>>::Parse(
        member.child("value").first_child());
    return;
  }
}

void Fill(const xml_node& member, PersonFault& data) {
  if (member.child("name").child_value() == std::string("faultCode")) {
    data.fault_code =
        std::stoi(member.child("value").first_child().child_value());
    return;
  }
  if (member.child("name").child_value() == std::string("faultString")) {
    data.fault_string = member.child("value").first_child().child_value();
    return;
  }
}
}  // namespace pugi

TEST(BalanceXMLRPC, Common) {
  static const std::string kExpected =
      "<methodCall><methodName>Balance.CreateClient</"
      "methodName><params><param><value><struct><member><name>client_id</"
      "name><value><i4>1</i4></value></member><member><name>some_field</"
      "name><value><string>str</string></value></member><member><name>vector</"
      "name><value><array><data><value><string>1</string></"
      "value><value><string>2</string></value><value><string>3</string></"
      "value></data></array></value></member><member><name>int_vector</"
      "name><value><array><data><value><i4>3</i4></value><value><i4>2</i4></"
      "value><value><i4>1</i4></value></data></array></value></"
      "member><member><name>opt_client_id</name><value><i4>1</i4></value></"
      "member><member><name>opt_some_field</name><value><string>str</string></"
      "value></member><member><name>opt_vector</"
      "name><value><array><data><value><string>1</string></"
      "value><value><string>2</string></value><value><string>3</string></"
      "value></data></array></value></member><member><name>opt_int_vector</"
      "name><value><array><data><value><i4>3</i4></value><value><i4>2</i4></"
      "value><value><i4>1</i4></value></data></array></value></member></"
      "struct></value></param></params></methodCall>";

  pugi::xml_document document;
  A a{1,       "str",          {"1", "2", "3"}, {3, 2, 1},   {123},
      {"321"}, {{"55", "66"}}, {{22, 33}},      std::nullopt};

  xmlrpc::Request balance_request("Balance.CreateClient");

  balance_request.AddParam(
      xmlrpc::Member{a.i, "client_id"}, xmlrpc::Member{a.str, "some_field"},
      xmlrpc::Member{a.str_v, "vector"}, xmlrpc::Member{a.int_v, "int_vector"},
      xmlrpc::Member{a.i, "opt_client_id"},
      xmlrpc::Member{a.str, "opt_some_field"},
      xmlrpc::Member{a.str_v, "opt_vector"},
      xmlrpc::Member{a.int_v, "opt_int_vector"},
      xmlrpc::Member{a.null_opt, "nullopt"});

  ASSERT_EQ(balance_request.ToString(), kExpected);
}

TEST(BalanceXMLRPC, ParseContracts) {
  static const std::string kResponse =
      "<?xml "
      "version='1.0'?>\\n<methodResponse>\\n<params>\\n<param>\\n<value><array>"
      "<data>\\n<value><struct>\\n<member>\\n<name>IS_FAXED</"
      "name>\\n<value><int>0</int></value>\\n</"
      "member>\\n<member>\\n<name>OFFER_ACCEPTED</name>\\n<value><int>0</int></"
      "value>\\n</member>\\n<member>\\n<name>COUNTRY</name>\\n<value><int>225</"
      "int></value>\\n</member>\\n<member>\\n<name>IS_SUSPENDED</"
      "name>\\n<value><int>0</int></value>\\n</"
      "member>\\n<member>\\n<name>IS_ACTIVE</name>\\n<value><int>1</int></"
      "value>\\n</member>\\n<member>\\n<name>IS_SIGNED</name>\\n<value><int>1</"
      "int></value>\\n</member>\\n<member>\\n<name>CONTRACT_TYPE</"
      "name>\\n<value><int>9</int></value>\\n</"
      "member>\\n<member>\\n<name>CURRENCY</name>\\n<value><string>RUR</"
      "string></value>\\n</member>\\n<member>\\n<name>FIRM_ID</"
      "name>\\n<value><int>130</int></value>\\n</"
      "member>\\n<member>\\n<name>SERVICES</"
      "name>\\n<value><array><data>\\n<value><int>1187</int></"
      "value>\\n<value><int>1188</int></value>\\n</data></array></value>\\n</"
      "member>\\n<member>\\n<name>PAYMENT_TYPE</name>\\n<value><int>2</int></"
      "value>\\n</member>\\n<member>\\n<name>PERSON_ID</"
      "name>\\n<value><int>22294577</int></value>\\n</"
      "member>\\n<member>\\n<name>IS_DEACTIVATED</name>\\n<value><int>0</int></"
      "value>\\n</member>\\n<member>\\n<name>DT</"
      "name>\\n<value><dateTime.iso8601>20220301T00:00:00</dateTime.iso8601></"
      "value>\\n</member>\\n<member>\\n<name>IS_CANCELLED</"
      "name>\\n<value><int>0</int></value>\\n</"
      "member>\\n<member>\\n<name>EXTERNAL_ID</name>\\n<value><string>5648808/"
      "22</string></value>\\n</member>\\n<member>\\n<name>ID</"
      "name>\\n<value><int>17923138</int></value>\\n</member>\\n</struct></"
      "value>\\n<value><struct>\\n<member>\\n<name>IS_FAXED</"
      "name>\\n<value><int>0</int></value>\\n</"
      "member>\\n<member>\\n<name>OFFER_ACCEPTED</name>\\n<value><int>0</int></"
      "value>\\n</member>\\n<member>\\n<name>COUNTRY</name>\\n<value><int>225</"
      "int></value>\\n</member>\\n<member>\\n<name>IS_SUSPENDED</"
      "name>\\n<value><int>0</int></value>\\n</"
      "member>\\n<member>\\n<name>IS_ACTIVE</name>\\n<value><int>1</int></"
      "value>\\n</member>\\n<member>\\n<name>IS_SIGNED</name>\\n<value><int>1</"
      "int></value>\\n</member>\\n<member>\\n<name>CONTRACT_TYPE</"
      "name>\\n<value><int>9</int></value>\\n</"
      "member>\\n<member>\\n<name>CURRENCY</name>\\n<value><string>RUR</"
      "string></value>\\n</member>\\n<member>\\n<name>FIRM_ID</"
      "name>\\n<value><int>130</int></value>\\n</"
      "member>\\n<member>\\n<name>SERVICES</"
      "name>\\n<value><array><data>\\n<value><int>1189</int></"
      "value>\\n<value><int>1191</int></value>\\n</data></array></value>\\n</"
      "member>\\n<member>\\n<name>PAYMENT_TYPE</name>\\n<value><int>2</int></"
      "value>\\n</member>\\n<member>\\n<name>PERSON_ID</"
      "name>\\n<value><int>22294577</int></value>\\n</"
      "member>\\n<member>\\n<name>IS_DEACTIVATED</name>\\n<value><int>0</int></"
      "value>\\n</member>\\n<member>\\n<name>DT</"
      "name>\\n<value><dateTime.iso8601>20220301T00:00:00</dateTime.iso8601></"
      "value>\\n</member>\\n<member>\\n<name>IS_CANCELLED</"
      "name>\\n<value><int>0</int></value>\\n</"
      "member>\\n<member>\\n<name>EXTERNAL_ID</name>\\n<value><string>5648811/"
      "22</string></value>\\n</member>\\n<member>\\n<name>ID</"
      "name>\\n<value><int>17923141</int></value>\\n</member>\\n</struct></"
      "value>\\n</data></array></value>\\n</param>\\n</params>\\n</"
      "methodResponse>\\n";

  xmlrpc::Response response(kResponse);
  auto contracts = response.GetParam<std::vector<Contract>>(0);
  ASSERT_EQ(contracts.size(), 2);
  ASSERT_EQ(contracts[0].contract_id, 17923138);
  ASSERT_EQ(contracts[0].services, std::vector<int>({1187, 1188}));
  ASSERT_EQ(contracts[1].contract_id, 17923141);
  ASSERT_EQ(contracts[1].services, std::vector<int>({1189, 1191}));
}

TEST(BalanceXMLRPC, ParseFault) {
  {
    static const std::string kResponse =
        "<methodResponse><fault><value><struct><member><name>faultCode</"
        "name><value><int>-1</int></value></member><member><name>faultString</"
        "name><value><string>&lt;error&gt;&lt;msg&gt;Email address "
        "\"editor@localhost\" is "
        "invalid&lt;/msg&gt;&lt;email&gt;editor@localhost&lt;/"
        "email&gt;&lt;wo-rollback&gt;0&lt;/"
        "wo-rollback&gt;&lt;method&gt;Balance.CreatePerson&lt;/"
        "method&gt;&lt;code&gt;WRONG_EMAIL&lt;/"
        "code&gt;&lt;parent-codes&gt;&lt;code&gt;INVALID_PARAM&lt;/"
        "code&gt;&lt;code&gt;EXCEPTION&lt;/code&gt;&lt;/"
        "parent-codes&gt;&lt;contents&gt;Email address \"editor@localhost\" is "
        "invalid&lt;/contents&gt;&lt;/error&gt;</string></value></member></"
        "struct></value></fault></methodResponse>";

    xmlrpc::Response response(kResponse);
    auto fault = response.GetFault<PersonFault>();
    ASSERT_EQ(fault.fault_code, -1);
    ASSERT_EQ(
        fault.fault_string,
        "<error><msg>Email address \"editor@localhost\" is "
        "invalid</msg><email>editor@localhost</email><wo-rollback>0</"
        "wo-rollback><method>Balance.CreatePerson</method><code>WRONG_EMAIL</"
        "code><parent-codes><code>INVALID_PARAM</code><code>EXCEPTION</code></"
        "parent-codes><contents>Email address \"editor@localhost\" is "
        "invalid</contents></error>");
  }
  {
    static const std::string kResponse =
        "<methodResponse><fault><value><struct><member><name>faultCode</"
        "name><value><int>-1</int></value></member><member><name>faultString</"
        "name><value><string>&lt;error&gt;&lt;msg&gt;Invalid "
        "INN&lt;/msg&gt;&lt;wo-rollback&gt;0&lt;/"
        "wo-rollback&gt;&lt;method&gt;Balance.CreatePerson&lt;/"
        "method&gt;&lt;code&gt;INVALID_INN&lt;/"
        "code&gt;&lt;parent-codes&gt;&lt;code&gt;INVALID_PARAM&lt;/"
        "code&gt;&lt;code&gt;EXCEPTION&lt;/code&gt;&lt;/"
        "parent-codes&gt;&lt;contents&gt;Invalid "
        "INN&lt;/contents&gt;&lt;/error&gt;</string></value></member></"
        "struct></value></fault></methodResponse>";

    xmlrpc::Response response(kResponse);
    auto fault = response.GetFault<PersonFault>();
    ASSERT_EQ(fault.fault_code, -1);
    ASSERT_EQ(
        fault.fault_string,
        "<error><msg>Invalid "
        "INN</msg><wo-rollback>0</wo-rollback><method>Balance.CreatePerson</"
        "method><code>INVALID_INN</code><parent-codes><code>INVALID_PARAM</"
        "code><code>EXCEPTION</code></parent-codes><contents>Invalid "
        "INN</contents></error>");
  }
}
