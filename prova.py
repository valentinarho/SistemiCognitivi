import re
import sys
import json

# difficolta: distinguere verbi intransitivi da predicati unari
#             supponiamo che una variabile venga utilizzata solo in al massimo un predicato (non ci sono aggettivi ad esempio)


# [
#   {
#       'VERB': verbo
#       'SUBJ': {NAME: nome, QUANT: quantificazione} # NAME e QUANT sono facoltativi
#       'OBJ':  {NAME: nome, QUANT: quantificazione}
#       'COMPL': {NAME: nome, QUANT: quantificazione}
#   }
# ]

verbiIntransitivi = ['sail']

formule = [line.strip() for line in open('assets/formule.txt')]

componenti = []
quantificazioni = {}
predicati = {}

s = "exists x.(man(x) & all z2.(women(z2) -> adore(x,z2)))"
s = "sail(caronte)"
s = "(exists z8.(hell(z8) & visit(dante,z8)) & exists x.(man(x) & exists z9.(hell(z9) & visit(x,z9))))"
#s = "exists z8.(hell(z8) & leave(e,v) & sail(z8) & leave(a,b,c)"

# caso particolare per gestire i verbi intransitivi
def trovaPredicati1Arg(espr):
    m = re.search('(.+)\(([^,]+?)\)(.*)', str(espr))
    while (m != None):
        pred = m.group(1)
        var = m.group(2)
        spazio = pred[::-1].find(" ")
        if (spazio != -1):
            spazio = len(pred)-spazio
        parentesi = pred[::-1].find("(")
        if (parentesi != -1):
            parentesi = len(pred)-parentesi

        if ( spazio >= 0 and (parentesi == -1 or parentesi < spazio)):
            sp = pred.split(" ")
            pred = sp[len(sp)-1]
        elif (parentesi >= 0):
            sp = pred.split("(")
            pred = sp[len(sp)-1]

        if pred not in verbiIntransitivi:
            # e' un predicato
            predicati[var] = pred
        else:
            # e' un verbo intransitivo
            componenti.append({'VERB':pred, 'SUBJ':var})

        espr1 = m.group(1)
        m = re.search('(.+)\(([^,]+?)\)(.*)', str(espr1))


def trovaVerbi2Arg(espr):
    m = re.search('(.+)\(([^,]+?),([^,]+?)\)(.*)', str(espr))
    while (m != None):
        verb = m.group(1)
        subj = m.group(2)
        obj = m.group(3)

        spazio = verb[::-1].find(" ")
        if (spazio != -1):
            spazio = len(verb)-spazio
        parentesi = verb[::-1].find("(")
        if (parentesi != -1):
            parentesi = len(verb)-parentesi

        if ( spazio >= 0 and (parentesi == -1 or parentesi < spazio)):
            sp = verb.split(" ")
            verb = sp[len(sp)-1]
        elif (parentesi >= 0):
            sp = verb.split("(")
            verb = sp[len(sp)-1]


        componenti.append({'VERB': verb, 'SUBJ':subj, 'OBJ':obj})
        espr1 = m.group(1)
        m = re.search('(.+)\((.+?),(.+?)\)(.*)', str(espr1))


# leave(a, b, c) a: chi, b: qualcosa, c: a qualcuno
def trovaVerbi3Arg(espr):
    m = re.search('(.+)\(([^,]+?),([^,\)]+?),([^,]+?)\)(.*)', str(s))
    while (m != None):
        verb = m.group(1)
        subj = m.group(2)
        obj = m.group(3)
        to =  m.group(4)

        spazio = verb[::-1].find(" ")
        if (spazio != -1):
            spazio = len(verb)-spazio
        parentesi = verb[::-1].find("(")
        if (parentesi != -1):
            parentesi = len(verb)-parentesi

        if ( spazio >= 0 and (parentesi == -1 or parentesi < spazio)):
            sp = verb.split(" ")
            verb = sp[len(sp)-1]
        elif (parentesi >= 0):
            sp = verb.split("(")
            verb = sp[len(sp)-1]


        componenti.append({'VERB': verb, 'SUBJ':subj, 'OBJ':obj, 'COMPL':to})

        espr1 = m.group(1)
        m = re.search('(.+)\((.+?),(.+?),(.+?)\)(.*)', str(espr1))


def trovaEsiste(espr):
    # trova l'ultima occorrenza
    m = re.search('(.*)exists (.+?)\.\((.+?)', str(espr))
    while (m != None):
        # trova l'exists
        var = m.group(2)
        quantificazioni[var] = "EXISTS"
        # se nel resto della stringa trovi un altra occorrenza di exists con lo stesso quantificatore rinomina le variabili
        split = espr.split("exists "+var+".(")

        if len(split) > 1:
            esprtemp = split[0]
            m = re.search('(.*)exists (.+?)\.\((.+?)', str(esprtemp))
        else:
            m = None

