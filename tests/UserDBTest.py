from dmxrelay.sink.auth.auth_manager import AuthManager

authmanager = AuthManager()

authmanager.createUser("tester", "password")

authmanager.storeDB()

authmanager2 = AuthManager()
authmanager2.loadDB()

ph1 = authmanager.getUserByName("tester").passwd_hash
ph2 = authmanager2.getUserByName("tester").passwd_hash

print(ph1)
print(ph2)

s1 = authmanager.getUserByName("tester").salt
s2 = authmanager2.getUserByName("tester").salt

print(s1)
print(s2)

