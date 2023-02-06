import json
import requests
import six


class Sensors:
    def __init__(self, data):
        self.data = data

    def find_sensor(self, labels):
        found = None
        for s in self.data:
            lbls = s["labels"]
            has_all_labels = all(lbls.get(k, None) == v for k, v in six.iteritems(labels))
            if not has_all_labels:
                continue
            new_found = s
            if found is not None:
                raise Exception("Multiple sensors matches for labels {}: {} and {}".format(labels, found, new_found))
            found = new_found

        return found["value"] if found is not None else None

    def collect_non_zeros(self):
        return [s for s in self.data if s["value"] != 0]

    def __str__(self):
        return str(self.data)


def load_json_sensors(url):
    response = requests.get(url)
    response.raise_for_status()
    data = json.loads(response.text)
    sensors = data.get("metrics")
    if sensors is None:
        sensors = data.get("sensors", [])
    return Sensors(sensors)
