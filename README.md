# preverb

## A connect_prev.py xtsv-modulként implementálva

Tökéletesen ugyanaz, mint a connect_prev.py legújabb változata, a kódsorok is teljesen megegyeznek, csak ki lett szedve belőle az, ami ugyanazt csinálta, mint az xtsv, illetve hozzá lettek adva az xtsv-hez szükséges dolgok.

A compound írása során azt nem sikerült átlátnom, hogy a parancssori kapcsolókat hogyan kezeli és adja át az xtsv, ezért az egyetlen parancssori kapcsolót (-v) kikommentáltam, az jelenleg nem használható.

Az output megegyezik a connect_prev.py outputjával.


## Testing

`make connect_preverbs` : ugyanaz, mint a preprocessben
`make connect_preverbs_no_compound` : csak hogy lássuk, hogy compound mező nélkül is hibátlanul lefut