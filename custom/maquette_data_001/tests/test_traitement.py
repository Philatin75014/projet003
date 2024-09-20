import unittest
import sys
import os

# Ajoutez le répertoire src au sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.traitement import traiter_donnees

class TestTraitementDonnees(unittest.TestCase):
    def test_traiter_donnees(self):
        donnees = [None, 'Hello', 'WORLD', 123, None]
        resultat_attendu = ['hello', 'world', 123]
        self.assertEqual(traiter_donnees(donnees), resultat_attendu)
        #self.assertEqual([1,2], [1,2])
        print(donnees,resultat_attendu)
if __name__ == '__main__':
    #unittest.main(buffer=False)  # Désactive la mise en tampon des sorties
    unittest.main(buffer=False)  # Désactive la mise en tampon des sorties