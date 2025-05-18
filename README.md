# Problem  
The oracle allows the user to create up to 20 hashes of either user-defined messages or the secret message. The user must then return the secret message to obtain the flag.  
# SDES2 algorithm  
First, a key K is composed of $k_1 \dots k_8$, and values $N$ and $P$ are chosen. The RSA box function $R_i(m,e)=m*k_i^e \mod N$. The encryption scheme generates a key seed $S$, then creates an exponent schedule $E_S={e_{S,1} \dots e_{S,8}}$ using $P$ \- this is static and known.
Then, the message $m_0$ is hashed through $m_{i+1}=R_i(m_i,e_{S,i})$, so the official message is $m=m_8=m_0\prod{k_i^{e_{S,i}}} \mod N$.  
# Solution  
First generate 16 such hashes of $m_0=1$ to generate $c_i=\prod_j{k_j^{e_{S_i,j}}} \mod N$ for 16 distinct $S_i$. Then, we have a series of 16 equations and 8 unknowns.
We then generate the target message hash of $c=m\prod{k_i^{e_{S,i}}} \mod N$ for seed $S$.
We notice that if we can find a linear sum of the previous $\sum{v_i * E_{S_i}}=E_S$, then $m=c*\prod{c_i^{-v_i}} \mod N$, which we can compute efficiently.
We can perform this by Gauss-Jordan elimination, however this does not inherently create a integer solution.
However, we can leverage the fact that Gauss-Jordan elimination would only need 8 rows, but we have 16.
Thus, by using the extended euclidean algorithm, we can, for each elimination stage of the row echelon form computation, begin the process by combining two rows to make the leftmost value 1 only using an integer-valued multiple of each row.
This will result in a full RREF with the computation being made of integer multiples of the rows, which we can then use for the target.
