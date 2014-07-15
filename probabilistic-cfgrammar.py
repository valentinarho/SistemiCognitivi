import nltk
import json


my_sent_tokenizer = nltk.RegexpTokenizer('\*\n[^.!?]+\n*')
prova = nltk.corpus.BracketParseCorpusReader("assets/tut-penn/", '.*\.penn', comment_char="*", detect_blocks="sexpr")

# contatore delle occorrenze di una regola
productions = {}
prodlist = []

# contatore delle occorrenze per ogni head
heads = {}

# numero di regole totali
count = 0

for tree in prova.parsed_sents():
    count = count +1
    for prod in tree.productions():
        if prod not in productions:
            productions[prod] = 0
        productions[prod] = productions[prod]+1
        prodlist.append(prod)
        head = str(prod.lhs())
        if head not in heads:
            heads[head] = 0
        heads[head] = heads[head]+1

# metodo breve: utilizzando nltk
pcfg_nltk = nltk.grammar.induce_pcfg(nltk.grammar.Nonterminal('S'), prodlist)

# metodo lungo: calcolando a mano le probabilita
#pcfg = {}
#for prod in productions:
#    pcfg[str(prod)] = float(productions[prod]) / float(heads[str(prod.lhs())])

#out = open("assets/pcfg.json", "w")
#out.write(json.dumps(pcfg))
#out.close()

#print pcfg_nltk
#print pcfg