def trovaPerOgni(espr):
    # trova l'ultima occorrenza
    m = re.search('(.*)all (.+?)\.\((.+?)', str(espr))
    while (m != None):
        # trova l'exists
        var = m.group(2)
        quantificazioni[var] = "FOREACH"
        # se nel resto della stringa trovi un altra occorrenza di exists con lo stesso quantificatore rinomina le variabili
        split = espr.split("all "+var+".(")

        if len(split) > 1:
            esprtemp = split[0]
            m = re.search('(.*)all (.+?)\.\((.+?)', str(esprtemp))
        else:
            m = None


def cleanFromFomula(espr, datogliere):
    espr = espr.replace(datogliere, "")
    return espr

def bindingVariabiliLibere():

    for comp in componenti:
        subj = comp['SUBJ']
        test = False
        dict = {}
        if (subj in quantificazioni):
            dict['QUANT'] = quantificazioni[subj]
            test = True
        if (subj in predicati):
            dict['NAME'] = predicati[subj]
            test = True
        # se non e' ne quantificato ne all'interno di un predicato allora e' un nome e non una variabile
        if (not test):
            dict['NAME'] = subj.title()

        comp['SUBJ'] = dict


        if 'OBJ' in comp:
            obj = comp['OBJ']
            test = False
            dict = {}
            if (obj in quantificazioni):
                dict['QUANT'] = quantificazioni[obj]
                test = True
            if (obj in predicati):
                dict['NAME'] = predicati[obj]
                test = True
            if (not test):
                dict['NAME'] = obj.title()

            comp['OBJ'] = dict

        if 'COMPL' in comp:
            c = comp['COMPL']
            test = False
            dict = {}
            if (c in quantificazioni):
                dict['QUANT'] = quantificazioni[c]
                test = True
            if (c in predicati):
                dict['NAME'] = predicati[c]
                test = True
            if (not test):
                dict['NAME'] = c.title()

            comp['COMPL'] = dict

def cleanQuantificazioni(s):
    for var in quantificazioni:
        if (quantificazioni[var] == "FOREACH"):
            s = cleanFromFomula(s, "all "+var+".")
        else:
            s = cleanFromFomula(s, "exists "+var+".")
    return s

def cleanPredicati1(s):
    for dict in componenti:
        if ('COMPL' not in dict and 'OBJ' not in dict ):
            s = cleanFromFomula(s, dict['VERB']+"("+dict['SUBJ']+")")

    for k in predicati:
        s = cleanFromFomula(s, predicati[k]+"("+k+")")

    return s

# p = "z8)) & exists x.(man(x) & exists z9.(hell(z9) & visit(x"
#
# m = re.search('(.+)\(([^,]+?),([^,\)]+?),([^,]+?)\)(.*)', str(s))
# print m.group(0)
# print m.group(1)
# print m.group(2)
# print m.group(3)
# exit()

output = file('sentence_plan.txt', 'w')

for s in formule:
    componenti = []
    quantificazioni = {}
    predicati = {}


    trovaEsiste(s)
    trovaPerOgni(s)

    #s = cleanQuantificazioni(s)

    trovaPredicati1Arg(s)
    #s = cleanPredicati1(s)
    trovaVerbi2Arg(s)
    trovaVerbi3Arg(s)

    print ""
    print s
    for c in componenti:
        print c

    for p in predicati:
        print p, predicati[p]

    bindingVariabiliLibere()
    print "--------------------------"
    for c in componenti:
        print c

    for p in predicati:
        print p, predicati[p]

    sys.stdout.flush()
    output.write(json.dumps(componenti));
    output.write("\n")

output.close()

exit()

# trova quantificatori e salva le quantificazioni



# trova i verbi a tre argomenti
trovaVerbi3Arg(s)

for dict in componenti:
    if ('COMPL' in dict):
        s = cleanFromFomula(s, dict['VERB']+"("+dict['SUBJ']+","+dict['OBJ']+","+dict['COMPL']+")")

trovaVerbi2Arg(s)
print componenti

for dict in componenti:
    if ('COMPL' not in dict and 'OBJ' in dict ):
        s = cleanFromFomula(s, dict['VERB']+"("+dict['SUBJ']+","+dict['OBJ']+")")

trovaPredicati1Arg(s)


# per ogni parentesi quantificata o per l'intera frase se non ci sono quantif
    # trova coordinazioni

    # per ogni coordinazione (o per l'intera frase se non ci sono
    # trova verbo a 3 argomenti

    # else trova verbo a 2 argomenti

    # else trova verbo a 1 argomento



# tolgo parentesi iniziale
# TODO dovremmo considerare il fatto di avere (...) and (...)

# if (s.find("(") == 0):
#     s = s[1:len(s)-1]
#     print s
#
# if (s.find("exists") == 0):
#     print "ciao"
#
# def trovaVerbo2(s):
#     dict = {}
#
#     s.find('')
#
#     m = re.search('(.+)\((.+),(.+)\)(.*)', str(s))
#     print m.group(1)
#
# #trovaVerbo2("exists x.(man(x) & all z2.(women(z2) -> adore(x,z2)))")
# #m = re.search('(.*)adore\((.+),(.+)\)(.*)', str(s))
# #print m.group(3)
#
#
#
#

