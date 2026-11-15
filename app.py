import hashlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from sqlalchemy import text

st.set_page_config(page_title="Quiniela Bufalà B", page_icon="⚽", layout="centered")
TZ = ZoneInfo("Europe/Madrid")
BONUS = 2  # puntos extra por acertar el marcador exacto del Bufalà
DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
T = {"SGA": "Sant Gabriel A", "CBB": "Can Buxeres B", "EEG": "E.E. Guineueta", "ALZ": "Alzamora A",
     "BUF": "Bufalà B", "POM": "Pomar B", "SAN": "Sant Andreu C", "BRA": "E. Brafa A",
     "FEG": "Fund. Esportiva FEG", "CAN": "Canyelles A", "ARR": "Arrabal-Calaf", "HOS": "L'Hospitalet C.",
     "SIG": "Sant Ignasi A", "EUR": "Europa C", "PRE": "EF Premier", "PNO": "Poble Nou A"}
# Calendario FCF (Juvenil Primera Divisió, grup 6): local-visitante-MMDD-HHMM
J = {
    8: "EEG-PNO-1114-1800 CAN-CBB-1114-1800 ARR-HOS-1114-1815 SIG-SGA-1114-1900 FEG-ALZ-1115-1400 BRA-BUF-1115-1700 EUR-PRE-1115-1700 SAN-POM-1115-1800",
    9: "SGA-EUR-1121-1200 EEG-SAN-1121-1800 BUF-CAN-1121-1900 CBB-SIG-1121-2000 ALZ-BRA-1122-1415 POM-FEG-1122-1545 PRE-ARR-1122-1900 PNO-HOS-1122-2000",
    10: "FEG-EEG-1128-1800 CAN-ALZ-1128-1800 ARR-SGA-1128-1815 HOS-PRE-1129-1000 SIG-BUF-1129-1200 SAN-PNO-1129-1600 BRA-POM-1129-1700 EUR-CBB-1129-1930",
    11: "SGA-HOS-1212-1200 CBB-ARR-1212-1600 EEG-BRA-1212-1800 ALZ-SIG-1212-1800 BUF-EUR-1212-1800 SAN-FEG-1213-1600 POM-CAN-1213-1750 PNO-PRE-1213-2000",
    12: "FEG-PNO-1219-1800 CAN-EEG-1219-1800 ARR-BUF-1219-1815 HOS-CBB-1220-1000 SIG-POM-1220-1200 BRA-SAN-1220-1700 EUR-ALZ-1220-1930 PRE-SGA-1220-2000",
    13: "CBB-PRE-0109-1600 FEG-BRA-0109-1800 EEG-SIG-0109-1800 ALZ-ARR-0109-1800 BUF-HOS-0109-1800 POM-EUR-0109-2000 SAN-CAN-0110-1600 PNO-SGA-0110-2000",
    14: "SGA-CBB-0116-1200 CAN-FEG-0116-1800 ARR-POM-0116-1815 HOS-ALZ-0117-1000 SIG-SAN-0117-1200 EUR-EEG-0117-1930 PNO-BRA-0117-2000 PRE-BUF-0117-2000",
    15: "CBB-PNO-0123-1600 FEG-SIG-0123-1800 EEG-ARR-0123-1800 ALZ-PRE-0123-1800 BUF-SGA-0123-1800 POM-HOS-0123-2000 SAN-EUR-0124-1600 BRA-CAN-0124-1700",
    16: "BUF-CBB-0130-1800 ALZ-SGA-0130-1800 EEG-HOS-0130-1800 FEG-EUR-0130-1800 CAN-PNO-0130-1800 POM-PRE-0130-2000 SAN-ARR-0131-1600 BRA-SIG-0131-1700",
    17: "SGA-POM-0213-1200 CBB-ALZ-0213-1600 ARR-FEG-0213-1815 HOS-SAN-0214-1000 SIG-CAN-0214-1200 EUR-BRA-0214-1930 PNO-BUF-0214-2000 PRE-EEG-0214-2000",
    18: "ALZ-BUF-0220-1800 EEG-SGA-0220-1800 FEG-HOS-0220-1800 CAN-EUR-0220-1800 POM-CBB-0220-2000 SIG-PNO-0221-1200 SAN-PRE-0221-1600 BRA-ARR-0221-1700",
    19: "SGA-SAN-0227-1200 CBB-EEG-0227-1600 BUF-POM-0227-1800 ARR-CAN-0227-1815 HOS-BRA-0228-1000 EUR-SIG-0228-1930 PNO-ALZ-0228-2000 PRE-FEG-0228-2000",
    20: "EEG-BUF-0306-1800 FEG-SGA-0306-1800 CAN-HOS-0306-1800 POM-ALZ-0306-2000 SIG-ARR-0307-1200 SAN-CBB-0307-1600 BRA-PRE-0307-1700 EUR-PNO-0307-1930",
    21: "SGA-BRA-0313-1200 CBB-FEG-0313-1600 ALZ-EEG-0313-1800 BUF-SAN-0313-1800 ARR-EUR-0313-1815 HOS-SIG-0314-1000 PNO-POM-0314-2000 PRE-CAN-0314-2000",
    22: "EEG-POM-0320-1800 FEG-BUF-0320-1800 CAN-SGA-0320-1800 ARR-PNO-0320-1815 SIG-PRE-0321-1200 SAN-ALZ-0321-1600 BRA-CBB-0321-1700 EUR-HOS-0321-1930",
    23: "SGA-SIG-0403-1200 CBB-CAN-0403-1600 ALZ-FEG-0403-1800 BUF-BRA-0403-1800 POM-SAN-0403-2000 HOS-ARR-0404-1000 PNO-EEG-0404-2000 PRE-EUR-0404-2000",
    24: "FEG-POM-0410-1800 CAN-BUF-0410-1800 ARR-PRE-0410-1815 HOS-PNO-0411-1000 SIG-CBB-0411-1200 SAN-EEG-0411-1600 BRA-ALZ-0411-1700 EUR-SGA-0411-1930",
    25: "SGA-ARR-0417-1200 CBB-EUR-0417-1600 EEG-FEG-0417-1800 ALZ-CAN-0417-1800 BUF-SIG-0417-1800 POM-BRA-0417-2000 PNO-SAN-0418-2000 PRE-HOS-0418-2000",
    26: "FEG-SAN-0424-1800 CAN-POM-0424-1800 ARR-CBB-0424-1815 HOS-SGA-0425-1000 SIG-ALZ-0425-1200 BRA-EEG-0425-1700 EUR-BUF-0425-1930 PRE-PNO-0425-2000",
    27: "SGA-PRE-0501-1200 CBB-HOS-0501-1600 EEG-CAN-0501-1800 ALZ-EUR-0501-1800 BUF-ARR-0501-1800 POM-SIG-0501-2000 SAN-BRA-0502-1600 PNO-FEG-0502-2000",
    28: "SGA-PNO-0508-1200 CAN-SAN-0508-1800 ARR-ALZ-0508-1815 HOS-BUF-0509-1000 SIG-EEG-0509-1200 BRA-FEG-0509-1700 EUR-POM-0509-1930 PRE-CBB-0509-2000",
    29: "CBB-SGA-0515-1600 FEG-CAN-0515-1800 EEG-EUR-0515-1800 ALZ-HOS-0515-1800 BUF-PRE-0515-1800 POM-ARR-0515-2000 SAN-SIG-0516-1600 BRA-PNO-0516-1700",
    30: "SGA-BUF-0522-1200 CAN-BRA-0522-1800 ARR-EEG-0522-1815 HOS-POM-0523-1000 SIG-FEG-0523-1200 EUR-SAN-0523-1930 PRE-ALZ-0523-2000 PNO-CBB-0523-2000",
}
M = {}
for k, v in J.items():
    M[k] = []
    for s in v.split():
        h, a, d, t = s.split("-")
        mo = int(d[:2])
        M[k].append((h, a, datetime(2026 if mo >= 8 else 2027, mo, int(d[2:]), int(t[:2]), int(t[2:]), tzinfo=TZ)))
