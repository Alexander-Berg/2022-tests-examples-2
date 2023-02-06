#pragma once

#include <util/generic/fwd.h>
#include <util/generic/noncopyable.h>
#include <util/folder/path.h>

namespace NJson {
    class TJsonValue;
}

namespace NMordaBlocks {
    namespace NTest {

        extern const TFsPath LOCAL_TEST_DATA_PATH;
        extern const TFsPath LOCAL_RESOURCES_DATA_PATH;

        class TGeobaseDataWrapper : public TMoveOnly {
        public:
            // Geobase resource (sbr://361769539) must be declared in every test project,
            // it's used. pathToSandboxResource should be equal to GetWorkPath()) / "geodata5.bin".
            explicit TGeobaseDataWrapper(const TFsPath& pathToSandboxResource);
            virtual ~TGeobaseDataWrapper();

            TString GetName() const;
        private:
            TFsPath TestDataFile_;
        };

    } // NTest
} // NMordaBlocks
