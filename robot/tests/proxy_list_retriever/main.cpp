#include <robot/saved_copy/server/src/lib/connection_pool/proxy_list_retriever.h>
#include <robot/saved_copy/server/src/lib/event_support/helpers.h>

#include <memory>

using namespace NSavedCopy;

void OnTimeout(int /*fd*/, short /*event*/, void* arg) {
    Cerr << "Cannot read data before timeout" << Endl;
    event_base_loopbreak(static_cast<event_base*>(arg));
}

int main() {
    auto eventBase = NEvent::CreateEventBase();
    auto dnsBase = NEvent::CreateDnsBase(eventBase.get());

    TProxyListRetriever retriever(eventBase.get(), dnsBase.get(), "banach.yt.yandex.net:80");
    retriever.Retrieve(
        [eventBase = eventBase.get()] (const TProxyListRetriever& retriever, TProxyListRetriever::EError error)
        {
            if (error == TProxyListRetriever::EError::No) {
                for (const auto& endpoint : retriever.GetEndpoints()) {
                    Cout << endpoint.Host << ':' << endpoint.Port << Endl;
                }
            } else {
                Cerr << "Error while retrieving proxy list" << Endl;
            }
            event_base_loopbreak(eventBase);
        });

    auto timer = evtimer_new(eventBase.get(), OnTimeout, eventBase.get());
    timeval timeout = {10, 0};
    evtimer_add(timer, &timeout);

    event_base_dispatch(eventBase.get());

    Cout << "Program finishes";

    return 0;
}