NUMS = sorted(M)
start = lambda j: min(m[2] for m in M[j])


def deadline(j):
    """Cierre de pronósticos: el sábado de esa jornada a las 00:01 (hora de Madrid)."""
    d = start(j).date()
    sat = d - timedelta(days=(d.weekday() - 5) % 7)
    return datetime(sat.year, sat.month, sat.day, 0, 1, tzinfo=TZ)

# ---------- Base de datos ----------
conn = st.connection("db", type="sql")


def run(q, **p):
    with conn.session as s:
        s.execute(text(q), p)
        s.commit()


@st.cache_resource
def init():
    run("CREATE TABLE IF NOT EXISTS players (name TEXT PRIMARY KEY, pin TEXT NOT NULL)")
    run("CREATE TABLE IF NOT EXISTS picks (name TEXT, jornada INT, idx INT, pick TEXT, PRIMARY KEY (name, jornada, idx))")
    run("CREATE TABLE IF NOT EXISTS results (jornada INT, idx INT, res TEXT, PRIMARY KEY (jornada, idx))")


init()
q = lambda sql, **p: conn.query(sql, params=p, ttl=0)
hpin = lambda n, pin: hashlib.sha256(f"bufala:{n.lower()}:{pin}".encode()).hexdigest()
fmt = lambda d: f"{DIAS[d.weekday()]} {d:%d/%m %H:%M}"

