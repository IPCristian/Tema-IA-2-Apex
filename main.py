import copy
import statistics
import sys
import time
import pygame

ADANCIME_MAX = 1

timp_gandire_calculator = []
noduri_generate = []
timp_total = time.time()
mutari_calculator = 0
mutari_jucator = 0
joc_terminat = 0

def elem_identice(lista):
    if (len(set(lista)) == 1):
        return lista[0] if lista[0] != Joc.GOL else False
    return False

class Joc:
    """
    Clasa care defineste jocul. Se va schimba de la un joc la altul.
    """
    JMIN = None
    JMAX = None
    GOL = '#'
    NR_LINII = None
    NR_COLOANE = None
    scor_maxim = 0

    def __init__(self, matr=None, NR_LINII=None, NR_COLOANE=None):
        # creez proprietatea ultima_mutare # (l,c)
        self.ultima_mutare = None

        if matr:
            # e data tabla, deci suntem in timpul jocului
            self.matr = matr
        else:
            # nu e data tabla deci suntem la initializare
            self.matr = [[self.__class__.GOL] * NR_COLOANE for i in range(NR_LINII)]

            if NR_LINII is not None:
                self.__class__.NR_LINII = NR_LINII
            if NR_COLOANE is not None:
                self.__class__.NR_COLOANE = NR_COLOANE

            ######## calculare scor maxim ###########
            self.__class__.scor_maxim = 16

    def deseneaza_grid(self):  # tabla de exemplu este ["#","x","#","0",......]

        self.__class__.display.fill((255, 255, 255))
        for ind in range((self.__class__.NR_COLOANE - 1) * (self.__class__.NR_LINII - 1)):
            linie = ind // (self.__class__.NR_COLOANE - 1)
            coloana = ind % (self.__class__.NR_COLOANE - 1)
            rect = pygame.Rect(self.dim_celula / 2 + coloana * (self.dim_celula),
                               self.dim_celula / 2 + linie * (self.dim_celula),
                               self.dim_celula, self.dim_celula)
            pygame.draw.rect(self.__class__.display, (0, 0, 0), rect, 1)

        for ind in range(self.__class__.NR_COLOANE * self.__class__.NR_LINII):
            linie = ind // self.__class__.NR_COLOANE  # // inseamna div
            coloana = ind % self.__class__.NR_COLOANE

            if self.matr[linie][coloana] == 'x':
                self.__class__.display.blit(self.__class__.x_img, (
                    coloana * (self.__class__.dim_celula + 1), linie * (self.__class__.dim_celula + 1)))
            elif self.matr[linie][coloana] == '0':
                self.__class__.display.blit(self.__class__.zero_img, (
                    coloana * (self.__class__.dim_celula + 1), linie * (self.__class__.dim_celula + 1)))

            elif self.matr[linie][coloana] == '*':
                self.__class__.display.blit(self.__class__.select_img, (
                    coloana * (self.__class__.dim_celula + 1), linie * (self.__class__.dim_celula + 1)))
        # pygame.display.flip()

        font = pygame.font.Font('freesansbold.ttf',32)
        piese_juc = 11
        piese_cal = 11
        for linie in self.matr:
            piese_juc -= linie.count(self.__class__.JMIN)
            piese_juc -= linie.count('*')
            piese_cal -= linie.count(self.__class__.JMAX)

        # Numar de fiecare data cate piese am pe tabla
        text = font.render('Piese Jucator: ' + str(piese_juc),True,(0,0,0))
        text2 = font.render('Piese Calculator: ' + str(piese_cal), True, (0, 0, 0))
        textRect = text.get_rect()
        text2Rect = text2.get_rect()
        textRect.center = (200,415)
        text2Rect.center = (200,465)
        self.__class__.display.blit(text,textRect)
        self.__class__.display.blit(text2,text2Rect)

        # In caz ca nu doresti sa muti piesa dupa ce o pui pe colt sau sa renunti la o mutare dupa selectare
        text3 = font.render('Treci peste mutare',True,(0,0,0))
        text3Rect = text.get_rect()
        text3Rect.center = (190, 515)

        pygame.draw.rect(self.__class__.display,(0,0,0),(47,487,317,62),0)
        pygame.draw.rect(self.__class__.display,(176,236,222),(50,490,310,55),0)

        self.__class__.display.blit(text3,text3Rect)

        pygame.display.update()

    @classmethod
    def jucator_opus(cls, jucator):
        return cls.JMAX if jucator == cls.JMIN else cls.JMIN

    @classmethod
    def initializeaza(cls, display, NR_LINII=6, NR_COLOANE=7, dim_celula=100):
        cls.display = display
        cls.dim_celula = dim_celula
        cls.x_img = pygame.image.load('negru.png')
        cls.x_img = pygame.transform.scale(cls.x_img, (dim_celula, dim_celula))
        cls.zero_img = pygame.image.load('alb.png')
        cls.zero_img = pygame.transform.scale(cls.zero_img, (dim_celula, dim_celula))
        cls.select_img = pygame.image.load('selectat.png')
        cls.select_img = pygame.transform.scale(cls.select_img, (dim_celula,dim_celula))
        cls.celuleGrid = []  # este lista cu patratelele din grid
        for linie in range(NR_LINII):
            for coloana in range(NR_COLOANE):
                patr = pygame.Rect(coloana * (dim_celula + 1), linie * (dim_celula + 1), dim_celula, dim_celula)
                cls.celuleGrid.append(patr)

    def parcurgere(self, poz_crt, anterioare):
        um = self.ultima_mutare  # (l,c)
        culoare = self.matr[um[0]][um[1]]
        directii = [(0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1), (1, 0), (-1, 0)]

        for directie in directii:
            crt = (poz_crt[0] + directie[0], poz_crt[1] + directie[1])
            if crt in anterioare:
                break
            anterioare.append(crt)
            if not 0 <= crt[0] < self.__class__.NR_LINII or not 0 <= crt[1] < self.__class__.NR_COLOANE:
                break
            if not self.matr[crt[0]][crt[1]] == culoare:
                break

            if culoare == 'x' and um == (self.__class__.NR_LINII - 1, 0):
                return True
            elif culoare == '0' and um == (self.__class__.NR_LINII - 1, self.__class__.NR_COLOANE - 1):
                return True
            else:
                return self.parcurgere(crt)

        return False

    def final(self):

        # Pentru fiecare culoare, plec dintr-un colt, pun pe stiva in ce alti vecini pot merge si trec mai departe
        # Cand unul din ele nu mai are vecini il scot de pe stiva si ii verific iarasi parintele daca mai are alti
        # fii.
        def recursie():

            poz_crt = coada[len(coada) - 1]

            if poz_crt not in vizitate:
                vizitate.append(poz_crt)

            nr_vec = 0
            for directie in directii:
                nou = (poz_crt[0] + directie[0], poz_crt[1] + directie[1])

                if not 0 <= nou[0] < self.__class__.NR_LINII or not 0 <= nou[1] < self.__class__.NR_COLOANE:
                    continue

                if not self.matr[nou[0]][nou[1]] == culoare:
                    continue

                if nou == stop:
                    # for element in coada:
                    #     self.matr[element[0]][element[1]] = '*'
                    # self.matr[start[0]][start[1]] = '*'
                    # self.matr[stop[0]][stop[1]] = '*'
                    # self.deseneaza_grid()
                    return culoare

                if nou not in vizitate:
                    nr_vec += 1
                    coada.append(nou)
                    return recursie()

            if nr_vec == 0:
                coada.pop()
                if coada:
                    return recursie()

            return "Gresit"

        if not self.ultima_mutare:  # daca e inainte de prima mutare
            return False

        culori = [self.__class__.JMAX,self.__class__.JMIN]
        directii = [(0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1), (1, 0), (-1, 0)]
        # Am decis arbitrar ca x (Negru) sa aiba stanga-jos, dreapta-sus
        # iar 0 (Alb) sa aiba stanga-sus, dreapta-jos

        for culoare in culori:
            # print("Culoare curenta: " + str(culoare))
            coada = []
            vizitate = []

            if culoare == 'x':
                start = (self.__class__.NR_LINII -1, 0)
                stop = (0, self.__class__.NR_COLOANE - 1)
            else :
                start = (0, 0)
                stop = (self.__class__.NR_LINII-1,self.__class__.NR_COLOANE-1)

            coada.append(copy.deepcopy(start))

            if self.matr[start[0]][start[1]] != culoare:
                continue

            if self.matr[stop[0]][stop[1]] != culoare:
                continue

            culoare_returnata = recursie()

            # print("Culoare returnata: " + str(culoare_returnata))
            if culoare_returnata != "Gresit":
                return culoare_returnata

        return False

    def final_colorat(self):

        def recursie():

            poz_crt = coada[len(coada) - 1]

            if poz_crt not in vizitate:
                vizitate.append(poz_crt)

            nr_vec = 0
            for directie in directii:
                nou = (poz_crt[0] + directie[0], poz_crt[1] + directie[1])

                if not 0 <= nou[0] < self.__class__.NR_LINII or not 0 <= nou[1] < self.__class__.NR_COLOANE:
                    continue

                if not self.matr[nou[0]][nou[1]] == culoare:
                    continue

                if nou == stop:
                    for element in coada:
                        self.matr[element[0]][element[1]] = '*'
                    self.matr[start[0]][start[1]] = '*'
                    self.matr[stop[0]][stop[1]] = '*'
                    self.deseneaza_grid()
                    return culoare

                if nou not in vizitate:
                    nr_vec += 1
                    coada.append(nou)
                    return recursie()

            if nr_vec == 0:
                coada.pop()
                if coada:
                    return recursie()

            return "Gresit"

        if not self.ultima_mutare:  # daca e inainte de prima mutare
            return False

        culori = [self.__class__.JMAX,self.__class__.JMIN]
        directii = [(0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1), (1, 0), (-1, 0)]
        # Am decis arbitrar ca x (Negru) sa aiba stanga-jos, dreapta-sus
        # iar 0 (Alb) sa aiba stanga-sus, dreapta-jos

        for culoare in culori:
            # print("Culoare curenta: " + str(culoare))
            coada = []
            vizitate = []

            if culoare == 'x':
                start = (self.__class__.NR_LINII -1, 0)
                stop = (0, self.__class__.NR_COLOANE - 1)
            else :
                start = (0, 0)
                stop = (self.__class__.NR_LINII-1,self.__class__.NR_COLOANE-1)

            coada.append(copy.deepcopy(start))

            if self.matr[start[0]][start[1]] != culoare:
                continue

            if self.matr[stop[0]][stop[1]] != culoare:
                continue

            culoare_returnata = recursie()

            # print("Culoare returnata: " + str(culoare_returnata))
            if culoare_returnata != "Gresit":
                return culoare_returnata

        return False

    def mutari(self, jucator):
        l_mutari = []

        # Daca mai avem piese de pus pe masa

        piese_juc = 11
        piese_cal = 11
        for linie in self.matr:
            piese_juc -= linie.count(self.__class__.JMIN)
            piese_cal -= linie.count(self.__class__.JMAX)

        if self.__class__.JMAX == jucator and piese_cal > 0:
            # 1. Punem o piesa noua intr-un colt detinut de jucator

            colturi = []
            if jucator == 'x':
                colturi.append((self.__class__.NR_LINII - 1, 0)) # Stanga jos
                colturi.append((0, self.__class__.NR_COLOANE - 1)) # Dreapta sus
            else:
                colturi.append((0, 0)) # Stanga sus
                colturi.append((self.__class__.NR_LINII - 1, self.__class__.NR_COLOANE - 1)) # Dreapta jos

            for colt in colturi:
                # Daca avem deja piesa in coltul asta, nu putem pune piese noi
                if self.matr[colt[0]][colt[1]] != self.__class__.GOL:
                    continue

                matr_tabla_noua = copy.deepcopy(self.matr)
                matr_tabla_noua[colt[0]][colt[1]] = jucator
                jn = Joc(matr_tabla_noua)
                jn.ultima_mutare = (colt[0], colt[1])
                if jn not in l_mutari:
                    l_mutari.append(jn)

            # 2. Punem o piesa noua pe tabla, pornind de la coltul detinut de jucator, fara sa trecem peste piese

            directii = [(0, 1), (1, 0), (-1, 0), (0, -1)]
            vizitate = []
            for colt in colturi:
                # if jucator == '0':
                #     print(colt)

                # Daca avem deja piesa in coltul asta, nu putem pune piese noi
                if self.matr[colt[0]][colt[1]] != self.__class__.GOL:
                    continue

                coada = [(colt[0],colt[1])]
                while coada:
                    poz_crt = coada.pop(0)
                    vizitate.append(poz_crt)

                    for directie in directii:
                        poz_noua = (poz_crt[0] + directie[0],poz_crt[1] + directie[1])

                        if 0 <= poz_noua[0] < self.__class__.NR_LINII and\
                            0 <= poz_noua[1] < self.__class__.NR_COLOANE:

                            if self.matr[poz_noua[0]][poz_noua[1]] != self.__class__.GOL:
                                continue

                            if poz_noua not in vizitate:
                                if poz_noua not in coada:
                                    coada.append((poz_noua[0],poz_noua[1]))
                                matr_tabla_noua = copy.deepcopy(self.matr)
                                matr_tabla_noua[poz_noua[0]][poz_noua[1]] = jucator
                                jn = Joc(matr_tabla_noua)
                                jn.ultima_mutare = (poz_noua[0], poz_noua[1])
                                if jn not in l_mutari:
                                    l_mutari.append(jn)

        # 3. Mutam o piesa existenta

        directii = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        vizitate = []
        for i in range(self.__class__.NR_LINII):
            for j in range(self.__class__.NR_COLOANE):
                if self.matr[i][j] == jucator:
                    coada = [(i, j)]
                    while coada:
                        poz_crt = coada.pop(0)
                        vizitate.append(poz_crt)
                        for directie in directii:
                            poz_noua = (poz_crt[0] + directie[0], poz_crt[1] + directie[1])

                            if 0 <= poz_noua[0] < self.__class__.NR_LINII and \
                                    0 <= poz_noua[1] < self.__class__.NR_COLOANE:

                                if self.matr[poz_noua[0]][poz_noua[1]] == jucator:
                                    continue

                                # Daca capturam o piesa adversara, avem grija sa nu capturam un vecin
                                ver = 1
                                if self.matr[poz_noua[0]][poz_noua[1]] != self.__class__.GOL:
                                    for verificare in directii:
                                        if i + verificare[0] == poz_noua[0] and j + verificare[1] == poz_noua[1]:
                                            ver = 0

                                if poz_noua not in vizitate and ver == 1:
                                    if poz_noua not in coada and self.matr[poz_noua[0]][poz_noua[1]] == self.__class__.GOL:
                                        coada.append((poz_noua[0], poz_noua[1]))
                                    matr_tabla_noua = copy.deepcopy(self.matr)
                                    matr_tabla_noua[poz_noua[0]][poz_noua[1]] = jucator
                                    # print("Mutare - " + str((i,j)) + " -> " + str(poz_noua))
                                    matr_tabla_noua[i][j] = self.__class__.GOL
                                    jn = Joc(matr_tabla_noua)
                                    jn.ultima_mutare = (poz_noua[0], poz_noua[1])
                                    if jn not in l_mutari:
                                        l_mutari.append(jn)


        return l_mutari

    def calcul_scor1(self, jucator):

        scor = 0

        if jucator == '0':
            for i in range(self.__class__.NR_LINII):
                for j in range(self.__class__.NR_COLOANE):
                    if self.matr[i][j] == jucator and abs(i-j) < 3:
                        scor +=  (7 - abs(i-j))

        if jucator == 'x':
            for i in range(self.__class__.NR_LINII):
                for j in range(self.__class__.NR_COLOANE):
                    if self.matr[i][j] == 'x' and abs(i+j-7) < 3:
                        scor += (7 - abs(i+j-7))

        return scor

    def calcul_scor2(self, jucator):

        scor = 0

        if jucator == '0':
            for i in range(self.__class__.NR_LINII):
                for j in range(self.__class__.NR_COLOANE):
                    if i==j and self.matr[i][j] == jucator:
                        scor += 1

        if jucator == 'x':
            for i in range(self.__class__.NR_LINII):
                for j in range(self.__class__.NR_COLOANE):
                    if i+j-7 == 0 and self.matr[i][j] == jucator:
                        scor += 1

        return scor

    def estimeaza_scor(self, adancime):
        t_final = self.final()
        # if (adancime==0):
        if t_final == self.__class__.JMAX:
            return (self.__class__.scor_maxim + adancime)
        elif t_final == self.__class__.JMIN:
            return (-self.__class__.scor_maxim - adancime)
        else:
            return (self.calcul_scor1(self.__class__.JMAX) - self.calcul_scor1(self.__class__.JMIN))

    def sirAfisare(self):
        sir = "  |"
        sir += " ".join([str(i) for i in range(self.NR_COLOANE)]) + "\n"
        sir += "-" * (self.NR_COLOANE + 1) * 2 + "\n"
        sir += "\n".join([str(i) + " |" + " ".join([str(x) for x in self.matr[i]]) for i in range(len(self.matr))])
        return sir

    def __str__(self):
        return self.sirAfisare()

    def __repr__(self):
        return self.sirAfisare()


