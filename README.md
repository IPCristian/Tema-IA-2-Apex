# Tema 2 IA - Apex

## Descrierea jocului

Se va implementa jocul Apex (cu mici modificări, după cum urmează).

* Jocul este intre doi jucatori. Unul din ei folosește piese negre și celălalt albe. Fiecare jucător deține două colțuri opuse pe hartă. Vom considera că jucătorul cu piese negre mută primul.
* Tabla inițială este un grid de dimensiune 7*7 fără nicio piesă plasată: 
* Fiecare jucător va primi 11 piese având culoarea cu care joacă. Piesele se plasează la intersecțiile liniilor gridului.
* Atunci când vine rândul unui jucător, acesta are următoarele opțiuni de mutare (trebuie să aleagă una dintre ele):
1. să plaseze o piesă nouă pe tablă într-unul dintre colțurile deținute de jucător. Plasarea poate fi urmată în cadrul aceleiași ture (aceleiași mutări) de o deplasare a piesei, pe linie sau coloană, cu oricâte spații, într-un loc liber de pe tablă, dar fără să sară peste vreo piesă (indiferent dacă proprie sau adversară).
2. să mute o piesă deja existentă cu oricâte spații, într-un loc liber de pe tablă, dar fără să sară peste vreo piesă (indiferent dacă proprie sau adversară) piesa poate fi deplasată și în locul unei piese adversare, nu neapărat într-un loc liber (dacă pe drumul ei, pe linie sau coloană, nu a trebuit să sară peste vreo piesă). Atunci când piesa ajunge peste o piesă adversară, piesa adversară este capturată (luată de pe tablă) și oferită adversarului care o pune în colecția de piese nepasate încă pe tablă (și, deci, o poate refolosi). O piesă însă nu poate captura piese imediat vecine (pe poziții adiacente). Deci trebuie să se deplaseze peste minim un spațiu liber ca să captureze o piesă adversară. Observație: acele piese adiacente ar putea fi capturate de către alte piese aflate la distanță; ele sunt protejate prin reguli doar față de piesa vecină.
3. Pentru a nu ajunge la capturi repetitive imediat ce sunt puse piesele pe tablă, vom considera că o captură poate fi făcută doar de câtre o piesă deja aflată pe tablă, și nu una nouă. 

Jocul se termină atunci când unul dintre jucători realizează un lanț de piese conectând colțurile opuse, desemnate la începutul jocului ca fiind ale lui. Se consideră că piesele sunt conectate dacă sunt vecine pe linie, coloană sau diagonală.