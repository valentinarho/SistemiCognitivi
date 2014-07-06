import re
import sys
import json

# gestione dei predicati unari:
# per distinguere i verbi intransitivi dai predicati (come man(x)) supponiamo di
# avere una lista di verbi intransitivi
verbiIntransitivi = ['sail']

# inoltre supponiamo che una variabile venga utilizzata
# solo in al massimo un predicato unario (non ci sono aggettivi ad esempio)

# OUTPUT:
# [
#   {
#       'VERB': verbo
#       'SUBJ': {NAME: nome, QUANT: quantificazione} # NAME e QUANT sono facoltativi
#       'OBJ':  {NAME: nome, QUANT: quantificazione}
#       'COMPL': {NAME: nome, QUANT: quantificazione}
#   }, {...},
# ]

componenti = []
quantificazioni = {}
predicati = {}

# caso particolare per gestire i verbi intransitivi
def trovaPredicati1Arg(espr):
    m = re.search('(.+)\(([^,]+?)\)(.*)', str(espr))
    while (m != None):
        pred = m.group(1)
        var = m.group(2)
        spazio = pred[::-1].find(" ")
        if (spazio != -1):
            spazio = len(pred) - spazio
        parentesi = pred[::-1].find("(")
        if (parentesi != -1):
            parentesi = len(pred) - parentesi

        if ( spazio >= 0 and (parentesi == -1 or parentesi < spazio)):
            sp = pred.split(" ")
            pred = sp[len(sp) - 1]
        elif (parentesi >= 0):
            sp = pred.split("(")
            pred = sp[len(sp) - 1]

        if pred not in verbiIntransitivi:
            # e' un predicato
            predicati[var] = pred
        else:
            # e' un verbo intransitivo
            componenti.append({'VERB': pred, 'SUBJ': var})

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
            spazio = len(verb) - spazio
        parentesi = verb[::-1].find("(")
        if (parentesi != -1):
            parentesi = len(verb) - parentesi

        if ( spazio >= 0 and (parentesi == -1 or parentesi < spazio)):
            sp = verb.split(" ")
            verb = sp[len(sp) - 1]
        elif (parentesi >= 0):
            sp = verb.split("(")
            verb = sp[len(sp) - 1]

        componenti.append({'VERB': verb, 'SUBJ': subj, 'OBJ': obj})
        espr1 = m.group(1)
        m = re.search('(.+)\((.+?),(.+?)\)(.*)', str(espr1))


# leave(a, b, c) a: chi, b: qualcosa, c: a qualcuno
def trovaVerbi3Arg(espr):
    m = re.search('(.+)\(([^,]+?),([^,\)]+?),([^,]+?)\)(.*)', str(espr))
    while (m != None):
        verb = m.group(1)
        subj = m.group(2)
        obj = m.group(3)
        to = m.group(4)

        spazio = verb[::-1].find(" ")
        if (spazio != -1):
            spazio = len(verb) - spazio
        parentesi = verb[::-1].find("(")
        if (parentesi != -1):
            parentesi = len(verb) - parentesi

        if ( spazio >= 0 and (parentesi == -1 or parentesi < spazio)):
            sp = verb.split(" ")
            verb = sp[len(sp) - 1]
        elif (parentesi >= 0):
            sp = verb.split("(")
            verb = sp[len(sp) - 1]

        componenti.append({'VERB': verb, 'SUBJ': subj, 'OBJ': obj, 'COMPL': to})

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
        split = espr.split("exists " + var + ".(")

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
        split = espr.split("all " + var + ".(")

        if len(split) > 1:
            esprtemp = split[0]
            m = re.search('(.*)all (.+?)\.\((.+?)', str(esprtemp))
        else:
            m = None


def cleanFromFomula(espr, datogliere):
    espr = espr.replace(datogliere, "")
    return espr


def bindingVariabiliLibere():
    global quantificazioni
    global componenti
    global predicati

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
            s = cleanFromFomula(s, "all " + var + ".")
        else:
            s = cleanFromFomula(s, "exists " + var + ".")
    return s


def cleanPredicati1(s):
    for dict in componenti:
        if ('COMPL' not in dict and 'OBJ' not in dict ):
            s = cleanFromFomula(s, dict['VERB'] + "(" + dict['SUBJ'] + ")")

    for k in predicati:
        s = cleanFromFomula(s, predicati[k] + "(" + k + ")")

    return s

# input: formule, una lista di formule logiche
# output_path: path di un file dove scrivere il sentence plan ottenuto, se None scrive su stdout
def trasforma_formule(formule, output_path):
    global componenti
    global quantificazioni
    global predicati

    if output_path != None:
        output = file(output_path, 'w')
    else:
        output = None

    for s in formule:
        print ""
        print "Formula: " + s

        sentence_plan = getSentencePlan(s)

        sys.stdout.flush()
        if (output != None):
            output.write(json.dumps(sentence_plan));
            output.write("\n")
        else:
            sys.stdout.write(json.dumps(sentence_plan));
            sys.stdout.write("\n")

    if output != None:
        output.close()


def getSentencePlan(formula):
    global quantificazioni
    global componenti
    global predicati

    componenti = []
    quantificazioni = {}
    predicati = {}

    # trova i quantificatori
    trovaEsiste(formula)
    trovaPerOgni(formula)

    #s = cleanQuantificazioni(s)

    trovaPredicati1Arg(formula)
    #s = cleanPredicati1(s)

    trovaVerbi2Arg(formula)
    trovaVerbi3Arg(formula)

    # for c in componenti:
    #     print c
    #
    # for p in predicati:
    #     print p, predicati[p]

    bindingVariabiliLibere()

    return componenti


if __name__ == "__main__":
    # trasforma tutte le formule nella lista e le salva nel file output
    formule = [line.strip() for line in open('assets/formule.txt')]
    # per stampare solo sulla console
    trasforma_formule(formule, None)

    # per salvare sul file sentence_plan.txt
    # output_path = 'assets/sentence_plan.txt'
    # trasforma_formule(formule, output_path)

    # per trasformare 1 sola formula
    # s = "exists x.(man(x) & all z2.(women(z2) -> love(x,z2)))"
    # sp = getSentencePlan(s)
    # print s
    # print sp