class Stare:
    """
    Clasa folosita de algoritmii minimax si alpha-beta
    Are ca proprietate tabla de joc
    Functioneaza cu conditia ca in cadrul clasei Joc sa fie definiti JMIN si JMAX (cei doi jucatori posibili)
    De asemenea cere ca in clasa Joc sa fie definita si o metoda numita mutari() care ofera lista cu configuratiile posibile in urma mutarii unui jucator
    """

    def __init__(self, tabla_joc, j_curent, adancime, parinte=None, scor=None):
        self.tabla_joc = tabla_joc
        self.j_curent = j_curent

        # adancimea in arborele de stari
        self.adancime = adancime

        # scorul starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.scor = scor

        # lista de mutari posibile din starea curenta
        self.mutari_posibile = []

        # cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        self.stare_aleasa = None

    def mutari(self):
        l_mutari = self.tabla_joc.mutari(self.j_curent)
        juc_opus = Joc.jucator_opus(self.j_curent)
        l_stari_mutari = [Stare(mutare, juc_opus, self.adancime - 1, parinte=self) for mutare in l_mutari]


        return l_stari_mutari

    def __str__(self):
        sir = str(self.tabla_joc) + "(Juc curent:" + self.j_curent + ")\n"
        return sir

    def __repr__(self):
        sir = str(self.tabla_joc) + "(Juc curent:" + self.j_curent + ")\n"
        return sir


