#!/usr/bin/env bats

# Requires the bats tool to be installed
# https://github.com/sstephenson/bats#installing-bats-from-source

# Test service responses for Cache-Control header.
# Behaviour:
# - Static files like "/1.1.10-76-gfd52c8c/index.js" should have cache header
# - Every other location like "/" (site root) or /index.html should NOT have cache header


export CACHE_HEADER='Cache-Control: max-age=1728000, private'
export NO_CACHE_HEADER='Cache-Control: no-store, no-cache, must-revalidate'

# use sed because the docker-compose command appends strange ^M character to result
export VERSION=$(docker-compose exec picker-nginx make version | sed -E s/\\r//)

@test 'site root has no cache' {
  export RESPONSE="$(curl -i http://localhost:8080/ 2>/dev/null | head -n 20 | grep "$NO_CACHE_HEADER" | sed -E s/\\r//)"
  [ "$NO_CACHE_HEADER" = "$RESPONSE" ]
}

@test 'index.html has no cache' {
  export RESPONSE="$(curl -i http://localhost:8080/index.html 2>/dev/null | head -n 20 | grep "$NO_CACHE_HEADER" | sed -E s/\\r//)"
  [ "$NO_CACHE_HEADER" = "$RESPONSE" ]
}

@test 'version.json has no cache' {
  export RESPONSE="$(curl -i http://localhost:8080/version.json 2>/dev/null | head -n 20 | grep "$NO_CACHE_HEADER" | sed -E s/\\r//)"
  [ "$NO_CACHE_HEADER" = "$RESPONSE" ]
}

@test 'a file under version has cache' {
  export RESPONSE="$(curl -i http://localhost:8080/$VERSION/index.js 2>/dev/null | head -n 20 | grep "$CACHE_HEADER" | sed -E s/\\r//)"
  [ "$CACHE_HEADER" = "$RESPONSE" ]
}
