#pragma once

#include <taxi/graph/libs/graph/gps_signal.h>

#include <util/generic/string.h>

#include <vector>

namespace NTaxi::NGraph2 {
    /// Loads test signals from given file, in json format
    std::vector<NTaxi::NGraph2::TGpsSignal> LoadSignalsFromFile(
        const TString& filename, bool noSpeed = false);

}