""" Algoritmul MinMax """


def min_max(stare):
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    # calculez toate mutarile posibile din starea curenta
    stare.mutari_posibile = stare.mutari()
    noduri_generate.append(len(stare.mutari_posibile))

    # aplic algoritmul minimax pe toate mutarile posibile (calculand astfel subarborii lor)
    mutari_scor = [min_max(mutare) for mutare in stare.mutari_posibile]

    if stare.j_curent == Joc.JMAX:
        # daca jucatorul e JMAX aleg starea-fiica cu scorul maxim
        stare.stare_aleasa = max(mutari_scor, key=lambda x: x.scor)
        print("Mutarea aleasa are scorul " + str(stare.stare_aleasa.scor))
    else:
        # daca jucatorul e JMIN aleg starea-fiica cu scorul minim
        stare.stare_aleasa = min(mutari_scor, key=lambda x: x.scor)
    stare.scor = stare.stare_aleasa.scor

    return stare


def alpha_beta(alpha, beta, stare):
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    if alpha > beta:
        return stare  # este intr-un interval invalid deci nu o mai procesez

    stare.mutari_posibile = stare.mutari()
    noduri_generate.append(len(stare.mutari_posibile))

    if stare.j_curent == Joc.JMAX:
        scor_curent = float('-inf')

        for mutare in stare.mutari_posibile:
            # calculeaza scorul
            stare_noua = alpha_beta(alpha, beta, mutare)

            if (scor_curent < stare_noua.scor):
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor
            if (alpha < stare_noua.scor):
                alpha = stare_noua.scor
                if alpha >= beta:
                    break

    elif stare.j_curent == Joc.JMIN:
        scor_curent = float('inf')
        for mutare in stare.mutari_posibile:

            stare_noua = alpha_beta(alpha, beta, mutare)

            if (scor_curent > stare_noua.scor):
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor

            if (beta > stare_noua.scor):
                beta = stare_noua.scor
                if alpha >= beta:
                    break
    stare.scor = stare.stare_aleasa.scor
    print("Mutarea aleasa are scorul " + str(stare.stare_aleasa.scor))

    return stare


