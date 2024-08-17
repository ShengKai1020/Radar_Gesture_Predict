import io
import rsa
import base64
import time
import h5py

def Get_Crypted_Key():
    RSA_public_key = {
        "n": 11127902757766976540234356830692921326746224132539887708040984545433063595203815127285375596696076912924726057554788414256963268230766718557980048603795467,
        "e": 65537
    }
    public_key = rsa.PublicKey(**RSA_public_key)
    return public_key

def Encode_BytesIOObject(BytesIOObject, public_key, SHA=64):

    # encrypted = b""
    encrypted_lsit = []
    encode_len = SHA - 11
    
    msg1 = BytesIOObject.getvalue()

    b_time = time.time()
    for i in range(0,len(msg1), encode_len):
        # encrypted += rsa.encrypt(msg1[i:i+encode_len], public_key)
        encrypted_lsit.append(rsa.encrypt(msg1[i:i+encode_len], public_key))
    encrypted = b''.join(encrypted_lsit)
    print("encode time:{}".format(time.time()-b_time))
    Encrypted_file = io.BytesIO(encrypted)
    Encrypted_string_b64 = base64.b64encode(encrypted).decode()

    return Encrypted_file, Encrypted_string_b64

def Decode_BytesIOObject(BytesIOObject, private_key, SHA=64):

    # decrypted = b""
    decrypted_list = []
    decode_len = SHA

    decrypted_bytes = BytesIOObject.getvalue()
    
    b_time = time.time()
    for i in range(0, len(decrypted_bytes), decode_len):
        # decrypted += rsa.decrypt(decrypted_bytes[i:i+decode_len], private_key)
        decrypted_list.append(rsa.decrypt(decrypted_bytes[i:i+decode_len], private_key))
    decrypted = b''.join(decrypted_list)
    print("Decode time:{}".format(time.time()-b_time))
    Decrypted_file = io.BytesIO(decrypted)
    Decrypted_string_b64 = base64.b64encode(decrypted).decode()
    
    return Decrypted_file, Decrypted_string_b64

def get_private_key():
    RSA_private_key = {
            "n": 11127902757766976540234356830692921326746224132539887708040984545433063595203815127285375596696076912924726057554788414256963268230766718557980048603795467,
            "e": 65537,
            "d": 2890432711986621933326356963682890577005370606042792749957759432334513960909829488388055655449110242185743316579979057994786577976154325198866001226202377,
            "p": 7343420648857135974363148940011890745885992198670448136739249821932994990609971503,
            "q": 1515356846607830284953776406734173204142919527848021272436646861297493989
    }
    private_key = rsa.PrivateKey(**RSA_private_key)
    return private_key

def main():
    select_source = 1
    File_source = {
        0: "without file system", \
        1: "with file system"
    }
    
    # Test the function 

    # Official release need to delete private key

    RSA_private_key = {
            "n": 11127902757766976540234356830692921326746224132539887708040984545433063595203815127285375596696076912924726057554788414256963268230766718557980048603795467,
            "e": 65537,
            "d": 2890432711986621933326356963682890577005370606042792749957759432334513960909829488388055655449110242185743316579979057994786577976154325198866001226202377,
            "p": 7343420648857135974363148940011890745885992198670448136739249821932994990609971503,
            "q": 1515356846607830284953776406734173204142919527848021272436646861297493989
    }
    RSA_public_key = {
        "n": 11127902757766976540234356830692921326746224132539887708040984545433063595203815127285375596696076912924726057554788414256963268230766718557980048603795467,
        "e": 65537
    }
    public_key, private_key = rsa.PublicKey(**RSA_public_key), rsa.PrivateKey(**RSA_private_key)

    if select_source == 0:
        f = io.BytesIO()
        with h5py.File(f, 'w') as F:
            F.create_dataset('ab', (13,))
    else:
        with open('test.h5', 'rb') as F:
            f = io.BytesIO(F.read())
    

    Ouput_IOFile, encrypted_b64 = Encode_BytesIOObject(f, public_key)

    with open('test_encrypt.kkt', 'wb') as F:
        F.write(Ouput_IOFile.getvalue())

    Decrypted_file, decrpyted_string = Decode_BytesIOObject(Ouput_IOFile, private_key)

    with h5py.File(Decrypted_file, 'r') as F:
        print("Check the content", F.keys())
        


    with open('test_decrypt.h5', 'wb') as F:
        F.write(Decrypted_file.getvalue())


if __name__ == "__main__":
    main()


