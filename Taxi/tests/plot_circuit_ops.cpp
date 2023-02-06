#include <gtest/gtest.h>

#include <boost/filesystem.hpp>
#include <radio/blocks/utils/buffer_sample.hpp>
#include <radio/circuit.hpp>

#include "tools/plotter.hpp"
#include "tools/test_data_file_reader.hpp"

namespace hejmdal::radio {

TEST(NotATest, DrawOpsQueryCircuit) {
  if constexpr (testutils::kIsRelease) return;

  std::vector<std::string> interesting_graphs{
      "/Users/stasmarkin/Downloads/data/ops-query/taxi-mrs01f.json",  //рост
                                                                      //в 2
                                                                      //раза
      //      "/Users/stasmarkin/Downloads/data/ops-query/"
      //      "stq-billing0-mrs-sas-01.json",  //нестандартный профиль
      //      "/Users/stasmarkin/Downloads/data/ops-query/"
      //      "users-mrs-shard1-iva-01.json",  //небольшой пик на 20%
      //      "/Users/stasmarkin/Downloads/data/ops-query/"
      //      "minor-mrs-shard2-vla-01.json",  //обычный профиль
      //      "/Users/stasmarkin/Downloads/data/ops-query/taxi-mrs01e.json",
      //      //падение
      //                                                                      //в
      //                                                                      2
      //                                                                      //раза
      //      "/Users/stasmarkin/Downloads/data/ops-query/"
      //      "stq-order1-mrs-sas-01.json",  //низкие значения
  };

  for (auto& path : interesting_graphs) {
    //  boost::filesystem::directory_iterator
    //  it{"/Users/stasmarkin/Downloads/data/ops-query"}; while (it !=
    //  boost::filesystem::directory_iterator{}) {
    //    auto path = it->path().generic_string();

    if (path.find("/request__") != std::string::npos) continue;

    testutils::Plotter plt;

    formats::json::ValueBuilder ops;
    ops["name"] = "ops";
    auto ops_schema = ops.ExtractValue();

    auto circuit_ptr = Circuit::Build("test-id", ops_schema);
    auto& circuit = *circuit_ptr;
    auto ep = circuit.GetEntryPoint("data");

    std::cout << path << '\n';
    auto reader = testutils::TestDataFileReader(path);

    std::vector<models::TimeSeriesView> views = reader.GetTimeSeries();
    for (const models::TimeSeriesView& view : views) {
      auto buffers = circuit.CreateDebugBuffers(view.size() * 3);
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
