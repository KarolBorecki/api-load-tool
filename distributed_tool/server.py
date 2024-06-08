from multiprocessing.managers import BaseManager
import queue, sys, os


class QueueManager(BaseManager):
    pass


def main(ip_address: str, port: int, password: bytes) -> None:
    in_queue = queue.Queue()
    out_queue = queue.Queue()

    QueueManager.register("in_queue", callable=lambda: in_queue)
    QueueManager.register("out_queue", callable=lambda: out_queue)

    manager = QueueManager(address=(ip_address, port), authkey=password)

    print(f"Server started at {ip_address}:{port}")

    server = manager.get_server()
    server.serve_forever()


def validate_input(ip_address: str, port: int) -> None:
    if port <= 0:
        print("Port must be greater than 0")
        sys.exit(1)

    if not ip_address:
        print("IP address must be provided")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python my_server.py [ip address] [port]")
        sys.exit(1)

    ip_address, port = sys.argv[1:3]
    validate_input(ip_address, int(port))
    password = os.environ.get('AUTHKEY', "test")
    if password is None:
        print("AUTHKEY must be provided in environment variables")
        sys.exit(1)
    main(ip_address=ip_address, port=int(port), password=bytes(password, 'utf-8'))
