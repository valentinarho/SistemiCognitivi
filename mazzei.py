import nltk
from nltk.parse.chart import ChartParser as Chart

grammatica = nltk.data.load('file:S0.cfg')
frase = "una donna e Dante lasciano un dono a Virgilio".split()


parser = Chart(grammatica)
trees = parser.nbest_parse(frase)
for tree in trees:
    print tree

trees[0].draw()





