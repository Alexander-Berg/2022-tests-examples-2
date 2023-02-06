#pragma once

#include <apphost/api/service/cpp/service_context.h>

#include <util/folder/path.h>
#include <util/generic/map.h>
#include <util/generic/noncopyable.h>
#include <util/generic/strbuf.h>
#include <util/generic/vector.h>

#include <memory>

namespace NJson {
    class TJsonValue;
}

namespace NMordaBlocks {

    namespace NTest {
        class TTestBlockDataProvider;
    } // namespace NTest

    class TBlockBase;
    class TConfig;
    class TCore;
    class TBaseBlockEnvironment;
    class TTestGeoBase;
    class TTestStatisticsCollector;
    class TTestHttpResponder;

    class TTestBlockRunner : public TNonCopyable {
    public:
        TTestBlockRunner();
        virtual ~TTestBlockRunner();

        void InitEnvironment();

        void SetConfigValue(TStringBuf section, TStringBuf param, const NJson::TJsonValue& value);
        void SetConfigFilePath(TStringBuf section, TStringBuf param, const TFsPath& filePath);
        void SetConfigFileData(TStringBuf section, TStringBuf param, TString data);

        void SetHttpOkResponse(TStringBuf httpResourceId, TString data);

        void AddBlock(std::unique_ptr<TBlockBase> block);
        virtual void Start();

        // ThreadSafe.
        void ProcessRequest(NAppHost::TServiceContextPtr context);

        const TVector<TString>& AddedBlockNames() {
            return AddedBlockNames_;
        }

        TTestGeoBase* TestGeoBase() {
            return TestGeoBase_.get();
        }

        TTestStatisticsCollector* TestStatisticsCollector() {
            return TestStatisticsCollector_;
        }

        void SetThreadCount(size_t threadCount);

        size_t ThreadCount() const {
            return ThreadCount_;
        }

    protected:
        const TVector<std::unique_ptr<TBlockBase>>& Blocks() const;

    private:
        class TTestBlockEnvironment;
        std::unique_ptr<TCore> TestCore_;
        std::unique_ptr<TConfig> TestConfig_;
        std::unique_ptr<NTest::TTestBlockDataProvider> TestDataProvider_;
        std::unique_ptr<TTestGeoBase> TestGeoBase_;
        std::unique_ptr<TTestHttpResponder> TestHttpResponder_;
        std::unique_ptr<TTestBlockEnvironment> Environment_;
        TTestStatisticsCollector* TestStatisticsCollector_ = nullptr;
        TVector<TString> AddedBlockNames_;
        size_t ThreadCount_ = 1;
        TMap<TString, TString> AppHostHttpResponses_;
    };

} // namespace NMordaBlocks
