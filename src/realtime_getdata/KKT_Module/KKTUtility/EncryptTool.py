import rsa
import base64
import h5py
import threading
import time
from io import BytesIO
import zlib


class EncryptTool(object):
    def __init__(self):
        # Record File Save Format for Normal Mode
        self.public_key = self.Get_Crypted_Key()
        self.private_key = self.Get_private_key()

        # self.SAVE_AS_H5_FILE = False
        # self.SAVE_AS_ENCODE_FILE = True
        # self.ENABLE_FILE_COMPRESS = False
        self.ENABLE_FILE_COMPRESS = True

    def Get_Crypted_Key(self):
        RSA_public_key = {
            "n": 11127902757766976540234356830692921326746224132539887708040984545433063595203815127285375596696076912924726057554788414256963268230766718557980048603795467,
            "e": 65537
        }
        public_key = rsa.PublicKey(**RSA_public_key)
        return public_key

    def Get_private_key(self):
        RSA_private_key = {
            "n": 11127902757766976540234356830692921326746224132539887708040984545433063595203815127285375596696076912924726057554788414256963268230766718557980048603795467,
            "e": 65537,
            "d": 2890432711986621933326356963682890577005370606042792749957759432334513960909829488388055655449110242185743316579979057994786577976154325198866001226202377,
            "p": 7343420648857135974363148940011890745885992198670448136739249821932994990609971503,
            "q": 1515356846607830284953776406734173204142919527848021272436646861297493989
        }
        private_key = rsa.PrivateKey(**RSA_private_key)
        return private_key

    def Encode_BytesIOObject(self, BytesIOObject, public_key, SHA=64):
        # encrypted = b""
        encrypted_lsit = []
        encode_len = SHA - 11

        msg1 = BytesIOObject.getvalue()

        b_time = time.time()
        for i in range(0, len(msg1), encode_len):
            # encrypted += rsa.encrypt(msg1[i:i+encode_len], public_key)
            encrypted_lsit.append(rsa.encrypt(msg1[i:i + encode_len], public_key))
        encrypted = b''.join(encrypted_lsit)
        print("encode time:{}".format(time.time() - b_time))
        Encrypted_file = BytesIO(encrypted)
        Encrypted_string_b64 = base64.b64encode(encrypted).decode()

        return Encrypted_file, Encrypted_string_b64

    def Decode_BytesIOObject(self, BytesIOObject, private_key, SHA=64):
        # decrypted = b""
        decrypted_list = []
        decode_len = SHA

        decrypted_bytes = BytesIOObject.getvalue()

        b_time = time.time()
        for i in range(0, len(decrypted_bytes), decode_len):
            # decrypted += rsa.decrypt(decrypted_bytes[i:i+decode_len], private_key)
            decrypted_list.append(rsa.decrypt(decrypted_bytes[i:i + decode_len], private_key))
        decrypted = b''.join(decrypted_list)
        print("Decode time:{}".format(time.time() - b_time))
        Decrypted_file = BytesIO(decrypted)
        Decrypted_string_b64 = base64.b64encode(decrypted).decode()

        return Decrypted_file, Decrypted_string_b64

    def Encrypt_file_save(self, BytesIOObject, output_path):

        print('File processing ...')

        if self.ENABLE_FILE_COMPRESS:
            btime = time.time()
            com_con = zlib.compress(BytesIOObject.getvalue())
            print("Compress time: {}".format(time.time() - btime))
            BytesIOObject = BytesIO(com_con)

        public_key = self.Get_Crypted_Key()
        Ouput_IOFile, encrypted_b64 = self.Encode_BytesIOObject(BytesIOObject, public_key)
        with open(output_path, 'wb') as f:
            f.write(Ouput_IOFile.getvalue())

        with open(output_path, 'rb') as F:
            Ouput_IOFile = BytesIO(F.read())

        private_key = self.Get_private_key()
        Decrypted_file, decrpyted_string = self.Decode_BytesIOObject(Ouput_IOFile, private_key)

        if self.ENABLE_FILE_COMPRESS:
            btime = time.time()
            decom_con = zlib.decompress(Decrypted_file.read())
            BytesIOObject = BytesIO(decom_con )
            print("Decompress time: {}".format(time.time() - btime))

        with h5py.File(BytesIOObject, 'r') as F:
            print("Check the content", F.keys())
        quit()

        BytesIOObject.close()
        print('Save Record File : ', output_path)


def encode_file(file_path, output_path):
    with open(file_path, 'rb') as F:
        f = BytesIO(F.read())

    encrypt_tool = EncryptTool()

    thd = threading.Thread(target=encrypt_tool.Encrypt_file_save, args=(f, output_path))
    thd.start()

    print('Wait until Thread is terminating')
    thd.join()
    print("EXIT __main__")


def test_func():
    # Test the function
    encrypt_tool = EncryptTool()

    # Official release need to delete private key
    public_key, private_key = encrypt_tool.Get_Crypted_Key(), encrypt_tool.Get_private_key()

    with open('final_model_checkpoint.h5', 'rb') as F:
        f = BytesIO(F.read())

    Ouput_IOFile, encrypted_b64 = encrypt_tool.Encode_BytesIOObject(f, public_key)

    with open('test_encrypt.kkt', 'wb') as F:
        F.write(Ouput_IOFile.getvalue())

    Decrypted_file, decrpyted_string = encrypt_tool.Decode_BytesIOObject(Ouput_IOFile, private_key)

    with h5py.File(Decrypted_file, 'r') as F:
        print("Check the content", F.keys())

    with open('test_decrypt.h5', 'wb') as F:
        F.write(Decrypted_file.getvalue())


if __name__ == "__main__":
    # Functional test
    # test_func()

    # Usage
    file_path = r'C:\Users\eric.li\Downloads\final_model_checkpoint.h5'
    output_path = r'C:\Users\eric.li\Downloads\final_model_checkpoint.kkt'
    encode_file(file_path, output_path)
