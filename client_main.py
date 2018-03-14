import requests


def main():
    f = open('S001R01.edf', 'rb')
    data = f.read()
    f.close()
    res = requests.post("http://127.0.0.1:50000", data)
    print res.content


main()