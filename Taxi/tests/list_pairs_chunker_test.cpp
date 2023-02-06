#include <itertools-cpp/chunker.hpp>

namespace {

template <class Container>
auto MakeChunksClosure(Container&& container, size_t chunk_size) {
  return itertools_cpp::MakeChunks<itertools_cpp::ChunkerType::ListOfPairs>(
      std::forward<Container>(container), chunk_size);
};

}  // namespace

#include <itertools-cpp/impl/test_template.hpp>
