#include <userver/utest/utest.hpp>

#include <eventus/sources/source_wrapper.hpp>

namespace {

class DummySource : public eventus::pipeline::Source {
 public:
  DummySource() : Source("dummy-source") {}
  virtual ~DummySource() = default;

  bool PopNoBlock(std::vector<eventus::pipeline::PipelineItem>& /*msg*/,
                  size_t /*max_bulk*/) override {
    return false;
  };
  bool Pop(std::vector<eventus::pipeline::PipelineItem>& /*msg*/,
           engine::Deadline /*deadline*/ = {}) override {
    return false;
  };
  /// message has been processed and can be committed to a source
  void Commit(eventus::pipeline::SeqNum /*msg*/) override{};

  // Used for testsuite purposes only
  void TestsuiteInvalidate() override{};
};

}  // namespace

UTEST(SourceWrapper, Test) {
  eventus::pipeline::SourceUPtr source = std::make_unique<DummySource>();
  const auto origin_source_ptr = source.get();
  {
    auto wrapper = std::make_unique<eventus::sources::SourceWrapper>(
        [&source](eventus::pipeline::SourceUPtr origin_source) {
          source = std::move(origin_source);
        },
        std::move(source));
    ASSERT_EQ(source.get(), nullptr);
  }
  ASSERT_EQ(source.get(), origin_source_ptr);
}
