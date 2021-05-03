import sys

#citire
inputfile = sys.argv[1]
f = open(inputfile, 'r+')
format_list = list()
input_list = f.readlines()
for x in range(0, len(input_list)):
    format_list.append(input_list[x].replace('\n',''))
no_states = format_list[0]
final_states = format_list[1:2]
f.close()

startStates = []
symbols = []
nextStates = []
unique_symbols = []
unique_states = []

#prelucrare pentru tranztiile fara epsilon
def search(dict, subState, word):
    new_list = []
    final_list = []
    for x in subState:
        if (x, word) in dict.keys():
            new_list += dict[(x, word)]
    return new_list

#prelucrare pentru tranzitii cu epsilon
def search_eps(dict, substring, symbol):
    new_list = []
    final_states = []
    for x in substring:
        if x in dict.keys():
            new_list += dict[(x)]
    return new_list

def reunion(result_list):
    result_union = list(set().union(*result_list))
    final_list = sorted(result_union)
    return result_union

#concatenare
def conc(initial_list):
    final_str = ''
    for x in initial_list:
        final_str += x
    return final_str

#prelucrare a datelor de intrare
for i in range(2, len(format_list)):
   startStates.append(format_list[i].split(' ')[0])
   symbols.append(format_list[i].split(' ')[1])
   nextStates.append(format_list[i].split(' ')[2:])

for i in range(0, len(symbols)):
    if symbols[i] not in unique_symbols:
        unique_symbols.append(symbols[i])

unique_symbols = sorted(unique_symbols)

#adaugarea tranzitiilor in dictionarul nfa
nfa = {}
dfa = {}
dfa_eps = {}
unique_symbols_eps = []
epsilon_trans = {}
epsilon_elements = []
for i in range(0, len(startStates)):
    nfa[(startStates[i], symbols[i])] = nextStates[i]

unique_symbols_eps = unique_symbols.copy()
if 'eps' in unique_symbols_eps:
    unique_symbols_eps.remove('eps')

#dictionarul epsilon-closure
for i in range(0, int(no_states)):
    epsilon_trans[str(i)] = [str(i)]

#epsilon-closure
for (state, symbol), next_state in nfa.items():
    if(symbol == 'eps'):
        for i in range(0, len(next_state)):
            epsilon_trans[state].append(next_state[i])
            epsilon_elements.append(next_state[i])
            while(epsilon_elements != []):
                if (epsilon_elements[0], 'eps') in nfa:
                    for j in range (0, len(nfa[(epsilon_elements[0], 'eps')])):
                        if ((nfa[(epsilon_elements[0], 'eps')])[j] not in epsilon_trans[state]):
                            epsilon_elements.append(nfa[(epsilon_elements[0], 'eps')][j])
                            epsilon_trans[state].append(nfa[(epsilon_elements[0], 'eps')][j])
                epsilon_elements.pop(0)
            epsilon_elements.clear()

for key,value in epsilon_trans.items():
    value = list(dict.fromkeys(value))
    epsilon_trans[key] = sorted(value)

helper = []
newStates = []

def epsilon_calculus(text, symbol):
    new_list = []
    new_list = list(dict.fromkeys(search_eps(epsilon_trans, search(nfa, text, symbol), symbol)))
    return sorted(new_list)

def normal_calculus(text, symbol):
    new_list = []
    new_list = list(dict.fromkeys(search(nfa, text, symbol)))
    return sorted(new_list)

#nfa to dfa
if 'eps' not in unique_symbols:
    for key, value in nfa.items():
        if(len(value) <= 1):
            for symbol in unique_symbols:
                if (key == ('0', symbol)):
                    dfa[key] = value
        else:
            if(conc(sorted(value)) not in helper):
                newStates.append(conc(sorted(value)))
                helper.append(conc(sorted(value)))
                dfa[key] = [(conc(sorted(value)))]
            while(newStates != []):
                for symbol in unique_symbols:
                    dfa[(newStates[0], symbol)] = normal_calculus(newStates[0], symbol)
                    dfa[(newStates[0], symbol)] = [conc(dfa[(newStates[0], symbol)])]
                    if(len(conc(dfa[(newStates[0], symbol)])) > 1 and conc(dfa[(newStates[0], symbol)]) not in helper):
                        newStates.append(conc(dfa[(newStates[0], symbol)]))
                        helper.append(conc(dfa[(newStates[0], symbol)]))
                newStates.pop(0)
            newStates.clear()
else:
    for key, value in epsilon_trans.items():
        if(len(value) > 1):
            if(conc(sorted(value)) not in helper):
                newStates.append(conc(value))
                helper.append(conc(value))
            while(newStates != []):
                for symbol in unique_symbols_eps:
                    dfa[(newStates[0], symbol)] = epsilon_calculus(newStates[0], symbol)
                    dfa[(newStates[0], symbol)] = [conc(dfa[(newStates[0], symbol)])]
                    if(len(conc(dfa[(newStates[0], symbol)])) > 1 and conc(dfa[(newStates[0], symbol)]) not in helper):
                        newStates.append(conc(dfa[(newStates[0], symbol)]))
                        helper.append(conc(dfa[(newStates[0], symbol)]))
                newStates.pop(0)
            newStates.clear()
            break


sink_state = False
dfa_copy = dfa.copy()
list_of_states = []
list_of_nextStates = []

for (x,y), z in dfa.items():
    list_of_states.append(x)
    list_of_nextStates.append(z[0])

#verific daca mai sunt tranzitii pe listele de lungime 1
if 'eps' not in unique_symbols:
    for (x,y), value in nfa.items():
        if(len(value) <= 1):
            if x in list_of_nextStates:
                dfa[(x,y)] = value

#adaug toate starile din dfa in lista
for i in list_of_nextStates:
    list_of_states.append(i)
list_of_states = list(dict.fromkeys(list_of_states))

states_to_write = []

#pun tranzitia starilor care nu sunt definite pe un simbol pe sink_state
for x in list_of_states:
    for symbol in unique_symbols_eps:
        if (x, symbol) not in dfa.keys():
           dfa[(x, symbol)] = ['99999']
           sink_state = True

#tranzitiile sink state-ului
if(sink_state == True):
    for symbol in unique_symbols_eps:
        dfa[('99999', symbol)] = ['99999']

#adaugarea starilor finale in lista
dfaFinalStates = []
for nextState in dfa.values():
    for x in final_states[0]:
        if x in nextState[0]:
            dfaFinalStates.append(nextState[0])

dfaFinalStates = list(dict.fromkeys(dfaFinalStates)) 
states_to_write = list(dict.fromkeys(states_to_write)) 

#afisare
outfile = sys.argv[2]
f = open(outfile, 'w+')
if(sink_state == False):
    f.write(str(len(list_of_states)))
else:
    f.write(str(len(list_of_states) + 1))
f.write("\n")
f.write(" ".join(dfaFinalStates))
f.write("\n")

for (x,y), z in dfa.items():
    f.write(x + " " + y + " " + z[0])
    f.write("\n")
f.close()


        







   





