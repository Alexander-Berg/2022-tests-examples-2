#!/bin/sh

CLOUDAPI_COMMON=../../../../cloud/bitbucket/common-api
CLOUDAPI_PUBLIC=../../../../cloud/bitbucket/public-api
if [ ! -d "$CLOUDAPI_PUBLIC" ] || [ ! -d "$CLOUDAPI_COMMON" ]; then
    echo "Please arc checkout cloud/bitbucket"
    exit 1
fi

python3.8 -m grpc.tools.protoc  \
  -I$CLOUDAPI_COMMON -I$CLOUDAPI_PUBLIC -I$CLOUDAPI_PUBLIC/third_party/googleapis \
  --python_out=. --grpc_python_out=. \
  google/api/http.proto google/api/annotations.proto google/rpc/status.proto \
  yandex/cloud/api/operation.proto yandex/cloud/operation/operation.proto \
  yandex/cloud/ai/stt/v2/stt_service.proto yandex/cloud/api/tools/options.proto \
  yandex/cloud/ai/tts/v3/tts_service.proto yandex/cloud/ai/tts/v3/tts.proto
