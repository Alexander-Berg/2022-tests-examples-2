#pragma once

#include <taxi/tools/dorblu/lib/include/util.h>

#include <optional>
#include <sstream>
#include <iostream>
#include <exception>

#include <unistd.h>

#define DORBLU_TEST(func) \
    try { \
        func(); \
    } catch (std::exception& e) { \
        std::cerr << (Color::RedBold << "\n" #func " failed with exception: ") << e.what() << std::endl; \
        exit(-1); \
    }

enum class Color: uint32_t {
    Normal = 0, NormalBold,
    Red, RedBold,
    Green, GreenBold,
    Yellow, YellowBold,
    _size_
};

class Colored
{
    public:
        Colored(const Color& color) { data_ << colorString(color); }
        Colored(const Colored& other) { data_ << other.data_.rdbuf(); }

        template <typename T>
            Colored& operator<<(const T& data) { data_ << data; return *this; }

        std::string data() const
        {
            data_ << colorString(Color::Normal);
            return data_.str();
        }

    private:
        inline const char* colorString(const Color& c) const
        {
            return colors[static_cast<uint32_t>(c)];
        }

        const char* colors[static_cast<uint32_t>(Color::_size_)] = {
            "\033[0m",     "\033[1m",   //Normal
            "\033[0;31m", "\033[1;31m", //Red
            "\033[0;32m", "\033[1;32m", //Green
            "\033[0;33m", "\033[1;33m"  //Yellow
        };

        mutable std::stringstream data_;
};

template<typename T>
Colored operator<<(const Color& color, const T& data)
{
    Colored c(color);
    c << data;
    return c;
}

std::ostream& operator<<(std::ostream& os, const Colored& colored)
{
    return os << colored.data();
}

struct TestResultMismatch: public std::exception
{
    template <typename T>
    std::string asStr(const T& value) {
        std::stringstream ss;
        ss << value;
        return ss.str();
    }

    template <typename T>
    std::string asStr(const std::optional<T>& value) {
        return value ? asStr(*value) : "<NONE>";
    }

    template <typename T>
    TestResultMismatch(const T& expected, const T& got)
    {
        auto wrapMultiline = [](const std::string& value) -> std::string {
            auto newline = value.find_first_of('\n');
            if (newline == std::string::npos)
                return value;

            return "\n---\n" + value + "\n---\n";
        };

        std::string expectedStr = asStr(expected);
        std::string gotStr = asStr(got);

        std::stringstream ss;
        ss << (Color::Red << "Result mismatch\n"
           << "Expected: " << wrapMultiline(expectedStr) << "\n"
           << "Got:      " << wrapMultiline(gotStr));
        what_ = ss.str();
    }
    const char* what() const noexcept { return what_.c_str(); }

    std::string what_;
};

template <typename T>
void TestEquals(const std::string& description, const T& expected, const T& got)
{
    std::cout << (Color::Yellow << "[TestEquals] " << description << ": ");
    if (expected == got) {
        std::cout << (Color::GreenBold << "[ OK ]") << std::endl;
        return;
    }

    std::cout << (Color::RedBold <<"[ FAILED ]") << std::endl;
    throw TestResultMismatch(expected, got);
}

template <class ExceptionT, class Function>
void TestThrowsException(const std::string& description, Function f)
{
    std::cout << (Color::Yellow << "[TestThrowsException] " << description << ": ");
    try {
        f();
    } catch (ExceptionT& e) {
        std::cout << (Color::GreenBold << "[ OK ] (caught <" << e.what() << ">)") << std::endl;
        return;
    } catch (std::exception& e) {
        std::cout << (Color::RedBold <<"[ FAILED ]") << std::endl;
        std::string expected = "Some correct exception";
        std::string got = "Unexpected exception: <" + std::string(e.what()) + ">";
        throw TestResultMismatch(expected, got);
    }

    std::cout << (Color::RedBold <<"[ FAILED ]") << std::endl;
    std::string expected = "Exception";
    std::string got = "No exception was thrown";
    throw TestResultMismatch(expected, got);
}

template <class Function>
void TestNotThrowsException(const std::string& description, Function f)
{
    std::cout << (Color::Yellow << "[TestNotThrowsException] " << description << ": ");
    try {
        f();
    } catch (std::exception& e) {
        std::cout << (Color::RedBold <<"[ FAILED ]") << std::endl;
        std::string expected = "No exception";
        std::string got = "Unexpected exception: <" + std::string(e.what()) + ">";
        throw TestResultMismatch(expected, got);
    }

    std::cout << (Color::GreenBold <<"[ OK ]") << std::endl;
}
