import requests
import json

load_registry_url = "http://logistic-platform.taxi.yandex.net/api/staff/employer/load_registry/?employer_code=yak&ignore_header=true&separator=%3B&serialize_to_json=true"
offer_create_url = "http://logistic-platform.taxi.yandex.net/api/b2b/platform/offers/create"
offer_confirm_url = "http://logistic-platform.taxi.yandex.net/api/b2b/platform/offers/confirm"

errors = open("registry_errors", "w+")
registry = open('registry.csv', 'rb')
failed = set()
success = set()

headers = {
  'Content-Type': 'text/csv'
}

print('start')
response = requests.request("POST", load_registry_url, headers=headers, data=registry)
print('finish')
for report in response.json()["report"]["requests"]:
    if "has_errors" in report and report["has_errors"]:
        print('start')
        errors.write(report["request_code"] + " : " + report["errors"][0]["description"])
        failed.add(report["request_code"])
        print('failed: ' + report["request_code"])

for offer in response.json()["offers"]:
    request_code = offer["info"]["operator_request_id"]
    if request_code in failed:
        continue
    headers = {
        'X-Ya-Service-Ticket': '3:serv:CJ2kARDTrPaRBiIICMWsexDhxXs:C2R3HkMWtBe1kXtSMqOG15HE5k_FfaG5O5_5-eSeRPqd6efOoR5pV_HWsptjNESoBJLJNEz551wMyOdUKk9L7M1Mdhu7a_vS5IsqyEpEbl3H0xillfnNacXq5L-UP8kmDidjWuKC6E4DaeL7TIftGCbgi2XWIbJmurMU4zoigDVQte3sJKH_Lsi4y6s4D4jt7izstnG16WKlpZSQvEaN06AUz6jMpolZ373fICatsfJE26gQ7dZsMzyz-WOxToAp2U0Fc-OasVX9wjUy_I_TuOR3Clp94nbxeI9a24BewfQUAJSooeqk051IHJXsAwi1v8JLIMQQU5668V7nkN0dlw',
        'X-B2B-Client-Id': '5ca6637ad5b041b8ba04776510dbd6c4',
        'Content-Type': 'application/json'
    }
    off_response = requests.request("POST", offer_create_url, headers=headers, data=json.dumps(offer))
    print(json.dumps(offer))
    print(off_response.content)
    if "offers" in off_response.json() and off_response.json()["offers"].size() and "offer_id" in off_response.json()["offers"][0]:
        conf_response = requests.request("POST", offer_confirm_url, headers=headers, data={"offer_id": off_response.json()["offers"][0]["offer_id"]})
        if "request_id" in conf_response.json():
            print(request_code, ':', conf_response.json()["request_id"])
            success.add(request_code)
        else:
            errors.write(request_code + ' : ' + conf_response.text)
            failed.add(request_code)
    else:
        errors.write(request_code + ' : ' + off_response.text)
        failed.add(request_code)
    print("SUCCESS:", len(success), "|", "FAILED:", len(failed))
