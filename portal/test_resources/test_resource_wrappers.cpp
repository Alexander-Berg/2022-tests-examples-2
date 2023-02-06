#include "test_resource_wrappers.h"

#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/tests_data.h>

#include <util/generic/string.h>

namespace NMordaBlocks {
    namespace NTest {
        namespace {
            const TFsPath ARCADIA_TESTS_DATA = GetArcadiaTestsData();
            constexpr bool USE_SANDBOX = true;
        }

        const TFsPath LOCAL_TEST_DATA_PATH = TFsPath(ArcadiaSourceRoot()) / "portal" / "morda" / "blocks" / "test_resources" / "data";
        const TFsPath LOCAL_RESOURCES_DATA_PATH = TFsPath(ArcadiaSourceRoot()) / "portal" / "morda" / "blocks" / "resources" / "resources";

        TGeobaseDataWrapper::TGeobaseDataWrapper(const TFsPath& pathToSandboxResource)
            : TestDataFile_(USE_SANDBOX ? pathToSandboxResource : ARCADIA_TESTS_DATA / "geo/geodata5.bin")
        {
        }

        TGeobaseDataWrapper::~TGeobaseDataWrapper() = default;

        TString TGeobaseDataWrapper::GetName() const {
            return TestDataFile_;
        }

    } // NTest
} // NMordaBlocks
