#include "test_tourist_blocks_storage.h"

namespace NMordaBlocks {

    TTestTouristBlocksStorage::TTestTouristBlocksStorage() {
        SetForTests(this);
    }

    TTestTouristBlocksStorage::~TTestTouristBlocksStorage() {
        SetForTests(nullptr);
    }

    bool TTestTouristBlocksStorage::IsTouristBlock(const TString& blockName) const {
        return TouristBlocks_.contains(blockName);
    }

    bool TTestTouristBlocksStorage::IsReady() const {
        return true;
    }

    void TTestTouristBlocksStorage::Start() {
    }

    void TTestTouristBlocksStorage::BeforeShutDown() {
    }

    void TTestTouristBlocksStorage::ShutDown() {
    }

    TString TTestTouristBlocksStorage::GetServiceName() const {
        return "TestTouristBlocksStorage";
    }

    void TTestTouristBlocksStorage::Reset() {
        TouristBlocks_.clear();
    }

    void TTestTouristBlocksStorage::MakeTourist(const TString& blockName) {
        TouristBlocks_.insert(blockName);
    }

    void TTestTouristBlocksStorage::MakeNotTourist(const TString& blockName) {
        TouristBlocks_.erase(blockName);
    }

}  // namespace NMordaBlocks
