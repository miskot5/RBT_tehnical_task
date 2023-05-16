# Web Indekser - Dokumentacija

Ova dokumentacija opisuje web indekser (web crawler) koji prikuplja informacije o nekretninama koje se izdaju ili prodaju u Srbiji. Web indekser povezuje se na web stranicu `https://www.nekretnine.rs/`, preuzima njen sadržaj i parsira ga kako bi pronašao informacije o nekretninama. Prikupljene informacije se čuvaju u MySQL bazi podataka.

### Prikupljanje informacija o nekretninama

Web indekser obilazi web stranicu `https://www.nekretnine.rs/`, prepoznaje linkove i ulazi na druge stranice kako bi ponovio proces prikupljanja informacija o nekretninama. Pored otkrivanja linkova, parser prepoznaje i druge sadržaje na stranici, kao što su `div`, `span`, `li`, itd. Informacije o nekretninama koje se prikupljaju uključuju:

- Tip nekretnine (stan ili kuća)
- Tip ponude (prodaja ili iznajmljivanje)
- Lokacija (grad i deo grada)
- Kvadratura nekretnine
- Godina izgradnje
- Površina zemljišta (samo za kuće)
- Spratnost (ukupna spratnost i sprat na kojem se nalazi, samo za stanove)
- Uknjiženost (da/ne)
- Tip grejanja
- Ukupan broj soba
- Ukupan broj kupatila (toaleta)
- Podaci o parkingu (da/ne)
- Dodatne informacije (prisustvo lifta, terase/lođe/balkona)

Ako neki od podataka nije dostupan u oglasu, polje u bazi ostaje prazno.

### Mini-aplikacija u Flask-u

Napravljena je mini-aplikacija koristeći Flask framework u Python-u koja pruža API za interakciju sa prikupljenim podacima o nekretninama. Aplikacija obezbeđuje sledeće API endpointe:

1.  GET/crawl - Dohvata informacije o svim nekretninama
2. `GET /real_estate/{id}` - Dohvata informacije o nekretnini na osnovu ID-ja nekretnine.
3. `GET /search` - Pretražuje nekretnine na osnovu zadatih parametara:
   - `tip` - Tip nekretnine (kuća/stan)
   - `minimalna_kvadratura` - Minimalna kvadratura nekretnine
   - `maksimalna_kvadratura` - Maksimalna kvadratura nekretnine
   - `parking` - Da/Ne (prisustvo parkinga)
4. `POST /real_estate` - Kreira novu nekretninu za prodaju/izdavanje.
5. `POST /update_real_estate` - Menja podatke nekretnine na osnovu ID-a nekretnine
6. 'POST /location' - Dodaje novu lokaciju 
7. 'POST /type_of_real_estate' - Dodaje nov tip nekrtnine

API za pretraživanje nekretnina omogućava pretragu na osnovu više parametara ili bez navođenja parametara. Implementirana je paginacija za rezultate pretrage nekretnina.

### Pokretanje aplikacije
Da biste pokrenuli aplikaciju, pratite sledeće korake:

1.Podesite MySQL bazu podataka sa odgovarajućim parametrima za povezivanje (migracije se kreiraju uz pomoc flaskove biblioteke flask-sqllchemy).
2.Pokrenite aplikaciju izvršavanjem python app.py u terminalu.
3.Aplikacija će biti dostupna na adresi http://localhost:5000.

### Napomena
Ova aplikacija je namenjena samo u edukativne svrhe. Pre upotrebe na stvarnim podacima, pobrinite se da poštujete pravila i uslove korišćenja web stranice https://www.nekretnine.rs/ i da imate dozvolu za prikupljanje i upotrebu podataka.
