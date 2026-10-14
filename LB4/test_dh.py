import unittest
from dh_core import DiffieHellmanParticipant, aes_encrypt, aes_decrypt

class TestDiffieHellmanAndChat(unittest.TestCase):
    def test_pairwise_diffie_hellman(self):
        alice = DiffieHellmanParticipant("Alice")
        bob = DiffieHellmanParticipant("Bob")

        alice_secret = alice.compute_pairwise_secret(bob.public_key)
        bob_secret = bob.compute_pairwise_secret(alice.public_key)

        self.assertEqual(alice_secret, bob_secret)
        self.assertEqual(alice.symmetric_key, bob.symmetric_key)
        print("Pairwise DH secrets match!")

    def test_aes_encryption_roundtrip(self):
        alice = DiffieHellmanParticipant("Alice")
        bob = DiffieHellmanParticipant("Bob")
        alice.compute_pairwise_secret(bob.public_key)
        bob.compute_pairwise_secret(alice.public_key)

        message = "Привіт, Боб! Це таємне повідомлення через канал зв'язку."
        enc = aes_encrypt(alice.symmetric_key, message)
        self.assertIn("iv_hex", enc)
        self.assertIn("ciphertext_hex", enc)

        decrypted = aes_decrypt(bob.symmetric_key, enc["iv_hex"], enc["ciphertext_hex"])
        self.assertEqual(decrypted, message)
        print("AES symmetric encryption roundtrip passed!")

    def test_three_party_group_key(self):
        alice = DiffieHellmanParticipant("Alice")
        bob = DiffieHellmanParticipant("Bob")
        charlie = DiffieHellmanParticipant("Charlie")

        self.assertNotEqual(alice.private_key, bob.private_key)
        self.assertNotEqual(bob.private_key, charlie.private_key)
        self.assertNotEqual(alice.public_key, bob.public_key)
        print("Three participants keys validated!")

if __name__ == '__main__':
    unittest.main()
