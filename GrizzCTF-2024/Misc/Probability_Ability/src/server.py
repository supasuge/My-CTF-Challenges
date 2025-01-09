import socketserver
import logging
import os

def show_banner():
    banner = b"""
----------------------------------------------------------------------------------    
| :'######:::'########::'####:'########:'########::'######::'########:'########: |
| '##... ##:: ##.... ##:. ##::..... ##::..... ##::'##... ##:... ##..:: ##.....:: |
|  ##:::..::: ##:::: ##:: ##:::::: ##::::::: ##::: ##:::..::::: ##:::: ##::::::: |
|  ##::'####: ########::: ##::::: ##::::::: ##:::: ##:::::::::: ##:::: ######::: |
|  ##::: ##:: ##.. ##:::: ##:::: ##::::::: ##::::: ##:::::::::: ##:::: ##...:::: |
|  ##::: ##:: ##::. ##::: ##::: ##::::::: ##:::::: ##::: ##:::: ##:::: ##::::::: |
| . ######::: ##:::. ##:'####: ########: ########:. ######::::: ##:::: ##::::::: |
| :......::::..:::::..::....::........::........:::......::::::..:::::..:::::::: |
----------------------------------------------------------------------------------\n\n\n"""
    return banner

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FlagHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.sendall(show_banner())
        self.request.sendall(b"Enter the answer: ")

        answer = self.request.recv(1024).decode().strip()

        logging.info(f"Received answer: {answer}")

        try:
            with open("ans.txt", "r") as f:
                correct_answer = f.read().strip()
        except FileNotFoundError:
            logging.error("ans.txt not found")
            self.request.sendall(b"ans.txt not found. Unable to verify answer.")
            return

        if answer == correct_answer:
            try:
                with open("flag.txt", "r") as f:
                    flag = f.read().strip()
            except FileNotFoundError:
                logging.error("flag.txt not found")
                self.request.sendall(b"flag.txt not found. Unable to send flag.")
                return

            self.request.sendall(flag.encode())
        else:
            self.request.sendall(b"Wrong answer. Try again.")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

def run_server(host, port):
    with ThreadedTCPServer((host, port), FlagHandler) as server:
        logging.info(f"Server starting on {host}:{port}")
        server.serve_forever()

def main():
    HOST = os.getenv('SERVER_HOST', 'localhost')
    PORT = int(os.getenv('SERVER_PORT', 9999))
    run_server(HOST, PORT)

if __name__ == "__main__":
    main()
