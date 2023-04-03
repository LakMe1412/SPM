# to genrate alpha numberic otps
#chr convert the asii values to string(a-z(97-122))(A-Z(65-90))
#ord covert the letter to asii value
import random
def genotp():
    u_c=[chr(i) for i in range(ord('A'),ord('Z')+1)]#list comprehension big
#letters
    l_c=[chr(i) for i in range(ord('a'),ord('z')+1)]#small letters
    otp=''
    for i in range(2):#it iterates 3 times at 1 st+ again it iterates 3 times 
        otp+=random.choice(u_c)
        otp+=str(random.randint(0,9))
        otp+=random.choice(l_c)
    return otp
