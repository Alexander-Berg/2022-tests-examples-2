#include <sstream>
#include <string>
#include <string_view>
#include <vector>

#include <gtest/gtest.h>
#include <pugixml.hpp>

#include <userver/decimal64/decimal64.hpp>

#include <xmlrpc/document.hpp>
#include <xmlrpc/serialization.hpp>

namespace xs = xmlrpc::serialization;

TEST(ParksReplica, SerializationInt) {
  xmlrpc::Document doc;
  xs::Serialize(doc.GetRoot(), static_cast<int64_t>(10));
  constexpr std::string_view kExpected = "<int>10</int>";
  ASSERT_EQ(kExpected, doc.DumpToString());
}

TEST(ParksReplica, SerializationString) {
  constexpr std::string_view kExpected = "<string>Hello world!</string>";
  {
    xmlrpc::Document doc;
    xs::Serialize(doc.GetRoot(), "Hello world!");
    EXPECT_EQ(kExpected, doc.DumpToString());
  }
  {
    xmlrpc::Document doc;
    xs::Serialize(doc.GetRoot(), std::string{"Hello world!"});
    EXPECT_EQ(kExpected, doc.DumpToString());
  }
}

TEST(ParksReplica, SerializationDecimal) {
  {
    xmlrpc::Document doc;
    xs::Serialize(doc.GetRoot(), decimal64::Decimal<2>{"123.45"});
    EXPECT_EQ(std::string_view{"<string>123.45</string>"}, doc.DumpToString());
  }
  {
    xmlrpc::Document doc;
    xs::Serialize(doc.GetRoot(), decimal64::Decimal<2>{"-123.45"});
    EXPECT_EQ(std::string_view{"<string>-123.45</string>"}, doc.DumpToString());
  }
  {
    xmlrpc::Document doc;
    xs::Serialize(doc.GetRoot(), decimal64::Decimal<2>{"123.00"});
    EXPECT_EQ(std::string_view{"<string>123.00</string>"}, doc.DumpToString());
  }
}

TEST(ParksReplica, SerializationBoolean) {
  {
    xmlrpc::Document doc;
    xs::Serialize(doc.GetRoot(), true);
    EXPECT_EQ(std::string_view{"<boolean>1</boolean>"}, doc.DumpToString());
  }
  {
    xmlrpc::Document doc;
    xs::Serialize(doc.GetRoot(), false);
    EXPECT_EQ(std::string_view{"<boolean>0</boolean>"}, doc.DumpToString());
  }
}

TEST(ParksReplica, SerializationVector) {
  {
    xmlrpc::Document doc;
    xs::Serialize(doc.GetRoot(), std::vector<int64_t>{});
    constexpr std::string_view kExpected = "<array><data/></array>";
    EXPECT_EQ(kExpected, doc.DumpToString());
  }
  {
    xmlrpc::Document doc;
    xs::Serialize(doc.GetRoot(), std::vector<int64_t>{0, 1});
    constexpr std::string_view kExpected =
        "<array><data>"
        "<value><int>0</int></value>"
        "<value><int>1</int></value>"
        "</data></array>";
    EXPECT_EQ(kExpected, doc.DumpToString());
  }
}

namespace {
class MyCustom {
 public:
  std::string field1;
  int64_t field2;
  class XmlRpcSerializerType final
      : public xmlrpc::serialization::AbstractStructSerializer<MyCustom> {
    void WriteFields(pugi::xml_node& struct_node,
                     const MyCustom& value) const final {
      WriteSingleField(struct_node, "f1", value.field1);
      WriteSingleField(struct_node, "f2", value.field2);
    }
  };
};

class MyCustomSerializerType2 final
    : public xmlrpc::serialization::AbstractStructSerializer<MyCustom> {
  void WriteFields(pugi::xml_node& struct_node,
                   const MyCustom& value) const final {
    WriteSingleField(struct_node, "field1", value.field1);
    WriteSingleField(struct_node, "field2", value.field2);
  }
};

class OtherCustomSerialzer;
struct OtherCustom {
  int root;
  using XmlRpcSerializerType = OtherCustomSerialzer;
};

class OtherCustomSerialzer final
    : public xmlrpc::serialization::AbstractStructSerializer<OtherCustom> {
  void WriteFields(pugi::xml_node& struct_node,
                   const OtherCustom& value) const final {
    const int64_t square = value.root * value.root;
    WriteSingleField(struct_node, "square", square);
  }
};

}  // namespace

TEST(ParksReplica, SerializeCustom) {
  {
    xmlrpc::Document doc;
    xs::Serialize(doc.GetRoot(), MyCustom{"Hello", 5});
    constexpr std::string_view kExpected =
        "<struct>"
        "<member><name>f1</name><value><string>Hello</string></value></member>"
        "<member><name>f2</name><value><int>5</int></value></member>"
        "</struct>";
    EXPECT_EQ(kExpected, doc.DumpToString());
  }
  {
    xmlrpc::Document doc;
    xs::Serialize(doc.GetRoot(), MyCustom{"Hello", -10},
                  MyCustomSerializerType2());
    constexpr std::string_view kExpected =
        "<struct>"
        "<member><name>field1</name><value><string>Hello</string></value></"
        "member>"
        "<member><name>field2</name><value><int>-10</int></value></member>"
        "</struct>";
    EXPECT_EQ(kExpected, doc.DumpToString());
  }
  {
    xmlrpc::Document doc;
    xs::Serialize(doc.GetRoot(), OtherCustom{7});
    constexpr std::string_view kExpected =
        "<struct>"
        "<member><name>square</name><value><int>49</int></value></member>"
        "</struct>";
    EXPECT_EQ(kExpected, doc.DumpToString());
  }
  {
    xmlrpc::Document doc;
    xs::Serialize(doc.GetRoot(), OtherCustom{8}, OtherCustomSerialzer());
    constexpr std::string_view kExpected =
        "<struct>"
        "<member><name>square</name><value><int>64</int></value></member>"
        "</struct>";
    EXPECT_EQ(kExpected, doc.DumpToString());
  }
}
