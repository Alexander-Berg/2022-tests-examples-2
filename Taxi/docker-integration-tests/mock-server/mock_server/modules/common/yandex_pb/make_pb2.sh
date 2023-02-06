#!/bin/bash

printf 'common2\n'
protoc --python_out=. --proto_path=. --proto_path=yandex/maps/proto/common2/ yandex/maps/proto/common2/*.proto

printf 'road_event\n'
protoc --python_out=. --proto_path=. --proto_path=yandex/maps/proto/road_events/ yandex/maps/proto/road_events/*.proto

printf 'driving\n'
protoc --python_out=. --proto_path=. --proto_path=yandex/maps/proto/driving/ --proto_path=yandex/maps/proto/common2/ yandex/maps/proto/driving/*.proto
