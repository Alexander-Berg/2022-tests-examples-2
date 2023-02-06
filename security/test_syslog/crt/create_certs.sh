#!/bin/bash

# Create root CA
openssl genrsa -out /crt/root.key 2048
openssl req -new -x509 -days 3653 -key /crt/root.key -out /crt/root.crt -config /crt/config/root.cnf

# Create server cert
openssl req -new -sha256 -nodes -newkey rsa:2048 \
    -config /crt/config/server.cnf \
    -keyout /crt/server.key \
    -out /tmp/server.csr

openssl x509 -req -sha256 -days 1100 \
    -extfile /crt/config/server.cnf \
    -CA /crt/root.crt \
    -CAkey /crt/root.key -CAcreateserial \
    -in /tmp/server.csr \
    -out /crt/server.crt
