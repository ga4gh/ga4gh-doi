import string
import random

def generateSuffix(): #suffix gen, only a-z, 0-9, and "-" other characters may escape, letters get capitalized
    # store all characters in lists 
    s1 = list(string.ascii_lowercase)
    s2 = list(string.digits)

    #removed due to possibility of confusing with 1, 0                
    s1.remove("i")
    s1.remove("l")
    s1.remove("o")

    # shuffle all lists
    random.shuffle(s1)
    random.shuffle(s2)  
    
    characters_number = random.randrange(5, 9) #generates suffix with 8 to 10 characters

    # calculate 30% & 20% of number of characters
    part1 = round(characters_number * (30/100))
    part2 = round(characters_number * (20/100))
        
    # generation of the password (60% letters and 40% digits & punctuations)
    result = []
    
    for x in range(part1):    
        result.append(s1[x])
        result.append(s2[x])
    random.shuffle(s2)  
    for x in range(part2):    
        result.append("-")
        result.append(s2[x])
        
    # shuffle result
    random.shuffle(result)
    # add character in first and last position to prevent suffix starting or ending with "-"
    result.insert(0,s1[random.randint(0, len(s1)-1)])
    result.append(s1[random.randint(0, len(s1)-1)])        
    # join result
    password = "".join(result)

    return password


def testSuffix(): # create suffixes until there is a duplicate
    
    suffixes = []
    counter = 0

    while True:
        suffix = generateSuffix()
        if suffix in suffixes:
            return counter, suffix
        else:
            suffixes.append(suffix)
            counter+=1


#print(generateSuffix())
print(testSuffix())

# test results
# 113091, 268255, 381628, 129773, 126750
# mean average suffixes until a duplicate suffix is created is 203899
# the mode average is approximately 126000
 
 
