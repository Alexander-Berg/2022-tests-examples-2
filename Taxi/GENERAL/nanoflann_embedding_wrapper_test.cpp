#include <nanoflann/nanoflann_embedding_wrapper.hpp>

#include <gtest/gtest.h>

namespace utils::nanoflann::tests {

template <class TEmbedding>
class SearchProcessor {
 public:
  void Process(const TEmbedding& embedding) { results_.push_back(embedding); }

  size_t Size() const { return results_.size(); }

 private:
  std::vector<TEmbedding> results_;
};

template <class TEmbedding, class TDistance>
class SearchCallback {
 public:
  SearchCallback(const std::vector<TEmbedding>& embeddings,
                 TDistance max_distance, SearchProcessor<TEmbedding>& processor)
      : embeddings_(embeddings),
        max_distance_(max_distance),
        processor_(processor) {}

  TDistance worstDist() const { return max_distance_; }

  bool full() const { return false; }

  size_t size() const { return processor_.Size(); }

  bool addPoint(double /* dist */, size_t index) {
    processor_.Process(embeddings_[index]);
    return true;
  }

 private:
  const std::vector<TEmbedding>& embeddings_;
  TDistance max_distance_;
  SearchProcessor<TEmbedding>& processor_;
};

TEST(EasyEmbeddingKDTree, EasyEmbeddingKDTree) {
  using TEmbeddingComponent = int;
  const int EmbeddingSize = 2;
  using TEmbedding = std::array<TEmbeddingComponent, EmbeddingSize>;
  std::vector<TEmbedding> embeddings;
  embeddings.push_back({0, 0});
  embeddings.push_back({10, 10});
  embeddings.push_back({11, 11});

  auto kd_tree =
      utils::nanoflann::EasyEmbeddingKDTree<TEmbedding, TEmbeddingComponent,
                                            EmbeddingSize>(embeddings);
  kd_tree.BuildIndex();

  int search_distance = 2;
  SearchProcessor<TEmbedding> processor;
  SearchCallback<TEmbedding, TEmbeddingComponent> callback(
      embeddings, search_distance, processor);
  TEmbedding search_embedding({10, 11});
  kd_tree.Search(search_embedding, callback);
  ASSERT_EQ(processor.Size(), 2);
}

}  // namespace utils::nanoflann::tests
