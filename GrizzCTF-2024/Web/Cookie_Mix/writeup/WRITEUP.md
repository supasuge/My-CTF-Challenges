# Cookie Mix

**Description:** I made a super secure login using my own encryption scheme. Can you bypass authorization using a forged cookie somehow? Bypass the login page as the `admin` get the flag.



Note that everytime you reload or access the page the cookie will look different because it is being signed with a different secret key. Make sure to not reload your page while working on this challenge. Knowing this now we can now sign a new cookie with the value of admin for "very_auth" as such:



![Solution](image-1.png)





To solve this challenge, simply use: [flask-session-cookie-manager](https://github.com/noraj/flask-session-cookie-manager) to forge a signed cookie as the `admin` user to get the flag. 