# ---------- Registro / acceso ----------
st.title("⚽ Quiniela Bufalà B")
st.caption("Juvenil Primera Divisió · Grup 6 · 2026-27 · 1 punto por acierto · +2 si aciertas el marcador del Bufalà")
if "user" not in st.session_state:
    st.subheader("Entra o regístrate")
    name = st.text_input("Tu nombre", max_chars=30).strip()
    pin = st.text_input("PIN de 4 cifras (invéntalo la primera vez)", type="password", max_chars=4)
    if st.button("Entrar / Registrarme", type="primary"):
        if not name or len(pin) != 4 or not pin.isdigit():
            st.error("Pon tu nombre y un PIN de 4 cifras.")
        else:
            row = q("SELECT pin FROM players WHERE lower(name)=:n", n=name.lower())
            if row.empty:
                run("INSERT INTO players VALUES (:n,:p)", n=name, p=hpin(name, pin))
                st.session_state["user"] = name
                st.rerun()
            elif row.iloc[0, 0] == hpin(name, pin):
                st.session_state["user"] = q("SELECT name FROM players WHERE lower(name)=:n", n=name.lower()).iloc[0, 0]
                st.rerun()
            else:
                st.error("Ese nombre ya existe y el PIN no coincide.")
    st.stop()

user = st.session_state["user"]
st.write(f"Hola, **{user}** 👋")
t1, t2, t3 = st.tabs(["Mi quiniela", "Clasificación", "Organizador"])

# ---------- Mi quiniela ----------
with t1:
    now = datetime.now(TZ)
    nxt = next((j for j in NUMS if start(j) > now), NUMS[-1])
    j = st.selectbox("Jornada", NUMS, index=NUMS.index(nxt), format_func=lambda x: f"Jornada {x} · {start(x):%d/%m}")
    locked = now >= deadline(j)
    dl = f"{DIAS[deadline(j).weekday()]} {deadline(j):%d/%m} a las 00:01"
    st.info(f"Jornada cerrada: el plazo terminó el {dl}." if locked else
            f"Elige 1 (gana el local), X (empate) o 2 (gana el visitante). Puedes cambiarla hasta el {dl}.")
    saved = dict(q("SELECT idx, pick FROM picks WHERE name=:n AND jornada=:j", n=user, j=j).values.tolist())
    with st.form(f"f{j}"):
        sel = {}
        for i, (h, a, dt) in enumerate(M[j]):
            if "BUF" in (h, a):
                st.markdown(f"⭐ **{T[h]} - {T[a]}** ({fmt(dt)}) · pon el marcador exacto")
                g1, g2 = saved[i].split("-") if "-" in saved.get(i, "") else (None, None)
                c1, c2 = st.columns(2)
                x = c1.number_input(T[h], 0, 20, value=int(g1) if g1 else None, step=1,
                                    disabled=locked, key=f"g{user}{j}{i}a")
                y = c2.number_input(T[a], 0, 20, value=int(g2) if g2 else None, step=1,
                                    disabled=locked, key=f"g{user}{j}{i}b")
                sel[i] = f"{int(x)}-{int(y)}" if x is not None and y is not None else None
            else:
                sel[i] = st.radio(f"{T[h]} - {T[a]}  ({fmt(dt)})", ["1", "X", "2"], horizontal=True,
                                  index=["1", "X", "2"].index(saved[i]) if saved.get(i) in ("1", "X", "2") else None,
                                  disabled=locked, key=f"p{user}{j}{i}")
        if st.form_submit_button("Guardar mi quiniela", disabled=locked, type="primary"):
            for i, v in sel.items():
                if v:
                    run("INSERT INTO picks VALUES (:n,:j,:i,:p) ON CONFLICT (name,jornada,idx) DO UPDATE SET pick=EXCLUDED.pick",
                        n=user, j=j, i=i, p=v)
            st.success("Guardada. Puedes cambiarla hasta el cierre.")
    if st.button("Cerrar sesión"):
        del st.session_state["user"]
        st.rerun()

