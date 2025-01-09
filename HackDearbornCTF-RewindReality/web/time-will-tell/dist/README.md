# Time will tell
- Web

## Build
- Need docker properly installed

```bash
cd time-will-tell/build
docker build -t time-tellv0.1 .
```


## Run
- Port for challenge exposed on port `8000`.

```bash
docker run -d -p 8000:8000 time-tellv0.1
```

Connect: `172.17.0.2`:`8000` once container is running if you want to test locally before trying your solution on the remote instance.

- It's preferred you do this so as not to put a heavy load on the container's network bandwidth, thus the rate-limiting put in place. This reasoning behind this will be clear when you have solved the challenge and understand how critical the response times can be....