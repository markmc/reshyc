#!/bin/bash

[ "$#" -eq 0 ] && { echo "usage: $0 <files>"; exit 1; }
[ -z "${FTP_SERVER}" -o -z "${FTP_USER}" -o -z "${FTP_PASSWORD}" ] && { echo "FTP_SERVER, FTP_USER, and FTP_PASSWORD must be set"; exit 1; }

ftp -n "${FTP_SERVER}" <<EOF
quote USER ${FTP_USER}
quote PASS ${FTP_PASSWORD}
binary
glob
prompt
cd reshyc/
mput $@
quit
EOF
