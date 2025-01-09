# Arigato Mr.Roboto

**Description:** What I wouldn't give to be normal. To live in that bubble. Reality of the naive.

This is a quote directly from Mr.Robot, this is the hint towards solving the challenge. 



## Build/Deploy instructions.
1. `cd src/app`
2. Build the container:
```bash
docker build -t arigato-mrroboto .
```
3. Run the container:
```bash
docker container run -p 8000:8000 -dit --name arigato arigato-mrroboto:latest
```


###### Challenge 
![site](./solution/image.png)