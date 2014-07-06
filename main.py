import nltk
from nltk.parse.chart import ChartParser as Chart
from nltk import load_parser
import re
import json

import cky
import sentence_planner
import sys

grammatica = nltk.data.load('file:assets/S0-NF.cfg')
grammatica_aumentata = 'file:assets/S0-NF-augmented.fcfg'

# A man loves all the women
# Paolo loves Francesca
# A man loves Francesca
# Francesca hates a man
# Paolo and Dante dream Francesca and Beatrice
# All the mans adore a woman
# Caronte sails
# Dante and a man visit an hell
# A woman and Dante leave a gift to Virgilio
# Dante sees the stars
# Dante loves all the women

frasi = ["un uomo adora tutte le donne",
         "Paolo ama Francesca",
         "Un uomo ama Francesca", #ok
         "Francesca odia un uomo", #ok
         "Paolo e Dante sognano Francesca e Beatrice",
         "Tutti gli uomini adorano una donna",
         "Caronte naviga", #ok
         "Dante e un uomo visitano un inferno",
         "Una donna e Dante lasciano un dono a Virgilio",
         "Dante rivede le stelle",
         "Dante adora tutte le donne"
]

# Restituisce l'albero di parsing relativo alla frase utilizzando nltk
def getTree(frase):
    parser = Chart(grammatica)
    # print sentence
    frase = frase.split()
    trees = parser.nbest_parse(frase)
    #trees[0].draw()
    if (len(trees) > 0):
        return trees[0]

# Restituisce l'albero di parsing relativo alla frase utilizzando CKY
def getTreeCKY(frase):
    # parser = Chart(grammatica)
    # print sentence
    frase = frase.split()
    tree = cky.CKYParser(frase, grammatica)
    #trees[0].draw()
    return tree

# Restituisce l'albero di parsing (con semantica) relativo alla frase
def getAugmentedTree(sentence):
    parser = load_parser(grammatica_aumentata, trace=0)
    # print sentence
    tokens = sentence.split()
    trees = parser.nbest_parse(tokens)
    #trees[0].draw()
    if (len(trees) > 0):
        return trees[0]

# Restituisce la formula logica relativa alla frase a partire
# dall'albero
def getFormulaFromRoot(tree):
    try:
        m = re.search('(?<=SEM\=\<)(.*)>', str(tree))
        return m.group(1)
    except:
        return None


def test_nf_grammar():
    for frase in frasi:
        print ""
        print frase
        print getTree(frase)


def test_nf_augmented_grammar():
    for frase in frasi:
        print ""
        print frase
        print getAugmentedTree(frase)


def test_completo_1_frase(frase):
    print frase
    print ""
    t1 = getTreeCKY(frase)
    print t1
    print ""
    #t1.draw()
    t2 = getAugmentedTree(frase)
    print t2
    print ""
    print getFormulaFromRoot(t2)


def test_recogniser(frase):
    sentence = "Un uomo adora tutte le donne"
    sentence_words = sentence.split()
    print sentence

    # prova di recogniser
    if cky.CKYRecogniser(sentence_words, grammatica):
        print "La frase e' stata riconosciuta."
    else:
        print "La frase non e' riconosciuta dalla grammatica."


if __name__ == "__main__":
    if len(sys.argv) == 1:
        frase = "Un uomo adora tutte le donne"
        print frase

        # TEST CKY + SEMANTICA PER TUTTE LE FRASI

        # test_nf_grammar()
        # test_nf_augmented_grammar()

        # TEST PER UNA SINGOLA FRASE
        # test_completo_1_frase(frase)

        # TEST SEPARATI
        # per provare il CKY recogniser implementato
        # test_recogniser(frase)

        # per ottenere l'albero di parsing con l'algoritmo CKY implementato
        # t1 = getTreeCKY(frase)
        # print t1
        # t1.draw()

        # per ottenere l'albero di parsing con nltk
        # t1 = getTree(frase)
        # print t1
        # t1.draw()

        # per ottenere l'albero di parsing con la grammatica con semantica
        # t2 = getAugmentedTree(frase)
        # print t2
        # t2.draw()

        # per ottenere la formula logica relativa all'albero con semantica
        t2 = getAugmentedTree(frase)
        formula = getFormulaFromRoot(t2)
        # print formula

        # per trasformare la formula logica in un sentence plan
        plan = sentence_planner.getSentencePlan(formula)
        print json.dumps(plan)

    else:
        # chiamato da linea di comando, il primo parametro e' una frase
        # facciamo la pipeline completa e stampiamo in output il sentence plan
        frase = sys.argv[1]
        t2 = getAugmentedTree(frase)
        formula = getFormulaFromRoot(t2)
        plan = sentence_planner.getSentencePlan(formula)
        print json.dumps(plan)