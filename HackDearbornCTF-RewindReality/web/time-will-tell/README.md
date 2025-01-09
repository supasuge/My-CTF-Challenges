# CHANGE_ME_6

## Description

Flask API with a protected endpoint that contains a timing attack vulnerablity due to how `strcmp` is written and the slight sleep set (19 ms) during the string comparison.

## Dist
- `chal.tar.xz`

## Build

```sh
cd time-will-tell/build
docker build -t time-will-tellv0.1 .
```

## Run

```sh
docker run -d -p 8000:8000 time-will-tellv0.1
```

### Solution
[solution/solve.py](./solution/solve.py)
