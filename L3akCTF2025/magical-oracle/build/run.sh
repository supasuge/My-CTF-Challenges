#!/usr/bin/env bash
exec socat \
    TCP-LISTEN:1338,reuseaddr,fork \
    EXEC:"python3 /opt/app/chal.py",pty,stderr,setsid,sigint,sane
