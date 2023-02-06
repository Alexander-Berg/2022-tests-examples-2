#include <taxi/tools/dorblu/lib/tests/testbase.h>

#include <iostream>
#include <memory>
#include <type_traits>

#include <taxi/tools/dorblu/lib/include/operation.h>
#include <taxi/tools/dorblu/lib/include/error.h>
#include <taxi/tools/dorblu/lib/include/tokenizer.h>

#include <maps/libs/deprecated/bson/include/bson11.h>

template <class T>
typename std::enable_if<std::is_base_of<Operation,T>::value, std::ostream&>::type
operator<<(std::ostream& os, const T& operation)
{
    return os << (std::string)operation;
}

template <class ExceptionT, class Function>
bool throwsException(Function f)
{
    try {
        f();
    } catch (ExceptionT& e) {
        std::cout << "ok (" << e.what() << ")." << std::endl;
        return true;
    } catch (...) {
        std::cout << "failed." << std::endl;
        std::cout << "Unexpected exception." <<  std::endl;
        return false;
    }
    std::cout << "failed." << std::endl;
    std::cout << "Did not throw." << std::endl;
    return false;

}

void checkOperation(
    const Tokenizer& t,
    const Operation& operation,
    const std::string& input,
    bool output)
{
    EXPECT_EQ(output, operation.match(*t.tokenize(input)));
}

/*template <class T>
typename std::enable_if<std::is_base_of<Operation,T>::value, bool>::type
compareValues(const std::unique_ptr<T>& expected, const std::unique_ptr<T>& got)
{
    if (expected == got) {
        std::cout << "ok." << std::endl;
        return true;
    } else {
        std::cout << "failed." << std::endl;
        std::cout << "Expected:\n" << expected
                  << "Got:\n" << got << std::endl;
        return false;
    }
}*/

TEST(Operation, OperationCreationTest)
{
    /* Test 1: constructing some objects */
    auto bsonStartsWith = bson::object("type", "StartsWith", "field", "request_url", "operand", "/ping");
    auto bsonEndsWith = bson::object("type", "EndsWith", "field", "request_url", "operand", "/ping");
    auto bsonEquals = bson::object("type", "Equals", "field", "request_url", "operand", "/ping");
    auto bsonContains = bson::object("type", "Contains", "field", "request_url", "operand", "/ping");
    auto bsonRegex = bson::object("type", "Regex", "field", "request_url", "operand", "/ping");

    auto opStartsWith = Operation::construct(bsonStartsWith);
    auto opEndsWith   = Operation::construct(bsonEndsWith);
    auto opEquals     = Operation::construct(bsonEquals);
    auto opContains   = Operation::construct(bsonContains);
    auto opRegex      = Operation::construct(bsonRegex);

    std::cout << "OperationStartsWith: ";
    EXPECT_EQ(std::string("(StartsWith request_url /ping)"), (std::string)*opStartsWith);
    std::cout << "OperationEndtsWith: ";
    EXPECT_EQ(std::string("(EndsWith request_url /ping)"), (std::string)*opEndsWith);
    std::cout << "OperationEquals: ";
    EXPECT_EQ(std::string("(Equals request_url /ping)"), (std::string)*opEquals);
    std::cout << "OperationContains: ";
    EXPECT_EQ(std::string("(Contains request_url /ping)"), (std::string)*opContains);
    std::cout << "OperationRegex: ";
    EXPECT_EQ(std::string("(Regex request_url /ping)"), (std::string)*opRegex);

    std::cout << "OperationStartsWith equals to itself: ";
    EXPECT_EQ(*opStartsWith, *opStartsWith);
    std::cout << "OperationEndsWith equals to itself: ";
    EXPECT_EQ(*opEndsWith, *opEndsWith);
    std::cout << "OperationEquals equals to itself: ";
    EXPECT_EQ(*opEquals, *opEquals);
    std::cout << "OperationContains equals to itself: ";
    EXPECT_EQ(*opContains, *opContains);
    std::cout << "OperationRegex equals to itself: ";
    EXPECT_EQ(*opRegex, *opRegex);

    auto bsonAnd = bson::object("type", "And", "children", bson::array(bsonStartsWith, bsonEndsWith));
    auto bsonOr = bson::object("type", "Or", "children", bson::array(bsonEquals, bsonContains));
    auto bsonNot = bson::object("type", "Not", "children", bson::array(bsonRegex));

    auto opAnd = Operation::construct(bsonAnd);
    auto opOr = Operation::construct(bsonOr);
    auto opNot = Operation::construct(bsonNot);

    std::cout << "OperationAnd: ";
    EXPECT_EQ(std::string("(And (StartsWith request_url /ping) (EndsWith request_url /ping) )"), (std::string)*opAnd);
    std::cout << "OperationOr: ";
    EXPECT_EQ(std::string("(Or (Equals request_url /ping) (Contains request_url /ping) )"), (std::string)*opOr);
    std::cout << "OperationNot: ";
    EXPECT_EQ(std::string("(Not (Regex request_url /ping) )"), (std::string)*opNot);

    std::cout << "OperationAnd equals to itself: ";
    EXPECT_EQ(*opAnd, *opAnd);
    std::cout << "OperationOr equals to itself: ";
    EXPECT_EQ(*opOr, *opOr);
    std::cout << "OperationStartsWith equals to itself: ";
    EXPECT_EQ(*opStartsWith, *opStartsWith);
}