# ---------- Clasificación ----------
with t2:
    df = q("SELECT p.name, p.jornada, p.pick, r.res FROM picks p "
           "JOIN results r ON r.jornada=p.jornada AND r.idx=p.idx WHERE r.res <> '-'")
    names = q("SELECT name FROM players")["name"]
    def outcome(v):
        if "-" in v:
            x, y = map(int, v.split("-"))
            return "1" if x > y else "2" if x < y else "X"
        return v

    def points(p, r):
        pts = int(outcome(p) == outcome(r))
        return pts + (BONUS if "-" in r and p == r else 0)

    if df.empty:
        st.write("Todavía no hay resultados cargados.")
    else:
        df["ok"] = [points(p, r) for p, r in zip(df.pick, df.res)]
        piv = df.pivot_table(index="name", columns="jornada", values="ok", aggfunc="sum", fill_value=0)
        piv = piv.reindex(names, fill_value=0).fillna(0).astype(int)
        piv.columns = [f"J{c}" for c in piv.columns]
        piv.insert(0, "Puntos", piv.sum(axis=1))
        piv = piv.sort_values("Puntos", ascending=False)
        piv.index = range(1, len(piv) + 1) if False else piv.index
        st.dataframe(piv, use_container_width=True)

# ---------- Organizador ----------
with t3:
    pw = st.text_input("Contraseña de organizador", type="password")
    if pw and pw == st.secrets.get("admin_password"):
        j2 = st.selectbox("Jornada a actualizar", NUMS, key="aj", format_func=lambda x: f"Jornada {x}")
        old = dict(q("SELECT idx, res FROM results WHERE jornada=:j", j=j2).values.tolist())
        with st.form("res"):
            out = {}
            for i, (h, a, dt) in enumerate(M[j2]):
                if "BUF" in (h, a):
                    o = old.get(i, "-")
                    g1, g2 = o.split("-") if o != "-" and "-" in o else (None, None)
                    st.markdown(f"⭐ **{T[h]} - {T[a]}** · marcador final")
                    c1, c2 = st.columns(2)
                    x = c1.number_input(T[h], 0, 20, value=int(g1) if g1 else None, step=1, key=f"ra{j2}{i}")
                    y = c2.number_input(T[a], 0, 20, value=int(g2) if g2 else None, step=1, key=f"rb{j2}{i}")
                    out[i] = f"{int(x)}-{int(y)}" if x is not None and y is not None else "-"
                else:
                    out[i] = st.radio(f"{T[h]} - {T[a]}", ["-", "1", "X", "2"], horizontal=True,
                                      index=["-", "1", "X", "2"].index(old.get(i, "-")) if old.get(i, "-") in ("-", "1", "X", "2") else 0,
                                      key=f"r{j2}{i}")
            if st.form_submit_button("Guardar resultados", type="primary"):
                for i, v in out.items():
                    run("INSERT INTO results VALUES (:j,:i,:r) ON CONFLICT (jornada,idx) DO UPDATE SET res=EXCLUDED.res",
                        j=j2, i=i, r=v)
                st.success("Resultados guardados.")
        env = q("SELECT name, COUNT(*) AS partidos FROM picks WHERE jornada=:j GROUP BY name", j=j2)
        st.write(f"Han enviado la jornada {j2}: {len(env)}")
        st.dataframe(env, use_container_width=True)
        st.subheader("Restablecer PIN")
        rn = st.selectbox("Jugador", list(q("SELECT name FROM players ORDER BY name")["name"]))
        np_ = st.text_input("Nuevo PIN (4 cifras)", max_chars=4)
        if st.button("Cambiar PIN") and len(np_) == 4 and np_.isdigit():
            run("UPDATE players SET pin=:p WHERE name=:n", p=hpin(rn, np_), n=rn)
            st.success("PIN cambiado.")
    elif pw:
        st.error("Contraseña incorrecta.")
