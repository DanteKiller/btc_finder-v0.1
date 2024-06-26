import numpy as np
from ecdsa import SigningKey, SECP256k1
import hashlib
from hashlib import sha256
import base58
import time, os, datetime
import concurrent.futures
from ranges import ranges
from colorama import init, Fore, Back

init()  # Initialize colorama

DEFAULT_VERSIONS = {
    'public': 0x00,
    'private': 0x80
}

ec_key = None
_versions = None
start_time = 0.0
segundos = 0

wallets_array = [line.strip() for line in open('wallets.txt', 'r').readlines()]
WALLET_SET = set(wallet.encode() for wallet in wallets_array)

def CoinKey(private_key, versions=None):
    global _versions, ec_key
    _versions = versions or DEFAULT_VERSIONS.copy()
    ec_key = SigningKey.from_string(private_key, curve=SECP256k1)

def public_address():
    global ec_key
    vk = ec_key.get_verifying_key()
    public_key = vk.to_string("compressed")
    sha256_hash = sha256(public_key).digest()
    ripemd160_hash = hashlib.new('ripemd160')
    ripemd160_hash.update(sha256_hash)
    hashed_public_key = ripemd160_hash.digest()
    return _encode(hashed_public_key, versions('public'))

def _encode(data, version):
    if(type(version) is int):
        return base58.b58encode_check(bytes([version]) + data)
    else:
        return base58.b58encode_check(version + data)

def versions(versions=None):
    global _versions
    _versions = DEFAULT_VERSIONS[versions]
    return _versions

def generate_public_key(private_keys_array):
  public_keys_dict = {}
  for private_key in private_keys_array:
      private_key_bytes = bytes.fromhex(private_key)
      CoinKey(private_key_bytes)
      public_key = public_address()
      public_keys_str = public_key.decode('utf-8')
      public_keys_dict[public_keys_str] = private_key
  return public_keys_dict

def private_keys(init: int = 1):
  final = 9999 + init
  private_keys_array = [f"{i:064x}" for i in range(init, final)]
  return private_keys_array

def find_key(private_keys_array):
  public_keys_dict = generate_public_key(private_keys_array)
  wallet_bufs = {}
  for public_key, private_key in public_keys_dict.items():
    if public_key in wallets_array:
        wallet_bufs[public_key] = private_key
  return wallet_bufs

def private_wif():
    global ec_key
    return _encode(ec_key.to_string(), versions('private'))

def generate_wif(private_key):
    private_key_bytes = bytes.fromhex(private_key)
    CoinKey(private_key_bytes)
    return private_wif()

def resultTime(key, _min, pkey, name):
    global segundos, start_time
    if time.time() - start_time > segundos:
        segundos += 10
        print(segundos / 1000)
        if segundos % 10 == 0:
            tempo = (time.time() - start_time)
            os.system('cls' if os.name == 'nt' else 'clear')
            print('Resumo: ')
            print('Velocidade:', (int(key) - int(_min)) / tempo, 'haves por segundo')
            print('Chaves buscadas: ', f"{int(key) - int(_min):,}")
            print('Ultima chave tentada: ', pkey)

            file_path = f'Ultima_chave_{name}.txt'  # File path to write to
            content = f"Ultima chave tentada: {pkey}"
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                print(f"Error writing to file: {e}")
    return segundos

def encontrar_bitcoins(key, _min, _max, walletNumber):
    global start_time
    start_time = time.time()
    wallet = wallets_array[walletNumber-1]
    name = f'{datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")}_{walletNumber}'
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            keys = [format(key + i, 'x').zfill(64) for i in range(10000)]
            splited = [keys[i::10] for i in range(10)]
            futures = [executor.submit(find_key, key) for key in splited]
            results = [future.result() for future in futures]
            for result in results:
                wallets = list(result.keys())
                if wallet in wallets:
                    pk = result[wallet]
                    tempo = time.time() - start_time
                    print(f'Velocidade: {(key - _min) / tempo:.2f} haves por segundo')
                    print(f'Tempo: {tempo:.2f} segundos')
                    print(f'Private key: {pk}')
                    print(f'WIF: {generate_wif(pk)}')
                    print(f'Wallet: {wallet}')
                    with open('keys.txt', 'a') as f:
                        f.write(f'Private key: {pk}, WIF: {generate_wif(pk)}, Wallet: {wallet}\n')
                    print('Chave escrita no arquivo com sucesso.')
                    raise Exception('ACHEI!!!! ')
            key += 10000
            resultTime(key, _min, keys[-1], name)

if __name__ == '__main__':
    print(Fore.CYAN + "╔════════════════════════════════════════════════════════╗\n" +
    "║" + Fore.CYAN + "   ____ _____ ____   _____ ___ _   _ ____  _____ ____   " + Fore.RESET + "║\n" +
    "║" + Fore.CYAN + "  | __ )_  _/ ___|  |  ___|_ _| \\ | |  _ \\| ____|  _ \\  " + Fore.RESET + "║\n" +
    "║" + Fore.CYAN + "  |  _ \\ | || |     | |_   | ||  \\| | | | |  _| | |_) | " + Fore.RESET + "║\n" +
    "║" + Fore.CYAN + "  | |_) || || |___  |  _|  | || |\\  | |_| | |___|  _ <  " + Fore.RESET + "║\n" +
    "║" + Fore.CYAN + "  |____/ |_| \\____| |_|   |___|_| \\_|____/|_____|_| \\_\\ " + Fore.RESET + "║\n" +
    "║" + Fore.CYAN + "                                                        " + Fore.RESET + "║\n" +
    "╚═══════════════════" + Fore.GREEN + "BTC FINDER - v0.1" + Fore.RESET + "════════════════════╝" + Fore.RESET)

    answer = input("Escolha uma carteira puzzle( 1 - 160): ")
    if int(answer) < 1 or int(answer) > 160:
        print(Back.RED + "Erro: voce precisa escolher um numero entre 1 e 160" + Back.RESET)
    else:
        min_max_value = list(ranges[int(answer) - 1].values())
        _min = min_max_value[0]
        _max = min_max_value[1]
        _max_int = int(_max, 16)
        _min_int = int(_min, 16)
        print("Carteira escolhida: ", Fore.CYAN + answer + Fore.RESET, " _min: ", Fore.YELLOW + str(_min) + Fore.RESET, " _max: ", Fore.YELLOW + str(_max) + Fore.RESET)
        print("Numero possivel de chaves:", Fore.YELLOW + str(_max_int - _min_int) + Fore.RESET)
        key = _min_int

        answer2 = input("Escolha uma opcao (1 - Comecar do inicio, 2 - Escolher uma porcentagem, 3 - Escolher minimo): ")

    if answer2 == '2':
        answer3 = input("Escolha um numero entre 0 e 1: ")
        if float(answer3) > 1 or float(answer3) < 0:
            print(Back.RED + "Erro: voce precisa escolher umnumero entre 0 e 1" + Back.RESET)
            raise ValueError("Numero invalido")
        else:
            percentual_range = int((_max_int - _min_int) * float(answer3))
            _min_int += percentual_range
            _min = _min_int
            _max = _max_int
            print("Comecando em: ", Fore.YELLOW + hex(_min) + Fore.RESET)
            key = _min
            encontrar_bitcoins(key, _min_int, _max, int(answer))
    elif answer2 == '3':
        answer3 = input("Entre o minimo: ")
        _min_int = int(answer3, 16)
        key = _min_int
        encontrar_bitcoins(key, _min_int, _max, int(answer))
    else:
        encontrar_bitcoins(key, _min_int, _max_int, int(answer))