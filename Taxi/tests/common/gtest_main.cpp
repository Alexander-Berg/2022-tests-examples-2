#include <gtest/gtest.h>

#include <boost/program_options.hpp>

#include <logging/logger.hpp>

namespace testing {
namespace internal {
// from gtest.cc
extern bool g_help_flag;
}  // namespace internal
}  // namespace testing

namespace {

struct Config {
  LogLevel log_level = LogLevel::WARNING;
};

Config ParseTaxiConfig(int argc, char** argv) {
  namespace po = boost::program_options;

  po::options_description desc("Allowed options");
  desc.add_options()("log-level,l",
                     po::value<std::string>()->default_value("NONE"),
                     "logging level");

  if (testing::internal::g_help_flag) {
    std::cout << desc << std::endl;
    return {};
  }

  po::variables_map vm;
  po::store(po::parse_command_line(argc, argv, desc), vm);
  po::notify(vm);

  Config config;
  if (vm.count("log-level"))
    config.log_level =
        CustomLogger::ParseLevelName(vm["log-level"].as<std::string>());

  return config;
}

}  // namespace

int main(int argc, char** argv) {
  ::testing::InitGoogleTest(&argc, argv);

  const Config& config = ParseTaxiConfig(argc, argv);
  CustomLogger::SetSystemLogLevel(config.log_level);
  CustomLogger::SetOutput(LoggerOutput::Console);

  return RUN_ALL_TESTS();
}
