#pragma once

#include <string>

namespace fastcgi {
class ComponentContext;
}

namespace utils {
namespace testsuite {

void SetHttpClientTimeoutMs(int timeout_ms);
int GetHttpClientTimeoutMs();

bool GetPeriodicalUpdateDisabled(fastcgi::ComponentContext* ccontext);

void SetMockserverUrl(const std::string& url);
void CheckHttpUrl(const std::string& url);

}  // namespace testsuite
}  // namespace utils
