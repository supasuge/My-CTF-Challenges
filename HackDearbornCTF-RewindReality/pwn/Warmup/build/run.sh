#!/bvin/bash
socat -T60 TCP-LISTEN:6000,reuseaddr,fork EXEC:"timeout 60 ./challenge"