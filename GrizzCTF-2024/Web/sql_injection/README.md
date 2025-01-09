# SQLi

**Description:** This challenge presents a simple SQL injection challenge. 
#### Build/Deployment instructions
1. cd into the correct directory (`src/app`)
`cd sql_injection\src\app`
2. Build the container
`docker build -t sql-injection .`
3. Run the container
`docker run -dit -p 9000:9000 --name sql-injection sql-injection:latest`


