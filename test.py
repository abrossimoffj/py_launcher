import random
import string
from decorator import *


import sys

#print(sys.argv)

def get_random_alphanumeric_string(letters_count, digits_count):
    sample_str = ''.join((random.choice(string.ascii_letters) for i in range(letters_count)))
    sample_str += ''.join((random.choice(string.digits) for i in range(digits_count)))

    # Convert string to list and shuffle it to mix letters and digits
    sample_list = list(sample_str)
    random.shuffle(sample_list)
    final_string = ''.join(sample_list)
    return final_string

@debug
def func2(test):
	print("zouuu")
	pif = "paf"
	pouf = "7777"
	#a,b = 2
	c,d = 3,4
	#waited_print()

@debug
def func(test_func,test2_func):
    local1 = 1
    local2 = 2
    print("dddddeep")
    return "42"


from time import sleep
print("First random alphanumeric string is:", get_random_alphanumeric_string(10, 3))
j=0
while(j<5):
	j+=1
	#print(waited_print+j)
	#waited_print()
	#waited_print()
	sleep(1)

	print(j)
	func2(j)
	func(72,89)