def afis_daca_final(stare_curenta):
    final = stare_curenta.tabla_joc.final_colorat()
    if (final):
        if final == '0':
            print("A castigat alb")
        elif final == 'x':
            print("A castigat negru")
        global joc_terminat
        joc_terminat = 1
        print("Timp maxim de gandire al calculatorului: " + str(max(timp_gandire_calculator)) + " milisecunde")
        print("Timp minim de gandire al calculatorului: " + str(min(timp_gandire_calculator)) + " milisecunde")
        timp_mediu = sum(timp_gandire_calculator) // len(timp_gandire_calculator)
        print("Timp mediu de gandire al calculatorului: " + str(timp_mediu) + " milisecunde")
        mediana = statistics.median(timp_gandire_calculator)
        print("Mediana timpului de gandire al calculatorului: " + str(mediana) + " milisecunde")
        print("Timp total: " + str(time.time() - timp_total))
        print("Mutari jucator: " + str(mutari_jucator))
        print("Mutari calculator: " + str(mutari_calculator))
        print("Numar maxim Noduri generate: " + str(max(noduri_generate)))
        print("Numar minim Noduri generate: " + str(min(noduri_generate)))
        nr_mediu = sum(noduri_generate) // len(noduri_generate)
        print("Numar mediu Noduri generate: " + str(nr_mediu))
        mediana = statistics.median(noduri_generate)
        print("Mediana nodurilor generate: " + str(max(noduri_generate)))
        return True

    return False


