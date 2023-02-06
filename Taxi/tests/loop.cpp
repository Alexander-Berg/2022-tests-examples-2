#include <unistd.h>
#include <cmath>

#include <gtest/gtest.h>

#include <yson/reader.hpp>
#include <yson/writer.hpp>
#include <yson/input.hpp>
#include <yson/output.hpp>

namespace {

constexpr const char* alphabet =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

void generate(yson::writer& writer, size_t count)
{
    writer.begin_stream();
    for (size_t i = 0; i < count; ++i) {
        writer.begin_map()
            .key("ints").begin_list()
                .int64(0)
                .int64(-1)
                .int64(1000)
                .int64(-1000)
                .end_list()
            .key("uints").begin_list()
                .uint64(0)
                .uint64(1000)
                .uint64(10000000)
                .end_list()
            .key("entities").begin_list()
                .entity()
                .begin_attributes()
                    .key("color").string("blue")
                    .key("size").int64(100)
                .end_attributes().entity()
                .entity()
                .end_list()
            .key("booleans").begin_list()
                .boolean(true)
                .boolean(false)
                .boolean(true)
                .end_list()
            .key("floats").begin_list()
                .float64(0.0)
                .float64(13.0e30)
                .float64(M_PI)
                .end_list()
            .key("strings").begin_list()
                .string("hello")
                .string("")
                .string("foo \"-bar-\" baz")
                .string("oh\nwow")
                .string(alphabet)
                .end_list()
            .end_map();
    }
    writer.end_stream();
}

void verify(yson::reader& reader, size_t count)
{
#define NEXT(name__) {auto& name__ = reader.next_event(); SCOPED_TRACE(e);
#define END_NEXT }
#define NEXT_TYPE(type__) NEXT(e) { \
    ASSERT_EQ(yson::event_type::type__, e.type()); \
} END_NEXT
#define NEXT_KEY(key__) NEXT(e) { \
    ASSERT_EQ(yson::event_type::key, e.type()); \
    ASSERT_EQ(key__, e.as_string()); \
} END_NEXT
#define NEXT_SCALAR(type__, value__) NEXT(e) { \
    ASSERT_EQ(yson::event_type::scalar, e.type()); \
    ASSERT_EQ(yson::scalar_type::type__, e.as_scalar().type()); \
    ASSERT_EQ(value__, e.as_scalar().as_##type__()); \
} END_NEXT
#define NEXT_ENTITY() NEXT(e) { \
    ASSERT_EQ(yson::event_type::scalar, e.type()); \
    ASSERT_EQ(yson::scalar_type::entity, e.as_scalar().type()); \
} END_NEXT
#define NEXT_FLOAT64(value__) NEXT(e) { \
    ASSERT_EQ(yson::event_type::scalar, e.type()); \
    ASSERT_EQ(yson::scalar_type::float64, e.as_scalar().type()); \
    ASSERT_DOUBLE_EQ(value__, e.as_scalar().as_float64()); \
} END_NEXT

    constexpr auto true_ = true;
    constexpr auto false_ = false;

    NEXT_TYPE(begin_stream);
    for (size_t i = 0; i < count; ++i) {
        NEXT_TYPE(begin_map);
        NEXT_KEY("ints") {
            NEXT_TYPE(begin_list);
            NEXT_SCALAR(int64, 0);
            NEXT_SCALAR(int64, -1);
            NEXT_SCALAR(int64, 1000);
            NEXT_SCALAR(int64, -1000);
            NEXT_TYPE(end_list);
        }
        NEXT_KEY("uints") {
            NEXT_TYPE(begin_list);
            NEXT_SCALAR(uint64, 0U);
            NEXT_SCALAR(uint64, 1000U);
            NEXT_SCALAR(uint64, 10000000U);
            NEXT_TYPE(end_list);
        }
        NEXT_KEY("entities") {
            NEXT_TYPE(begin_list);
            NEXT_ENTITY();
            NEXT_TYPE(begin_attributes) {
                NEXT_KEY("color") {
                    NEXT_SCALAR(string, "blue");
                }
                NEXT_KEY("size") {
                    NEXT_SCALAR(int64, 100);
                }
            } NEXT_TYPE(end_attributes);
            NEXT_ENTITY();
            NEXT_ENTITY();
            NEXT_TYPE(end_list);
        }
        NEXT_KEY("booleans") {
            NEXT_TYPE(begin_list);
            NEXT_SCALAR(boolean, true_);
            NEXT_SCALAR(boolean, false_);
            NEXT_SCALAR(boolean, true_);
            NEXT_TYPE(end_list);
        }
        NEXT_KEY("floats") {
            NEXT_TYPE(begin_list);
            NEXT_FLOAT64(0.0);
            NEXT_FLOAT64(13.0e30);
            NEXT_FLOAT64(M_PI);
            NEXT_TYPE(end_list);
        }
        NEXT_KEY("strings") {
            NEXT_TYPE(begin_list);
            NEXT_SCALAR(string, "hello");
            NEXT_SCALAR(string, "");
            NEXT_SCALAR(string, "foo \"-bar-\" baz");
            NEXT_SCALAR(string, "oh\nwow");
            NEXT_SCALAR(string, alphabet);
            NEXT_TYPE(end_list);
        }
        NEXT_TYPE(end_map);
    }
    NEXT_TYPE(end_stream);

#undef NEXT
#undef END_NEXT
#undef NEXT_TYPE
#undef NEXT_KEY
#undef NEXT_SCALAR
}

class sys_error { };

