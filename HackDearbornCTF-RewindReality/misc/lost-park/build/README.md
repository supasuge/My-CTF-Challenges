# Lost Park

OSINT challenge

## Dist
- `dist/image.png`


## Build
Have tried rust server, rust stdio binary that runs over `socat` to forward stdin/out over TCP, and both in python. CTFd just wont gimme a mf port smh. unlucky


## Run

```sh
cd build/
docker build -t lost-park .
docker run -d -p 9494:9494 --rm lost-park
```
