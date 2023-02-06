# Test script, which uses taxi-atlas-backend-router environment (python3)

import sys
import atlas.domain.anomaly as anomalies

if __name__ == '__main__':
    if sys.version_info.major != 3:
        raise RuntimeError(f'Wrong python version: {sys.version}')

    print(
        'Anomalies to notify: {}'.format(
            len(anomalies.get_storage().get_anomalies_to_notify()),
        ),
    )
