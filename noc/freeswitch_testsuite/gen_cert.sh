#!/bin/sh

# make local CA and add its key to trust
echo "Create and install to trust mock CA certificate"
mkdir -p cert/CA
cd cert/CA
openssl req -new -newkey rsa:2048 -nodes -out CA.csr -keyout CA.key -config ../../tmpl_ca.ext
openssl x509 -trustout -signkey CA.key -days 1 -req -in CA.csr -out CA.pem

if [ -f '/usr/local/share/ca-certificates/mock.crt' ]; then
    rm /usr/local/share/ca-certificates/mock.crt
    update-ca-certificates -f
fi
cp CA.pem /usr/local/share/ca-certificates/mock.crt
update-ca-certificates

echo "Create Mock-signed server certificate and key"
# make certificate for localhost
cd ../
openssl genrsa -out server.key
openssl req -new -key server.key -out server.csr -config ../tmpl_server.ext
openssl x509 -req -in server.csr -CA CA/CA.pem -CAkey CA/CA.key -CAcreateserial -days 1 -sha256 -extfile ../tmpl_server.ext -out server.crt
cd ../

