"""
Panel de Control — Costos Ocultos en Gastronomía (Demo)
Prototipo navegable que muestra cómo un sistema autónomo de control puede
exponer, en un solo panel, los 10 puntos críticos típicos de un restaurante:
administración financiera, desvíos, decomisos, energía, FIFO, estandarización,
selección de personal, inventario, capacitación de mozos y fichas técnicas.

Todos los datos son simulados — el panel está pensado para conectarse
a la información real de cada local (POS, sensores, planillas de stock).
"""

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# CONFIG
# ============================================================

DATA_DIR = Path(__file__).parent / "data"

st.set_page_config(
    page_title="Panel de Costos Ocultos — Demo",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# ESTILOS — Dark "control room" con acentos teal/ámbar
# ============================================================

st.markdown(
    """
<style>
    .stApp { background-color: #0b1220; }
    h1, h2, h3 { color: #e5e7eb !important; }
    .stMarkdown p { color: #cbd5e1; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #2dd4bf !important; }

    /* Tarjetas KPI */
    .kpi-card {
        background: #121b2e;
        border: 1px solid #1f2c45;
        border-radius: 14px;
        padding: 16px 18px;
        height: 100%;
    }
    .kpi-label { color: #94a3b8; font-size: 13px; margin: 0; }
    .kpi-value { color: #f1f5f9; font-size: 26px; font-weight: 800; margin: 2px 0 0 0; }
    .kpi-sub { font-size: 12px; margin-top: 4px; }
    .kpi-sub.bad { color: #f87171; }
    .kpi-sub.warn { color: #fbbf24; }
    .kpi-sub.good { color: #34d399; }

    /* Chips de estado */
    .chip {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
    }
    .chip-critico { background: rgba(248,113,113,0.15); color: #f87171; border: 1px solid rgba(248,113,113,0.4); }
    .chip-warn    { background: rgba(251,191,36,0.15); color: #fbbf24; border: 1px solid rgba(251,191,36,0.4); }
    .chip-ok      { background: rgba(52,211,153,0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.4); }
    .chip-neutral { background: rgba(148,163,184,0.15); color: #94a3b8; border: 1px solid rgba(148,163,184,0.4); }

    /* Banner superior */
    .hero {
        padding: 18px 22px;
        border-radius: 16px;
        background: linear-gradient(135deg, #0f3a35 0%, #0b1220 70%);
        border: 1px solid #1f3d3a;
        margin-bottom: 18px;
    }
    .hero-title { color: #f1f5f9; font-size: 30px; font-weight: 800; margin: 0; }
    .hero-sub { color: #99e6d8; font-size: 14px; margin-top: 6px; }

    /* Filas de tabla simple */
    .row-card {
        background: #121b2e;
        border: 1px solid #1f2c45;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .row-title { color: #f1f5f9; font-weight: 700; font-size: 14px; }
    .row-detail { color: #94a3b8; font-size: 12px; }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# CARGA DE DATOS
# ============================================================

def load_json(name: str) -> dict:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


financiero = load_json("financiero.json")
inventario = load_json("inventario.json")["productos"]
decomisos = load_json("decomisos.json")["registros"]
energia = load_json("energia.json")
fichas = load_json("fichas_tecnicas.json")["platos"]
equipo = load_json("equipo.json")

ARS = lambda v: f"${v:,.0f}".replace(",", ".")
# En textos markdown puros, "$" se interpreta como delimitador de fórmula (LaTeX);
# esta variante escapa el signo para que se muestre literal cuando hay varios montos en una línea.
ARS_md = lambda v: ARS(v).replace("$", r"\$")

# ------------------------------------------------------------
# Tablas derivadas — se calculan una vez y se reutilizan en los
# KPIs (popovers de detalle) y en cada pestaña.
# ------------------------------------------------------------
df_fin = pd.DataFrame(financiero["dias"]).sort_values("hace_dias", ascending=False)
df_fin["día"] = df_fin["hace_dias"].apply(lambda d: f"-{d}d")
df_fin["costo_objetivo"] = df_fin["ingresos"] * df_fin["costo_objetivo_pct"]
df_fin["brecha"] = df_fin["costos"] - df_fin["costo_objetivo"]

df_inv = pd.DataFrame(inventario).sort_values("dias_restantes")
df_dec = pd.DataFrame(decomisos)
no_declarados = df_dec[~df_dec["declarado"]]

# ============================================================
# HEADER + KPIs GLOBALES
# ============================================================

st.markdown(
    """
<div class="hero">
    <p class="hero-title">🔍 Panel de Costos Ocultos — Demo</p>
    <p class="hero-sub">
        Prototipo de sistema autónomo de control para gastronomía · datos simulados,
        listo para conectarse a la información real de tu local (POS, stock, sensores).
    </p>
</div>
""",
    unsafe_allow_html=True,
)

resumen_fin = financiero["resumen_30_dias"]
productos_riesgo = sum(1 for p in inventario if p["dias_restantes"] <= 2)
total_decomisos = sum(d["costo_estimado"] for d in decomisos)
decomisos_no_declarados = sum(1 for d in decomisos if not d["declarado"])
energia_resumen = energia["resumen"]

productos_en_riesgo = df_inv[df_inv["dias_restantes"] <= 2]
zonas_con_alerta = [z for z in energia["zonas"] if z["alerta"]]
peores_dias = df_fin.sort_values("brecha", ascending=False).head(5)

kpi_cols = st.columns(4)
kpis = [
    ("Costos ocultos detectados (30 días)", ARS(resumen_fin["costos_ocultos_estimados"]),
     f"Costo real {resumen_fin['costo_real_pct']*100:.1f}% vs. objetivo {resumen_fin['costo_objetivo_pct']*100:.0f}%", "bad"),
    ("Productos en riesgo de vencer (≤48 h)", f"{productos_riesgo}",
     "Sin alerta automática, se pierden sin que nadie lo note", "warn"),
    ("Decomisos del mes sin declarar", ARS(sum(d['costo_estimado'] for d in decomisos if not d['declarado'])),
     f"{decomisos_no_declarados} de {len(decomisos)} registros no se cargaron en el sistema", "bad"),
    ("Energía desperdiciada estimada / mes", ARS(energia_resumen["costo_estimado_mensual_total"]),
     f"{energia_resumen['alertas_activas']} zonas con consumo fuera de horario", "warn"),
]
for col, (label, value, sub, tone) in zip(kpi_cols, kpis):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <p class="kpi-label">{label}</p>
                <p class="kpi-value">{value}</p>
                <p class="kpi-sub {tone}">{sub}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.popover("🔎 Ver detalle", use_container_width=True):
            if label.startswith("Costos ocultos"):
                st.markdown("**¿De dónde sale esta brecha de "
                            f"{ARS(resumen_fin['costos_ocultos_estimados'])}?**")
                st.caption("Los 5 días del mes con mayor desvío entre el costo real y el costo objetivo (32%):")
                for _, d in peores_dias.iterrows():
                    st.markdown(f"- Hace **{d['hace_dias']} días** → costo real {ARS_md(d['costos'])} "
                                f"vs. objetivo {ARS_md(d['costo_objetivo'])} · brecha de **{ARS_md(d['brecha'])}**")
                st.caption("El sistema marca estos picos apenas ocurren — no hace falta esperar al cierre de mes para verlos.")

            elif label.startswith("Productos en riesgo"):
                st.markdown(f"**{len(productos_en_riesgo)} productos** que se vencen hoy o mañana "
                            "y todavía no se usaron:")
                for _, p in productos_en_riesgo.iterrows():
                    st.markdown(f"- **{p['nombre']}** — {p['cantidad']} {p['unidad']} · "
                                f"vence en {p['dias_restantes']} día(s) · valor {ARS(p['cantidad']*p['costo_unitario'])}")
                st.caption("La recomendación de uso (orden FIFO) está en la pestaña 📦 Inventario & FIFO.")

            elif label.startswith("Decomisos"):
                st.markdown(f"**{len(no_declarados)} de {len(df_dec)} pérdidas** que el sistema detectó "
                            "cruzando stock contra ventas — y que nadie cargó como decomiso:")
                for _, d in no_declarados.sort_values("costo_estimado", ascending=False).head(6).iterrows():
                    st.markdown(f"- **{d['producto']}** — {d['cantidad']} · {d['motivo']} · "
                                f"costo estimado {ARS(d['costo_estimado'])} (hace {d['hace_dias']} días)")
                st.caption("El detalle completo, con el motivo de cada pérdida, está en la pestaña 🗑️ Decomisos.")

            else:  # Energía desperdiciada
                st.markdown(f"**{len(zonas_con_alerta)} zonas** consumiendo energía fuera de horario "
                            "o sin necesidad real:")
                for z in zonas_con_alerta:
                    st.markdown(f"- **{z['nombre']}** ({z['tipo']}) — {z['actividad']} · "
                                f"sobrecosto estimado {ARS(z['costo_estimado_mensual'])}/mes")
                st.caption("Con sensores de movimiento y temperatura, el sistema corrige esto automáticamente — sin esperar a que alguien lo note.")

st.write("")

# ============================================================
# TABS
# ============================================================

tab_resumen, tab_inventario, tab_decomisos, tab_energia, tab_fichas, tab_equipo = st.tabs(
    [
        "📊 Resumen financiero",
        "📦 Inventario & FIFO",
        "🗑️ Decomisos",
        "⚡ Energía",
        "📋 Fichas técnicas",
        "👥 Equipo & capacitación",
    ]
)

# ------------------------------------------------------------
# TAB 1 — Resumen financiero (puntos 1 y 2: gasto ineficiente y desvíos)
# ------------------------------------------------------------
with tab_resumen:
    st.subheader("¿Cuánto debería costar tu operación vs. cuánto te está costando?")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_fin["día"], y=df_fin["ingresos"], name="Ingresos",
                             line=dict(color="#2dd4bf", width=2)))
    fig.add_trace(go.Scatter(x=df_fin["día"], y=df_fin["costos"], name="Costo real",
                             line=dict(color="#f87171", width=2)))
    fig.add_trace(go.Scatter(x=df_fin["día"], y=df_fin["costo_objetivo"], name="Costo objetivo (32%)",
                             line=dict(color="#fbbf24", width=2, dash="dash")))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0b1220", plot_bgcolor="#0b1220",
        height=380, margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos (30 días)", ARS(resumen_fin["total_ingresos"]))
    c2.metric("Costo de mercadería real", ARS(resumen_fin["total_costos"]),
              f"{resumen_fin['costo_real_pct']*100:.1f}% sobre ventas")
    c3.metric("Brecha vs. costo objetivo", ARS(resumen_fin["costos_ocultos_estimados"]),
              delta=f"+{(resumen_fin['costo_real_pct'] - resumen_fin['costo_objetivo_pct'])*100:.1f} pts", delta_color="inverse")

    st.info(
        "💡 **Lectura para el dueño:** la brecha entre la línea roja y la amarilla no es 'mala suerte', "
        "es la suma de los otros 5 paneles de este sistema — decomisos no cargados, vencimientos, "
        "energía mal gestionada y platos sin ficha técnica. El sistema autónomo conecta estos puntos "
        "automáticamente, en vez de que alguien los descubra a fin de mes mirando el balance."
    )

# ------------------------------------------------------------
# TAB 2 — Inventario & FIFO (puntos 5 y 8)
# ------------------------------------------------------------
with tab_inventario:
    st.subheader("¿Qué tenés, dónde está y qué hay que usar primero?")
    st.caption("Orden automático por fecha de vencimiento — así nunca más se pierde algo por no saber qué había.")

    valor_total = (df_inv["cantidad"] * df_inv["costo_unitario"]).sum()
    en_riesgo = df_inv[df_inv["dias_restantes"] <= 2]
    valor_en_riesgo = (en_riesgo["cantidad"] * en_riesgo["costo_unitario"]).sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Valor total de inventario", ARS(valor_total))
    c2.metric("Productos a usar HOY o MAÑANA", f"{len(en_riesgo)}")
    c3.metric("Valor en riesgo de pérdida", ARS(valor_en_riesgo), delta_color="inverse")

    st.markdown("##### Orden de uso recomendado (FIFO automático)")
    for _, p in df_inv.head(8).iterrows():
        if p["dias_restantes"] <= 1:
            chip, texto = "chip-critico", f"Usar HOY · vence en {p['dias_restantes']} día"
        elif p["dias_restantes"] <= 3:
            chip, texto = "chip-warn", f"Usar en los próximos {p['dias_restantes']} días"
        else:
            chip, texto = "chip-ok", f"Margen de {p['dias_restantes']} días"
        st.markdown(
            f"""
            <div class="row-card">
                <span class="row-title">{p['nombre']}</span>
                &nbsp;<span class="chip {chip}">{texto}</span>
                <div class="row-detail">{p['cantidad']} {p['unidad']} · {p['categoria']} ·
                ingresó hace {p['ingreso_hace_dias']} días · valor {ARS(p['cantidad']*p['costo_unitario'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Ver inventario completo"):
        st.dataframe(
            df_inv[["nombre", "categoria", "cantidad", "unidad", "dias_restantes", "costo_unitario"]]
            .rename(columns={"nombre": "Producto", "categoria": "Categoría", "cantidad": "Cantidad",
                             "unidad": "Unidad", "dias_restantes": "Días restantes", "costo_unitario": "Costo unitario ($)"}),
            use_container_width=True, hide_index=True,
        )

# ------------------------------------------------------------
# TAB 3 — Decomisos (punto 3)
# ------------------------------------------------------------
with tab_decomisos:
    st.subheader("Lo que se tira también es plata — y casi nunca queda registrado")

    no_decl = no_declarados

    c1, c2, c3 = st.columns(3)
    c1.metric("Pérdida total estimada (30 días)", ARS(df_dec["costo_estimado"].sum()))
    c2.metric("Registrada formalmente", ARS(df_dec[df_dec["declarado"]]["costo_estimado"].sum()))
    c3.metric("Sin declarar (descubierta por el sistema)", ARS(no_decl["costo_estimado"].sum()), delta_color="inverse")

    fig = go.Figure(go.Bar(
        x=df_dec.groupby("motivo")["costo_estimado"].sum().sort_values(ascending=True).values,
        y=df_dec.groupby("motivo")["costo_estimado"].sum().sort_values(ascending=True).index,
        orientation="h", marker_color="#f87171",
    ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0b1220", plot_bgcolor="#0b1220",
        height=320, margin=dict(l=10, r=10, t=30, b=10),
        title="Pérdida acumulada por motivo ($)",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### Últimos registros")
    for _, d in df_dec.sort_values("hace_dias").head(6).iterrows():
        chip = "chip-ok" if d["declarado"] else "chip-critico"
        texto = "Declarado" if d["declarado"] else "No declarado — detectado por el sistema"
        st.markdown(
            f"""
            <div class="row-card">
                <span class="row-title">{d['producto']}</span>
                &nbsp;<span class="chip {chip}">{texto}</span>
                <div class="row-detail">Hace {d['hace_dias']} días · {d['cantidad']} · motivo: {d['motivo']} ·
                costo estimado {ARS(d['costo_estimado'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.warning(
        "⚠️ El sistema cruza salida de stock contra ventas registradas: si algo entró y no se vendió "
        "ni se cargó como decomiso, queda marcado como **pérdida fantasma** — automáticamente, sin que nadie tenga que acordarse de avisar."
    )

# ------------------------------------------------------------
# TAB 4 — Energía (punto 4)
# ------------------------------------------------------------
with tab_energia:
    st.subheader("Luces, cámaras y equipos: el costo invisible que se paga todos los meses")

    c1, c2 = st.columns(2)
    c1.metric("Costo estimado de desperdicio / mes", ARS(energia_resumen["costo_estimado_mensual_total"]))
    c2.metric("Proyección anual si no se corrige", ARS(energia_resumen["costo_estimado_anual"]), delta_color="inverse")

    for z in energia["zonas"]:
        chip = "chip-critico" if z["alerta"] else "chip-ok"
        texto = "⚠ Alerta activa" if z["alerta"] else "Normal"
        extra = f" · sobrecosto estimado {ARS(z['costo_estimado_mensual'])}/mes" if z["alerta"] else ""
        st.markdown(
            f"""
            <div class="row-card">
                <span class="row-title">{z['nombre']}</span>
                &nbsp;<span class="chip {chip}">{texto}</span>
                <div class="row-detail">{z['tipo']} · estado: {z['estado']} · {z['actividad']}{extra}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info(
        "💡 Con sensores simples de movimiento y temperatura, el sistema apaga automáticamente lo que "
        "nadie está usando y avisa cuando una cámara queda abierta — sin depender de que el personal se acuerde."
    )

# ------------------------------------------------------------
# TAB 5 — Fichas técnicas (puntos 6 y 10)
# ------------------------------------------------------------
with tab_fichas:
    st.subheader("¿Cada plato tiene una receta con costo definido — o se cocina 'a ojo'?")

    df_f = pd.DataFrame(fichas)
    df_f["margen_real"] = (df_f["precio_venta"] - df_f["costo_real"]) / df_f["precio_venta"]
    df_f["desvio_costo"] = df_f["costo_real"] - df_f["costo_teorico"]
    sin_ficha = df_f[~df_f["tiene_ficha"]]

    c1, c2, c3 = st.columns(3)
    c1.metric("Platos sin ficha técnica", f"{len(sin_ficha)} de {len(df_f)}")
    c2.metric("Sobrecosto acumulado por falta de estandarización", ARS(df_f["desvio_costo"].clip(lower=0).sum()))
    c3.metric("Margen promedio real vs. objetivo",
              f"{df_f['margen_real'].mean()*100:.0f}%",
              f"objetivo promedio {df_f['margen_objetivo'].mean()*100:.0f}%", delta_color="off")

    for _, p in df_f.sort_values("desvio_costo", ascending=False).iterrows():
        bajo_objetivo = p["margen_real"] < p["margen_objetivo"]
        chip_ficha = "chip-ok" if p["tiene_ficha"] else "chip-critico"
        texto_ficha = "Con ficha técnica" if p["tiene_ficha"] else "Sin ficha — costo no estandarizado"
        chip_margen = "chip-warn" if bajo_objetivo else "chip-ok"
        texto_margen = f"Margen real {p['margen_real']*100:.0f}% (objetivo {p['margen_objetivo']*100:.0f}%)"
        st.markdown(
            f"""
            <div class="row-card">
                <span class="row-title">{p['nombre']}</span>
                &nbsp;<span class="chip {chip_ficha}">{texto_ficha}</span>
                &nbsp;<span class="chip {chip_margen}">{texto_margen}</span>
                <div class="row-detail">Costo teórico {ARS(p['costo_teorico'])} · costo real {ARS(p['costo_real'])} ·
                desvío {ARS(p['desvio_costo'])} · precio de venta {ARS(p['precio_venta'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info(
        "💡 Cuando el costo real se aleja del teórico, el sistema lo señala plato por plato — "
        "generalmente es la huella de un decomiso, una porción servida de más, o un insumo que subió de precio "
        "y nadie actualizó la ficha."
    )

# ------------------------------------------------------------
# TAB 6 — Equipo & capacitación (puntos 7 y 9)
# ------------------------------------------------------------
with tab_equipo:
    st.subheader("Lo que el mozo no sabe vender, también es un costo oculto")

    res_eq = equipo["resumen"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Rotación anual estimada del salón", f"{res_eq['rotacion_anual_estimada']*100:.0f}%")
    c2.metric("Antigüedad promedio", f"{res_eq['promedio_antiguedad_meses']:.1f} meses")
    c3.metric("Conocimiento promedio del menú", f"{res_eq['promedio_conocimiento_menu']*100:.0f}%")

    for m in sorted(equipo["mozos"], key=lambda x: x["conocimiento_menu"]):
        pct = m["conocimiento_menu"]
        chip = "chip-critico" if pct < 0.5 else ("chip-warn" if pct < 0.75 else "chip-ok")
        st.markdown(f"**{m['nombre']}** — {pct*100:.0f}% de conocimiento del menú "
                    f"<span class='chip {chip}'>{'Necesita capacitación' if pct < 0.5 else ('Reforzar' if pct < 0.75 else 'Sólido')}</span>",
                    unsafe_allow_html=True)
        st.progress(pct)
        st.caption(f"{m['antiguedad_meses']} meses en el puesto · última capacitación hace {m['ultima_capacitacion_dias']} días")

    st.info(
        "💡 El sistema no reemplaza la selección de personal, pero sí estandariza la evaluación: "
        "mide qué sabe cada uno del menú del día, detecta quién necesita repaso antes de salir al salón, "
        "y deja de depender de que 'alguien le explique' al nuevo el primer día."
    )

st.write("")
st.caption(
    "Demo construida sobre los 10 puntos críticos de costos ocultos en gastronomía — "
    "datos 100% simulados. El mismo panel se conecta a información real (POS, planillas de stock, "
    "sensores de temperatura/movimiento) en una implementación a medida."
)
