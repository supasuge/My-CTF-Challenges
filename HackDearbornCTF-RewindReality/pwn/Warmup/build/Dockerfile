# Use an Alpine base image for a small footprint
FROM alpine:latest

# Install socat for networking
RUN apk add --no-cache socat
WORKDIR /challenge
# Copy the binary and flag file to the container
COPY challenge /challenge/binary
COPY flag.txt /challenge/flag.txt

# Set working directory


# Ensure binary has execute permissions
RUN chmod +x /challenge/binary

# Expose port 6000
EXPOSE 6000

# Run socat to listen on port 6000 and forward connections to the binary
CMD ["socat", "TCP-LISTEN:6000,reuseaddr,fork", "EXEC:./binary"]
