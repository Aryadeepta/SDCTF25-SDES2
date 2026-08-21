# Historical SDCTF 2025 challenge code; not used by the current test suite.

from math import gcd
import secrets

EXPONENT_BITS = 16
BASE_BITS = 32
NUM_BOXES = 8

N = 94879793147291298476721783294187445671264672494875032831129557319548520130487168324917679986052672729113562509486413401411372593283386734883795994908851074407159233933625803763510710542534207403621838561485897109991552457145707812125981258850253074177933543163534990455821426644577454934996432224034425315179

# use this to generate exponent schedule, using P as modulus for modular exponent. Not related to N
P = 270301083588606647149832441301256778567
EXPO_P = 13
SEED_BITS = 128
SEED_BYTES = SEED_BITS // 8

class RSABox:
    def __init__(self, box_key):
        assert(gcd(box_key, N) == 1)
        self.box_key = box_key

    def encrypt(self, pt, e):
        return (pt * pow(self.box_key, e, N)) % N

    def decrypt(self, ct, e):
        return (ct * pow(self.box_key, -e, N)) % N
def genSchedule(seed):
    e = seed & ((1 << EXPONENT_BITS) - 1)
    exponent_schedule = [e]
    for _ in range(NUM_BOXES - 1):
        seed = pow(seed, EXPO_P, P)
        e = seed & ((1 << EXPONENT_BITS) - 1)
        exponent_schedule.append(e)
    return exponent_schedule
class SDES2:
    # key is [p1, p2 ...], a list of integers, one for each RSABox
    def __init__(self, key):
        self.key = key
        self.boxes = [RSABox(box_key) for box_key in key]

    def encrypt(self, message):
        m = int.from_bytes(message, byteorder="big")

        initial_seed = (secrets.randbelow(P - 1) + 1)
        seed = initial_seed
        e = seed & ((1 << EXPONENT_BITS) - 1)
        exponent_schedule = [e]
        for _ in range(NUM_BOXES - 1):
            seed = pow(seed, EXPO_P, P)
            e = seed & ((1 << EXPONENT_BITS) - 1)
            exponent_schedule.append(e)
        for (box, e) in zip(self.boxes, exponent_schedule):
            m = box.encrypt(m, e)
        header = initial_seed.to_bytes(SEED_BYTES, byteorder="big")
        ct_bytes = m.to_bytes(m.bit_length() // 8 + 1, byteorder="big")
        print(header, ct_bytes)
        print(len(header), len(ct_bytes))
        print(genSchedule(int.from_bytes(header,"big"))==exponent_schedule)
        return header + ct_bytes

    def decrypt(self, ciphertext):
        header_len = SEED_BYTES
        header_bytes = ciphertext[:header_len]
        seed = int.from_bytes(header_bytes, byteorder="big")
        e = seed & ((1 << EXPONENT_BITS) - 1)
        exponent_schedule = [e]
        for _ in range(NUM_BOXES - 1):
            seed = pow(seed, EXPO_P, P)
            e = seed & ((1 << EXPONENT_BITS) - 1)
            exponent_schedule.append(e)
        ct_bytes = ciphertext[header_len:]
        ct = int.from_bytes(ct_bytes, byteorder="big")
        for (box, e) in zip(self.boxes[::-1], exponent_schedule[::-1]):
            ct = box.decrypt(ct, e)
        message = ct.to_bytes(ct.bit_length() // 8 + 1, byteorder="big")
        return message


def generate_key():
    base_list = []
    for _ in range(NUM_BOXES):
        while True:
            base = secrets.randbits(BASE_BITS)
            if gcd(base, N) == 1:
                base_list.append(base)
                break
    return base_list