TEST(Operation, BadOperationsTest)
{
    auto noOperand = bson::object("type", "StartsWith", "field", "request_url");
    auto noField = bson::object("type", "StartsWith", "operand", "/ping");
    auto noType = bson::object("field", "request_url", "field", "request_url");

    std::cout << "Operation without operand: ";
    EXPECT_THROW(Operation::construct(noOperand), DorBluTypeMismatch);

    std::cout << "Operation without field: ";
    EXPECT_THROW(Operation::construct(noField), DorBluTypeMismatch);

    std::cout << "Operation without type: ";
    EXPECT_THROW(Operation::construct(noType), DorBluTypeMismatch);
}

TEST(Operation, StartsWithTest)
{
    std::string type = "StartsWith";
    Tokenizer t("files/basic_log_format.conf", false);
    auto operation = Operation::construct(bson::object("type", type, "field", "request_url", "operand", "/ping"));
    operation->indexFields(t);

    checkOperation(t, *operation, "\"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /ping2 HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /notping HTTP/1.1\" 200 0.100 \"0.098\" -", false);
    checkOperation(t, *operation, "\"GET /pin HTTP/1.1\" 200 0.100 \"0.098\" -", false);
}

TEST(Operation, EndsWithTest)
{
    std::string type = "EndsWith";
    Tokenizer t("files/basic_log_format.conf", false);
    auto operation = Operation::construct(bson::object("type", type, "field", "request_url", "operand", "/ping"));
    operation->indexFields(t);

    checkOperation(t, *operation, "\"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /blah/ping HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /notping HTTP/1.1\" 200 0.100 \"0.098\" -", false);
    checkOperation(t, *operation, "\"GET ping HTTP/1.1\" 200 0.100 \"0.098\" -", false);
}

TEST(Operation, EqualsTest)
{
    std::string type = "Equals";
    Tokenizer t("files/basic_log_format.conf", false);
    auto operation = Operation::construct(bson::object("type", type, "field", "request_url", "operand", "/ping"));
    operation->indexFields(t);

    checkOperation(t, *operation, "\"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /blah/ping HTTP/1.1\" 200 0.100 \"0.098\" -", false);
    checkOperation(t, *operation, "\"GET /notping HTTP/1.1\" 200 0.100 \"0.098\" -", false);
    checkOperation(t, *operation, "\"GET /pingggg HTTP/1.1\" 200 0.100 \"0.098\" -", false);
}

TEST(Operation, ContainsTest)
{
    std::string type = "Contains";
    Tokenizer t("files/basic_log_format.conf", false);
    auto operation = Operation::construct(bson::object("type", type, "field", "request_url", "operand", "/ping"));
    operation->indexFields(t);

    checkOperation(t, *operation, "\"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /blah/ping HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /ping2 HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /notping HTTP/1.1\" 200 0.100 \"0.098\" -", false);
}

TEST(Operation, LessThanTest)
{
    std::string type = "LessThan";
    Tokenizer t("files/basic_log_format.conf", false);
    auto operationBson = bson::object("type", type, "field", "upstream_response_time", "operand", "1.053");
    auto operation = Operation::construct(operationBson);
    operation->indexFields(t);

    checkOperation(t, *operation, "\"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /notping HTTP/1.1\" 200 0.100 \"0.01\" -", true);
    checkOperation(t, *operation, "\"GET /blah/ping HTTP/1.1\" 200 0.100 \"1.053\" -", false);
    checkOperation(t, *operation, "\"GET /ping2 HTTP/1.1\" 200 0.100 \"48\" -", false);
}

