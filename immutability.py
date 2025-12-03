s = "shalini"
l = [1,2,3]
s = "hello"
print("ID before:", id(s))

s = s + " world"
print("ID after :", id(s))

s = "hello"
print("Hash before:", hash(s))

# Modify the list by creating a new one
s = s + " world"
print("Hash after :", hash(s))


print("ID before:", id(l))
# print("Hash before:", hash(l)) # TypeError: unhashable type: 'list'
l.append(8)

print("ID after :", id(l))

# print("Hash after :", hash(l))