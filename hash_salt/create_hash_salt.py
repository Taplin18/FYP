import numpy as np
import base64

def create_salt_file():
	salt_file = "hash_salt"
	hash_salts = []

	for i in range(5):
		hash_salts.append(np.random.bytes(64))

	with open(salt_file, 'w') as hash_salt_file:
		for j in hash_salts:
			hash_salt_file.write(base64.b64encode(j).decode('UTF-8') + "\n")

if __name__ == '__main__':
	create_salt_file()