class Buton:
    def __init__(self, display=None, left=0, top=0, w=0, h=0, culoareFundal=(53, 80, 115),
                 culoareFundalSel=(89, 134, 194), text="", font="arial", fontDimensiune=16, culoareText=(255, 255, 255),
                 valoare=""):
        self.display = display
        self.culoareFundal = culoareFundal
        self.culoareFundalSel = culoareFundalSel
        self.text = text
        self.font = font
        self.w = w
        self.h = h
        self.selectat = False
        self.fontDimensiune = fontDimensiune
        self.culoareText = culoareText
        # creez obiectul font
        fontObj = pygame.font.SysFont(self.font, self.fontDimensiune)
        self.textRandat = fontObj.render(self.text, True, self.culoareText)
        self.dreptunghi = pygame.Rect(left, top, w, h)
        # aici centram textul
        self.dreptunghiText = self.textRandat.get_rect(center=self.dreptunghi.center)
        self.valoare = valoare

    def selecteaza(self, sel):
        self.selectat = sel
        self.deseneaza()

    def selecteazaDupacoord(self, coord):
        if self.dreptunghi.collidepoint(coord):
            self.selecteaza(True)
            return True
        return False

    def updateDreptunghi(self):
        self.dreptunghi.left = self.left
        self.dreptunghi.top = self.top
        self.dreptunghiText = self.textRandat.get_rect(center=self.dreptunghi.center)

    def deseneaza(self):
        culoareF = self.culoareFundalSel if self.selectat else self.culoareFundal
        pygame.draw.rect(self.display, culoareF, self.dreptunghi)
        self.display.blit(self.textRandat, self.dreptunghiText)


