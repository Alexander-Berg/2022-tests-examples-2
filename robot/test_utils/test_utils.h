#pragma once

#include <util/generic/array_ref.h>


namespace NMelter {
    bool SanityCheckErfContent(const TArrayRef<const char>& erfLump, const ui64 zDocId);
    bool SanityCheckErfContent(const TString& erfBlob, const ui64 zDocId);
}
