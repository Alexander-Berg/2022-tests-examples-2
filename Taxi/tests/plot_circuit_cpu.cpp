#include <gtest/gtest.h>

#include <boost/filesystem.hpp>
#include <radio/circuit.hpp>

#include "tools/plotter.hpp"
#include "tools/test_data_file_reader.hpp"
#include "tools/testutils.hpp"

namespace hejmdal::radio {

TEST(NotATest, DrawCpuCircuit) {
  if constexpr (testutils::kIsRelease) return;

  std::vector<std::string> interesting_graphs{
      "/Users/stasmarkin/Downloads/data/cpu-usage/"
      "taxi-users-mrs01f.json",  //резкий скачок
      "/Users/stasmarkin/Downloads/data/cpu-usage/"
      "users-mrs-shard1-vla-01.json",  //лечкий скач
      "/Users/stasmarkin/Downloads/data/cpu-usage/"
      "taxi-minor-mrs01h.json",  // нагрузка до .35
      "/Users/stasmarkin/Downloads/data/cpu-usage/"
      "minor-mrs-shard3-vla-01.json",  // oob с середины
      "/Users/stasmarkin/Downloads/data/cpu-usage/taxi-stq-mrs01f.json",  // 0.4
                                                                          // -
                                                                          // 0.8
      "/Users/stasmarkin/Downloads/data/cpu-usage/"
      "stq-billing0-mrs-myt-01.json",
      "/Users/stasmarkin/Downloads/data/cpu-usage/taxi-mrs02f.json",
      "/Users/stasmarkin/Downloads/data/cpu-usage/"
      "stq-billing0-mrs-sas-01.json",  // peak 1.0
      "/Users/stasmarkin/Downloads/data/cpu-usage/"
      "stq-billing0-mrs-vla-01.json",                                 // jump
      "/Users/stasmarkin/Downloads/data/cpu-usage/taxi-mrs01e.json",  // 1.0 cpu
      "/Users/stasmarkin/Downloads/data/cpu-usage/"
      "taxi-users-mrs01e.json",  //резкое падение
  };

  for (auto& path : interesting_graphs) {
    //  boost::filesystem::directory_iterator
    //  it{"/Users/stasmarkin/Downloads/data/cpu-query"}; while (it !=
    //  boost::filesystem::directory_iterator{}) {
    //    auto path = it->path().generic_string();

    if (path.find("/request__") != std::string::npos) continue;

    testutils::Plotter plt;

    formats::json::ValueBuilder cpu;
    cpu["name"] = "cpu";
    auto cpu_schema = cpu.ExtractValue();

    auto circuit_ptr = Circuit::Build("test-id", cpu_schema);
    auto& circuit = *circuit_ptr;
    auto ep = circuit.GetEntryPoint("data");

    std::cout << path << '\n';
    auto reader = testutils::TestDataFileReader(path);

    std::vector<models::TimeSeriesView> views = reader.GetTimeSeries();
    for (const models::TimeSeriesView& view : views) {
      auto buffers = circuit.CreateDebugBuffers(view.size() * 2);
      for (const models::SensorValue& val : view) {
        ep.DataIn(val.GetTime(), val.GetValue());
      }
      for (auto& buffer : buffers) {
        auto ts_map = buffer->ExtractTimeSeries();
        plt.Plot(ts_map);
      }
    }
  }
}

}  // namespace hejmdal::radio
