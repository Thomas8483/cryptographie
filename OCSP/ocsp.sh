#!/bin/bash

#lancement du serveur ocsp
openssl ocsp -index index.txt -port 8888 -rsigner ocsp.crt -rkey ocsp.key -CA ../ACI/intermediate_ca.crt -text -out log.txt
