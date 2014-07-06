from pprint import pprint
import nltk
import sys

grammar_path = "assets/S0-NF.cfg"
stato_iniziale = "S"

# input:
# words <- lista di parole della frase da analizzare
# grammar <- nltk grammar in forma normale di chomsky
# output:
# True se la frase e' riconosciuta dalla grammatica, False altrimenti
def CKYRecogniser(words, grammar):
    # numero di parole nella sentence
    n_words = len(words)
    # abbiamo bisogno di un array tridimensionale
    # per gestire la tabella prodotta dall'algoritmo CKY

    # table e' una matrice bidimensionale dove ogni cella e' una lista di non terminali
    # numero colonne = n_words + 1
    # numero righe = n_words
    table = [[set() for x in range(0, n_words + 1)] for x in range(0, n_words)]

    for j in range(1, n_words + 1):
        parola = words[j - 1]
        #print parola

        # nella cella j-1, j andremo a inserire
        # la testa delle regole di produzione della grammatica che hanno
        # la parola j-esima come conseguente
        rules = grammar.productions(None, parola)
        for r in rules:
            table[j - 1][j].add(r.lhs())
            #print "+ " + str(r.lhs()) + " in ", j - 1, ",", j

        # e' un for downto j-2 fino a 0 (compreso)
        for i in reversed(range(0, j - 1)):
            #print "Scorro da " + str(j - 2) + " a 0"
            for k in range(i + 1, j):
                #print "Scorro da " + str(i + 1) + " a " + str(j - 1)
                # aggiungiamo alla cella tutte le teste
                # delle regole che hanno come corpo BC
                # tali che B e' in table[i][k] e C e' in table[k][j]

                for b in table[i][k]:
                    #print "Contenuto di " + str(i) + "," + str(k) + " = " + str(b)
                    brules = grammar.productions(None, nltk.Nonterminal(str(b)))
                    #for temp in brules:
                    #print "Regola trovata: " + str(temp)

                    for c in table[k][j]:
                        #print "Contenuto di " + str(k) + "," + str(j) + " = " + str(c)
                        for bcrule in brules:
                            if bcrule.rhs()[1] == c:
                                table[i][j].add(bcrule.lhs())

    for i in table[0][n_words]:
        if str(i) == stato_iniziale:
            return True

    return False

# input:
# words <- lista di parole della frase da analizzare
# grammar <- nltk grammar in forma normale di chomsky
# output:
# Tree tree <- un possibile albero di parsing
def CKYParser(words, grammar):
    # numero di parole nella sentence
    n_words = len(words)
    # abbiamo bisogno di un array tridimensionale
    # per gestire la tabella prodotta dall'algoritmo CKY
    # table infatti e' una matrice bidimensionale dove ogni cella e' una lista di non terminali
    # numero colonne = n_words + 1
    # numero righe = n_words
    table = [[set() for x in range(0, n_words + 1)] for x in range(0, n_words)]

    # per ogni cella (stesse dimensioni della table)
    # dizionario per mantenere per ogni non terminale una lista di backpointer
    # un backpointer e' una tupla (pos, nonterm1, nonterm2), dove:
    # nonterm1 e nonterm2 sono i componenti della regola che e' stata applicata
    # per ottenere il non terminale in questione e pos ci permette di capire la provenienza
    # di nonterm1 e nonterm2 perche' supponendo di trovarci nella cella back[i][j] avremo che:
    # nonterm1 sara' in table[i][k]
    # nonterm2 sara' in table[k][j]
    back = [[dict() for x in range(0, n_words + 1)] for x in range(0, n_words)]

    for j in range(1, n_words + 1):
        parola = words[j - 1]

        # nella cella j-1, j andremo a inserire
        # la testa delle regole di produzione della grammatica che hanno
        # la parola j-esima come conseguente
        rules = grammar.productions(None, parola)
        for r in rules:
            table[j - 1][j].add(r.lhs())

        # e' un for downto j-2 fino a 0 (compreso)
        for i in reversed(range(0, j - 1)):
            # l'estremo superiore del range non e' incluso quindi mettiamo j invece di j-1
            for k in range(i + 1, j):
                # aggiungiamo alla cella tutte le teste
                # delle regole che hanno come corpo B C
                # tali che B e' in table[i][k] e C e' in table[k][j]

                for b in table[i][k]:
                    brules = grammar.productions(None, nltk.Nonterminal(str(b)))

                    for c in table[k][j]:

                        for bcrule in brules:
                            # se la regola e' ? -> b c
                            if bcrule.rhs()[1] == c:
                                table[i][j].add(bcrule.lhs())
                                # memorizzo il puntatore alla cella di provenienza di B e C
                                # B si trovera' in table[i][k]
                                # C si trovera' in table[k][j]
                                back[i][j][str(bcrule.lhs())] = tuple((k, b, c))

    # costruiamo l'albero a partire dal backpointer per S in
    # backpointer[0, n]
    for i in table[0][n_words]:
        if str(i) == stato_iniziale:
            stringtree = buildParsingTree(back, words)
            return nltk.Tree(stringtree)

    return None

# presa la matrice back ricostruisce l'albero di parsing
# della frase
def buildParsingTree(back, words):
    n_words = len(words)

    # ricostruiamo a partire dallo stato iniziale
    b = buildSubtree(0, n_words, stato_iniziale, back, words)
    #print b
    return b


def buildSubtree(i, j, root_nonterm, back, words):
    if root_nonterm in back[i][j]:
        # siamo in un nodo non terminale
        node = back[i][j][root_nonterm]
        # A -> B C
        sys.stdout.flush()
        # ricostruiamo B
        b = buildSubtree(0, node[0], str(node[1]), back, words)
        # ricostruiamo C
        c = buildSubtree(node[0], j, str(node[2]), back, words)

        return "(" + root_nonterm + " " + b + " " + c + ")"
    else:
        # abbiamo raggiunto un terminale
        return "(" + root_nonterm + " " + words[j - 1] + ")"


if __name__ == "__main__":
    # test
    # sentence = "Paolo e Dante sognano Francesca e Beatrice"
    sentence = "Un uomo adora tutte le donne"
    sentence_words = sentence.split()
    grammar = nltk.data.load("file:" + grammar_path)

    print sentence

    # prova di recogniser
    if CKYRecogniser(sentence_words, grammar):
        print "La frase e' stata riconosciuta."
    else:
        print "La frase non e' riconosciuta dalla grammatica."

    # prova di parser
    t = CKYParser(sentence_words, grammar)

    print t
    t.draw()


    # prende tutte le regole che hanno NP come testa
    # grammar.productions(nltk.Nonterminal("NP"))

    # prende tutte le regole che hanno il terminale 'ama' come corpo
    # grammar.productions(None, "ama")