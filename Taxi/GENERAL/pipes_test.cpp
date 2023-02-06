#include <userver/utest/utest.hpp>

#include <pipes/pipes.hpp>

namespace {

void RunSink(pipes::Consumer<char> sink, const std::string& str) {
  pipes::Process<const std::string&, char> to_char =
      [](std::string in, pipes::Sink<char>& sink) {
        for (auto c : in) sink(c);
      };
  auto pipe = to_char | sink;
  RunOn(pipe, str);
}

void RunProcess(pipes::Process<char, char> process, const std::string& in,
                const std::string& out) {
  pipes::Process<const std::string&, char> to_char =
      [](const std::string& in, pipes::Sink<char>& sink) {
        for (auto c : in) sink(c);
      };

  std::string result;
  pipes::Consumer<char> to_string = [&result](char in) { result += in; };

  auto pipe = to_char | process | to_string;

  RunOn(pipe, in);

  ASSERT_EQ(out, result);
}

}  // namespace

TEST(Pipes, MoveOnlyPipe) {
  auto to_char = pipes::Pipe([](const std::string& in, auto& sink) {
    for (auto c : in) sink(c);
  });

  auto p = std::make_unique<int>();
  auto move_only_to_upper = [p = std::move(p)](char in, auto& out) {
    out(std::toupper(in));
  };

  std::string result;
  auto to_string = [&result](char in, auto&) { result += in; };

  auto pipe = to_char | std::move(move_only_to_upper) | to_string;

  RunOn(pipe, "hello world");

  ASSERT_EQ(result, "HELLO WORLD");
}

TEST(Pipes, Pipe) {
  auto fetch_words = pipes::Pipe([](const auto& in, auto& sink) {
    for (const auto& word : in) sink(word);
  });

  auto to_char = [](const std::string& in, auto& sink) {
    for (auto c : in) sink(c);
  };

  auto to_upper = [](char in, auto& out) { out(std::toupper(in)); };

  std::string result;
  auto to_string = [&result](char in, auto&) { result += in; };

  auto pipe = fetch_words | to_char | to_upper | to_string;

  RunOn(pipe, std::vector{"hello", " ", "world"});

  ASSERT_EQ(result, "HELLO WORLD");
}

TEST(Pipes, Sink) {
  auto to_upper =
      pipes::Pipe([](char in, auto& out) { out(std::toupper(in)); });

  std::string result;
  auto to_string = [&result](char in, auto&) { result += in; };

  auto pipe = to_upper | to_string;
  RunSink(pipes::ToConsumer<char>(pipe), "hello world");

  ASSERT_EQ(result, "HELLO WORLD");
}

TEST(Pipes, Process) {
  auto to_upper = [](char in, auto& out) { out(std::toupper(in)); };

  auto filter_digits = [](char in, auto& out) {
    if (!std::isdigit(in)) out(in);
  };

  auto pipe = pipes::Pipe(filter_digits) | to_upper;

  RunProcess(pipes::ToProcess<char, char>(pipe), "hello111 world111",
             "HELLO WORLD");
}