class GrupButoane:
    def __init__(self, listaButoane=[], indiceSelectat=0, spatiuButoane=10, left=0, top=0):
        self.listaButoane = listaButoane
        self.indiceSelectat = indiceSelectat
        self.listaButoane[self.indiceSelectat].selectat = True
        self.top = top
        self.left = left
        leftCurent = self.left
        for b in self.listaButoane:
            b.top = self.top
            b.left = leftCurent
            b.updateDreptunghi()
            leftCurent += (spatiuButoane + b.w)

    def selecteazaDupacoord(self, coord):
        for ib, b in enumerate(self.listaButoane):
            if b.selecteazaDupacoord(coord):
                self.listaButoane[self.indiceSelectat].selecteaza(False)
                self.indiceSelectat = ib
                return True
        return False

    def deseneaza(self):
        # atentie, nu face wrap
        for b in self.listaButoane:
            b.deseneaza()

    def getValoare(self):
        return self.listaButoane[self.indiceSelectat].valoare


############# ecran initial ########################
def deseneaza_alegeri(display, tabla_curenta):
    btn_alg = GrupButoane(
        top=30,
        left=30,
        listaButoane=[
            Buton(display=display, w=80, h=30, text="minimax", valoare="minimax"),
            Buton(display=display, w=80, h=30, text="alphabeta", valoare="alphabeta")
        ],
        indiceSelectat=1)
    btn_juc = GrupButoane(
        top=100,
        left=30,
        listaButoane=[
            Buton(display=display, w=35, h=30, text="negru", valoare="x"),
            Buton(display=display, w=35, h=30, text="alb", valoare="0")
        ],
        indiceSelectat=0)
    ok = Buton(display=display, top=170, left=30, w=40, h=30, text="ok", culoareFundal=(155, 0, 55))
    btn_alg.deseneaza()
    btn_juc.deseneaza()
    ok.deseneaza()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                if joc_terminat == 0:
                    print("Timp maxim de gandire al calculatorului: " + str(max(timp_gandire_calculator)) + " milisecunde")
                    print("Timp minim de gandire al calculatorului: " + str(min(timp_gandire_calculator)) + " milisecunde")
                    timp_mediu = sum(timp_gandire_calculator) // len(timp_gandire_calculator)
                    print("Timp mediu de gandire al calculatorului: " + str(timp_mediu) + " milisecunde")
                    mediana = statistics.median(timp_gandire_calculator)
                    print("Mediana timpului de gandire al calculatorului: " + str(mediana) + " milisecunde")
                    print("Timp total: " + str(time.time() - timp_total))
                    print("Mutari jucator: " + str(mutari_jucator))
                    print("Mutari calculator: " + str(mutari_calculator))
                    print("Numar maxim Noduri generate: " + str(max(noduri_generate)))
                    print("Numar minim Noduri generate: " + str(min(noduri_generate)))
                    nr_mediu = sum(noduri_generate) // len(noduri_generate)
                    print("Numar mediu Noduri generate: " + str(nr_mediu))
                    mediana = statistics.median(noduri_generate)
                    print("Mediana nodurilor generate: " + str(max(noduri_generate)))
                sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if not btn_alg.selecteazaDupacoord(pos):
                    if not btn_juc.selecteazaDupacoord(pos):
                        if ok.selecteazaDupacoord(pos):
                            display.fill((0, 0, 0))  # stergere ecran
                            tabla_curenta.deseneaza_grid()
                            return btn_juc.getValoare(), btn_alg.getValoare()
        pygame.display.update()


