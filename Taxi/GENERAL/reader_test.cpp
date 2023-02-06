#include <yson.hpp>
#include "print.hpp"

namespace {

void consume_stdin() {
    auto input_range = yson::stream_events_range(
        yson::input::from_posix_fd(STDIN_FILENO),
        yson::stream_type::list_fragment
    );
    int indent = 0;
    for (auto& event: input_range) {
        auto current_indent = indent;
        switch (event.type()) {
            case yson::event_type::begin_stream:
            case yson::event_type::begin_list:
            case yson::event_type::begin_map:
            case yson::event_type::begin_attributes:
                ++indent;
                break;

            case yson::event_type::end_list:
            case yson::event_type::end_map:
            case yson::event_type::end_attributes:
            case yson::event_type::end_stream:
                --indent;
                --current_indent;
                break;

            default: break;
        }
        for (int i = 0; i < current_indent; ++i) {
            print("  ");
        }
        println(event);
    }
}

} // anonymous namespace

int main(int argc, char* argv[]) {
    std::ios_base::sync_with_stdio(false);

    if (argc > 1 && argv[1][0] == 'e') {
        consume_stdin(); // let exceptions propagate: useful for debugging
    } else {
        try {
            consume_stdin();
        } catch (const std::exception &err) {
            println("ERROR: ", err.what());
        }
    }

    return 0;
}
