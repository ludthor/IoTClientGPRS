from app .Client import Client


def main():
    client = Client()
    client.loop()

if __name__ == '__main__':
    print("Starting agroriego client application...")
    main()