def main():
    global mutari_calculator
    global mutari_jucator
    # setari interf grafica
    pygame.init()
    pygame.display.set_caption("Ilie Petre-Cristian - Apex")
    # dimensiunea ferestrei in pixeli
    nl = 8
    nc = 8
    w = 50
    ecran = pygame.display.set_mode(size=(nc * (w + 1) - 1, nl * (w + 1) - 1 + 150))  # N *w+ N-1= N*(w+1)-1
    Joc.initializeaza(ecran, NR_LINII=nl, NR_COLOANE=nc, dim_celula=w)

    # initializare tabla
    tabla_curenta = Joc(NR_LINII=8, NR_COLOANE=8);
    Joc.JMIN, tip_algoritm = deseneaza_alegeri(ecran, tabla_curenta)
    print(Joc.JMIN, tip_algoritm)

    Joc.JMAX = '0' if Joc.JMIN == 'x' else 'x'
    # Joc.JMAX_piese = 11
    # Joc.JMIN_piese = 11

    print("Tabla initiala")
    print(str(tabla_curenta))

    # creare stare initiala
    stare_curenta = Stare(tabla_curenta, 'x', ADANCIME_MAX)

    tabla_curenta.deseneaza_grid()
    t_inainte = None
    pozitie_timp = 0

    while True:

        if (stare_curenta.j_curent == Joc.JMIN):

            if pozitie_timp == 2:
                # afisarea starii jocului in urma mutarii utilizatorului
                print("\nTabla dupa mutarea jucatorului")
                print(str(stare_curenta))

                t_dupa = int(round(time.time() * 1000))
                print("Jucatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")
                print("Este randul Calculatorului\n")
                stare_curenta.tabla_joc.deseneaza_grid()
                # testez daca jocul a ajuns intr-o stare finala
                # si afisez un mesaj corespunzator in caz ca da
                if afis_daca_final(stare_curenta):
                    break

                # S-a realizat o mutare. Schimb jucatorul cu cel opus
                stare_curenta.j_curent = Joc.jucator_opus(stare_curenta.j_curent)
                mutari_jucator += 1
                pozitie_timp = 0

            piese_juc = 11
            tabla_joc = copy.deepcopy(stare_curenta.tabla_joc.matr)
            for lin in tabla_joc:
                piese_juc -= lin.count(Joc.JMIN)

            colturi = []
            if Joc.JMIN == 'x':
                colturi.append((Joc.NR_LINII - 1, 0))  # Stanga jos
                colturi.append((0, Joc.NR_COLOANE - 1))  # Dreapta sus
            else:
                colturi.append((0, 0))  # Stanga sus
                colturi.append((Joc.NR_LINII - 1, Joc.NR_COLOANE - 1))  # Dreapta jos

            if not t_inainte:
                t_inainte = int(round(time.time() * 1000))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # iesim din program
                    if joc_terminat == 0:
                        print("Timp maxim de gandire al calculatorului: " + str(
                            max(timp_gandire_calculator)) + " milisecunde")
                        print("Timp minim de gandire al calculatorului: " + str(
                            min(timp_gandire_calculator)) + " milisecunde")
                        timp_mediu = sum(timp_gandire_calculator) // len(timp_gandire_calculator)
                        print("Timp mediu de gandire al calculatorului: " + str(timp_mediu) + " milisecunde")
                        mediana = statistics.median(timp_gandire_calculator)
                        print("Mediana timpului de gandire al calculatorului: " + str(mediana) + " milisecunde")
                        print("Timp total: " + str(time.time() - timp_total))
                        print("Mutari jucator: " + str(mutari_jucator))
                        print("Mutari calculator: " + str(mutari_calculator))
                        print("Numar maxim Noduri generate: " + str(max(noduri_generate)))
                        print("Numar minim Noduri generate: " + str(min(noduri_generate)))
                        nr_mediu = sum(noduri_generate) // len(noduri_generate)
                        print("Numar mediu Noduri generate: " + str(nr_mediu))
                        mediana = statistics.median(noduri_generate)
                        print("Mediana nodurilor generate: " + str(max(noduri_generate)))
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEMOTION:

                    pos = pygame.mouse.get_pos()  # coordonatele cursorului

                    if 50 <= pos[0] <= 360 and 490 <= pos[1] <= 545:
                        stare_curenta.tabla_joc.deseneaza_grid()
                        break

                    for np in range(len(Joc.celuleGrid)):
                        if Joc.celuleGrid[np].collidepoint(pos):
                            stare_curenta.tabla_joc.deseneaza_grid()
                            break

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()  # coordonatele cursorului la momentul clickului

                    if pozitie_timp == 0:
                        for np in range(len(Joc.celuleGrid)):

                            if Joc.celuleGrid[np].collidepoint(pos):
                                linie = np // Joc.NR_COLOANE
                                coloana = np % Joc.NR_COLOANE

                                ###############################

                                if (stare_curenta.tabla_joc.matr[linie][coloana] == Joc.GOL) and (piese_juc > 0)\
                                        and ((linie,coloana) in colturi):

                                    stare_curenta.tabla_joc.matr[linie][coloana] = '*'

                                    coada = [(linie, coloana)]
                                    vizitate = []
                                    poz_valide = []
                                    directii = [(0, 1), (1, 0), (-1, 0), (0, -1)]

                                    while coada:
                                        poz_crt = coada.pop(0)
                                        vizitate.append(poz_crt)

                                        for directie in directii:
                                            nou = (poz_crt[0] + directie[0], poz_crt[1] + directie[1])

                                            if not 0 <= nou[0] < Joc.NR_LINII or \
                                                    not 0 <= nou[1] < Joc.NR_COLOANE:
                                                continue

                                            if stare_curenta.tabla_joc.matr[nou[0]][nou[1]] == Joc.JMIN:
                                                continue

                                            if stare_curenta.tabla_joc.matr[nou[0]][nou[1]] == '*':
                                                continue

                                            if stare_curenta.tabla_joc.matr[nou[0]][nou[1]] == Joc.JMAX:
                                                continue

                                            if nou not in vizitate:
                                                if nou not in coada:
                                                    coada.append(nou)
                                                    poz_valide.append(nou)

                                    pozitie_timp = 1

                                elif stare_curenta.tabla_joc.matr[linie][coloana] == Joc.JMIN:
                                    stare_curenta.tabla_joc.matr[linie][coloana] = '*'

                                    coada = [(linie, coloana)]
                                    vizitate = []
                                    poz_valide = []
                                    directii = [(0, 1), (1, 0), (-1, 0), (0, -1)]

                                    while coada:
                                        poz_crt = coada.pop(0)
                                        vizitate.append(poz_crt)

                                        for directie in directii:
                                            nou = (poz_crt[0] + directie[0], poz_crt[1] + directie[1])

                                            if not 0 <= nou[0] < Joc.NR_LINII or \
                                                    not 0 <= nou[1] < Joc.NR_COLOANE:
                                                continue

                                            if stare_curenta.tabla_joc.matr[nou[0]][nou[1]] == Joc.JMIN:
                                                continue

                                            if stare_curenta.tabla_joc.matr[nou[0]][nou[1]] == '*':
                                                continue

                                            if stare_curenta.tabla_joc.matr[nou[0]][nou[1]] == Joc.JMAX:
                                                ver = 1
                                                for verificare in directii:
                                                    if linie + verificare[0] == nou[0] and\
                                                            coloana + verificare[1] == nou[1]:
                                                        ver = 0
                                                if ver == 0:
                                                    continue

                                            if stare_curenta.tabla_joc.matr[nou[0]][nou[1]] == Joc.GOL:
                                                if nou not in vizitate:
                                                    if nou not in coada:
                                                        coada.append(nou)

                                            poz_valide.append(nou)

                                    pozitie_timp = 1


                    elif pozitie_timp == 1:

                        if 50 <= pos[0] <= 360 and 490 <= pos[1] <= 545:
                            stare_curenta.tabla_joc.matr[linie][coloana] = Joc.JMIN
                            pozitie_timp = 2

                        else:
                            for np in range(len(Joc.celuleGrid)):

                                if Joc.celuleGrid[np].collidepoint(pos):
                                    linie_noua = np // Joc.NR_COLOANE
                                    coloana_noua = np % Joc.NR_COLOANE
                                    if (linie_noua,coloana_noua) in poz_valide:
                                        stare_curenta.tabla_joc.matr[linie_noua][coloana_noua] = Joc.JMIN
                                        stare_curenta.tabla_joc.matr[linie][coloana] = Joc.GOL
                                        pozitie_timp = 2
                                        poz_valide = []

        # --------------------------------
        else:  # jucatorul e JMAX (calculatorul)
            # Mutare calculator

            # preiau timpul in milisecunde de dinainte de mutare
            t_inainte = int(round(time.time() * 1000))
            if tip_algoritm == 'minimax':
                stare_actualizata = min_max(stare_curenta)
            else:  # tip_algoritm=="alphabeta"
                stare_actualizata = alpha_beta(-500, 500, stare_curenta)
            if stare_curenta.tabla_joc != stare_actualizata.stare_aleasa.tabla_joc:
                mutari_calculator += 1
            stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc

            print("Tabla dupa mutarea calculatorului\n" + str(stare_curenta))

            # preiau timpul in milisecunde de dupa mutare
            t_dupa = int(round(time.time() * 1000))
            timp_gandire_calculator.append(t_dupa-t_inainte)
            print("Calculatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")
            print("Este randul Jucatorului\n")

            stare_curenta.tabla_joc.deseneaza_grid()
            if afis_daca_final(stare_curenta):
                break

            # S-a realizat o mutare. Schimb jucatorul cu cel opus
            stare_curenta.j_curent = Joc.jucator_opus(stare_curenta.j_curent)




