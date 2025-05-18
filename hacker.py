import subprocess,time
import binascii
import numpy as np
from sympy import Matrix, mod_inverse, lcm, gcdex,eye, Integer

EXPONENT_BITS = 16
BASE_BITS = 32
NUM_BOXES = 8

N = 94879793147291298476721783294187445671264672494875032831129557319548520130487168324917679986052672729113562509486413401411372593283386734883795994908851074407159233933625803763510710542534207403621838561485897109991552457145707812125981258850253074177933543163534990455821426644577454934996432224034425315179

# use this to generate exponent schedule, using P as modulus for modular exponent. Not related to N
P = 270301083588606647149832441301256778567
EXPO_P = 13
SEED_BITS = 128
SEED_BYTES = 2 * SEED_BITS // 8

def compute_target_product(E, c_list, exps, N):
    OE=Matrix(E)
    E=Matrix(E)
    tu=eye(16)
    print(E==tu*OE,tu)
    for i in range(8):
        for j in range(i+1,16):
            a,b,g=gcdex(E[i,i],E[j,i])
            if g!=1:
                continue
            E[i,:]=a*E[i,:]+b*E[j,:]
            tu[i,:]=a*tu[i,:]+b*tu[j,:]
            for k in range(i+1,16):
                v=E[k,i]
                E[k,:]-=v*E[i,:]
                tu[k,:]-=v*tu[i,:]
            break
        else:
            print(E)
            print(i)
            print("broken")
            return
    print(E==tu*OE,tu)
    for i in range(7,-1,-1):
        for j in range(i):
            v=E[j,i]
            E[j,:]-=v*E[i,:]
            tu[j,:]-=v*tu[i,:]
    print(E==tu*OE,tu)
    for i in range(8):
        E[i,:]*=exps[i]
        tu[i,:]*=exps[i]
    print(E==tu*OE,tu)
    ttu=[sum([tu[j,i] for j in range(16)]) for i in range(16)]
    print(ttu)
    mult=1
    for i in range(16):
        mult=(mult*pow(Integer(c_list[i]),ttu[i],Integer(N)))%N
    print(mult)
    return(mult)
process = subprocess.Popen('cmd', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
def runner(cmd,olines):
    print(cmd)
    process.stdin.write((cmd+'\n').encode())
    process.stdin.flush()
    out=[]
    for _ in range(olines):
        out.append(process.stdout.readline())
    print('\n'.join([i.decode() for i in out]))
    return out
def genSchedule(seed):
    e = seed & ((1 << EXPONENT_BITS) - 1)
    exponent_schedule = [e]
    for _ in range(NUM_BOXES - 1):
        seed = pow(seed, EXPO_P, P)
        e = seed & ((1 << EXPONENT_BITS) - 1)
        exponent_schedule.append(e)
    return exponent_schedule
runner('cd "C:\\Program Files (x86)\\Nmap',5)
runner('.\\ncat 52.8.15.62 8008',7)
E=[]
C=[]
for _ in range(16):
    runner('E',1)
    x=runner('01',8)[1]
    seed,c=int.from_bytes(binascii.unhexlify(x[:SEED_BYTES].decode()),"big"),int.from_bytes(binascii.unhexlify(x[SEED_BYTES:-1].decode()),"big")
    E.append(genSchedule(seed))
    C.append(c)
##def confirm(exps,c,ans):
##    m=1
##    for i in range(8):
##        m=(m*pow(ans[i],exps[i],N))%N
##    return(c==m)
##for i in range(16):
##    print(confirm(matrix[i][:-1],matrix[i][-1],ans))
x=runner('T',8)[1]
seed,c=int.from_bytes(binascii.unhexlify(x[:SEED_BYTES].decode()),"big"),int.from_bytes(binascii.unhexlify(x[SEED_BYTES:-1].decode()),"big")
print(x[SEED_BYTES:-1])
exps=genSchedule(seed)
multiplier=compute_target_product(E,C,exps,N)
m=(c*mod_inverse(multiplier,N))%N
print(m)
runner('G',1)
runner(binascii.hexlify(m.to_bytes(m.bit_length() // 8 + 1,"big")).decode(),1)
process.stdin.close()
print(process.stdout.readlines())