TEST(Operation, GreaterTest)
{
    std::string type = "GreaterThan";
    Tokenizer t("files/basic_log_format.conf", false);
    auto operation = Operation::construct(bson::object("type", type, "field", "upstream_response_time", "operand", "1.053"));
    operation->indexFields(t);

    checkOperation(t, *operation, "\"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -", false);
    checkOperation(t, *operation, "\"GET /notping HTTP/1.1\" 200 0.100 \"0.01\" -", false);
    checkOperation(t, *operation, "\"GET /blah/ping HTTP/1.1\" 200 0.100 \"1.053\" -", false);
    checkOperation(t, *operation, "\"GET /ping2 HTTP/1.1\" 200 0.100 \"48\" -", true);
}

TEST(Operation, RegexTest)
{
    std::string type = "Regex";
    Tokenizer t("files/basic_log_format.conf", false);
    auto operation = Operation::construct(bson::object("type", type, "field", "request_url", "operand", "^/[pr]ing.*"));
    operation->indexFields(t);

    checkOperation(t, *operation, "\"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /ringing HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /png HTTP/1.1\" 200 0.100 \"0.098\" -", false);
    checkOperation(t, *operation, "\"GET /notping HTTP/1.1\" 200 0.100 \"0.098\" -", false);

    auto operation2 = Operation::construct(bson::object("type", type, "field", "request_url", "operand", "^sat[0-9]+.maps.yandex.net$"));
    operation2->indexFields(t);
}

TEST(Operation, AndTest)
{
    std::string type = "And";
    Tokenizer t("files/basic_log_format.conf", false);
    auto subop1 = bson::object("type", "StartsWith", "field", "request_url", "operand", "/p");
    auto subop2 = bson::object("type", "EndsWith", "field", "request_url", "operand", "ing");
    auto operation = Operation::construct(bson::object("type", type, "children", bson::array(subop1, subop2)));
    operation->indexFields(t);

    checkOperation(t, *operation, "\"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /piiiiing HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /png HTTP/1.1\" 200 0.100 \"0.098\" -", false);
    checkOperation(t, *operation, "\"GET /notping HTTP/1.1\" 200 0.100 \"0.098\" -", false);
}

TEST(Operation, OrTest)
{
    std::string type = "Or";
    Tokenizer t("files/basic_log_format.conf", false);
    auto subop1 = bson::object("type", "StartsWith", "field", "request_url", "operand", "/p");
    auto subop2 = bson::object("type", "EndsWith", "field", "request_url", "operand", "ing");
    auto operation = Operation::construct(bson::object("type", type, "children", bson::array(subop1, subop2)));
    operation->indexFields(t);

    checkOperation(t, *operation, "\"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /png HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /notping HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /notpong HTTP/1.1\" 200 0.100 \"0.098\" -", false);
}

TEST(Operation, NotTest)
{
    std::string type = "Not";
    Tokenizer t("files/basic_log_format.conf", false);
    auto subop = bson::object("type", "StartsWith", "field", "request_url", "operand", "/ping");
    auto operation = Operation::construct(bson::object("type", type, "children", bson::array(subop)));
    operation->indexFields(t);

    checkOperation(t, *operation, "\"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -", false);
    checkOperation(t, *operation, "\"GET /ping2 HTTP/1.1\" 200 0.100 \"0.098\" -", false);
    checkOperation(t, *operation, "\"GET /notping HTTP/1.1\" 200 0.100 \"0.098\" -", true);
    checkOperation(t, *operation, "\"GET /pin HTTP/1.1\" 200 0.100 \"0.098\" -", true);
}

TEST(Operation, SerializationTest)
{
    auto subop1 = bson::object("type", "StartsWith", "field", "request_url", "operand", "/p");
    auto subop2 = bson::object("type", "EndsWith", "field", "request_url", "operand", "ing");
    auto operation = Operation::construct(bson::object("type", "And", "children", bson::array(subop1, subop2)));

    DorBluPB::Filter pbFilter;
    operation->serializeTo(&pbFilter);

    auto deserialized = Operation::construct(pbFilter);

    std::cout << "Comparing serialized and deserialized Operations: ";
    EXPECT_EQ(*operation, *deserialized);
}
