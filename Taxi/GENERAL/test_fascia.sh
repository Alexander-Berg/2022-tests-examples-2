#!/usr/bin/env bats

# docker sockets issue makes us to do |sudo docker ...|
S=sudo

@test "example test works really" {
  result="$(echo 2+2 | bc)"
  [ "$result" -eq 4 ]
}

@test "example test of command" {
  run cat nonexistent_filename
  [ "$status" -eq 1 ]
  [ "$output" = "cat: nonexistent_filename: No such file or directory" ]
}

@test "docker nginx process starts" {
  $S make start_dbn
  result="$($S docker ps | grep -E 'nginx.*Up')"
  [ -n "$result" ]
  $S make stop_dbn
}

@test "nginx serves" {
  $S make start_dbn
  result=$(curl localhost:80 | grep nginx)
  [ -n "$result" ]
  $S make stop_dbn
}

@test "db starts" {
  $S make start_dbn
  WAIT_CMD='make wait-db DB_TIME_LIMIT=5 DB_HOST=localhost'
  result=$($WAIT_CMD | grep 'DB is ready')
  [ -n "$result" ]
  $S make stop_db
}

@test "python tests run" {
  S=sudo
  $S make start_dbn
  source ~/.profile
  sudo mkdir -p /var/www
  sudo chown -R woody:woody /var/www
  pyenv activate woody
  #
  python woody/initialize.py
  result="$(make test-lavka-small)"
  errors="$(echo $result | grep ERROR || true)"
  [ -n "$result" ]
  [ -z "$errors" ]
  #
  pyenv deactivate woody
  $S make stop_dbn
}
