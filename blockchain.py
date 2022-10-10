import datetime
import hashlib
from binascii import unhexlify, hexlify
import pprint
import time
import json
import os
import multiprocessing
from threading import Thread

# https://habr.com/ru/post/561914/
# https://www.youtube.com/watch?v=_160oMzblY8
# https://ethereum.org/en/developers/docs/intro-to-ethereum/
# https://github.com/anders94/blockchain-demo


class BlockChain():

    def __init__(self, prev_hash, transaction, amount):
        self.next = None
        time = str(datetime.datetime.now())
        self.__data = {
            "amount": amount,
            "hash": "",
            "prev_hash": prev_hash,
            "time": time,
            "transaction": transaction,
        }
        hash = self.make_hash()
        self.__data["hash"] = hash
        write_block(amount, hash, time, transaction, prev_hash)

    def get_data(self):
        return self.__data

    def append(self, transaction, amount):
        n = self
        while n.next:
            n = n.next
        prev_hash = n.get_data()["hash"]
        end = BlockChain(prev_hash, transaction, amount)
        n.next = end

    def to_hash256(self, string):
        return hexlify(hashlib.sha256(unhexlify(string)).digest()).decode("utf-8")

    def to_hash512(self, string):
        return hexlify(hashlib.sha512(unhexlify(string)).digest()).decode("utf-8")

    def to_hashmd5(self, string):
        return hashlib.md5(string.encode()).hexdigest()

    def make_hash(self):
        difficulty = 4
        s = 0
        start = time.time()
        test_hash = self.to_hash512(self.get_data()["prev_hash"])
        while test_hash[:difficulty] != "0" * difficulty:
            test_hash = self.to_hash512(test_hash)
            s = s + 1
        finist = time.time() - start
        # print(test_hash)
        # print(finist)
        # print('iter', s)
        return test_hash


def print_blocks(block):
    node = block
    pprint.pprint(node.get_data())
    while node.next:
        node = node.next
        pprint.pprint(node.get_data())


def generate(i):
    file_data = get_last_file_data()

    chain = BlockChain(
        file_data["hash"], 'Kolya', 153)
    chain.append('Pety', 1044)
    chain.append('Masa', 1120)
    chain.append('Ira', 1120)
    print_blocks(chain)


def multithread():
    thread_pool = []
    for i in range(5):
        th = Thread(target=generate, args=(i,))
        th.start()
        thread_pool.append(th)

    for th in thread_pool:
        th.join()


def multiproc():
    process_pool = []
    for i in range(5):
        t = multiprocessing.Process(target=generate, args=(i,))
        t.start()
        process_pool.append(t)
    for t in process_pool:
        t.join()


blockchain_dir = "chain\\"


def get_files():
    return os.listdir(path=blockchain_dir)


def get_last_file_data():
    files = get_files()
    last_file = files[-1]
    with open(blockchain_dir+last_file) as json_file:
        data = json.load(json_file)
        return data


def get_hash(filepath):
    with open(blockchain_dir+filepath) as json_file:
        data = json.load(json_file)
        return data['hash']


def write_block(amount, hash, time, transaction, prev_hash=''):
    files = get_files()
    prev_file = str(files[-1])
    prev_file_num = int(prev_file[:-5])
    filename = str(prev_file_num + 1) + '.json'
    prev_hash = get_hash(str(prev_file))

    data = {
        'amount': amount,
        'hash': hash,
        'prev_hash': prev_hash,
        'time': time,
        'transaction': transaction,
    }

    with open(blockchain_dir + filename, 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
        return prev_hash


def check_integrity():
    files = get_files()
    result = []
    for file in files[1:]:
        hash_in_file = json.load(open(blockchain_dir + str(file)))['hash']
        prev_file_num = int(file[:-5])
        prev_file = str(prev_file_num) + '.json'
        hash_in_prev_file = get_hash(prev_file)
        if hash_in_file == hash_in_prev_file:
            res = True
        else:
            res = False
        result.append({'block': prev_file, 'result': res})
    return result


if __name__ == '__main__':
    # multiprocessing.freeze_support()
    # start_time = time.time()
    # multiproc()
    # print("--- %s seconds ---" % (time.time() - start_time))
    # start_time = time.time()
    # multithread()
    # print("--- %s seconds ---" % (time.time() - start_time))

    generate(1)