std::ostream& operator <<(std::ostream& stream, const sys_error&)
{
    stream << strerror(errno);
    return stream;
}

template <typename Here, typename There>
void pipe(Here&& reader, There&& writer)
{
    int fildes[2];
    ASSERT_EQ(0, ::pipe(fildes)) << sys_error();
    auto read_fd = fildes[0];
    auto write_fd = fildes[1];

    auto pid = ::fork();
    ASSERT_TRUE(pid >= 0) << sys_error();
    if (pid > 0) {
        // parent
        ASSERT_EQ(0, ::close(write_fd)) << sys_error();
        reader(read_fd);
        ASSERT_EQ(0, ::close(read_fd)) << sys_error();
    } else {
        // child
        ASSERT_EQ(0, ::close(read_fd)) << sys_error();
        try {
            writer(write_fd);
        } catch (...) {
            ADD_FAILURE() << "Exception in writer!";
        }
        ASSERT_EQ(0, ::close(write_fd)) << sys_error();
        ::exit(0);
    }
    int stat_loc;
    ASSERT_EQ(pid, ::waitpid(pid, &stat_loc, 0)) << sys_error();
}

yson::reader make_reader(std::unique_ptr<yson::input::stream> stream)
{
    return yson::reader(
        std::move(stream),
        yson::stream_type::list_fragment
    );
}

template<typename Function>
void test_memory(Function make_writer, size_t nrepeat)
{
    std::ostringstream stream;
    {
        auto writer = make_writer(
            yson::output::from_ostream(stream)
        );
        generate(writer, nrepeat);
    }
    auto text = stream.str();
    {
        auto reader = make_reader(
            yson::input::from_memory(text)
        );
        verify(reader, nrepeat);
    }
    {
        std::istringstream istream {text};
        auto reader = make_reader(
            yson::input::from_istream(istream, /* buffer_size = */ 1)
        );
        verify(reader, nrepeat);
    }
}

template<typename Function>
void test_posix_fd(
    Function make_writer,
    size_t nrepeat,
    size_t read_buffer_size,
    size_t write_buffer_size)
{
    pipe(
        [&](int fd) {
            auto reader = make_reader(
                yson::input::from_posix_fd(fd, read_buffer_size)
            );
            verify(reader, nrepeat);
        },
        [&](int fd) {
            auto writer = make_writer(
                yson::output::from_posix_fd(fd, write_buffer_size)
            );
            generate(writer, nrepeat);
        }
    );
}


template<typename Function>
void test_stdio_file(
    Function make_writer,
    size_t nrepeat,
    size_t read_buffer_size,
    size_t write_buffer_size)
{
    pipe(
        [&](int fd) {
            auto file = ::fdopen(fd, "rb");
            ASSERT_TRUE(file != nullptr) << sys_error();
            auto reader = make_reader(
                yson::input::from_stdio_file(file, read_buffer_size)
            );
            verify(reader, nrepeat);
        },
        [&](int fd) {
            auto file = ::fdopen(fd, "wb");
            (void) write_buffer_size;
            auto writer = make_writer(
                yson::output::from_stdio_file(file, write_buffer_size)
            );
            generate(writer, nrepeat);
            fflush(file);
        }
    );
}


yson::writer text(std::unique_ptr<yson::output::stream> stream)
{
    return yson::text_writer(
        std::move(stream),
        yson::stream_type::list_fragment
    );
}

yson::writer pretty_text(std::unique_ptr<yson::output::stream> stream)
{
    return yson::pretty_text_writer(
        std::move(stream),
        yson::stream_type::list_fragment
    );
}

yson::writer binary(std::unique_ptr<yson::output::stream> stream)
{
    return yson::pretty_text_writer(
        std::move(stream),
        yson::stream_type::list_fragment
    );
}

} // anonymous namespace


TEST(loop, memory_pretty_text)
{
    test_memory(pretty_text, 100);
}

TEST(loop, memory_text)
{
    test_memory(text, 100);
}

TEST(loop, memory_binary)
{
    test_memory(binary, 100);
}

TEST(loop, posix_fd_pretty_text_buffered)
{
    test_posix_fd(pretty_text, 100, 1024, 1024);
}

TEST(loop, posix_fd_pretty_text_unbuffered)
{
    test_posix_fd(pretty_text, 100, 1, 0);
}

TEST(loop, posix_fd_text_buffered)
{
    test_posix_fd(text, 100, 1024, 1024);
}

TEST(loop, posix_fd_text_unbuffered)
{
    test_posix_fd(text, 100, 1, 0);
}

TEST(loop, posix_fd_binary_buffered)
{
    test_posix_fd(binary, 100, 1024, 1024);
}

TEST(loop, posix_fd_binary_unbuffered)
{
    test_posix_fd(binary, 100, 1, 0);
}

TEST(loop, stdio_file_pretty_text_buffered)
{
    test_stdio_file(pretty_text, 100, 1024, 1024);
}

TEST(loop, stdio_file_pretty_text_unbuffered)
{
    test_stdio_file(pretty_text, 100, 1, 0);
}

TEST(loop, stdio_file_text_buffered)
{
    test_stdio_file(text, 100, 1024, 1024);
}

TEST(loop, stdio_file_text_unbuffered)
{
    test_stdio_file(text, 100, 1, 0);
}

TEST(loop, stdio_file_binary_buffered)
{
    test_stdio_file(binary, 100, 1024, 1024);
}

TEST(loop, stdio_file_binary_unbuffered)
{
    test_stdio_file(binary, 100, 1, 0);
}