if __name__ == "__main__":
    main()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if joc_terminat == 0:
                    print("Timp maxim de gandire al calculatorului: " + str(
                        max(timp_gandire_calculator)) + " milisecunde")
                    print("Timp minim de gandire al calculatorului: " + str(
                        min(timp_gandire_calculator)) + " milisecunde")
                    timp_mediu = sum(timp_gandire_calculator) // len(timp_gandire_calculator)
                    print("Timp mediu de gandire al calculatorului: " + str(timp_mediu) + " milisecunde")
                    mediana = statistics.median(timp_gandire_calculator)
                    print("Mediana timpului de gandire al calculatorului: " + str(mediana) + " milisecunde")
                    print("Timp total: " + str(time.time() - timp_total))
                    print("Mutari jucator: " + str(mutari_jucator))
                    print("Mutari calculator: " + str(mutari_calculator))
                    print("Numar maxim Noduri generate: " + str(max(noduri_generate)))
                    print("Numar minim Noduri generate: " + str(min(noduri_generate)))
                    nr_mediu = sum(noduri_generate) // len(noduri_generate)
                    print("Numar mediu Noduri generate: " + str(nr_mediu))
                    mediana = statistics.median(noduri_generate)
                    print("Mediana nodurilor generate: " + str(max(noduri_generate)))
                pygame.quit()
                sys.exit()
