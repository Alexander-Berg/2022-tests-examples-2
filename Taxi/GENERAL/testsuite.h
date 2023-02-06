#pragma once

#include <taxi/logistic-dispatcher/library/testsuite/client.h>

namespace testsuite {
    void EnableTestpoint(const TTestsuiteClient *client);
    void DisableTestpoint();
}
