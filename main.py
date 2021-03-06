import argparse
import os
import time
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

parser = argparse.ArgumentParser()
parser.add_argument('path', help='Путь к папке с файлами')
group = parser.add_mutually_exclusive_group(required = True)
group.add_argument('-gen', '--generation', help='Запускает режим генерации ключей')
group.add_argument('-enc', '--encryption', help='Запускает режим шифрования')
group.add_argument('-dec', '--decryption', help='Запускает режим дешифрования')
args = parser.parse_args()


# path = "C:\\Users\\79371\\Desktop\\resources"
symmetric_key = args.path + "\\symmetric_key.txt"
public_pem = args.path + "\\public.pem"
private_pem = args.path + "\\private.pem"
orig_text = args.path + "\\orig.txt"
encrypt_text = args.path + "\\encrypt.txt"
decrypt_text = args.path + "\\decrypt.txt"
vector_init = args.path + "\\iv"
resource = (orig_text, encrypt_text, private_pem, symmetric_key, public_pem, decrypt_text, vector_init)


def generation(symmetric_k, public_p, private_p):
    # сериализация ключа симмеричного алгоритма в файл
    print("Enter length of key (5-16 bytes)\n")
    length = int(input())
    time.sleep(1)
    while length < 5 or length > 16:
        length = 0
        print("Enter length of key (5-16 bytes)\n")
        length = int(input())
    key = os.urandom(length)
    time.sleep(1)
    print("Key:" + str(key) + "\n")
    # генерация пары ключей для асимметричного алгоритма шифрования
    keys = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    private_key = keys
    public_key = keys.public_key()
    from cryptography.hazmat.primitives.asymmetric import padding
    c_key = public_key.encrypt(key,
                               padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(),
                                            label=None))
    with open(symmetric_k, 'wb') as key_file:
        key_file.write(c_key)
    time.sleep(1)
    print('Symmetric encryption key serialized at: ', symmetric_k, "\n")
    # сериализация открытого ключа в файл
    with open(public_p, 'wb') as public_out:
        public_out.write(public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                 format=serialization.PublicFormat.SubjectPublicKeyInfo))
    # сериализация закрытого ключа в файл
    with open(private_p, 'wb') as private_out:
        private_out.write(private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                                                    encryption_algorithm=serialization.NoEncryption()))
    time.sleep(1)
    print('Asymmetric encryption keys serialized at: ', private_p, "\t", public_p, "\n")
    pass


def encryption(orig_t, encrypt_t, private_p, symmetric_k, vec_init):
    with open(private_p, 'rb') as pem_in:
        private_bytes = pem_in.read()
    private_key = load_pem_private_key(private_bytes, password=None, )
    with open(symmetric_k, 'rb') as key:
        symmetric_bytes = key.read()
    from cryptography.hazmat.primitives.asymmetric import padding
    d_key = private_key.decrypt(symmetric_bytes,
                                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(),
                                             label=None))
    time.sleep(1)
    print("Key:" + str(d_key) + "\n")
    with open(orig_t, 'rb') as o_text:
        text = o_text.read()
    from cryptography.hazmat.primitives import padding
    pad = padding.ANSIX923(64).padder()
    padded_text = pad.update(text) + pad.finalize()
    # случайное значение для инициализации блочного режима, должно быть размером с блок и каждый раз новым
    iv = os.urandom(8)
    with open(vec_init, 'wb') as iv_file:
        iv_file.write(iv)
    cipher = Cipher(algorithms.CAST5(d_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    c_text = encryptor.update(padded_text) + encryptor.finalize()
    with open(encrypt_t, 'wb') as encrypt_file:
        encrypt_file.write(c_text)
    time.sleep(1)
    print("Text encrypted and serialized at: ", encrypt_t, "\n")
    pass


def decryption(private_p, encrypt_t, symmetric_k, decrypt_t, vec_init):
    with open(private_p, 'rb') as pem_in:
        private_bytes = pem_in.read()
    private_key = load_pem_private_key(private_bytes, password=None, )
    with open(symmetric_k, 'rb') as key:
        symmetric_bytes = key.read()
    from cryptography.hazmat.primitives.asymmetric import padding
    d_key = private_key.decrypt(symmetric_bytes,
                                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(),
                                             label=None))
    with open(encrypt_t, 'rb') as e_text:
        text = e_text.read()
    # дешифрование и депаддинг текста симметричным алгоритмом
    with open(vec_init, 'rb') as iv_file:
        iv = iv_file.read()
    cipher = Cipher(algorithms.CAST5(d_key), modes.CBC(iv))
    decrypter = cipher.decryptor()
    from cryptography.hazmat.primitives import padding
    unpadded = padding.ANSIX923(64).unpadder()
    d_text = unpadded.update(decrypter.update(text) + decrypter.finalize()) + unpadded.finalize()
    time.sleep(1)
    print("Text:\n")
    print(d_text.decode('UTF-8'))
    time.sleep(1)
    print("\nText (bytes):\n")
    print(d_text)
    with open(decrypt_t, 'w', encoding='UTF-8') as decrypt_file:
        decrypt_file.write(d_text.decode('UTF-8'))
    time.sleep(1)
    print("\nText decrypted and serialized at:", decrypt_t, "\n")
    pass


if args.generation is not None:
    generation(resource[3], resource[4], resource[2])
else:
    if args.encryption is not None:
        encryption(resource[0], resource[1], resource[2], resource[3], resource[6])
    else:
        if args.decryption is not None:
            decryption(resource[2], resource[1], resource[3], resource[5], resource[6])
        else:
            if args.u is not None:
                generation(resource[3], resource[4], resource[2])
                encryption(resource[0], resource[1], resource[2], resource[3], resource[6])
                decryption(resource[2], resource[1], resource[3], resource[5], resource[6])
