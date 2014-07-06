import nltk
from nltk.parse.chart import ChartParser as Chart
from nltk import load_parser
import re



grammatica = nltk.data.load('file:assets/S0-NF.cfg')

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

def getTree(frase):
    parser = Chart(grammatica)
    print ""
    print frase
    frase = frase.split()
    trees = parser.nbest_parse(frase)
    if (len(trees) > 0):
        return trees[0]

def test_nf_grammar():
    parser = Chart(grammatica)
    for frase in frasi:
        print ""
        print frase
        frase = frase.split()
        trees = parser.nbest_parse(frase)
        if (len(trees) > 0):
            print trees[0]
        trees[0].draw()



def getAugmentedTree(sentence):
    parser = load_parser('file:assets/augmented-S0-NF.fcfg', trace=0)
    #parser = load_parser('file:prova.fcfg', trace=1)
    print sentence
    tokens = sentence.split()
    trees = parser.nbest_parse(tokens)
    #print trees
    if (len(trees) > 0):
        return trees[0]

    #trees[0].draw()

def getFormulaFromRoot(t2):
    try:
        m = re.search('(?<=SEM\=\<)(.*)>', str(t2))
        return m.group(1)
    except:
        return None

def estraiDipendenze(logicf):
    dict = {}
    s = "exists x.(man(x) & all z2.(women(z2) -> adore(x,z2)))"
    m = re.search('(.*)adore\((.+),(.+)\)(.*)', str(s))
    print m.group(3)
    pass

# TEST TOTALE

test_nf_grammar()

# s = "Una donna e Dante lasciano un dono a Virgilio"
# t1 = getTree(s)
# print t1

#t2 = getAugmentedTree(s)
#print t2

# otteniamo l'espressione logica relativa alla semantica della radice dell'albero
# logicf = getFormulaFromRoot(t2)
# print logicf

# estraiDipendenze(logicf)

# TEST PER TUTTE LE FRASI
#for frase in frasi:
#    t = getAugmentedTree(frase)
#    print t


