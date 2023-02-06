#include "test_utils.h"

#include <robot/melter/library/erf/erf.h>

#include <kernel/urlid/urlhash.h>


namespace NMelter {
    namespace {
        ui64 CalculateZDocId(const NJupiter::SDocErf2InfoProto& erfProto) {
            return PackUrlHash64(erfProto.GetUrlHash1(), erfProto.GetUrlHash2());
        }
    }

    bool SanityCheckErfContent(const TArrayRef<const char>& erfLump, const ui64 zDocId) {
        const TString erf{erfLump.data(), erfLump.size()};
        return SanityCheckErfContent(erf, zDocId);
    }

    bool SanityCheckErfContent(const TString& erfBlob, const ui64 zDocId) {
        const NJupiter::SDocErf2InfoProto erfProto = ParseErfBlob(erfBlob);
        return CalculateZDocId(erfProto) == zDocId;
    }
}
