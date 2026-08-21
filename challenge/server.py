#!/bin/python3
# Historical SDCTF 2025 service code; not used by the current test suite.

from SDES2 import SDES2, generate_key
import secrets
import binascii

flag='pp'
##with open("flag.txt", "r") as f:
##    flag = f.read()

OPTIONS_MSG = """Select an option:
(E) Encrypt an arbitrary message (max 127 bytes)
(T) Get an encryption of the target message
(G) Guess the target message
"""
QUERY_MSG = "What is the message you want to encrypt? (max length 127 bytes)"
PROMPT_MSG = "> "
INVALID_MSG = "Invalid input."
TOO_LONG_MSG = "Message is too long."
QUOTA_DEPLETED_MSG = "Sorry, you have exhausted your message quota"
ENCRYPTED_DESCRIPTION_MSG = "Encrypted message: "
TARGET_CIPHERTEXT = """Encrypted target message: """
ASK_TARGET_MSG = "Guess what the target message is (in hex form):"

MAX_LENGTH = 127

message_quota = 20

key = generate_key()
sdes_instance = SDES2(key)

target_message = secrets.token_bytes(8)
print(target_message)
print(binascii.hexlify(target_message))
while True:
    print(f"You are allowed to encrypt {message_quota} more messages.")
    print(OPTIONS_MSG)
    answer = input(PROMPT_MSG)
    if (answer.upper() == "E"):
        if message_quota == 0:
            print(QUOTA_DEPLETED_MSG)
            continue
        print(QUERY_MSG)
        pt_hex = input(PROMPT_MSG)
        pt = binascii.unhexlify(pt_hex)
        print(pt)
        if len(pt) > MAX_LENGTH:
            print(TOO_LONG_MSG)
            continue
        ct = sdes_instance.encrypt(pt)
        ct_hex = binascii.hexlify(ct).decode()
        print(ENCRYPTED_DESCRIPTION_MSG)
        print(ct_hex)
        message_quota -= 1
    elif (answer.upper() == "T"):
        if message_quota == 0:
            print(QUOTA_DEPLETED_MSG)
            continue
        ct = sdes_instance.encrypt(target_message)
        ct_hex = binascii.hexlify(ct).decode()
        print(TARGET_CIPHERTEXT)
        print(ct_hex)
        message_quota -= 1
    elif (answer.upper() == "G"):
        print(ASK_TARGET_MSG)
        answer = input(PROMPT_MSG)
        target_guess = binascii.unhexlify(answer)
        if (target_guess == target_message):
            print(f"You win! Here's the flag: {flag}")
            break
        else:
            print("Sorry, that wasn't the plaintext. Better luck next time!")
            break
    else:
        print(INVALID_MSG)
        continue
