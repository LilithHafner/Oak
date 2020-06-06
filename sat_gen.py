from random import randint

#web:     150, 620; 1000,  1000;  500, 10000 <https://msoos.github.io/cryptominisat_web/>
#pycosat: 200, 849; 10000, 10000; 500, 10000 (<.1 s) Documents/pycosat_test
    # pycosat: .086s
         # web: 8.6s
def generate(variables = 10, terms = 30, term_length = 3):
    return [[(randint(0,1)*2-1)*randint(1,variables) for i in range(term_length)] for j in range(terms)]

def to_string(problem):
    return '\n'.join(' '.join(map(str, term))+' 0' for term in problem)

def show(problem):
    print(to_string(problem))

def save(problem, file='sat_gen.dat'):
    open(file, 'w').write(to_string(problem))

save(generate())
