#pragma once

#include <portal/morda/blocks/services/tourist_blocks_storage/tourist_blocks_storage.h>

#include <util/generic/set.h>

#include <memory>

namespace NMordaBlocks {

    class TTestTouristBlocksStorage : public ITouristBlocksStorage {
    public:
        TTestTouristBlocksStorage();
        ~TTestTouristBlocksStorage() override;

        bool IsTouristBlock(const TString& blockName) const override;

        // IService overrides:
        bool IsReady() const override;
        void Start() override;
        void BeforeShutDown() override;
        void ShutDown() override;
        TString GetServiceName() const override;

        void Reset();
        void MakeTourist(const TString& blockName);
        void MakeNotTourist(const TString& blockName);

    private:
        TSet<TString> TouristBlocks_;
    };

} // namespace NMordaBlocks
