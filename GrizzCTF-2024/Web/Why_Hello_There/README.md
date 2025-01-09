# Why Hello There (500 Points)
This challenge presents the participant with a single file `app.py`. This site is live on port `2222`. The vulnerability in this challenge lies within the parameter `{name}` and the lack of input escaping/sanitization.

To identify the possible SSTI parameter send the following:

```
?name={{7*7}}
```

The payload above should change the `name` parameter to `49`.


##### Build/Deploy
1. cd into the correct directory
`cd Why_Hello_There\src\app`
2. Build the container
`docker build -t why-hello-there .`
3. Deploy the container
`docker run -dit -p 2222:2222 --name why-hello-there why-hello-there:latest`
